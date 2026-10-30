"""Allowlisted runnable examples. No eval/exec of user-supplied Python."""
import base64
import contextlib
import io
import os
from pathlib import Path
import tempfile
from typing import Any

import adk_patterns as adk
import llm_patterns as llm
from google.adk import Event
from google.genai import types
from pydantic import BaseModel, ConfigDict, Field


class Summary(BaseModel):
    summary: str
    keywords: list[str] = Field(min_length=3)


class Dates(BaseModel):
    model_config = ConfigDict(extra='forbid')
    start: str
    end: str


def prompt_spec(data):
    return llm.PromptSpec(**data).render()


def few_shot(data):
    return llm.few_shot_messages(data['instruction'], data['examples'], data['query'])


def chain(data):
    # Deterministic example: full original input and prior results remain accessible.
    return llm.run_chain(data['text'], [
        llm.Step('normalize', lambda s: ' '.join(s['input'].split())),
        llm.Step('summary', lambda s: {'original':s['input'], 'normalized':s['normalize'],
                                      'characters':len(s['normalize'])}),
    ])


def vote(data):
    # These are supplied sample values, not claims of independent model calls.
    samples = data['samples']
    return llm.sample_vote(iter(samples).__next__, samples=len(samples))


def refinement(data):
    return llm.refine(data['draft'],
        review=lambda text: (len(text) >= data['min_length'], '增加具体例子'),
        revise=lambda text, feedback: text + data['addition'],
        max_revisions=data['max_revisions'])


def action(data):
    return llm.Action.model_validate(data).model_dump()


def tool_loop(data):
    def decide(request, history):
        if history:
            return llm.Action(kind='finish', answer=str(history[-1]['observation']))
        return llm.Action(kind='tool', tool='dates', arguments=request)
    tools = {'dates':llm.Tool(Dates, llm.days_between)}
    return llm.run_tool_loop({'start':data['start'],'end':data['end']}, decide, tools,
                             max_steps=data.get('max_steps', 3))


def date_difference(data):
    return llm.days_between(data['start'], data['end'])


def amount_total(data):
    return str(llm.sum_amounts(data['amounts']))


def route_scores(data):
    return llm.routing_report(data['expected'], data['predicted'])


def vision(data):
    # Uploaded bytes only; do not open user-provided filesystem paths.
    raw = base64.b64decode(data['image_base64'], validate=True)
    if len(raw) > 2_000_000:
        raise ValueError('图片最大 2 MB')
    with tempfile.TemporaryDirectory() as folder:
        path = Path(folder) / 'upload'
        path.write_bytes(raw)
        messages = llm.vision_messages(data.get('question','描述图片'), [path])
    return {'bytes':len(raw), 'messages':messages}


def model_config(data):
    config = adk.ModelConfig(model=data['model'], api_base=data.get('api_base'))
    model = config.build()
    return {'model':model.model, 'api_base':config.api_base,
            'note':'仅构造配置，没有调用模型。密钥由进程环境读取。'}


def content_text(data):
    content = types.Content(role='user', parts=[types.Part(text=t) for t in data['parts']])
    return adk.content_to_text(content)


def approval_schema(data):
    return adk.ApprovalDecision.model_validate(data).model_dump()


def event_demo(data):
    event = Event(author='demo', content=types.Content(role='model', parts=[
        types.Part(text=data['text'])]), output=data.get('output'),
        actions={'state_delta':data.get('state',{})})
    with contextlib.redirect_stdout(io.StringIO()) as stream:
        adk.print_event(event)
    return {'event_text':adk.event_text(event), 'printed':stream.getvalue()}


def completion(data):
    # Live request. Model and credentials are configured in server environment.
    client = llm.CompletionClient.from_env()
    try:
        result = client.complete(data['prompt'], response_model=Summary if data.get('structured') else None)
        return result.model_dump() if isinstance(result, BaseModel) else result
    finally:
        client.close()


async def agent_call(data):
    agent = adk.make_agent('workbench_agent', data['instruction'])
    client = adk.LocalSession(agent)
    try:
        sid = await client.create()
        events = [adk.event_text(e) async for e in client.stream(sid, data['message'])]
        return {'responses':[e for e in events if e]}
    finally:
        await client.close()


async def mcp_tools(data):
    # Environment endpoint only. Discovery does not execute remote tools.
    toolset = adk.mcp_http(os.environ['MCP_URL'], tool_filter=data.get('tool_filter'))
    try:
        tools = await toolset.get_tools()
        return {'tools':[{'name':t.name, 'description':t.description} for t in tools],
                'note':'已发现工具；未执行远端工具。'}
    finally:
        await toolset.close()


async def crewai_wrapper(data):
    from crewai.tools import BaseTool
    class EchoArgs(BaseModel):
        text: str
    class EchoTool(BaseTool):
        name: str = 'echo'
        description: str = 'Return the supplied text; no network access.'
        args_schema: type[BaseModel] = EchoArgs
        def _run(self, text: str) -> str:
            return text.upper()
    wrapped = adk.crewai_tool(EchoTool(), name='echo', description='本地大写转换')
    return await wrapped.run_async(args={'text':data['text']}, tool_context=None)


def tracing(data):
    # Runs in an isolated worker process. Exports only the synthetic sample span.
    from opentelemetry import trace
    provider = adk.enable_phoenix(data['project'], mode=data['mode'], batch=False)
    try:
        with trace.get_tracer('workbench').start_as_current_span('workbench.sample'):
            pass
        flushed = provider.force_flush(timeout_millis=5000)
        return {'flush_completed':flushed,
                'note':'已尝试导出样例 span；flush 完成不等于 collector 已接收，请在 Phoenix 查看。'}
    finally:
        provider.shutdown()
