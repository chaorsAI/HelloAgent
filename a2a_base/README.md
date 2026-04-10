# A2A Demo 项目

这是一个基于Agent to Agent (A2A)的演示项目，展示了如何使用A2A来构建简单的 Agent 间通讯，以及 A2A + MCP协作的简单示例。
目前项目包含功能：
- 1. 加法，A2A 服务端自行计算
- 2. 减法，A2A 服务端充当 MCP 客户端从 MCP 服务端获取

## 项目结构
```
mcp_base/
├── a2a_server.py               # A2A Server/MCP Client 实现
├── a2a_client.py               # A2A Client 实现
├── mcp_minus_server            # MCP Server 实现
├── pyproject.toml              # 项目依赖-uv管理，只包含 mcp_base 增量依赖。公共依赖继承自根目录.toml
└── README.md                   # 项目说明
```

## 安装说明

1安装依赖：
```bash
uv sync --package mcp_base
```

2启动 FastMCP 服务
```bash
uv run mcp_minus_server.py
```

3启动 a2a_server 服务
```bash
uv run a2a_server.py
```

4运行客户端：
```bash
uv run a2a_client.py
```

## 技术栈
- Python 3.11
- MCP SDK
- asyncio (异步支持)
- A2A
- FastAPI、FastMCP 服务
