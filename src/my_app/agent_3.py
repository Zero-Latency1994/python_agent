import re
from langchain.agents import create_agent
from langchain.agents.middleware import wrap_tool_call
from langchain.messages import ToolMessage

from my_app.agent import get_weather, search


@wrap_tool_call
def handle_tool_errors(request, handler):
    """Handle tool execution errors with custom messages."""

    try:
        return handler(request)
    except Exception as e:
        return ToolMessage(context=f"{str(e)}", tool_call_id=request.tool_call["id"])


agent=create_agent(
    model="",
    tools=[search,get_weather],
    middleware=[handle_tool_errors]
)