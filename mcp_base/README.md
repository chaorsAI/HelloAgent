# MCP Demo 项目

这是一个基于Model Context Protocol (MCP)的演示项目，展示了如何使用MCP来构建简单的工具服务。
目前项目包含功能：
- 1. 计算BMI
- 2. 获取资源(当前时间)
- 3. 健康提示(Prompt)

## 项目结构
```
mcp_base/
├── bmi_server.py               # MCP Server实现
├── bmi_client.py               # MCP Client实现
├── pyproject.toml              # 项目依赖-uv管理，只包含 mcp_base 增量依赖。公共依赖继承自根目录.toml
└── README.md                   # 项目说明
```

## 功能说明

### 1. 计算器功能
- 支持基本的四则运算
- 支持复杂的数学表达式
- 包含错误处理和输入验证

## 安装说明

1安装依赖：
```bash
uv sync --package mcp_base
```

2启动FastMCP服务
```bash
python client/bmi_server.py
```

3运行客户端：
```bash
python client/bmi_client.py
```

## 技术栈
- Python 3.11
- MCP SDK
- asyncio (异步支持)
