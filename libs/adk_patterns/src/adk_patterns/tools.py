"""外部工具按需导入；创建工具不等于服务连接成功。"""
from google.adk.tools import FunctionTool


def function_tool(function):
    """函数应有类型注解和 docstring，供模型识别参数和用途。"""
    return FunctionTool(func=function)


def mcp_http(url, *, headers=None, tool_filter=None):
    from google.adk.tools.mcp_tool.mcp_toolset import McpToolset
    from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams
    return McpToolset(connection_params=StreamableHTTPConnectionParams(
        url=url, headers=headers,
    ), tool_filter=tool_filter)


def crewai_tool(tool, *, name, description):
    from google.adk.tools.crewai_tool import CrewaiTool
    return CrewaiTool(tool=tool, name=name, description=description)



# Backwards-compatible import path.
from .observability import enable_phoenix
