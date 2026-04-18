from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("请设置环境变量 OPENAI_API_KEY")

base_url = os.getenv("OPENAI_BASE_URL")

model = os.getenv("OPENAI_MODEL")

client = OpenAI(api_key=api_key, base_url=base_url)


completion = client.chat.completions.create(
    model=model,
    messages=[{"role": "user", "content": "你是谁"}],
    temperature=2,
    stream=True,
)

# print(completion.choices[0].message.content)
for chunk in completion:
    # 注意：流式模式下，内容在 delta 里，而不是 message
    content = chunk.choices[0].delta.content

    if content:  # 防止打印 None
        print(content, end="")
