"""
FastAPI 主服务
提供智能助手API接口
"""
import os
from typing import List, Optional
from dotenv import load_dotenv
from pydantic import BaseModel

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from rag import rag_assistant

# 加载环境变量
load_dotenv()

# 创建FastAPI应用
app = FastAPI(
    title="智能助手服务",
    description="基于RAG的智能对话助手API",
    version="1.0.0"
)

# 配置CORS - 允许Java后端调用
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应限制来源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 请求模型
class ChatRequest(BaseModel):
    """对话请求"""
    question: str
    history: Optional[List[dict]] = None


class ChatResponse(BaseModel):
    """对话响应"""
    status: str
    answer: str
    sources: List[dict] = []


# API路由
@app.get("/")
async def root():
    """健康检查"""
    return {"status": "ok", "message": "智能助手服务运行中"}


@app.get("/health")
async def health():
    """健康检查接口"""
    return {"status": "healthy"}


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    对话接口
    
    接收用户问题，返回基于知识库的回答
    """
    if not request.question or not request.question.strip():
        raise HTTPException(status_code=400, detail="问题不能为空")
    
    result = rag_assistant.chat(
        question=request.question,
        history=request.history
    )
    
    return ChatResponse(**result)


@app.post("/reload")
async def reload_knowledge():
    """
    重新加载知识库
    
    当知识库文档更新后调用此接口
    """
    result = rag_assistant.reload_knowledge()
    return result


@app.get("/knowledge/status")
async def knowledge_status():
    """获取知识库状态"""
    knowledge_dir = "./knowledge"
    if not os.path.exists(knowledge_dir):
        return {"status": "empty", "document_count": 0, "documents": []}
    
    documents = [f for f in os.listdir(knowledge_dir) 
                 if f.endswith('.md') or f.endswith('.txt')]
    
    return {
        "status": "loaded",
        "document_count": len(documents),
        "documents": documents
    }


if __name__ == "__main__":
    host = os.getenv("PYTHON_SERVICE_HOST", "127.0.0.1")
    port = int(os.getenv("PYTHON_SERVICE_PORT", 8001))
    
    print(f"启动智能助手服务: http://{host}:{port}")
    uvicorn.run(app, host=host, port=port)
