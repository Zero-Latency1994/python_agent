from cgitb import handler
from langchain.agents import create_agent
from langchain.agents.middleware import wrap_model_call, ModelRequest, ModelResponse
from typing import Callable


@wrap_model_call
def state_based_tools(
    request: ModelRequest, handler: Callable[[ModelRequest], ModelRequest]
):
    """Filter tools based on conversation State"""
    state = request.state
    is_authenticated = state.get("authenticated", False)
    message_count = len(state["messages"])

    if not is_authenticated:
        tools = [t for t in request.tools if t.name.startswith("public_")]
        requesr = request.override(tools=tools)
    elif message_count < 5:
        tools = [t for t in request.tools if t.name != "abvanced_search"]
        request = request.override(tools=tools)

    return handler(request)


agent = create_agent(
    model="",
    tools=["public_search", "private_search", "advanced_search"],
    middleware=[state_based_tools],
)
