# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

新疆大学食堂菜品交流论坛 — SpringBoot 2.1 + Vue 2.6 的前后端不分离Web应用，前端静态页面直接放在 `static/` 下由SpringBoot托管。

## 常用命令

```bash
# 启动Java后端（默认端口8080）
mvn spring-boot:run

# 启动AI助手Python服务（端口8001，需先配置 ai-assistant/.env 的 DASHSCOPE_API_KEY）
cd ai-assistant && pip install -r requirements.txt && python main.py

# 编译打包
mvn clean package

# 导入数据库（需本地MySQL运行）
mysql -u root -p < deliciousfoods.sql
```

## 访问地址

- 用户前端: `http://localhost:8080/front/index.html`
- 管理后端: `http://localhost:8080/end/index.html`

## 架构

### Java后端（SpringBoot）

标准三层架构，包结构 `com.example`：

- **controller/** — REST接口，返回 `Result<T>` 统一响应体
- **service/** — 业务逻辑，使用 `@Service` + `@Resource` 注入DAO
- **dao/** — MyBatis Mapper接口，继承 `tk.mybatis.mapper.common.Mapper<T>`，自定义查询在 `resources/mapper/*.xml`
- **entity/** — 数据库实体，对应MySQL表
- **vo/** — 视图对象，用于联表查询结果（如 `XxxVo extends Xxx`）
- **common/** — `Result`/`ResultCode` 统一响应、`MyInterceptor` 拦截器、`WebMvcConfig`
- **exception/** — `GlobalExceptionHandler` 全局异常处理，`CustomException` 业务异常

### 前端

纯静态HTML + Vue 2.6 + Element UI，无构建工具：
- `static/front/` — 用户端页面
- `static/end/` — 管理端页面
- 通过 Axios 调用后端API，Vue实例绑定在页面DOM上

### AI助手模块

独立Python服务（`ai-assistant/`），RAG架构：
- `main.py` — FastAPI服务，端口8001
- `rag.py` — LangChain + Chroma + 通义千问（qwen-plus）
- `knowledge/` — 知识库文档目录（.md/.txt）
- Java后端通过 `AiAssistantController` 代理转发到Python服务

## 关键配置

- 数据库连接: `src/main/resources/application.yml` → `spring.datasource`
- 权限配置: `authority.info` 字段定义角色和模块权限（JSON格式）
- 拦截器: `/end/page/**` 路径需登录，排除 login.html 和 register.html

## 开发模式

新增功能时的标准流程：
1. `entity/` 新建实体类
2. `dao/` 新建Mapper接口（继承 `Mapper<T>`），`resources/mapper/` 新建XML
3. `vo/` 新建视图对象（如需联表）
4. `service/` 新建服务类
5. `controller/` 新建Controller，返回 `Result.success(data)`

## 注意事项

- 密码使用 `SecureUtil.md5()` 加密（Hutool工具包）
- 默认密码: `123456`
- 分页使用 PageHelper：`PageHelper.startPage(pageNum, pageSize)` 后紧跟查询
- 文件上传限制 200MB，配置在 `application.yml`
- 无单元测试，无CI/CD
