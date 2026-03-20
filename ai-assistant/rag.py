"""
RAG 检索增强生成模块
使用 LangChain + Chroma + 通义千问
"""
import os
from typing import List, Optional
from dotenv import load_dotenv

from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_community.llms import Tongyi
from langchain_core.documents import Document

# 加载环境变量
load_dotenv()

# 配置
PERSIST_DIRECTORY = "./chroma_db"
KNOWLEDGE_DIRECTORY = "./knowledge"


class RAGAssistant:
    """RAG智能助手"""
    
    def __init__(self):
        self.embeddings = None
        self.vectorstore = None
        self.llm = None
        self._initialized = False
    
    def initialize(self):
        """初始化RAG系统"""
        if self._initialized:
            return
        
        api_key = os.getenv("DASHSCOPE_API_KEY")
        if not api_key or api_key == "your_dashscope_api_key_here":
            raise ValueError("请在 .env 文件中配置有效的 DASHSCOPE_API_KEY")
        
        # 初始化通义千问嵌入模型
        self.embeddings = DashScopeEmbeddings(
            model="text-embedding-v2",
            dashscope_api_key=api_key
        )
        
        # 初始化通义千问大模型
        self.llm = Tongyi(
            model_name="qwen-plus",
            dashscope_api_key=api_key,
            temperature=0.7
        )
        
        # 加载或创建向量数据库
        if os.path.exists(PERSIST_DIRECTORY) and os.listdir(PERSIST_DIRECTORY):
            try:
                self.vectorstore = Chroma(
                    persist_directory=PERSIST_DIRECTORY,
                    embedding_function=self.embeddings
                )
            except Exception as e:
                print(f"加载向量数据库失败，将重新创建: {e}")
                self._create_vectorstore()
        else:
            self._create_vectorstore()
        
        self._initialized = True
    
    def _create_vectorstore(self):
        """创建向量数据库"""
        documents = self._load_documents()
        if documents:
            self.vectorstore = Chroma.from_documents(
                documents=documents,
                embedding=self.embeddings,
                persist_directory=PERSIST_DIRECTORY
            )
        else:
            # 如果没有文档，创建空的向量数据库
            self.vectorstore = Chroma.from_texts(
                texts=["知识库暂无内容，请添加文档后重新加载。"],
                embedding=self.embeddings,
                persist_directory=PERSIST_DIRECTORY
            )
    
    def _load_documents(self) -> List[Document]:
        """加载知识库文档"""
        documents = []
        
        if not os.path.exists(KNOWLEDGE_DIRECTORY):
            os.makedirs(KNOWLEDGE_DIRECTORY)
            return documents
        
        for filename in os.listdir(KNOWLEDGE_DIRECTORY):
            if filename.endswith('.md') or filename.endswith('.txt'):
                filepath = os.path.join(KNOWLEDGE_DIRECTORY, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # 按Markdown标题分割
                    markdown_splitter = MarkdownHeaderTextSplitter(
                        headers_to_split_on=[
                            ("#", "header1"),
                            ("##", "header2"),
                            ("###", "header3"),
                        ]
                    )
                    md_splits = markdown_splitter.split_text(content)
                    
                    if not md_splits:
                        text_splitter = RecursiveCharacterTextSplitter(
                            chunk_size=500,
                            chunk_overlap=50
                        )
                        chunks = text_splitter.split_text(content)
                        for i, chunk in enumerate(chunks):
                            documents.append(Document(
                                page_content=chunk,
                                metadata={"source": filename, "chunk": i}
                            ))
                    else:
                        text_splitter = RecursiveCharacterTextSplitter(
                            chunk_size=500,
                            chunk_overlap=50
                        )
                        for split in md_splits:
                            chunks = text_splitter.split_text(split.page_content)
                            for i, chunk in enumerate(chunks):
                                documents.append(Document(
                                    page_content=chunk,
                                    metadata={**split.metadata, "source": filename, "chunk": i}
                                ))
                    
                    print(f"已加载文档: {filename}")
                    
                except Exception as e:
                    print(f"加载文档 {filename} 失败: {e}")
        
        print(f"共生成 {len(documents)} 个文本块")
        return documents
    
    def reload_knowledge(self) -> dict:
        """重新加载知识库"""
        import shutil
        if os.path.exists(PERSIST_DIRECTORY):
            shutil.rmtree(PERSIST_DIRECTORY)
        
        self._initialized = False
        self.initialize()
        
        return {"status": "success", "message": "知识库已重新加载"}
    
    def chat(self, question: str, history: Optional[List[dict]] = None) -> dict:
        """对话接口"""
        self.initialize()
        
        # 检索相关文档
        docs = self.vectorstore.similarity_search(question, k=3)
        
        # 构建上下文
        context = "\n\n".join([doc.page_content for doc in docs])
        
        # 构建提示
        if history:
            history_text = "\n".join([
                f"{'用户' if h['role'] == 'user' else '助手'}: {h['content']}"
                for h in history[-5:]
            ])
            prompt = f"""你是一个智能助手，请根据以下知识库内容回答用户问题。
如果知识库中没有相关信息，请诚实地说"抱歉，我在知识库中没有找到相关信息"，不要编造答案。

历史对话:
{history_text}

知识库内容:
{context}

用户问题: {question}

回答:"""
        else:
            prompt = f"""你是一个智能助手，请根据以下知识库内容回答用户问题。
如果知识库中没有相关信息，请诚实地说"抱歉，我在知识库中没有找到相关信息"，不要编造答案。

知识库内容:
{context}

用户问题: {question}

回答:"""
        
        try:
            # 调用大模型
            answer = self.llm.invoke(prompt)
            
            # 构建来源信息
            sources = []
            seen_sources = set()
            for doc in docs:
                source = doc.metadata.get("source", "未知来源")
                if source not in seen_sources:
                    sources.append({
                        "source": source,
                        "content": doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content
                    })
                    seen_sources.add(source)
            
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
