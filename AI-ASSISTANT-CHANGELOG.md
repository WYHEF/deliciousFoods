# AI智能助手功能新增说明

## 功能概述

为新疆大学食堂菜品交流论坛新增了基于 RAG（检索增强生成）的智能对话助手，用户可以通过右下角悬浮气泡与助手对话，助手基于知识库回答问题。

## 技术架构

```
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│   Vue前端   │ ──── │ Java后端    │ ──── │ Python服务  │
│ 悬浮气泡    │ HTTP │ Controller  │ HTTP │ LangChain   │
│ 对话界面    │      │ 代理转发    │      │ RAG检索     │
└─────────────┘      └─────────────┘      └─────────────┘
                                                   │
                                            ┌──────┴──────┐
                                            │ Markdown文档│
                                            │ Chroma向量库│
                                            └─────────────┘
```

## 技术选型

| 组件 | 技术方案 | 说明 |
|------|----------|------|
| 前端组件 | 纯JavaScript | 避免与现有Vue实例冲突 |
| 后端代理 | Spring Boot + Hutool | 代理转发到Python服务 |
| RAG框架 | LangChain | 文档切分、向量检索 |
| 大模型 | 通义千问 (qwen-plus) | 阿里云DashScope |
| 向量数据库 | Chroma | 轻量级本地向量存储 |
| 嵌入模型 | text-embedding-v2 | 通义千问嵌入模型 |
| Web框架 | FastAPI | Python异步Web服务 |

## 新增文件

### Python服务 (ai-assistant/)

```
ai-assistant/
├── main.py              # FastAPI主程序，提供HTTP接口
├── rag.py               # RAG核心逻辑：文档加载、向量存储、检索生成
├── requirements.txt     # Python依赖
├── .env                 # 环境变量配置（API Key）
├── .env.example         # 环境变量模板
├── README.md            # 使用说明
└── knowledge/           # 知识库目录
    └── example.md       # 示例知识库文档
```

### Java后端

```
src/main/java/com/example/controller/
└── AiAssistantController.java    # AI助手代理Controller
```

### 前端组件

```
src/main/resources/static/front/js/
└── ai-assistant.js               # 悬浮气泡组件（纯JS实现）
```

### 配置文件修改

- `application.yml` - 新增 `ai.service.url` 配置

## API接口

### Java后端接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/ai/chat` | POST | 对话接口 |
| `/ai/reload` | POST | 重新加载知识库 |
| `/ai/knowledge/status` | GET | 查看知识库状态 |
| `/ai/health` | GET | 健康检查 |

### Python服务接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/chat` | POST | RAG对话 |
| `/reload` | POST | 重载知识库 |
| `/knowledge/status` | GET | 知识库状态 |
| `/health` | GET | 健康检查 |

## 使用说明

### 1. 配置API Key

编辑 `ai-assistant/.env`：
```bash
DASHSCOPE_API_KEY=your_api_key_here
```

### 2. 启动服务

```bash
# 终端1: 启动Python服务
cd ai-assistant
pip install -r requirements.txt
python main.py

# 终端2: 启动Java后端
mvn spring-boot:run
```

### 3. 添加知识库文档

将 `.md` 或 `.txt` 文件放入 `ai-assistant/knowledge/` 目录，然后调用：

```bash
curl -X POST http://localhost:8080/ai/reload
```

---

## 踩坑记录

### 1. requirements.txt 编码问题

**问题**：pip安装时报错 `UnicodeDecodeError: 'gbk' codec can't decode`

**原因**：Windows下pip默认使用GBK编码读取requirements.txt，但文件包含中文注释

**解决**：移除所有中文注释，只保留纯英文包名和版本号

### 2. LangChain版本兼容问题

**问题**：`ModuleNotFoundError: No module named 'langchain.chains'`

**原因**：LangChain新版本（2.x）移除了旧的chains模块，API大幅变化

**解决**：
- 旧版：`from langchain.chains import RetrievalQA`
- 新版：直接使用 `llm.invoke(prompt)` 方式，手动实现检索+生成流程

### 3. LangChain导入路径变化

**问题**：`ModuleNotFoundError: No module named 'langchain.schema'`

**原因**：新版LangChain将核心模块迁移到 `langchain_core`

**解决**：
```python
# 旧版
from langchain.schema import Document
from langchain.prompts import PromptTemplate

# 新版
from langchain_core.documents import Document
from langchain_core.prompts import PromptTemplate
```

### 4. 前端Vue实例冲突

**问题**：点击悬浮气泡无反应，控制台报Vue相关错误

**原因**：页面已有Vue实例（`#wrapper`），新组件也尝试创建Vue实例，产生冲突

**解决**：改用纯JavaScript实现前端组件，不依赖Vue框架

### 5. 缺少dashscope模块

**问题**：`ModuleNotFoundError: No module named 'dashscope'`

**原因**：通义千问API需要阿里云SDK，但未在requirements.txt中声明

**解决**：`pip install dashscope`

### 6. chroma-hnswlib编译问题

**问题**：chromadb安装时chroma-hnswlib编译失败

**原因**：缺少C++编译环境

**解决**：使用预编译的wheel包，或安装Visual Studio Build Tools

---

## 依赖版本

```
fastapi>=0.100.0
uvicorn>=0.23.0
python-multipart>=0.0.6
langchain>=0.2.0
langchain-community>=0.2.0
langchain-openai>=0.1.0
langchain-text-splitters>=0.2.0
langchain-core>=0.2.0
langchain-chroma>=0.1.0
chromadb>=0.4.0
dashscope>=1.14.0
markdown>=3.5.0
httpx>=0.25.0
pydantic>=2.0.0
python-dotenv>=1.0.0
```

---

## 后续优化建议

1. **流式输出**：实现打字机效果，提升用户体验
2. **多轮对话优化**：更好的上下文管理
3. **知识库管理界面**：前端可视化添加/删除文档
4. **引用跳转**：点击来源文档可跳转到原文
5. **意图识别**：区分闲聊和知识库问答
6. **缓存优化**：减少重复问题的API调用

---

## 更新日期

2026-03-20
