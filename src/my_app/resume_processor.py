import json
import os
import re
import sys
from pathlib import Path

import pdfplumber
# 本地向量：使用 langchain-huggingface（勿用未安装的 langchain_community 回退，否则 IDE/运行都会报错）
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI  # 仍用 OpenAI 兼容类对接 MiniMax 等网关
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv

load_dotenv()

class ResumeProcessor:
    def __init__(self, persist_directory="./db_resumes"):
        
        # --- 修改 2: 配置 HuggingFace Embeddings (本地运行) ---
        # 指定一个中文或通用的开源 Embedding 模型
        # 常用模型推荐：
        # 英文: "sentence-transformers/all-MiniLM-L6-v2" (轻量级，速度快)
        # 中文: "uer/sbert-base-chinese-nli" 或 "BAAI/bge-small-zh-v1.5"
        
        model_name = "uer/sbert-base-chinese-nli" # 你可以根据需要更改
        
        print(f"正在加载本地 Embedding 模型: {model_name} ...")
        self.embeddings = HuggingFaceEmbeddings(model_name=model_name)
        print("本地 Embedding 模型加载完成")

        # --- 保持不变: 初始化 LLM (对接 MiniMax) ---
        # 注意：我们依然使用 ChatOpenAI，因为它兼容 OpenAI 格式的接口
        llm_kwargs = {
            "model": os.getenv("OPENAI_MODEL", "abab6.5-chat"), # MiniMax 的模型名示例
            "temperature": 0,
        }
        if os.getenv("OPENAI_API_KEY"):
            llm_kwargs["api_key"] = os.getenv("OPENAI_API_KEY")
        if os.getenv("OPENAI_BASE_URL"):
            # 这里填 MiniMax 的 Base URL
            llm_kwargs["base_url"] = os.getenv("OPENAI_BASE_URL") 
        
        self.llm = ChatOpenAI(**llm_kwargs)
        print("LLM (MiniMax) 初始化完成")

        # --- 保持不变: 初始化向量数据库 ---
        self.vector_db = Chroma(
            collection_name="resumes",
            embedding_function=self.embeddings, # 现在使用的是本地 HuggingFace 模型
            persist_directory=persist_directory,
        )
        print("简历处理器已初始化")

    # --- 以下函数保持不变 ---
    
    def extract_text_from_pdf(self, file_path):
        text = ""
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text()
        return text

    @staticmethod
    def _parse_json_from_llm(text: str) -> dict:
        text = (text or "").strip()
        if not text:
            raise ValueError("模型返回内容为空。")

        m = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
        if m:
            text = m.group(1).strip()
            if not text:
                raise ValueError("模型在 markdown 代码块内未输出任何内容")

        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        start, end = text.find("{"), text.rfind("}")
        if start != -1 and end != -1 and end > start:
            snippet = text[start : end + 1]
            try:
                return json.loads(snippet)
            except json.JSONDecodeError as e:
                raise ValueError(f"截取到的内容仍不是合法 JSON: {e}")

        raise ValueError(f"回复里未找到 JSON 对象。")

    def parse_resume_with_llm(self, raw_text):
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "你是专业招聘助手。根据简历文本提取信息。\n"
                    "硬性要求：你的整条回复必须且只能是一个 JSON 对象；"
                    "第一个字符必须是左花括号，最后一个字符必须是右花括号；"
                    "不要 markdown、不要代码块、不要前后解释。\n"
                    "键必须为: name, phone, skills, experience, education, years_of_experience；"
                    "years_of_experience 为整数，其余为字符串。",
                ),
                ("user", "简历内容：\n{resume_text}"),
            ]
        )
        
        # --- 修改 3: 移除 bind(force_no_tool=True) ---
        # HuggingFaceEmbeddings 和 MiniMax 的兼容性问题主要在 Embedding 层，
        # 这里的 LLM 调用保持原样，或者根据 MiniMax 的实际报错决定是否加 bind
        chain = prompt | self.llm
        
        msg = chain.invoke({"resume_text": raw_text})
        raw_content = msg.content
        
        # ... (后续解析逻辑保持不变) ...
        
        return self._parse_json_from_llm(raw_content)

    def process_and_store(self, file_path, resume_id):
        print(f" 正在处理: {file_path} ...")
        raw_text = self.extract_text_from_pdf(file_path)
        if not raw_text:
            print(" 提取文本为空")
            return

        try:
            structured_data = self.parse_resume_with_llm(raw_text)
            print(f" 解析成功: {structured_data['name']}")
        except Exception as e:
            print(f" LLM 解析失败: {e}")
            return

        vector_content = f"{structured_data['skills']} {structured_data['experience']}"
        
        self.vector_db.add_texts(
            texts=[vector_content],
            metadatas=[
                {
                    "source_id": resume_id,
                    "name": structured_data["name"],
                    "phone": structured_data["phone"],
                    "education": structured_data["education"],
                    "years": structured_data["years_of_experience"],
                    "full_info": json.dumps(structured_data, ensure_ascii=False),
                }
            ],
            ids=[resume_id],
        )
        print(f" {structured_data['name']} 已成功存入向量数据库")

if __name__ == "__main__":
    # 确保你的 .env 文件里配置了 MiniMax 的参数
    # OPENAI_API_KEY=你的MiniMaxKey
    # OPENAI_BASE_URL=https://api.minimax.chat/v1
    # OPENAI_MODEL=abab6.5-chat (或 MiniMax 对应的模型名)
    
    processor = ResumeProcessor()
    
    my_pdf_path = "D://test//XXX-数据开发.pdf"
    my_resume_id = "resume_001"
    processor.process_and_store(my_pdf_path, my_resume_id)