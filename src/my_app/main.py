import os
from langchain.agents import create_agent
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

# 1. 加载环境变量
load_dotenv()

# 2. 初始化 LLM (保持你原本正确的写法)
llm = ChatOpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL"),
    model=os.getenv("OPENAI_MODEL"),
    temperature=0.2,
    timeout=60
)

# 3. 定义工具
@tool
def get_weekly():
    """
    用于获取当前的星期几或是否为周末。
    当用户询问时间、日期或星期时调用此工具。
    """
    # 这里为了演示写死返回，实际可以调用 datetime 库
    return "今天是星期六，是周末。"

# 4. 创建 Agent
# 注意：旧版本使用 prompt，新版本才支持 state_modifier
agent = create_agent(
    llm,  # 第一个参数必须是 llm 对象
    tools=[get_weekly],
    system_prompt="你是一名周末监控员。请利用提供的工具回答用户关于时间的问题。"
)

# 5. 调用 Agent (避免使用 request 作为变量名)
request = agent.invoke(
    {
        "messages": [
            {"role": "user", "content": "今天星期几？"}
        ]
    }
)

print(request["messages"][-1].content)