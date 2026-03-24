# CustomReActAgent.python
# Langchain 1.0 新范式下 creat_rect_agent 的实现
# creat_rect_agent 属于 langchian_classic 兼容包，不建议再直接使用


import json
from dotenv import load_dotenv
from typing import *

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import BaseTool
from langchain_core.runnables import Runnable, RunnableConfig
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage
from langchain_core.outputs import ChatGeneration, ChatResult

from langchain.agents import create_agent

from langchain_tavily import TavilySearch

from models import get_lc_o_ali_model_client, ALI_TONGYI_MAX_MODEL
from tool import calculator


load_dotenv()

# ========== 1. 定义工具 ==========
# 使用现成


# ========== 2. 构建 ReAct 提示模板 ==========
def build_react_prompt(tools: List[BaseTool]) -> ChatPromptTemplate:
    """构建 ReAct 格式的提示词"""
    tool_descriptions = "\n".join([
        f"{tool.name}: {tool.description}" for tool in tools
    ])

    return ChatPromptTemplate.from_messages([
        SystemMessage(content=f"""你是一个智能助手，可以使用工具来回答问题。

可用的工具：
{tool_descriptions}

请严格按照以下格式回答：
思考: 分析问题并决定下一步
行动: 要使用的工具名称，必须是以下之一：[{', '.join(t.name for t in tools)}]
行动输入: 工具的输入参数
观察: 工具返回的结果
...（这个思考/行动/观察循环可以重复多次）
思考: 我现在有足够信息回答问题了
最终答案: 对原始问题的最终回答

现在开始："""),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="history"),
    ])


# ========== 3. 解析 LLM 响应 ==========
def parse_llm_response(text: str) -> Dict[str, str]:
    """解析 LLM 的响应，提取思考、行动、行动输入"""
    result = {"thought": "", "action": None, "action_input": None, "final_answer": None}

    # 解析思考
    if "思考:" in text:
        thought_part = text.split("思考:")[1]
        if "行动:" in thought_part:
            result["thought"] = thought_part.split("行动:")[0].strip()
        elif "最终答案:" in thought_part:
            result["thought"] = thought_part.split("最终答案:")[0].strip()
        else:
            result["thought"] = thought_part.strip()

    # 解析行动
    if "行动:" in text and "行动输入:" in text:
        action_part = text.split("行动:")[1]
        if "行动输入:" in action_part:
            action_line = action_part.split("行动输入:")[0].strip()
            result["action"] = action_line.strip('"\' ')

    # 解析行动输入
    if "行动输入:" in text:
        action_input_part = text.split("行动输入:")[1]
        if "观察:" in action_input_part:
            result["action_input"] = action_input_part.split("观察:")[0].strip().strip('"\'')
        else:
            result["action_input"] = action_input_part.strip().strip('"\'')

    # 解析最终答案
    if "最终答案:" in text:
        answer_part = text.split("最终答案:")[1]
        result["final_answer"] = answer_part.strip()

    return result


# ========== 4. 实现 ReAct 循环 ==========
class CustomReActAgent:
    """纯 Runnable 实现的 ReAct Agent"""

    def __init__(self, llm: Runnable, tools: List[BaseTool], max_iterations: int = 5):
        self.llm = llm
        self.tools = {tool.name: tool for tool in tools}
        self.max_iterations = max_iterations
        self.prompt_template = build_react_prompt(tools)

    def invoke(self, input_text: str, config: Optional[RunnableConfig] = None) -> Dict[str, Any]:
        """执行 ReAct 循环"""
        history = []  # 存储对话历史
        iterations = 0

        print(f"🤔 问题: {input_text}")
        print("-" * 50)

        while iterations < self.max_iterations:
            iterations += 1

            # 构建提示
            prompt = self.prompt_template.format_messages(
                input=input_text,
                history=history
            )

            # 调用 LLM
            response: ChatResult = self.llm.invoke(prompt, config=config)
            llm_output = response.content

            print(f"🔁 第 {iterations} 轮思考:")
            print(f"   LLM 原始输出:\n   {llm_output}")

            # 解析响应
            parsed = parse_llm_response(llm_output)

            if parsed["thought"]:
                print(f"   思考: {parsed['thought']}")

            # 检查是否是最终答案
            if parsed["final_answer"]:
                print(f"✅ 最终答案: {parsed['final_answer']}")
                return {
                    "output": parsed["final_answer"],
                    "iterations": iterations,
                    "history": history
                }

            # 执行工具调用
            if parsed["action"] and parsed["action"] in self.tools:
                tool = self.tools[parsed["action"]]
                print(f"   行动: 调用工具 '{parsed['action']}'，输入: {parsed['action_input']}")

                try:
                    # 执行工具
                    tool_result = tool.invoke(parsed["action_input"])
                    print(f"   观察: {tool_result}")

                    # 更新历史
                    history.extend([
                        AIMessage(content=llm_output),
                        ToolMessage(
                            content=str(tool_result),
                            tool_call_id=f"call_{iterations}"
                        )
                    ])

                except Exception as e:
                    error_msg = f"工具调用失败: {str(e)}"
                    print(f"   ❌ {error_msg}")
                    history.extend([
                        AIMessage(content=llm_output),
                        ToolMessage(content=error_msg, tool_call_id=f"call_{iterations}")
                    ])
            else:
                error_msg = f"无效行动: {parsed.get('action')}"
                print(f"   ⚠️  {error_msg}")
                history.append(AIMessage(content=llm_output))
                history.append(ToolMessage(
                    content=f"错误: 无法识别行动 '{parsed.get('action')}'，可用行动: {list(self.tools.keys())}",
                    tool_call_id=f"call_{iterations}"
                ))

            print("-" * 30)

        # 达到最大迭代次数
        return {
            "output": f"达到最大迭代次数({self.max_iterations})仍未解决问题",
            "iterations": iterations,
            "history": history
        }


# ========== 5. 使用示例 ==========
def main():
    # 初始化组件
    llm = get_lc_o_ali_model_client()

    # 创建工具
    search = TavilySearch(max_results=3)
    tools = [calculator, search]

    # 创建 ReAct Agent
    agent = CustomReActAgent(
        llm=llm,
        tools=tools,
        max_iterations=3
    )

    # 测试简单问题
    print("测试1: 简单计算")
    result1 = agent.invoke("计算 25 的平方根是多少？")
    print(f"\n结果: {result1['output']}")

    print("\n" + "=" * 60 + "\n")

    # 测试需要多步推理的问题
    print("测试2: 需要搜索和计算的问题")
    result2 = agent.invoke(
        "苹果公司创始人是谁？如果他今年还活着，是多少岁？"
    )
    print(f"\n最终结果: {result2['output']}")

    print("\n" + "=" * 60 + "\n")

    # 查看思考历史
    print("思考历史:")
    for i, msg in enumerate(result2.get('history', [])):
        if isinstance(msg, AIMessage):
            print(f"{i}: 🤖 {msg.content[:100]}...")
        elif isinstance(msg, ToolMessage):
            print(f"{i}: 🔧 工具结果: {msg.content[:100]}...")


if __name__ == "__main__":
    main()