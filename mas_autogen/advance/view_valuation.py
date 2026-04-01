# view_valuation.py
# 使⽤autoGen查看股价变动实例


import os
import asyncio

from autogen_ext.code_executors.docker import DockerCommandLineCodeExecutor
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.ui import Console
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_agentchat.conditions import (
    TextMentionTermination,
    MaxMessageTermination
)
from autogen_agentchat.agents import (
    AssistantAgent,
    CodeExecutorAgent
)

from models import  get_ag_ali_model_client


async def main():
    try:
        # 初始化模型客户端
        model_client = get_ag_ali_model_client()

        # 创建助手代理
        assistant = AssistantAgent(
            name="coder",
            system_message='''你需要编写 python/shell 代码来解决任务。将代码包装在指定脚本类型的代码块中。
            用户无法修改您的代码。因此，不要建议需要其他人修改的不完整代码。如果代码块不打算由执行器执行，请不要使用它。
            不要在一个响应中包含多个代码块。不要要求其他人复制和粘贴结果。检查执行器返回的执行结果。
            如果结果表明存在错误，请修复错误并再次输出代码。建议使用完整代码而不是部分代码或代码更改。
            如果错误无法修复，或者即使代码成功执行后任务仍未解决，请分析问题，重新审视您的假设，收集您需要的其他信息，
            并考虑尝试其他方法。''',
            model_client=model_client
        )

        # 创建代码执行器
        code_executor = DockerCommandLineCodeExecutor(work_dir="workspace/stockprice")
        await code_executor.start()

        # 创建执行器代理
        executor = CodeExecutorAgent(
            name="executor",
            code_executor=code_executor
        )

        # 设置终止条件
        max_msg_termination = MaxMessageTermination(max_messages=10)
        text_termination = TextMentionTermination("TERMINATE")
        combined_termination = max_msg_termination | text_termination

        # 创建团队聊天
        team = RoundRobinGroupChat(
            [assistant, executor],
            termination_condition=combined_termination
        )

        # 运行任务
        stream = team.run_stream(task="今天是几号，获取美团公司(三快科技)本月至今的股票变化信息，并且用文字对股票变化进行分析")
        await Console(stream)

    except Exception as e:
        print(f"发生错误: {str(e)}")
    finally:
        if 'code_executor' in locals():
            await code_executor.stop()

if __name__ == "__main__":
    asyncio.run(main())