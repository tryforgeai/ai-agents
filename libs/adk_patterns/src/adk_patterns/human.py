"""人工审批：由 ADK Web 展示 RequestInput 并恢复暂停的工作流。"""
from typing import Literal

from google.adk import Event
from google.adk.events import RequestInput
from pydantic import BaseModel, field_validator

from .workflows import sequence


class ApprovalDecision(BaseModel):
    decision: Literal["approve", "revise", "reject"]
    notes: str = ""

    @field_validator("notes", mode="before")
    @classmethod
    def normalize_notes(cls, value):
        return "" if value is None else value


def approval_workflow(name, draft_node):
    """生成草稿→暂停审批→返回决定；不隐式执行操作或自动重写。"""
    async def request_approval(node_input):
        yield RequestInput(
            message=f"请审核以下草稿，选择 approve / revise / reject：\n{node_input}",
            payload=node_input, response_schema=ApprovalDecision,
        )

    def apply_decision(node_input: ApprovalDecision):
        return Event(output=node_input.model_dump(),
                     state={"approval_decision": node_input.decision,
                            "approval_notes": node_input.notes})

    return sequence(name, draft_node, request_approval, apply_decision)


def reviewed_pipeline(name, prepare, writer, publish, *, max_revisions=2):
    """嵌套采集/分析→写稿→人工审核→发布或有限重写。

    writer 从 state 读取 source_material、review_draft、review_feedback。
    publish 接收批准的草稿。每次新请求重置审核状态。
    """
    from google.adk import Context, Workflow
    if max_revisions < 0:
        raise ValueError("max_revisions must be nonnegative")

    def begin(node_input):
        return Event(output=node_input, state={"review_round": 0,
            "review_feedback": "", "review_draft": "", "review_status": "pending"})

    def remember(node_input):
        return Event(output=node_input, state={"source_material": node_input})

    async def ask(node_input, ctx: Context):
        yield Event(state={"review_draft": node_input})
        yield RequestInput(message=f"审核草稿：\n{node_input}", payload=node_input,
                           response_schema=ApprovalDecision)

    def route(node_input: ApprovalDecision, ctx: Context):
        rounds = ctx.state.get("review_round", 0)
        decision = node_input.decision
        status = decision
        if decision == "revise" and rounds >= max_revisions:
            decision, status = "stop", "exhausted"
        elif decision == "reject":
            decision, status = "stop", "rejected"
        elif decision == "revise":
            rounds += 1
        return Event(output=ctx.state["review_draft"], route=decision,
                     state={"review_round": rounds, "review_feedback": node_input.notes,
                            "review_status": status})

    def stop(node_input, ctx: Context):
        return Event(output={"status": ctx.state["review_status"], "draft": node_input})

    return Workflow(name=name, edges=[
        ("START", begin, prepare, remember, writer, ask, route),
        (route, {"approve": publish, "revise": writer, "stop": stop}),
    ])
