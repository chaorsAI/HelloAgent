import asyncio
import os

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_agentchat.ui import Console
from autogen_core import CancellationToken

from models import get_ag_ali_model_client


# 定义一个网络搜索工具
async def web_search(query: str) -> str:
    """在网络上查找信息"""
    return "AutoGen 是一个用于构建多代理应用程序的编程框架。"

# 创建一个使用 qwen 模型的Agent
model_client = get_ag_ali_model_client()

# 创建AssistantAgent
agent = AssistantAgent(
    name="assistant",
    model_client=model_client,
    tools=[web_search],
    system_message="使用工具来解决任务。",
)

"""
AgentChat 提供了一组预设Agent，每个Agent对消息的响应方式各不相同：
- AssistantAgent：是一个内置的Agent，使用大语言模型，并且具有使用工具的能力
- UserProxyAgent： 接受用户输入并将其作为响应返回的代理。
- CodeExecutorAgent： 可以执行代码的代理。
- OpenAIAssistantAgent： 由 OpenAI Assistant 支持的代理，能够使用自定义工具。
- MultimodalWebSurfer： 可以搜索网络并访问网页以获取信息的多模态代理。
- FileSurfer： 可以搜索和浏览本地文件以获取信息的代理。
- VideoSurfer： 可以观看视频以获取信息的代理。
"""

#调用大模型获得响应
async def assistant_run() -> None:
    # 使用高级、封装好的便捷方法run()方法返回 TaskResult 对象
    # - 根据任务字符串，自动构建初始的系统提示和用户消息。
    # - 可能隐式地创建并管理一个内部会话，自动维护对话历史。
    # - 在特定配置下（如启用了code_execution_config），会自动调用代码解释器并整合结果。
    # - 为了一次性完成“任务”，它可能在内部多次调用类似on_messages的流程。
    # print("===============【run】===============")
    # response = await agent.run(
    #     task = TextMessage(content="查找关于 AutoGen 的信息", source="user"),
    #     cancellation_token=CancellationToken(),
    # )
    # print(response.messages)

    # on_messages（） 方法来获取代理对给定消息的响应
    # 是一个底层、原子性的操作。接收一个消息列表，让Agent基于其自身的
    # 系统提示、能力、工具配置以及对话历史（如果支持），处理这“一批”输入消息，
    # 并生成一个响应。它只负责“处理这一轮”的对话。您需要自行管理对话的轮次、
    # 历史消息的拼接以及可能的复杂流程
    print("===============【on_messages】===============")
    response = await agent.on_messages(
        [TextMessage(content="查找关于 AutoGen 的信息", source="user")],
        cancellation_token=CancellationToken(),
    )
    print("===============【inner_messages】===============")
    print(response.inner_messages)
    print("===============【chat_message】===============")
    print(response.chat_message)

asyncio.run(assistant_run())


async def assistant_run_stream() -> None:
    # 使用run_stream()
    await Console(
        agent.run_stream(
            task=TextMessage(content="查找关于 AutoGen 的信息", source="user"),
            cancellation_token=CancellationToken()
        )


    # 使用on_messages_stream()
    # agent.on_messages_stream(
    #     [TextMessage(content="查找关于 AutoGen 的信息", source="user")],
    #     cancellation_token=CancellationToken(),
    # )
)
print("===============【on_stream】===============")
asyncio.run(assistant_run_stream())


async def assistant_run_stream_custom() -> None:
    # 流式处理stream_result，这时自定义处理不得使用Console
    stream_result = agent.run_stream(
        task=TextMessage(content="查找关于 AutoGen 的信息", source="user"),
        cancellation_token=CancellationToken()
    )
    full_response = ""  # 用于累积完整回复
    # 使用 async for 循环从生成器中逐个取出块（chunk）
    async for chunk in stream_result:
        # chunk的类型可能是多种，我们需要从中提取文本
        if hasattr(chunk, 'content') and isinstance(chunk.content, str):
            text = chunk.content
            full_response += "-->"
            full_response += text
        # 也可能包含其他信息，如工具调用，这里简单处理
        elif isinstance(chunk, dict) and chunk.get("type") == "text":
            full_response += "-->"
        full_response += chunk.get("text", "")
    print(f"\n\n【完整回复已接收】\n{full_response}")

print("===============【on_stream_custom】===============")
# asyncio.run(assistant_run_stream_custom())