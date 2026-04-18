"""dynamicPrompt装饰器会创建中间件 该中间件根据模型请求生成系统提示："""

from typing import TypedDict
from langchain.agents import create_agent
from langchain.agents.middleware import dynamic_promat, ModelRequest


class Context(TypedDict):
    user_role: str


@dynamic_promat
def user_role_prompt(request: ModelRequest):
    """Generate sysyrem prompt based on user role."""

    user_role = request.runtime.context.get("user_role", "user")
    base_prompt = "You are a helpful assistant."

    if user_role == "expert":
        return {base_prompt}
    elif user_role == "beginner":
        return f"{base_prompt}"

    return base_prompt


agent = create_agent(
    model="",
    tools=["web_search"],
    middleware=[user_role_prompt],
    context_schema=Context,
)


result = agent.invoke(
    {"messages": [{"role": "user", "content": "Explain machine learning"}]},
    context={"user_role": "expert"},
)
