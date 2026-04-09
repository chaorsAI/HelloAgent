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
            name="Coder",
            system_message='''你需要编写 python/shell 代码来解决任务。将代码包装在指定脚本类型的代码块中。
            用户无法修改您的代码。因此，不要建议需要其他人修改的不完整代码。如果代码块不打算由执行器执行，请不要使用它。
            不要在一个响应中包含多个代码块。不要要求其他人复制和粘贴结果。检查执行器返回的执行结果。
            如果结果表明存在错误，请修复错误并再次输出代码。建议使用完整代码而不是部分代码或代码更改。
            如果错误无法修复，或者即使代码成功执行后任务仍未解决，请分析问题，重新审视您的假设，收集您需要的其他信息，
            并考虑尝试其他方法。
            请务必完成用户所有的要求！！！''',
            model_client=model_client
        )

        # 创建代码执行器
        code_executor = DockerCommandLineCodeExecutor(work_dir="workspace/stockprice")
        await code_executor.start()

        # 创建执行器代理
        executor = CodeExecutorAgent(
            name="Executor",
            code_executor=code_executor
        )

        # 创建一个评论家assistant
        critic = AssistantAgent(
            name="Critic",
            system_message="""
                    评论家。您是一位乐于助人的助手，能够通过提供 1（差）- 10（好）的分数来评估给定可视化代码的质量，同时提供明确的理由。您必须为每次评估考虑可视化最佳实践。具体来说，您可以从以下维度仔细评估代码
            - 错误（bug）：是否存在错误、逻辑错误、语法错误或拼写错误？代码编译失败的原因是什么？应该如何修复？如果存在任何错误，错误分数必须小于 5。
            - 数据转换（transformation）：数据是否针对可视化类型进行了适当的转换？例如，数据集是否根据需要进行了适当的过滤、聚合或分组？如果使用日期字段，是否先将日期字段转换为日期对象等？
            - 目标合规性（compliance）：代码与指定可视化目标的匹配程度如何？
            - 可视化类型 (type)：考虑最佳实践，可视化类型是否适合数据和意图？是否有更有效地传达见解的可视化类型？如果其他可视化类型更合适，则分数必须小于 5。
            - 数据编码 (encoding)：数据是否适合可视化类型编码？
            - 美学 (aestics)：可视化的美学是否适合可视化类型和数据？

            您必须为上述每个维度提供分数。
            {错误：0，转换：0，合规性：0，类型：0，编码：0，美观性：0}
            不建议代码。
            最后，根据上述批评，建议程序员应采取的具体行动清单，以改进代码。
            要求：务必全程使用中文进行交流和反馈！！！"
            """,
            model_client=model_client,
        )

        # 设置终止条件
        # max_msg_termination = MaxMessageTermination(max_messages=10)
        text_termination = TextMentionTermination("TERMINATE")
        # combined_termination = max_msg_termination | text_termination
        combined_termination = text_termination

        # 创建团队聊天
        team = RoundRobinGroupChat(
            [assistant, executor, critic],
            termination_condition=combined_termination
        )

        # 运行任务
        stream = team.run_stream(task="今天是几号，获取美团公司(三快科技)本月至今的股票变化信息，并且用文字对股票变化进行分析。同时获取最近一周美团的股价信息，并绘制成K线图，生成图片保存到当前目录！请务必生成一张K线图图片")
        await Console(stream)

    except Exception as e:
        print(f"发生错误: {str(e)}")
    finally:
        if 'code_executor' in locals():
            await code_executor.stop()

if __name__ == "__main__":
    asyncio.run(main())