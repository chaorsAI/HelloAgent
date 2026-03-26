import os
from dotenv import load_dotenv

import langchain

from langchain_classic.agents import AgentExecutor, create_self_ask_with_search_agent

from langchain_community.tools.tavily_search import TavilyAnswer
from langchain_core.prompts import PromptTemplate

from models import (
    get_lc_o_ali_model_client,
    get_langsimth_client,
    ALI_TONGYI_MAX_MODEL,
    ALI_TONGYI_DEEPSEEK_V3
)


load_dotenv()
#开启调试模型
langchain.debug = True

llm = get_lc_o_ali_model_client(model=ALI_TONGYI_DEEPSEEK_V3)

# 加载在线 Prompt模板
# client = get_langsimth_client()
# prompt = client.pull_prompt("hwchase17/self-ask-with-search")
# print("hwchase17/self-ask-with-search:",prompt)

# template_template = '''
# Answer the following question. When needed, you can ask follow-up questions and answer them to reach the final answer. Always use English format for follow-up questions and answers:
#
# Examples:
# Question: Who lived longer, Muhammad Ali or Alan Turing?
# Are follow up questions needed here: Yes.
# Follow up: How old was Muhammad Ali when he died?
# Intermediate answer: Muhammad Ali was 74 years old when he died.
# Follow up: How old was Alan Turing when he died?
# Intermediate answer: Alan Turing was 41 years old when he died.
# So the final answer is: Muhammad Ali
#
# Question: When was the founder of craigslist born?
# Are follow up questions needed here: Yes.
# Follow up: Who founded craigslist?
# Intermediate answer: Craigslist was founded by Craig Newmark.
# Follow up: When was Craig Newmark born?
# Intermediate answer: Craig Newmark was born on December 6, 1952.
# So the final answer is: December 6, 1952
#
# Question: Who was George Washington's paternal grandfather?
# Are follow up questions needed here: Yes.
# Follow up: Who was George Washington's father?
# Intermediate answer: George Washington's father was Augustine Washington.
# Follow up: Who was Augustine Washington's father?
# Intermediate answer: Augustine Washington's father was Lawrence Washington.
# So the final answer is: Lawrence Washington
#
# IMPORTANT:
# 1. ONLY use the exact format shown above
# 2. DO NOT include any explanations or extra text
# 3. DO NOT use markdown formatting like **bold**
# 4. ONLY output in the specified format
# 5. End your response with "So the final answer is: [answer]"
#
# Question: {input}
# Are follow up questions needed here: {agent_scratchpad}
# '''

"""
当然我们也可以【按照上述格式】将 PromptTemplate 翻译成中文
📢 📢 📢 但是这里特别注意：
关键引导词必须保留不变：Question、Follow up、Intermediate answer、So the final answer is
也就是冒号前面的词 保留英文！！！
【原因】create_self_ask_with_search_agent-SelfAskOutputParser对模型输出的格式有严格、硬编码的英文【关键字依赖】
详见 langchain_classic.agents.output_parsers.self_ask.py
- "Follow up:" : 作为 followups 来源
- "So the final answer is: " : finish_string 来源；⚠️⚠️⚠️：这里末尾还有个【空格】一定不能丢
- "Intermediate Answer" : 作为 action 的调用源
"""
# ❌❌❌【错误示例】❌❌❌
# template_template_x = '''
# 在回答用户问题时，可以自己提出问题并回答，来增强对问题的理解以提高回答质量。
# 示例：
# 问题：谁活得更久，穆罕默德·阿里还是阿兰·图灵？
# 这里是否需要后续问题：是的。
# 追问：穆罕默德·阿里去世时几岁？
# 中间答案：穆罕默德·阿里去世时74岁。
# 追问：阿兰·图灵去世时几岁？
# 中间答案：阿兰·图灵去世时41岁。
# 最终答案：穆罕默德·阿里
#
# 用户问题: {input}
# 解决问题:{agent_scratchpad}
# '''

# ✅✅✅【正确示例】✅✅✅
template_template = '''
在回答用户问题时，可以自己提出问题并回答，来增强对问题的理解以提高回答质量。
示例:
Question: 谁活得更久，穆罕默德·阿里还是阿兰·图灵？
这里是否需要后续问题：是的。
Follow up: 穆罕默德·阿里去世时几岁？
Intermediate answer: 穆罕默德·阿里去世时74岁。 
Follow up: 阿兰·图灵去世时几岁？
Intermediate answer: 阿兰·图灵去世时41岁。
So the final answer is: 穆罕默德·阿里。

用户问题: {input}
解决问题:{agent_scratchpad}
'''
prompt = PromptTemplate.from_template(template_template)

tools = [TavilyAnswer(
    max_results=1,
    include_raw_content=True,
    name="Intermediate Answer",
    tavily_api_key=os.getenv("TAVILY_API_KEY"))]

agent = create_self_ask_with_search_agent(llm, tools, prompt)
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    handle_parsing_errors=True)

print(agent_executor.invoke({"input": "《大白鲨》和《皇家赌场》的导演都来自同一个国家吗?"}))
"""
示例四：
问：《大白鲨》和《皇家赌场》的导演都来自同一个国家吗？
这里是否需要后续问题：是的。
追问：《大白鲨》的导演是谁？
中间答案：《大白鲨》的导演是史蒂文·斯皮尔伯格。
追问：史蒂文·斯皮尔伯格来自哪里？
中间答案：美国。
追问：皇家赌场的导演是谁？
中间答案：皇家赌场的导演是马丁·坎贝尔。
追问：马丁·坎贝尔来自哪里？
中间答案：新西兰。
所以最终的答案是：不是
"""