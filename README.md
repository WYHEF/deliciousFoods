# 新疆大学食堂菜品交流论坛

## 🍽️ 项目简介
基于SpringBoot和Vue.js开发的新疆大学食堂菜品交流平台，为学生提供菜品分享、评论交流和食堂资讯的一站式服务。

## 🚀 技术栈

### 后端技术
- **框架**: SpringBoot 2.1.0
- **持久层**: MyBatis + tk.MyBatis
- **数据库**: MySQL 8.0
- **分页**: PageHelper
- **工具库**: Hutool工具包
- **文件处理**: Apache POI
- **图片处理**: Thumbnailator

### 前端技术
- **框架**: Vue.js 2.6.11
- **UI组件**: Element UI
- **HTTP客户端**: Axios
- **滑动组件**: Swiper
- **富文本编辑器**: Quill

### 开发工具
- **构建工具**: Maven
- **IDE**: IntelliJ IDEA
- **数据库管理**: MySQL Workbench

## 📋 功能模块

### 用户端功能
- 👥 用户注册登录系统
- 🍲 菜品信息浏览与搜索
- 💬 菜品评论与交流
- ❤️ 菜品收藏功能
- 📝 个人笔记管理
- 🔔 消息通知系统

### 管理端功能
- 👨‍💼 管理员权限管理
- 📊 数据统计与分析
- 📢 资讯发布管理
- 🖼️ 文件上传与管理
- 📈 系统数据监控

## 🗃️ 数据库设计
项目包含完整的数据库设计，主要表结构包括：
- 用户信息表(UserInfo)
- 菜品信息表(FoodsMenuInfo)
- 食材信息表(FoodsMaterialInfo)
- 分类信息表(ClassifyInfo)
- 评论表(NotesInfoComment)
- 收藏表(CollectInfo)
- 点赞表(PraiseInfo)
- 消息表(MessageInfo)
- 新闻表(NewsInfo)

## 🛠️ 部署运行

### 环境要求
- JDK 1.8+
- MySQL 5.7+
- Maven 3.6+

### 启动步骤
1. 导入数据库脚本: `deliciousfoods.sql`
2. 配置数据库连接: `src/main/resources/application.yml`
3. 运行主程序: `Application.java`
4. 访问前端页面: http://localhost:8080/front/index.html

### 默认访问地址
- 用户前端: http://localhost:8080/front/index.html
- 管理后端: http://localhost:8080/end/index.html

## 📁 项目结构
```
deliciousFoods/
├── src/main/java/com/example/
│   ├── Application.java          # SpringBoot启动类
│   ├── common/                   # 通用组件
│   ├── controller/               # 控制器层
│   ├── dao/                      # 数据访问层
│   ├── entity/                   # 实体类
│   ├── service/                  # 服务层
│   └── vo/                       # 值对象
├── src/main/resources/
│   ├── application.yml           # 应用配置
│   ├── mapper/                   # MyBatis映射文件
│   └── static/                   # 静态资源
│       ├── front/                # 用户前端页面
│       └── end/                  # 管理后端页面
└── deliciousfoods.sql            # 数据库脚本
```

## 🌟 项目特色

1. **前后端分离**: 采用SpringBoot + Vue.js前后端分离架构
2. **响应式设计**: 支持PC端和移动端访问
3. **权限控制**: 完善的用户权限管理系统
4. **文件管理**: 集成文件上传下载功能
5. **数据可视化**: 使用ECharts实现数据统计展示

## 👨‍💻 开发者信息
- **开发者**: 五氧化二钒 (WYHEF)
- **专业**: 软件工程
- **项目类型**: 小学期实践项目
- **学校**: 新疆大学
- **GitHub**: https://github.com/WYHEF

## 📄 许可证
本项目仅用于学习交流，请勿用于商业用途。

---

💡 **提示**: 项目已成功部署到GitHub，包含完整的源代码和文档说明。

如有任何问题或建议，欢迎联系开发者！