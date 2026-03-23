# helloAgent.py
# 基于 Langchain 的 agent 示例

from dotenv import load_dotenv

# create_agent：1.0 基于 LangGraph 状态的智能执行体
from langchain.agents import create_agent
# 旧范式下的 Agent 调用方式
from langchain_classic.agents import create_tool_calling_agent, AgentExecutor

from langchain_community.tools import tool, TavilySearchResults

from langchain_core.prompts import ChatPromptTemplate

from models import get_lc_o_ali_model_client


# 从 .env 文件加载所有环境变量
load_dotenv()

# 定义工具
@tool
def magic_function(input: int) -> int:
    """模拟工具函数."""
    return input + 2


"""
{agent_scratchpad}为必需，中间代理操作和工具输出消息将在这里传递。
"""
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "你是一个AI助手"),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ]
)

# 定义llm
llm = get_lc_o_ali_model_client()

#Tavily需要申请api_key才可使用，并设置系统环境变量 TAVILY_API_KEY
#没有申请的可以使用.env中的api_key，但是因为TAVILY有限制，可能出现调用次数过多导致限额用完或者被封禁等情况
search = TavilySearchResults(max_results=3)
tools = [magic_function, search]

# 旧范式，新版本已不推荐
# agent = create_tool_calling_agent(llm, tools, prompt)
# agent_executor = AgentExecutor(
#     agent=agent,
#     tools=tools,
#     verbose=True)

# 推荐使用的新范式!!!
agent = create_agent(
    model=llm,
    tools=tools,
    # debug=True
)

# LLM 自己内部能搞定
# result = agent_executor.invoke({"input": "你是谁？"})
result = agent.invoke(
    {"messages":[{
        "role":"user",
        "content":"你是谁？"}]
    }
)
print(result)

# magic_function 需要借助 custom tool
# result = agent_executor.invoke({"input": "magic_function(3)的值是多少？"})
result = agent.invoke(
    {"messages":[{
        "role":"user",
        "content":"magic_function(3)的值是多少？"}]
    }
)
print(result)

# LLM 的知识边界导致不知道现在的事，会尝试规划找”人“帮忙
# result = agent_executor.invoke({"input": "请问现任的美国总统的年龄的平方是多少? 请用中文告诉我答案"})
result = agent.invoke(
    {"messages":[{
        "role":"user",
        "content":"请问现任的美国总统的年龄的平方是多少? 请用中文告诉我答案"}]
    }
)
print("===============")
print(result)







