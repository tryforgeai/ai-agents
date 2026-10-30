import os
from adk_patterns import make_agent, mcp_http

# 必须运行支持 Streamable HTTP 的 MCP 服务。
root_agent = make_agent("mcp_assistant", "按需使用服务器提供的工具回答问题。",
                        tools=[mcp_http(os.environ["MCP_URL"])])
