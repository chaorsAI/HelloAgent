# 命理机器人

命理机器人是一个基于 基于 FastAPI + LangChain + 阿里通义千问大模型构建的国风占卜 / 算命类 AI 聊天服务。

## 整体功能
1.   **智能聊天交互**：通过`/chat`接口提供多会话聊天服务，所有回复强制使用繁体中文，角色语气随用户情绪动态调整（如友好、愤怒、愉悦等）。

2.   **情绪识别驱动回复**：基于大模型分析用户输入，识别情绪标签（如`friendly`/`angry`/`depressed`等），并切换对应角色设定（如愤怒语气带诅咒、友好语气加 “亲爱的” 等）。

3.   **多工具集成调用**：封装八字测算、姓名配对、手机号吉凶、占卜抽签、解梦、办公室风水知识库检索、实时搜索等工具，严格按用户问题类型精准调用（一次对话仅调用一次工具）。

4.   **知识库管理**：通过`/add_urls`接口抓取网页内容，分割后存入 Qdrant 向量库，支持风水常识的检索增强生成（RAG）。

5.   **会话状态管理**：基于 Redis 存储聊天历史，通过`session_id`实现多用户会话隔离，配置 TTL（10 分钟）自动过期。

6.   **日志与容错**：基于 loguru 配置结构化日志，对接第三方国学 API（缘份居）时处理异常，保证服务稳定性。

## 核心技术
-   **LCEL（LangChain Expression Language）** ：构建无 Agent 的原生对话链，整合 Prompt、大模型、输出解析，支持动态 Prompt 替换。

-   **RAG（检索增强生成）** ：网页内容抓取→文本分割→Qdrant 向量存储→相似度检索，实现风水常识精准问答。

-   **工具封装与调用**：基于 `@tool` 装饰器封装工具，严格限定调用场景，保证工具调用的唯一性和精准性。

-   **情绪驱动的动态 Prompt**：根据情绪识别结果，动态绑定角色设定（如愤怒 / 友好语气），调整回复风格。

-   **多会话隔离**：基于`session_id`和 Redis TTL 实现用户会话隔离，防止历史消息串扰。

## 目录结构

```
命理机器人/
├── local_qdrand/         # 本地知识库及相关数据
├── static/               # 前端静态资源（CSS/JS/图片）
├── templates/            # 前端模板（HTML）
├── mytools.py            # 【工具函数】
├── logger.py             # 日志配置
├── models.py             # 【LLM客户端】
├── pyproject.toml        # Python 依赖包列表
├── server.py             # 主服务端代码
└── README.md             # 本文件，项目说明文档
```

## 快速开始

### 1. 安装依赖

建议使用虚拟环境(toml文件已提供)：

```bash
uv venv
uv sync
```

### 2. 启动服务

```bash
python stock_server.py
```

默认会在本地 http://127.0.0.1:8000/ 启动 Web 服务。

### 3. 访问前端

浏览器打开 [http://127.0.0.1:8000/index](http://127.0.0.1:8000/index) 即可体验命理机器人。
浏览器打开 [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) 即可打开API文档，并通过接口新增知识。

## 主要功能

- 命理相关知识问答
- 本地知识库检索和知识增加
- 现代 Web 前端界面
- 可扩展的工具函数（mytools.py）


## 使用以下命令构建和运行Docker镜像：
### 方法一：
使用docker build
docker build -t numerology-bot .

运行容器
docker run --name numerology-bot -p 8000:8000 numerology-bot

###  方法二： 
或者使用docker-compose（推荐）
docker-compose -p numerology-bot up --build
