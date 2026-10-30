"""Local-only method workbench; user source files are never executed."""
import asyncio
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
import importlib.util
import json
from pathlib import Path
import secrets
import sys
import time
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
for library in ('adk_patterns', 'llm_patterns'):
    sys.path.insert(0, str(ROOT/'libs'/library/'src'))

from fastapi import FastAPI, HTTPException, Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict
from starlette.middleware.trustedhost import TrustedHostMiddleware
from google.genai import types
from adk_patterns import LocalSession, ApprovalDecision, event_text
from catalog import catalog
from sources import scan_sources, search, source_text, WORKSPACE
from worker import redact

HERE = Path(__file__).resolve().parent
CATALOG = catalog()
MAX_SESSIONS = 64
SESSION_TTL = 1800
WORKERS = asyncio.Semaphore(4)


@dataclass
class ActiveSession:
    method: str
    client: LocalSession
    sid: str
    pending: Any = None
    touched: float = field(default_factory=time.monotonic)
    lock: asyncio.Lock = field(default_factory=asyncio.Lock)


SESSIONS: dict[str, ActiveSession] = {}
RECORDS = {}


@asynccontextmanager
async def lifespan(app):
    global RECORDS
    RECORDS = await asyncio.to_thread(scan_sources)
    yield
    for active in list(SESSIONS.values()):
        await active.client.close()
    SESSIONS.clear()


app = FastAPI(title='AI Agents · 方法实验台', lifespan=lifespan)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=['127.0.0.1','localhost','[::1]','testserver'])


@app.middleware('http')
async def local_requests(request: Request, call_next):
    origin = request.headers.get('origin')
    if origin and origin != f'{request.url.scheme}://{request.headers.get("host")}':
        return JSONResponse({'detail':'只接受同源请求'}, status_code=403)
    try:
        length = int(request.headers.get('content-length', '0'))
    except ValueError:
        return JSONResponse({'detail':'无效请求长度'}, status_code=400)
    if length > 3_000_000:
        return JSONResponse({'detail':'请求最大 3 MB'}, status_code=413)
    response = await call_next(request)
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'"
    response.headers['Cache-Control'] = 'no-store'
    return response


@app.get('/')
async def index():
    return FileResponse(HERE/'static/index.html')


@app.get('/api/catalog')
async def methods():
    import os
    items = []
    for entry in CATALOG.values():
        items.append({k:v for k,v in entry.items() if k not in ('demo','implementation','demo_code')} |
                     {'missing_env':[name for name in entry['env'] if not os.getenv(name)]})
    return {'methods':items, 'source_count':len(RECORDS),
            'groups':sorted({record['group'] for record in RECORDS.values()})}


@app.get('/api/method/{method_id}')
async def method(method_id: str):
    if method_id not in CATALOG:
        raise HTTPException(404, '方法不存在')
    return CATALOG[method_id]


@app.get('/api/sources')
async def files(q: str='', group: str='', offset: int=0):
    return search(RECORDS, q[:200], group, max(offset, 0))


@app.get('/api/source')
async def source(path: str):
    if path not in RECORDS:
        raise HTTPException(404, '文件不在只读源码目录中')
    try:
        text = await asyncio.to_thread(source_text, WORKSPACE/path)
    except (OSError, ValueError):
        raise HTTPException(404, '文件已移除或不在查看范围')
    return {'path':path, 'content':text, 'notebook':path.endswith('.ipynb')}


class RunInput(BaseModel):
    model_config = ConfigDict(extra='forbid')
    method: str
    data: Any
    session: str | None = None
    allow_external: bool = False


class ReviewInput(BaseModel):
    model_config = ConfigDict(extra='forbid')
    decision: ApprovalDecision


async def prune():
    now = time.monotonic()
    for token, active in list(SESSIONS.items()):
        if now - active.touched > SESSION_TTL and not active.lock.locked():
            SESSIONS.pop(token)
            await active.client.close()


async def create_session(entry):
    await prune()
    if len(SESSIONS) >= MAX_SESSIONS:
        raise HTTPException(429, '会话已满，请先结束不用的会话')
    path = ROOT/'libs/adk_patterns/examples'/entry['example']/'agent.py'
    spec = importlib.util.spec_from_file_location('workbench_example_'+secrets.token_hex(6),path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    client = LocalSession(module.root_agent)
    sid = await client.create()
    token = secrets.token_urlsafe(24)
    active = ActiveSession(entry['id'], client, sid)
    SESSIONS[token] = active
    return token, active


async def execute(active, message):
    records, final = [], None
    active.pending = None
    async for event in active.client.stream(active.sid, message):
        if event.error_message:
            raise ValueError(event.error_message)
        pending = None
        for part in event.content.parts or [] if event.content else []:
            call = part.function_call
            if call and call.name == 'adk_request_input':
                active.pending = call
                pending = call.args
        if event.output is not None:
            final = event.output
        text = event_text(event)
        records.append({'author':event.author, 'text':text, 'output':event.output,
                        'state_delta':event.actions.state_delta if event.actions else {},
                        'approval':pending})
        if len(records) > 300:
            raise ValueError('事件数量超出实验上限')
    state = await active.client.state(active.sid)
    active.touched = time.monotonic()
    return jsonable_encoder({'ok':True, 'result':final, 'events':records,
        'state':{k:v for k,v in state.items() if not k.startswith('_')},
        'pending':active.pending.args if active.pending else None})


async def guarded_execute(token, active, message):
    if active.lock.locked():
        raise HTTPException(409, '本会话正在运行')
    async with active.lock:
        try:
            result = await asyncio.wait_for(execute(active,message), timeout=60)
            return result | {'session':token}
        except Exception as error:
            SESSIONS.pop(token, None)
            await active.client.close()
            return JSONResponse({'ok':False,'error':redact(f'{type(error).__name__}: {error}'),
                                 'session_closed':True}, status_code=422)


@app.post('/api/run')
async def run(payload: RunInput):
    entry = CATALOG.get(payload.method)
    if not entry:
        raise HTTPException(404, '方法不存在')
    if entry['external'] and not payload.allow_external:
        raise HTTPException(400, '请勾选允许本次外部请求')
    if entry['example']:
        if payload.session:
            active = SESSIONS.get(payload.session)
            if not active or active.method != payload.method:
                raise HTTPException(404, '会话已过期，请重置会话')
            token = payload.session
        else:
            token, active = await create_session(entry)
        if active.pending:
            raise HTTPException(409, '请先回复当前审批，或重置会话')
        return await guarded_execute(token, active, payload.data)
    async with WORKERS:
        proc = await asyncio.create_subprocess_exec(
            sys.executable, str(HERE/'worker.py'), stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        try:
            stdout, stderr = await asyncio.wait_for(proc.communicate(
                json.dumps({'id':entry['id'],'data':payload.data}).encode()), timeout=60)
            if proc.returncode:
                return JSONResponse({'ok':False, 'error':redact(stderr.decode()[-5000:])}, status_code=422)
            result = json.loads(stdout)
            return JSONResponse(result, status_code=200 if result['ok'] else 422)
        except asyncio.TimeoutError:
            proc.kill()
            await proc.communicate()
            return JSONResponse({'ok':False,'error':'运行超过 60 秒，工作进程已终止'},status_code=408)
        finally:
            if proc.returncode is None:
                proc.kill()
                await proc.wait()


@app.post('/api/session/{token}/review')
async def review(token: str, payload: ReviewInput):
    active = SESSIONS.get(token)
    if not active or not active.pending:
        raise HTTPException(404, '审批已结束或会话已过期')
    call = active.pending
    message = types.Content(role='user', parts=[types.Part(function_response=types.FunctionResponse(
        name=call.name, id=call.id, response=payload.decision.model_dump()))])
    return await guarded_execute(token, active, message)


@app.delete('/api/session/{token}')
async def reset(token: str):
    active = SESSIONS.get(token)
    if active and active.lock.locked():
        raise HTTPException(409, '请等当前运行结束后重置')
    if active:
        SESSIONS.pop(token)
        await active.client.close()
    return {'ok':True}


app.mount('/static', StaticFiles(directory=HERE/'static'), name='static')
