# 问数 - 自然语言数据查询智能体

问数是一个基于MCP (Model Context Protocol)的智能体，允许用户通过自然语言查询各种类型的数据库和数据仓库，无需编写复杂的SQL语句。

## 项目架构

整个系统基于以下架构设计：

![架构图](architecture.png)

### 核心组件

1. **前端界面**
   - 基于Vue.js的交互式界面
   - 支持多轮对话
   - 查询历史记录和收藏功能
   - 结果可视化展示

2. **后端服务**
   - Flask RESTful API
   - 用户认证与授权
   - 会话管理
   - 查询记录与分析

3. **MCP服务器**
   - 各类数据库连接器(MySQL, PostgreSQL, Oracle, SQLServer等)
   - 数据库元数据获取
   - 查询执行与结果处理
   - 错误处理与恢复机制

4. **LLM处理流程**
   - 自然语言解析
   - SQL生成
   - SQL验证与修正
   - 结果解释

## 实现流程

系统的工作流程如下：

1. 用户输入自然语言查询
2. LLM解析用户意图，生成初始SQL
3. 执行SQL查询
4. 如出现语法错误或结果为空，LLM修正SQL
5. 执行修正后的SQL
6. 将结果返回给用户，并提供自然语言解释
7. 用户反馈用于进一步优化

## 挑战与解决方案

### 1. 自然语言复杂性
- 使用RAG技术增强上下文理解
- 实现多轮对话机制解决歧义和不完整问题
- 构建同义词和术语词典

### 2. 业务上下文缺乏
- 创建Schema Linking机制
- 构建业务术语与表/列的映射
- 支持自定义业务知识库导入

### 3. 数据库复杂性
- 通过MCP服务器自动获取数据库元数据
- 建立表间关系模型
- 支持数据库特定语法自适应

### 4. 模型幻觉
- 实现SQL语法验证
- 查询结果验证机制
- 执行前的安全检查

### 5. 复杂查询
- 查询分解与优化
- 提供示例辅助生成
- 增量构建复杂查询

## 实施路线图

### 阶段一：基础框架搭建（已完成）
- 创建前端界面
- 实现基本Flask后端
- 构建MySQL MCP服务器
- 实现基础的SQL生成功能

### 阶段二：功能增强（进行中）
- 添加更多数据库支持
- 实现多轮对话修正
- 引入错误处理机制
- 增加结果可视化
- 支持多种LLM模型（已支持Anthropic Claude和DeepSeek）

### 阶段三：高级功能（计划中）
- 业务知识库集成
- 支持复杂查询
- 查询历史分析
- 性能优化
- 更多LLM模型支持

## 技术栈

- **前端**: Vue.js, ElementUI
- **后端**: Python 3.12, Flask
- **数据库连接器**: SQLAlchemy
- **MCP实现**: Python
- **LLM集成**: 
  - Anthropic Claude API
  - DeepSeek API
  - 可扩展的LLM服务框架

## 快速开始

### 环境要求
- Python 3.12+
- Docker 和 Docker Compose (可选)
- MySQL 数据库

### 安装与运行

1. 克隆仓库
```bash
git clone https://github.com/xiaoshi7915/wenshu.git
cd wenshu
```

2. 设置环境变量（复制.env.example并修改）
```bash
cp .env.example .env
# 编辑.env文件，填入API密钥和数据库连接信息
```

3. 使用启动脚本（推荐）
```bash
# Linux/macOS
./start.sh

# Windows
start.bat
```

4. 或者使用Docker启动
```bash
docker-compose up -d
```

5. 访问应用
打开浏览器访问 http://localhost:5000

详细使用说明请参考 [USAGE.md](USAGE.md) 和 [SETUP.md](SETUP.md)

## 开发指南

### 项目结构
```
app/
├── controllers/       # 控制器，处理HTTP请求
├── models/            # 数据模型
├── mcp/
│   └── servers/       # MCP服务器实现
├── services/          # 业务逻辑服务
├── static/            # 静态资源
├── templates/         # HTML模板
└── __init__.py        # 应用初始化
```

### 添加新数据库支持
1. 在`app/mcp/servers/`目录下创建新的数据库服务器类
2. 在`app/mcp/__init__.py`中的`MCPServerFactory`类中添加新数据库类型
3. 实现`get_database_metadata`、`get_sample_data`和`execute_readonly_query`方法

### 添加新LLM服务支持
1. 在`app/services/llm_service.py`中的`LLMService`类中添加新的API调用方法
2. 修改`_call_llm_api`方法，增加对新LLM服务的支持
3. 在`.env`文件中添加相应的API密钥配置

### 前端开发
前端使用Vue.js和Element UI构建，主要文件：
- `app/templates/index.html`: 主页面模板
- `app/static/js/main.js`: Vue应用代码
- `app/static/css/style.css`: 样式表

### 测试
运行单元测试:
```bash
pytest
```

手动测试可以使用示例数据库，执行:
```bash
mysql -u root -p < db_init.sql
```

## 社区贡献

欢迎贡献代码、报告问题或提出功能建议！请参考以下步骤：

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建Pull Request

## 许可证

本项目采用 MIT 许可证 - 详情参见 [LICENSE](LICENSE) 文件

## 联系我们

如有任何问题或建议，请通过以下方式联系我们：
- 电子邮件: chenxiaoshivivid@126.com
- GitHub Issues: [https://github.com/xiaoshi7915/wenshu/issues](https://github.com/xiaoshi7915/wenshu/issues) 