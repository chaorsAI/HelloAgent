import asyncio
import os
from typing import Literal, Optional
from pydantic import BaseModel, Field
from enum import Enum

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.ui import Console
from autogen_ext.models.openai import OpenAIChatCompletionClient

from models import *


# 定义代理的响应格式，使用 Pydantic BaseModel
class Emotion(str, Enum):
    HAPPY = "高兴"
    SAD = "悲伤"
    NEUTRAL = "一般"
    ANGRY = "愤怒"

class AgentResponse(BaseModel):
    thoughts: str
    response: Emotion

model_client = OpenAIChatCompletionClient(
    model=ALI_TONGYI_MAX1_MODEL,
    api_key=os.getenv(ALI_TONGYI_API_KEY_OS_VAR_NAME),
    base_url=ALI_TONGYI_URL,
    response_format=AgentResponse,
    model_info={
        "vision": True,
        "function_calling": True,
        "json_output": True,
        "family": "unknown",
        "structured_output": True
    },
)

agent = AssistantAgent(
    "assistant",
    model_client=model_client,
    system_message='''按照以下JSON格式将输入分类为高兴、悲伤或一般：
    {
        "thoughts": "分析用户情绪的原因", 
        "response": "高兴|悲伤|一般|愤怒"
    }'''
)

asyncio.run(Console(agent.run_stream(task="哇哦，今天的天气好好啊。")))
asyncio.run(Console(agent.run_stream(task="气死我了，想起那个事情就火大")))
asyncio.run(Console(agent.run_stream(task="今天是2026年4月1号")))
