import asyncio
import os

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_core import CancellationToken
from autogen_core.model_context import BufferedChatCompletionContext
from autogen_ext.models.openai import OpenAIChatCompletionClient

from models import get_ag_ali_model_client


# 定义一个网络搜索工具
async def web_search(query: str) -> str:
    """在网络上查找信息"""
    return "AutoGen 是一个用于构建多代理应用程序的编程框架。"

# 创建一个使用 qwen 模型的Agent
model_client = get_ag_ali_model_client()

agent = AssistantAgent(
    name="assistant",
    model_client=model_client,
    tools=[web_search],  # 假设已经定义了 web_search 工具
    system_message="使用工具来解决任务。",
    model_context=BufferedChatCompletionContext(buffer_size=5),  # 只使用最近 5 条消息
)
