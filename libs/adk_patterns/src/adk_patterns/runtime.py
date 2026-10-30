"""Notebook/脚本运行入口；同一对象复用同一个内存会话服务。"""
import json
from uuid import uuid4

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from pydantic import BaseModel


class LocalSession:
    def __init__(self, agent, *, app_name="adk_patterns", user_id="user1"):
        self.app_name = app_name
        self.user_id = user_id
        self.sessions = InMemorySessionService()
        self.runner = Runner(agent=agent, app_name=app_name,
                             session_service=self.sessions)

    async def create(self, *, state=None):
        session = await self.sessions.create_session(
            app_name=self.app_name, user_id=self.user_id,
            session_id=str(uuid4()), state=state or {},
        )
        return session.id

    async def stream(self, session_id, message):
        """流式返回原始 ADK Event；异常原样传播，不伪装成成功。"""
        if isinstance(message, types.Content):
            pass
        elif isinstance(message, BaseModel):
            message = message.model_dump_json()
        elif not isinstance(message, (str, types.Content)):
            message = json.dumps(message, ensure_ascii=False)
        if isinstance(message, str):
            message = types.Content(role="user", parts=[types.Part(text=message)])
        async for event in self.runner.run_async(
            user_id=self.user_id, session_id=session_id, new_message=message,
        ):
            yield event

    async def state(self, session_id):
        session = await self.sessions.get_session(
            app_name=self.app_name, user_id=self.user_id, session_id=session_id,
        )
        if session is None:
            raise KeyError(session_id)
        return dict(session.state)

    async def close(self):
        """释放 Runner 管理的资源；调用方另外持有的 MCP 工具也应关闭。"""
        await self.runner.close()


def event_text(event):
    """只取可展示文本，跳过模型 thought 字段。"""
    if not event.content:
        return ""
    return "\n".join(part.text for part in event.content.parts or []
                     if part.text and not part.thought)


def print_event(event):
    print(f"[{event.author}]")
    if event.error_message:
        print("ERROR:", event.error_message)
    if event.output is not None:
        print("OUTPUT:", event.output)
    text = event_text(event)
    if text:
        print(text)
    if event.actions and event.actions.state_delta:
        print("STATE:", event.actions.state_delta)
