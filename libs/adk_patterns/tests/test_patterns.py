"""真实 ADK Runner 的离线集成测试，不调用模型或外部服务器。"""
import importlib.util
from pathlib import Path
import unittest

from google.genai import types
from pydantic import ValidationError
from adk_patterns import (
    LocalSession, ApprovalDecision, ModelConfig, bounded_loop, mcp_http,
)

ROOT = Path(__file__).resolve().parents[1]


def example(name):
    spec = importlib.util.spec_from_file_location(
        f"example_{name}", ROOT / "examples" / name / "agent.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.root_agent


async def outputs(client, session_id, message):
    events = [event async for event in client.stream(session_id, message)]
    errors = [e.error_message for e in events if e.error_message]
    if errors:
        raise AssertionError(errors)
    return [e.output for e in events if e.output is not None]


class PatternTests(unittest.IsolatedAsyncioTestCase):
    async def run_example(self, name, message):
        client = LocalSession(example(name))
        self.addAsyncCleanup(client.close)
        sid = await client.create()
        return await outputs(client, sid, message)

    async def test_calculator_uses_input_and_validates(self):
        result = await self.run_example("calculator", {"a": 7, "b": 8})
        self.assertIn({"a": 7, "b": 8, "sum": 15}, result)
        with self.assertLogs("google_adk", level="ERROR"), self.assertRaises(ValidationError):
            await self.run_example("calculator", {"a": "invalid"})

    async def test_session_continuity_and_isolation(self):
        client = LocalSession(example("counter"))
        self.addAsyncCleanup(client.close)
        one, two = await client.create(), await client.create()
        await outputs(client, one, "go")
        await outputs(client, one, "go")
        await outputs(client, two, "go")
        self.assertEqual((await client.state(one))["attempts"], 2)
        self.assertEqual((await client.state(two))["attempts"], 1)

    async def test_routing_preserves_payload(self):
        for message, handler in [("请总结", "summary"), ("修复错误", "support")]:
            result = await self.run_example("routing", message)
            self.assertIn({"handler": handler, "request": message}, result)
            self.assertFalse(any(isinstance(x, dict) and x.get("handler") not in
                                 (None, handler) for x in result))

    async def test_parallel_join(self):
        result = await self.run_example("parallel", "hello world")
        self.assertIn({"length": 11, "uppercase": "HELLO WORLD"}, result)

    async def test_loop_success_limit_and_reset(self):
        result = await self.run_example("loop", "0")
        self.assertIn({"result": 3, "iterations": 3, "status": "completed"}, result)
        result = await self.run_example("loop", "-10")
        self.assertIn({"result": -5, "iterations": 5, "status": "exhausted"}, result)
        client = LocalSession(example("loop"))
        self.addAsyncCleanup(client.close)
        sid = await client.create()
        await outputs(client, sid, "0")
        result = await outputs(client, sid, "2")
        self.assertIn({"result": 3, "iterations": 1, "status": "completed"}, result)

    async def test_approval_emits_request(self):
        client = LocalSession(example("approval"))
        self.addAsyncCleanup(client.close)
        sid = await client.create()
        events = [event async for event in client.stream(sid, "增加输入校验")]
        serialized = "\n".join(e.model_dump_json() for e in events)
        self.assertIn("approve", serialized)
        self.assertNotIn("approval_decision", await client.state(sid))

    async def test_approval_resume_all_decisions(self):
        for decision in ("approve", "revise", "reject"):
            client = LocalSession(example("approval"))
            self.addAsyncCleanup(client.close)
            sid = await client.create()
            events = [e async for e in client.stream(sid, "修改 Notebook")]
            calls = [p.function_call for e in events if e.content
                     for p in e.content.parts or [] if p.function_call
                     and p.function_call.name == "adk_request_input"]
            self.assertEqual(len(calls), 1)
            response = types.Content(role="user", parts=[types.Part(
                function_response=types.FunctionResponse(
                    name=calls[0].name, id=calls[0].id,
                    response={"decision": decision, "notes": "测试意见"},
                ))])
            result = await outputs(client, sid, response)
            self.assertIn({"decision": decision, "notes": "测试意见"}, result)
            self.assertEqual((await client.state(sid))["approval_decision"], decision)

    def test_approval_validation(self):
        self.assertEqual(ApprovalDecision(decision="revise", notes=None).notes, "")
        with self.assertRaises(ValidationError):
            ApprovalDecision(decision="maybe")

    def test_config_and_bounds(self):
        with self.assertRaises(ValueError):
            ModelConfig(" ")
        self.assertNotIn("secret", repr(ModelConfig("gpt-4o-mini", api_key="secret")))
        with self.assertRaises(ValueError):
            bounded_loop("invalid", lambda x: x, lambda x: False, max_iterations=0)

    async def test_mcp_construction(self):
        tool = mcp_http("http://127.0.0.1:9000/mcp")
        await tool.close()


class WebTests(unittest.TestCase):
    def test_web_discovers_and_runs_calculator(self):
        from fastapi.testclient import TestClient
        from google.adk.cli.fast_api import get_fast_api_app
        app = get_fast_api_app(agents_dir=str(ROOT / "examples"),
                               web=True, use_local_storage=False)
        with TestClient(app) as client:
            response = client.get("/list-apps")
            response.raise_for_status()
            self.assertIn("calculator", response.json())
            client.post("/apps/calculator/users/tester/sessions/web_test",
                        json={}).raise_for_status()
            response = client.post("/run", json={
                "appName": "calculator", "userId": "tester", "sessionId": "web_test",
                "newMessage": {"role": "user", "parts": [{"text": '{"a":7,"b":8}'}]},
            })
            response.raise_for_status()
            self.assertTrue(any(e.get("output", {}).get("sum") == 15
                                for e in response.json()
                                if isinstance(e.get("output"), dict)))


if __name__ == "__main__":
    unittest.main()
