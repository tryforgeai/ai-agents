"""图模式：节点可以是函数、FunctionTool、Agent 或嵌套 Workflow。"""
from google.adk import Context, Event, Workflow
from google.adk.workflow import JoinNode


def sequence(name, *nodes):
    if not nodes:
        raise ValueError("sequence needs at least one node")
    return Workflow(name=name, edges=[("START", *nodes)])


def branching(name, router, routes):
    """router 应同时返回 Event(output=原始数据, route=路由名)。"""
    if not routes:
        raise ValueError("routes must not be empty")
    return Workflow(name=name, edges=[("START", router), (router, routes)])


def parallel(name, *workers, reducer=None):
    """并行后显式 Join；reducer 收到 {节点名: 节点输出}。"""
    if len(workers) < 2:
        raise ValueError("parallel needs at least two workers")
    join = JoinNode(name=f"{name}_join")
    tail = (join,) if reducer is None else (join, reducer)
    return Workflow(name=name, edges=[("START", tuple(workers), *tail)])


def bounded_loop(name, worker, is_done, *, max_iterations=5):
    """worker 输出反馈给下一轮；同步 is_done(output) 判断成功。

    计数在每次调用开始时重置；终端输出明确区分成功与次数耗尽。
    """
    if max_iterations < 1:
        raise ValueError("max_iterations must be >= 1")
    key = f"{name}_iterations"

    def initialize(node_input):
        return Event(output=node_input, state={key: 0})

    def check(node_input, ctx: Context):
        count = ctx.state.get(key, 0) + 1
        done = bool(is_done(node_input))
        stop = done or count >= max_iterations
        output = ({"result": node_input, "iterations": count,
                   "status": "completed" if done else "exhausted"}
                  if stop else node_input)
        return Event(output=output, state={key: count},
                     route="stop" if stop else "retry")

    def finish(node_input):
        return Event(output=node_input)

    return Workflow(name=name, edges=[
        ("START", initialize, worker, check),
        (check, {"retry": worker, "stop": finish}),
    ])
