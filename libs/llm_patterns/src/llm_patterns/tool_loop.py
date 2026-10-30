"""Bounded action/observation loop; observations come ONLY from registered tools."""
from copy import deepcopy
from dataclasses import dataclass
from typing import Any, Callable, Literal
from pydantic import BaseModel, ConfigDict, Field, model_validator


class Action(BaseModel):
    model_config = ConfigDict(extra="forbid")
    kind: Literal["tool", "finish"]
    tool: str | None = None
    arguments: dict[str, Any] = Field(default_factory=dict)
    answer: str | None = None

    @model_validator(mode="after")
    def check_shape(self):
        if self.kind == "tool" and (not self.tool or self.answer is not None):
            raise ValueError("tool actions need a tool name and no final answer")
        if self.kind == "finish" and (self.answer is None or self.tool or self.arguments):
            raise ValueError("finish actions need an answer and no tool arguments")
        return self


@dataclass(frozen=True)
class Tool:
    arguments: type[BaseModel]
    run: Callable[..., Any]


def run_tool_loop(request, decide, tools, *, max_steps=5):
    if max_steps < 1:
        raise ValueError("max_steps must be positive")
    history = []
    for _ in range(max_steps):
        action = Action.model_validate(decide(request, deepcopy(history)))
        if action.kind == "finish":
            return {"status": "completed", "answer": action.answer, "history": history}
        if action.tool not in tools:
            raise ValueError(f"unregistered tool: {action.tool}")
        tool = tools[action.tool]
        args = tool.arguments.model_validate(action.arguments)
        try:
            observation = {"ok": True, "value": tool.run(**args.model_dump())}
        except Exception as error:
            observation = {"ok": False, "error_type": type(error).__name__, "error": str(error)}
        history.append({"action": action.model_dump(), "observation": observation})
    return {"status": "exhausted", "answer": None, "history": history}
