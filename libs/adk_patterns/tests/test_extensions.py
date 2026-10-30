import os
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch, MagicMock
from google.genai import types
from adk_patterns import LocalSession
from adk_patterns import observability
from test_patterns import example, outputs


async def reply(client, sid, events, decision, notes=""):
    calls = [p.function_call for e in events if e.content for p in e.content.parts or []
             if p.function_call and p.function_call.name == "adk_request_input"]
    if len(calls) != 1:
        raise AssertionError(f"expected one pause, got {len(calls)}")
    call = calls[0]
    message = types.Content(role="user", parts=[types.Part(function_response=types.FunctionResponse(
        id=call.id, name=call.name, response={"decision":decision,"notes":notes}))])
    return [e async for e in client.stream(sid, message)]


class ReviewedTests(unittest.IsolatedAsyncioTestCase):
    async def setup_client(self):
        client = LocalSession(example("reviewed_digest"))
        self.addAsyncCleanup(client.close)
        sid = await client.create()
        events = [e async for e in client.stream(sid, "AI")]
        return client, sid, events

    async def test_rewrite_preserves_sources_and_then_approves(self):
        client, sid, events = await self.setup_client()
        events = await reply(client, sid, events, "revise", "更简洁")
        self.assertIn("更简洁", (await client.state(sid))["review_draft"])
        self.assertEqual(len((await client.state(sid))["source_material"]), 2)
        events = await reply(client, sid, events, "approve")
        self.assertTrue(any(isinstance(e.output, dict) and e.output.get("status") == "approved" for e in events))
        self.assertIn("更简洁", (await client.state(sid))["final_markdown"])

    async def test_reject_and_revision_limit(self):
        for decisions, status in [(["reject"], "rejected"), (["revise"]*3, "exhausted")]:
            client, sid, events = await self.setup_client()
            for decision in decisions:
                events = await reply(client, sid, events, decision, "修改")
            self.assertTrue(any(isinstance(e.output, dict) and e.output.get("status") == status for e in events))
            self.assertNotIn("final_markdown", await client.state(sid))


class TracingTests(unittest.TestCase):
    def setUp(self):
        self.old_provider = observability._provider
        self.old_config = observability._configuration
        observability._provider = observability._configuration = None

    def tearDown(self):
        observability._provider = self.old_provider
        observability._configuration = self.old_config

    def test_disabled_and_missing_endpoint(self):
        self.assertIsNone(observability.enable_phoenix("test", enabled=False))
        with patch.dict(os.environ, {}, clear=True), self.assertRaises(ValueError):
            observability.enable_phoenix("test")

    def test_official_registration_and_idempotence(self):
        with patch('phoenix.otel.register') as register:
            endpoint = 'http://127.0.0.1:6006/v1/traces'
            first = observability.enable_phoenix("test", endpoint=endpoint)
            self.assertIs(first, observability.enable_phoenix("test", endpoint=endpoint))
            register.assert_called_once_with(project_name="test",endpoint=endpoint,
                protocol="http/protobuf",batch=True,auto_instrument=True,verbose=False)
            with self.assertRaises(RuntimeError):
                observability.enable_phoenix("other", endpoint=endpoint)

    def test_native_keeps_other_processors(self):
        # Separate process because OTEL's global provider can only be installed once.
        script = '''
from unittest.mock import patch
from opentelemetry import trace
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from adk_patterns import enable_phoenix
first, second = InMemorySpanExporter(), InMemorySpanExporter()
with patch('phoenix.otel.HTTPSpanExporter', return_value=first):
    provider = enable_phoenix('test', mode='native', endpoint='http://localhost:6006/v1/traces', batch=False)
provider.add_span_processor(SimpleSpanProcessor(second))
with trace.get_tracer('test').start_as_current_span('coexistence'):
    pass
provider.force_flush()
assert len(first.get_finished_spans()) == len(second.get_finished_spans()) == 1
assert first.get_finished_spans()[0].resource.attributes['openinference.project.name'] == 'test'
import asyncio
from google.adk import Event
from adk_patterns import LocalSession, sequence

def step(node_input: str):
    return Event(output="done")

async def run():
    client = LocalSession(sequence("traced_flow", step))
    try:
        sid = await client.create()
        async for event in client.stream(sid, "test"):
            pass
    finally:
        await client.close()

asyncio.run(run())
provider.force_flush()
assert len(first.get_finished_spans()) > 1, "ADK produced no spans"
assert len(first.get_finished_spans()) == len(second.get_finished_spans())
provider.shutdown()
'''
        result = subprocess.run([sys.executable, '-c', script], capture_output=True, text=True, timeout=20)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
