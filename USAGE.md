# WenShu 使用说明

## 1. 环境配置

### 1.1 配置环境变量

复制`.env.example`文件并重命名为`.env`，然后编辑该文件：

```bash
cp .env.example .env
```

编辑`.env`文件，修改数据库连接信息和API密钥：

```
# Flask配置
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=your_secret_key_here

# 数据库配置
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=password
DB_NAME=wenshu
DB_PORT=3306

# LLM配置
LLM_PROVIDER=deepseek  # 可选: anthropic, deepseek
ANTHROPIC_API_KEY=your_anthropic_api_key_here
DEEPSEEK_API_KEY=your_deepseek_api_key_here

# 日志配置
LOG_LEVEL=INFO
```

### 1.2 LLM服务配置

WenShu支持多种LLM服务提供商，可以通过修改`LLM_PROVIDER`环境变量来选择：

1. **Anthropic Claude**: 设置 `LLM_PROVIDER=anthropic`
   - 需要提供有效的`ANTHROPIC_API_KEY`
   - 提供高质量的SQL生成和结果解释

2. **DeepSeek**: 设置 `LLM_PROVIDER=deepseek`
   - 需要提供有效的`DEEPSEEK_API_KEY`
   - 支持中文输入的更好体验
   - 提供本地化的查询处理能力

默认服务提供商为DeepSeek，可根据需要进行切换。

### 1.3 使用启动脚本

使用提供的启动脚本可以快速设置环境并启动应用：

```bash
# Linux/macOS
./start.sh

# Windows
start.bat
```

### 1.4 使用Docker启动

使用Docker Compose可以快速启动整个应用和数据库：

```bash
docker-compose up -d
```

服务将在后台运行，可以通过以下命令查看日志：

```bash
docker-compose logs -f
```

### 1.5 本地开发启动

如果你想在本地开发环境运行，首先安装依赖：

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# 安装依赖
pip install -r requirements.txt
```

然后启动应用：

```bash
python run.py
```

## 2. 使用指南

### 2.1 访问应用

应用启动后，在浏览器中访问：http://localhost:5000

### 2.2 连接数据库

1. 点击界面右上角的"连接数据库"按钮
2. 在弹出的对话框中输入数据库连接信息
3. 点击"连接"按钮

样例数据库连接信息：
- 数据库类型：MySQL
- 主机：localhost (如使用Docker环境，则为`mysql`)
- 端口：3306
- 数据库名：wenshu
- 用户名：wenshu (或 root)
- 密码：wenshu (或 password)

### 2.3 查询数据

连接数据库后，可以使用自然语言输入查询，例如：

- "查询所有员工的姓名和薪资"
- "哪个部门的平均薪资最高?"
- "2018年入职的员工有哪些?"
- "研发部有多少名员工?"
- "列出所有职位的最低和最高薪资"

### 2.4 直接使用SQL

如果你熟悉SQL，也可以直接输入SQL查询：

1. 点击输入框旁边的"使用SQL"按钮
2. 在弹出的对话框中输入SQL语句
3. 点击"执行"按钮

### 2.5 查看数据库结构

连接数据库后，点击右上角数据库名称，在下拉菜单中选择"查看数据库结构"，可以查看数据库中的表、字段及其关系。

### 2.6 导出查询结果

查询结果显示后，可以点击结果区域右上角的"导出"按钮，将结果导出为CSV文件。

## 3. 常见问题

### 3.1 连接数据库失败

- 检查数据库服务是否正常运行
- 确认数据库连接信息是否正确
- 如果使用Docker环境，主机名应为`mysql`而不是`localhost`

### 3.2 查询返回错误

- 检查网络连接是否正常
- 确认LLM API密钥是否有效
- 尝试切换LLM服务提供商
- 尝试简化查询语句或使用更明确的描述

### 3.3 没有返回预期的结果

- 使用更明确、具体的查询描述
- 尝试使用数据库中存在的表名和字段名
- 查看数据库结构，了解可查询的内容
- 如果使用中文查询效果不佳，尝试切换到DeepSeek服务

### 3.4 LLM服务问题

- 如果API请求失败，检查API密钥是否正确
- 确认所选LLM服务是否可用
- 尝试切换到另一个LLM服务提供商
- 调整配置参数（如max_tokens, temperature等）

## 4. 系统限制

- 当前仅支持MySQL数据库
- 仅支持只读查询操作
- 对于非常复杂的查询可能需要多次尝试
- 查询结果最多返回100条记录
- LLM服务有API调用限制和潜在费用 