# 智能助手服务

基于 LangChain + 通义千问 + Chroma 的 RAG 智能对话助手。

## 快速开始

### 1. 安装依赖

```bash
cd ai-assistant
pip install -r requirements.txt
```

### 2. 配置API Key

复制 `.env.example` 为 `.env`，并填入你的通义千问 API Key：

```bash
cp .env.example .env
```

编辑 `.env` 文件：
```
DASHSCOPE_API_KEY=sk-your-actual-api-key
```

### 3. 添加知识库文档

将 Markdown 文档放入 `knowledge/` 目录：

```bash
# 示例
cp your-docs/*.md knowledge/
```

### 4. 启动服务

```bash
python main.py
```

服务将在 `http://127.0.0.1:8001` 启动。

## API 接口

### 对话接口

```http
POST /chat
Content-Type: application/json

{
  "question": "今天食堂有什么好吃的？",
  "history": [
    {"role": "user", "content": "你好"},
    {"role": "assistant", "content": "你好！我是智能助手"}
  ]
}
```

响应：
```json
{
  "status": "success",
  "answer": "根据今天的菜单...",
  "sources": [
    {"source": "menu.md", "content": "..."}
  ]
}
```

### 重新加载知识库

```http
POST /reload
```

### 查看知识库状态

```http
GET /knowledge/status
```

## 目录结构

```
ai-assistant/
├── main.py           # FastAPI 主服务
├── rag.py            # RAG 核心逻辑
├── requirements.txt  # Python 依赖
├── .env.example      # 环境变量模板
├── knowledge/        # 知识库文档目录
│   └── *.md          # Markdown 文档
└── chroma_db/        # 向量数据库（自动生成）
```

## 注意事项

1. 首次运行会自动处理知识库文档并构建向量索引
2. 更新知识库文档后，调用 `/reload` 接口重新加载
3. 通义千问 API 需要[阿里云 DashScope](https://dashscope.console.aliyun.com/) 账号
