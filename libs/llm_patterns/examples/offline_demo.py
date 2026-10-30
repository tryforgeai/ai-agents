"""Run without credentials; model decisions are explicitly simulated."""
from pydantic import BaseModel
from llm_patterns import (
    Action, Tool, run_tool_loop, days_between, sum_amounts,
    Step, run_chain, sample_vote, routing_report,
)

class Dates(BaseModel):
    start: str
    end: str


def decide(request, history):
    if not history:
        return Action(kind="tool", tool="days_between",
                      arguments={"start":"2020-07-22", "end":"2021-12-01"})
    return Action(kind="finish", answer=str(history[-1]["observation"]["value"]))


if __name__ == "__main__":
    print("工具循环（模拟决策，真实计算）：", run_tool_loop(
        "计算日期差", decide, {"days_between": Tool(Dates, days_between)}))
    print("精确求和：", sum_amounts(["0.10", "0.20"]))
    print("独立采样投票（模拟样本）：", sample_vote(iter(["A", "B", "A"]).__next__))
    print("链式数据：", run_chain("input", [Step("draft", lambda s: s["input"]+" draft"),
                                          Step("review", lambda s: s["draft"]+" reviewed")]))
    print("路由评估：", routing_report([None, "summary"], [None, "summary"]))
