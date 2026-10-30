"""Every public library export maps to a runnable example and its real source."""
import ast
import inspect
import os
from pathlib import Path

import adk_patterns
import llm_patterns
import demos

ROOT = Path(__file__).resolve().parents[2]


def row(package, symbol, title, group, description, default, *, demo=None, example=None,
        requirements=(), external=False, env=(), notes=''):
    function = getattr(adk_patterns if package=='adk_patterns' else llm_patterns, symbol)
    code = inspect.getsource(function)
    source = Path(inspect.getsourcefile(function)).relative_to(ROOT).as_posix()
    if example:
        demo_path = ROOT/'libs/adk_patterns/examples'/example/'agent.py'
        demo_code = demo_path.read_text()
    else:
        demo_function = getattr(demos, demo)
        function_code = inspect.getsource(demo_function)
        names = {node.id for node in ast.walk(ast.parse(function_code)) if isinstance(node, ast.Name)}
        helpers = ""
        for helper in (demos.Summary, demos.Dates):
            if helper.__name__ in names:
                helper_code = inspect.getsource(helper)
                helpers += helper_code + "\n\n"
                names.update(node.id for node in ast.walk(ast.parse(helper_code)) if isinstance(node, ast.Name))
        imports_by_name = {
            'adk':'import adk_patterns as adk', 'llm':'import llm_patterns as llm',
            'asyncio':'import asyncio', 'base64':'import base64', 'contextlib':'import contextlib',
            'io':'import io', 'os':'import os', 'tempfile':'import tempfile',
            'Path':'from pathlib import Path', 'Any':'from typing import Any',
            'Event':'from google.adk import Event', 'types':'from google.genai import types',
            'BaseModel':'from pydantic import BaseModel', 'ConfigDict':'from pydantic import ConfigDict',
            'Field':'from pydantic import Field',
        }
        if inspect.iscoroutinefunction(demo_function):
            names.add('asyncio')
        demo_code = "\n".join(statement for name, statement in imports_by_name.items() if name in names) + "\n\n" + helpers + function_code
        data_code = repr(default)
        if demo == 'vision':
            data_code = "{\"question\": \"描述图片\", \"image_base64\": base64.b64encode(Path(\"your-image.png\").read_bytes()).decode()}"
        invocation = f"{demo}({data_code})"
        if inspect.iscoroutinefunction(demo_function):
            invocation = f"asyncio.run({invocation})"
        demo_code += f"\n\nif __name__ == '__main__':\n    print({invocation})\n"
    setup = "# 在 AI Agents 项目根目录启动\nbash libs/workbench/run.sh 9010"
    if symbol == 'CompletionClient':
        setup = "# 在启动终端配置模型与密钥（不要提交到 Git）\nexport LLM_MODEL=gpt-4o-mini\n# 设置 OPENAI_API_KEY；兼容服务可设置 OPENAI_BASE_URL\n" + setup
    elif symbol == 'make_agent':
        setup = "export ADK_MODEL=gpt-4o-mini\n# 设置 OPENAI_API_KEY；兼容服务可设置 ADK_API_BASE / ADK_API_KEY\n" + setup
    elif symbol == 'mcp_http':
        setup = "# 先启动你的 Streamable HTTP MCP 服务\nexport MCP_URL=http://127.0.0.1:9000/mcp\n" + setup
    elif symbol == 'enable_phoenix':
        setup = "# 另一个终端中启动已安装的 Phoenix：phoenix serve\nexport PHOENIX_COLLECTOR_ENDPOINT=http://127.0.0.1:6006/v1/traces\n# 云端还需 PHOENIX_API_KEY\n" + setup
    elif symbol == 'crewai_tool':
        setup = "# 在工作台使用的 Python 环境安装可选依赖\npython -m pip install crewai-tools\n" + setup
    return dict(id=f'{package}.{symbol}' , package=package, symbol=symbol, title=title,
                group=group, description=description, default=default, demo=demo,
                example=example, external=external, requirements=list(requirements),
                env=list(env), notes=notes, source=source, implementation=code,
                demo_code=demo_code, setup=setup)


def catalog():
    a='adk_patterns'; l='llm_patterns'
    rows=[
        row(l,'CompletionClient','统一模型调用','模型与输入','文本响应或 Instructor 结构化响应。',
            {'prompt':'解释什么是 Agent，并提取三个关键词。','structured':True}, demo='completion',
            external=True,env=['LLM_MODEL'], requirements=['OpenAI-compatible 服务','openai / instructor'],
            notes='从终端环境读取密钥；这是实际模型请求，可能产生费用。'),
        row(l,'PromptSpec','CO-STAR 提示','提示与流程','用六个维度明确任务和输出要求。',
            {'context':'学习 Agent 开发','objective':'解释工具调用','audience':'初学者','response':'三个要点'}, demo='prompt_spec'),
        row(l,'few_shot_messages','Few-shot 消息','提示与流程','把示例组装为交替的 user / assistant 消息。',
            {'instruction':'判断情感','examples':[['很好','positive'],['很差','negative']],'query':'还不错'},demo='few_shot'),
        row(l,'Step','命名步骤','提示与流程','定义可读取完整上下文的步骤。',{'text':'  AI   Agents  '},demo='chain'),
        row(l,'run_chain','多阶段数据链','提示与流程','规范化文本并生成摘要对象，保留全部阶段结果。',{'text':'  AI   Agents  '},demo='chain',notes='确定性演示，不调用模型。'),
        row(l,'sample_vote','采样结果投票','提示与流程','对提供的样本做严格多数投票；没有多数则弃权。',{'samples':['A','B','A']},demo='vote',notes='交互样本由你提供；库函数可把 sample 替换为真实模型调用。'),
        row(l,'refine','有限反馈重写','提示与流程','按长度规则检查草稿，最多重写指定次数。',{'draft':'草稿','min_length':12,'addition':'。补充一个具体例子','max_revisions':2},demo='refinement'),
        row(l,'Action','动作 schema','工具与计算','检查 tool / finish 动作是否满足字段约束。',{'kind':'tool','tool':'dates','arguments':{'start':'2020-07-22','end':'2021-12-01'}},demo='action'),
        row(l,'Tool','注册确定性工具','工具与计算','Pydantic 参数校验后执行真实日期计算。',{'start':'2020-07-22','end':'2021-12-01','max_steps':3},demo='tool_loop'),
        row(l,'run_tool_loop','行动与观察循环','工具与计算','模拟决策→真实工具→观察→完成，带步数上限。',{'start':'2020-07-22','end':'2021-12-01','max_steps':3},demo='tool_loop'),
        row(l,'days_between','日期差','工具与计算','用 Python 日期运算，结束日期减开始日期。',{'start':'2020-07-22','end':'2021-12-01'},demo='date_difference'),
        row(l,'sum_amounts','Decimal 精确求和','工具与计算','金额使用字符串输入，避免浮点误差。',{'amounts':['0.10','0.20','12.35']},demo='amount_total'),
        row(l,'routing_report','触发路由评估','工具与计算','比较预期和实际标签，null 代表不触发。',{'expected':[None,'summary','clean'],'predicted':['clean','summary',None]},demo='route_scores'),
        row(l,'image_data_url','图片转 Data URL','模型与输入','上传图片，识别 MIME 并转换为 data URL。',{'question':'转录并解释图片'},demo='vision',notes='先上传图片；最大 2 MB，不会发送给模型。'),
        row(l,'vision_messages','多模态消息','模型与输入','组装文字和图片的 OpenAI-compatible 消息。',{'question':'先转录文字，标记不确定处，再解释'},demo='vision',notes='先上传图片；最大 2 MB，不会发送给模型。'),
        row(a,'ModelConfig','模型配置','模型与输入','构建 LiteLlm 模型配置，不发起请求。',{'model':'gpt-4o-mini'},demo='model_config'),
        row(a,'make_agent','运行单轮 Agent','模型与输入','使用终端配置的模型回答一条消息。',{'instruction':'用中文简洁回答。','message':'什么是 Agent？'},demo='agent_call',external=True,env=['ADK_MODEL'],requirements=['可用模型服务']),
        row(a,'content_to_text','消息转文本','模型与输入','从 Content.parts 提取文本。',{'parts':['你好','ADK']},demo='content_text'),
        row(a,'sequence','顺序工作流','工作流与状态','读取数字→函数工具→结果和状态。',{'a':7,'b':8},example='calculator'),
        row(a,'function_tool','函数作为图工具','工具与计算','将带类型注解的加法函数包装成工具节点。',{'a':7,'b':8},example='calculator'),
        row(a,'branching','条件路由','工作流与状态','关键词判断后只执行一个处理节点。','请总结这段文字',example='routing'),
        row(a,'parallel','并行与汇总','工作流与状态','字符数与大写并行执行，JoinNode 等待汇总。','hello world',example='parallel'),
        row(a,'bounded_loop','有上限的循环','工作流与状态','每轮加一，达到 3 或最多 5 轮后停止。','0',example='loop'),
        row(a,'LocalSession','会话状态','工作流与状态','连续运行时复用当前会话，计数逐次增加。','继续',example='counter'),
        row(a,'ApprovalDecision','审批响应校验','审批与追踪','检查三种决定，notes 为 null 时转为空字符串。',{'decision':'approve','notes':None},demo='approval_schema'),
        row(a,'approval_workflow','人工审批','审批与追踪','生成固定草稿→暂停→人工选择→返回决定。','给 Notebook 增加输入校验',example='approval'),
        row(a,'reviewed_pipeline','采集与审核重写','审批与追踪','模拟多源采集→去重→写稿→人工审核→有限重写。','AI Agents',example='reviewed_digest',notes='模拟资料；不抓取真实新闻，不对外发布。'),
        row(a,'event_text','提取事件文本','工作流与状态','提取可展示响应，跳过 thought 字段。',{'text':'运行完成','output':{'sum':15},'state':{'last_sum':15}},demo='event_demo'),
        row(a,'print_event','显示执行事件','工作流与状态','查看响应、节点输出和状态变更。',{'text':'运行完成','output':{'sum':15},'state':{'last_sum':15}},demo='event_demo'),
        row(a,'mcp_http','MCP 工具发现','工具与计算','连接环境中的 MCP_URL，列出工具，不执行工具。',{'tool_filter':None},demo='mcp_tools',external=True,env=['MCP_URL'],requirements=['运行中的 Streamable HTTP MCP 服务']),
        row(a,'crewai_tool','CrewAI 工具包装','工具与计算','包装并调用本地大写转换工具，不访问网络。',{'text':'hello agent'},demo='crewai_wrapper',requirements=['crewai / crewai-tools']),
        row(a,'enable_phoenix','Phoenix 追踪','审批与追踪','独立进程配置追踪并尝试导出一条样例 span。',{'project':'workbench-demo','mode':'native'},demo='tracing',external=True,env=['PHOENIX_COLLECTOR_ENDPOINT'],requirements=['Phoenix collector','tracing extra'],notes='导出日志也会显示；请在 Phoenix 项目中确认接收结果。'),
    ]
    return {item['id']:item for item in rows}
