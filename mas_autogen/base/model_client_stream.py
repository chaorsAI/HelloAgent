import asyncio
import os

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_core import CancellationToken


from models import get_ag_ali_model_client

# 创建一个使用 qwen 模型的Agent
model_client = get_ag_ali_model_client()

streaming_assistant = AssistantAgent(
    name="assistant",
    model_client=model_client,
    system_message="你是一位得力的助手",
    model_client_stream=True,  # 流式传输模型客户端生成的文本
)


async def main():
    print("=============== 【model_client_stream】 ===============")

    # async for message in streaming_assistant.on_messages_stream(
    #         [TextMessage(content="请说出两个南美洲城市的名字", source="user")],
    #         cancellation_token=CancellationToken(),
    # ):
    #     print("---------- on_messages_stream ----------")
    #     print(message)

    # 使用run_stream()产生同样的效果
    # async for message in streaming_assistant.run_stream(task="请说出两个南美洲城市的名字"):  # type: ignore
    #     print("---------- run_stream ----------")
    #     print(message)


    response = await streaming_assistant.run(task="请说出两个南美洲城市的名字")
    print("---------- run ----------")
    print(f"返回类型: {type(response)}")
    print(response)

asyncio.run(main())