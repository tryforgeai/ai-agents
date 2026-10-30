import base64
from decimal import Decimal
import tempfile
from pathlib import Path
from types import SimpleNamespace as NS
import unittest
from unittest.mock import MagicMock, patch
from pydantic import BaseModel, ValidationError

from llm_patterns import *


class Patterns(unittest.TestCase):
    def test_prompt_examples(self):
        self.assertIn("Objective", PromptSpec("context", "task").render())
        messages = few_shot_messages("instruction", [("a", "b")], "c")
        self.assertEqual([m["role"] for m in messages], ["system", "user", "assistant", "user"])

    def test_chain_preserves_all_results_and_isolates_mutation(self):
        result = run_chain(3, [Step("first", lambda s: s["input"] + 1),
                               Step("second", lambda s: s["first"] * s["input"])])
        self.assertEqual(result, {"input": 3, "first": 4, "second": 12})
        with self.assertRaises(ValueError):
            run_chain(1, [Step("input", lambda s: 0)])

    def test_votes_are_separate_calls_and_ties_abstain(self):
        sample = MagicMock(side_effect=[1, 1, 2])
        self.assertEqual(sample_vote(sample)["winner"], 1)
        self.assertEqual(sample.call_count, 3)
        self.assertIsNone(sample_vote(iter([1, 2]).__next__, samples=2)["winner"])

    def test_refinement_success_and_exhaustion(self):
        review = lambda v: (v >= 2, "increase")
        revise = lambda v, f: v + 1
        self.assertEqual(refine(0, review, revise)["result"], 2)
        self.assertEqual(refine(0, review, revise, max_revisions=1)["status"], "exhausted")
        with self.assertRaises(TypeError):
            refine(0, lambda v: ("false", "x"), revise)

    def test_vision_mime_uses_content_and_limit(self):
        png = base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+jRZkAAAAASUVORK5CYII=')
        with tempfile.TemporaryDirectory() as folder:
            p = Path(folder) / 'wrong.jpg'
            p.write_bytes(png)
            self.assertTrue(image_data_url(p).startswith('data:image/png;base64,'))
            self.assertEqual(len(vision_messages('describe', [p])[0]['content']), 2)
            with self.assertRaises(ValueError):
                image_data_url(p, max_bytes=1)
            p.write_text('not an image')
            with self.assertRaises(ValueError):
                image_data_url(p)

    def test_decimal_and_dates(self):
        self.assertEqual(days_between('2020-07-22', '2021-12-01'), 497)
        self.assertEqual(sum_amounts(['0.1', '0.2']), Decimal('0.3'))
        for value, error in [(0.1, TypeError), ('NaN', ValueError)]:
            with self.assertRaises(error): sum_amounts([value])

    def test_routing_abstentions(self):
        report = routing_report([None, 'clean', 'summary'], ['clean', None, 'summary'])
        self.assertEqual(report['false_triggers'], 1)
        self.assertEqual(report['missed_triggers'], 1)
        self.assertAlmostEqual(report['accuracy'], 1/3)

    def test_tool_observations_and_limits(self):
        class Args(BaseModel):
            value: int
        def decide(request, history):
            if history:
                self.assertEqual(history[0]['observation']['value'], 4)
                return {'kind': 'finish', 'answer': '4'}
            return {'kind': 'tool', 'tool': 'double', 'arguments': {'value': 2}}
        tools = {'double': Tool(Args, lambda value: value * 2)}
        self.assertEqual(run_tool_loop('double', decide, tools)['answer'], '4')
        self.assertEqual(run_tool_loop('double', decide, tools, max_steps=1)['status'], 'exhausted')
        with self.assertRaises(ValueError):
            run_tool_loop('x', lambda *_: {'kind': 'tool', 'tool': 'shell'}, tools)
        with self.assertRaises(ValidationError):
            Action.model_validate({'kind':'tool','tool':'double','observation':'fake'})

    def test_tool_errors_are_not_success(self):
        class Args(BaseModel):
            value: int
        result = run_tool_loop('x', lambda *_: {'kind':'tool','tool':'divide','arguments':{'value':0}},
                               {'divide':Tool(Args, lambda value: 1/value)}, max_steps=1)
        self.assertFalse(result['history'][0]['observation']['ok'])

    def test_client_text_and_empty(self):
        raw = MagicMock()
        raw.chat.completions.create.return_value = NS(choices=[NS(message=NS(content='hello'))])
        client = CompletionClient('test', raw_client=raw)
        self.assertEqual(client.complete('hi'), 'hello')
        with self.assertRaises(ValueError): client.complete('hi', messages=[])
        raw.chat.completions.create.return_value = NS(choices=[])
        with self.assertRaises(ValueError): client.complete('hi')
        client.close()
        raw.close.assert_not_called()

    def test_instructor_schema_then_raw(self):
        import httpx
        from openai import OpenAI
        class Answer(BaseModel):
            value: int
        calls = []
        def handler(request):
            calls.append(request)
            return httpx.Response(200, json={"id":"test", "object":"chat.completion", "created":0,
                "model":"test", "choices":[{"index":0,"finish_reason":"stop",
                    "message":{"role":"assistant","content":'{"value": 4}'}}],
                "usage":{"prompt_tokens":1,"completion_tokens":1,"total_tokens":2}})
        raw = OpenAI(api_key='test', http_client=httpx.Client(transport=httpx.MockTransport(handler)))
        try:
            client = CompletionClient('test', raw_client=raw)
            self.assertEqual(client.complete('give value', response_model=Answer).value, 4)
            self.assertEqual(client.complete('give text'), '{"value": 4}')
            self.assertEqual(len(calls), 2)
        finally:
            raw.close()

if __name__ == '__main__':
    unittest.main()
