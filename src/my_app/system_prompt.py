from langchain.agents import create_agent
from langchain.messages import SystemMessage, HumanMessage

literary_agent = create_agent(
    model="",
    system_prompt=SystemMessage(
        content=[
            {
                "type": "text",
                "text": "You are an AI assistant tasked with analyzing literary works.",
            },
            {
                "type": "text",
                "text": "<the entire cntents of>",
                "cache_control": {"type": "ephemeral"},
            },
        ]
    ),
)


result = literary_agent.invoke(
    {"messages": [HumanMessage("Anyalyze the major themes in 'Pride and Prejudice'.")]}
)
