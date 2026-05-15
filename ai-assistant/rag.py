"""
RAG 智能助手
使用 小米MiMo大模型 + 关键词匹配检索
"""
import os
from typing import List, Optional
from dotenv import load_dotenv
from openai import OpenAI

# 加载环境变量
load_dotenv()

# MiMo API 配置
MIMO_API_KEY = os.getenv("MIMO_API_KEY")
MIMO_BASE_URL = os.getenv("MIMO_BASE_URL", "https://platform.xiaomimimo.com/v1")

# 知识库目录
KNOWLEDGE_DIRECTORY = "./knowledge"


class RAGAssistant:
    """RAG智能助手"""

    def __init__(self):
        self.client = None
        self.documents = []
        self._initialized = False

    def initialize(self):
        """初始化"""
        if self._initialized:
            return

        api_key = MIMO_API_KEY
        if not api_key or api_key == "your_api_key_here":
            raise ValueError("请在 .env 文件中配置有效的 MIMO_API_KEY")

        print(f"[DEBUG] API Key: {api_key[:10]}...")
        print(f"[DEBUG] Base URL: {MIMO_BASE_URL}")

        self.client = OpenAI(
            api_key=api_key,
            base_url=MIMO_BASE_URL,
            default_headers={"api-key": api_key}
        )

        self._load_documents()
        self._initialized = True

    def _load_documents(self):
        """加载知识库文档"""
        self.documents = []

        if not os.path.exists(KNOWLEDGE_DIRECTORY):
            os.makedirs(KNOWLEDGE_DIRECTORY)
            return

        for filename in os.listdir(KNOWLEDGE_DIRECTORY):
            if filename.endswith('.md') or filename.endswith('.txt'):
                filepath = os.path.join(KNOWLEDGE_DIRECTORY, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    self.documents.append({
                        "source": filename,
                        "content": content
                    })
                    print(f"已加载文档: {filename}")
                except Exception as e:
                    print(f"加载文档 {filename} 失败: {e}")

        print(f"共加载 {len(self.documents)} 个文档")

    def reload_knowledge(self) -> dict:
        """重新加载知识库"""
        self._initialized = False
        self.initialize()
        return {"status": "success", "message": "知识库已重新加载"}

    def _search(self, query: str) -> str:
        """简单关键词搜索"""
        if not self.documents:
            return "知识库暂无内容"

        results = []
        for doc in self.documents:
            # 简单关键词匹配
            if any(kw in doc["content"] for kw in query):
                results.append(doc["content"])
            elif any(kw in doc["content"] for kw in query.split()):
                results.append(doc["content"])

        if results:
            return "\n\n".join(results[:3])

        # 没有匹配时返回所有文档摘要
        return "\n\n".join([doc["content"][:500] for doc in self.documents[:3]])

    def chat(self, question: str, history: Optional[List[dict]] = None) -> dict:
        """对话接口"""
        self.initialize()

        # 检索相关内容
        context = self._search(question)

        # 构建消息
        messages = [
            {"role": "system", "content": f"""你是一个智能助手，请根据以下知识库内容回答用户问题。
如果知识库中没有相关信息，请诚实地说"抱歉，我在知识库中没有找到相关信息"，不要编造答案。

知识库内容:
{context}"""}
        ]

        # 添加历史对话
        if history:
            for h in history[-5:]:
                messages.append({"role": h["role"], "content": h["content"]})

        # 添加用户问题
        messages.append({"role": "user", "content": question})

        try:
            response = self.client.chat.completions.create(
                model="mimo-v2.5-pro",
                messages=messages,
                temperature=0.7,
                max_tokens=1024
            )

            answer = response.choices[0].message.content

            # 构建来源信息
            sources = [{"source": doc["source"], "content": doc["content"][:200]} for doc in self.documents]

            return {
                "status": "success",
                "answer": answer,
                "sources": sources
            }

        except Exception as e:
            import traceback
            traceback.print_exc()
            return {
                "status": "error",
                "answer": f"抱歉，处理您的问题时出现错误: {str(e)}",
                "sources": []
            }


# 全局RAG助手实例
rag_assistant = RAGAssistant()
