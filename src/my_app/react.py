import json
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("请设置环境变量 OPENAI_API_KEY")

base_url = os.getenv("OPENAI_BASE_URL")

model = os.getenv("OPENAI_MODEL")

clinet = OpenAI(api_key=api_key, base_url=base_url)


def get_info_on_ball_game(game_name):
    data = [
        {
            "name": "篮球(Basketball)",
            "description": "两只球队通过投篮得分，比赛氛围四节，没节时间因联赛而异",
            "team_members": 12,
            "players_on_field": 5,
        },
        {
            "name": "排球(Volleyball)",
            "description": "两队隔网对抗，通过击球过网并使其落在对方的场地得分",
            "team_members": 12,
            "players_on_field": 6,
        },
        {
            "name": "足球(Soccer)",
            "description": "两球队通过踢球进入对方球门得分，比赛分为上下半场",
            "team_members": 11,
            "players_on_field": 11,
        },
        {
            "name": "沙滩排球(Beach Volleyball)",
            "description": "排球的变种，在沙滩进行，每队人数较少",
            "team_members": 2,
            "players_on_field": 2,
        },
        {
            "name": "网球(Tennis)",
            "description": "单打或者双打比赛，球员用球拍击球过网，使对手无法还击",
            "team_members": 1,
            "players_on_field": 1,
        },
    ]
    ret = []

    for d in data:
        if game_name.lower() in d["name"].lower():
            ret.append(d)

    return ret


tools = [
    {
        "type": "function",
        "description": "获取球类比赛的基本信息和人员规模",
        "parameters": {
            "type": "object",
            "properties": {
                "gema_name": {"type": "string"},
                "required": ["latitude"],
                "additionalproperties": False,
            },
            "strict": True,
        },
    }
]


system_promat = """
你运行在一个和思考，行动，观察和回答的循环，再循环结束时，你输出最终答案
用 思考 来描述你对被问问题的想法
用 操作 运行您可用的操作之一
观察 将是运行操作的结果
答案 将是分析观察结果的结果
"""


message_history = []
message_history.append({"role": "system", "content": system_promat})


def get_completion(message):
    message_history.append(message)

    response = clinet.chat.completions.create(
        model=model, messages=message_history, tools=tools
    )

    response_dict = dict(response.choices[0].message)
    message_history.append(response_dict)
    return response_dict


def agent(query):
    max_turns = 5
    current_turns = 1
    next_message = {"role": "user", "content": query}

    while current_turns <= max_turns:

        message = get_completion(next_message)
        print(message)

        if message["tool_calls"]:
            func_call_id = message["content"][0].id
            func_kwargs = json.loads(message["tool_calls"][0].function.arguments)
            func_result = get_info_on_ball_game(**func_kwargs)

            print(f"观察：{func_result}")
            next_message = {
                "role": "tool",
                "tool_call_id": func_call_id,
                "content": str(func_result),
            }
        else:
            break


if __name__ == "__main__":
    query = "比赛场上，篮球队的球员人数乘以排球队的人数，结果是多少？"
    agent(query)
