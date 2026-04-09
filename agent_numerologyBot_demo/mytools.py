import os
import requests
import json
from loguru import logger
from dotenv import load_dotenv

from langchain_core.tools import tool
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_community.utilities import SerpAPIWrapper
from langchain_qdrant import Qdrant
from qdrant_client import QdrantClient

from models import get_lc_ali_embeddings, get_lc_ali_model_client

from logger import setup_logger


load_dotenv()

#缘份居国学研究接口的密钥，缘份居提供老黄历查询，黄历每日吉凶宜忌查询
#docker部署时，也请将这个key写入.env文件中
YUANFENJU_API_KEY = os.getenv("YUANFENJU_API_KEY")

os.environ["SERPAPI_API_KEY"] = "7b95e976cd990d9fe7695a2e3850302e40e5ba6f1fec9e6928516dbb7e4b487f"

BAZI_URL = f"https://api.yuanfenju.com/index.php/v1/Bazi/cesuan"
NAME_PAIR = f"https://api.yuanfenju.com/index.php/v1/Peidui/xingming"
PHONE_LUCK = f"https://api.yuanfenju.com/index.php/v1/Jixiong/shouji"
ZHANBU_URL = f"https://api.yuanfenju.com/index.php/v1/Zhanbu/meiri"
ZHOUGONG_URL = f"https://api.yuanfenju.com/index.php/v1/Gongju/zhougong"


# @tool 表示工具
@tool
def serp_search(query: str):
    """
    只有需要了解实时信息或不知道的事情的时候才会使用这个工具。
    """
    logger.info(f"-------- tool calling:【serp_search】--------")
    serp = SerpAPIWrapper()
    result = serp.run(query)
    logger.info(f"实时搜索结果: {result}")
    # 优化：将复杂对象转为友好字符串
    if isinstance(result, (list, dict)):
        # 只取前5个景点，格式化输出
        if isinstance(result, list) and len(result) > 0 and 'title' in result[0]:
            lines = [f"{i+1}. {item['title']}（{item.get('description','')}，評分：{item.get('rating','N/A')}）" for i, item in enumerate(result[:5])]
            return "\n".join(lines)
        return json.dumps(result, ensure_ascii=False)
    return str(result)


#对知识库的检索，本质就是个RAG
@tool
def get_info_from_local_db(query: str):
    """
    只有回答与办公室风水常识相关的问题的时候，会使用这个工具。
    """
    logger.info(f"-------- tool calling:【get_info_from_local_db】--------")
    client = Qdrant(
        QdrantClient(path="./local_qdrand"),
        "local_documents",
        get_lc_ali_embeddings(),
    )

    retriever = client.as_retriever(search_type="mmr")
    result = retriever.get_relevant_documents(query)
    return result


@tool
def bazi_cesuan(query: str):
    """
    只有用户说要测试算八字或做八字排盘的时候才会使用这个工具,需要输入用户姓名和出生年月日时，
    如果缺少用户姓名和出生年月日时则不可用.
    """
    logger.info(f"-------- tool calling:【bazi_cesuan】--------")
    if YUANFENJU_API_KEY is None:
        return "今日天机之门已闭，请改日再来。"
    prompt = ChatPromptTemplate.from_template(
        """你是一个参数查询助手，根据用户输入内容找出相关的参数并按json格式返回。
        JSON字段如下： 
        -"api_key":"{api_key}", 
        - "name":"姓名", 
        - "sex":"性别，0表示男，1表示女，如果用户输入内容中未提供，则根据姓名判断", 
        - "type":"日历类型，0农历，1公历，默认1",
        - "year":"出生年份 例：1998", 
        - "month":"出生月份 例 8", - "day":"出生日期，例：8", - "hours":"出生小时 例 14", 
        - "minute":"0"，
        如果没有找到相关参数，则需要提醒用户告诉你这些内容，只返回数据结构，不要有其他的评论，用户输入:{query}""")
    parser = JsonOutputParser()
    prompt = prompt.partial(format_instructions=parser.get_format_instructions())
    logger.info(f"参数查询prompt: {prompt.messages}")
    chain = prompt | get_lc_ali_model_client(streaming=False) | parser
    data = chain.invoke({"query": query,"api_key": YUANFENJU_API_KEY})
    logger.info(f"大模型返回参数抽取结果: {data}")
    result = requests.post(BAZI_URL, data=data)
    if result.status_code == 200:
        logger.info(f"缘分居接口返回JSON: {result.json()}")
        try:
            json = result.json()
            returnstring = "八字为:" + json["data"]["bazi_info"]["bazi"] + json["data"]["chenggu"]["description"] + json["data"]["yinyuan"]["sanshishu_yinyuan"]
            return returnstring
        except Exception as e:
            return "八字查询失败,可能是你忘记询问用户姓名或者出生年月日时了。"
    else:
        return "今日天机之门已闭，请改日再来。"

@tool
def name_pair(query: str):
    """
    只有用户说要根据姓名测试两人之间的缘份指数的时候才会使用这个工具,需要输入男女双方姓名，
    如果缺少用户姓名时则不可用，男女双方姓名必须齐备.
    """
    logger.info(f"-------- tool calling:【name_pair】--------")
    if YUANFENJU_API_KEY is None:
        return "今日天机之门已闭，请改日再来。"
    prompt = ChatPromptTemplate.from_template(
        """
        你是一个参数查询助手，根据用户输入内容找出相关的参数并按json格式返回。
        JSON字段如下： 
        -"api_key":"{api_key}", 
        - "name_male":"男方姓名", 
        - "name_female":"女方姓名",
        如果没有找到相关参数，则需要提醒用户告诉你这些内容，只返回数据结构，不要有其他的评论，用户输入:{query}
        """)
    parser = JsonOutputParser()
    prompt = prompt.partial(format_instructions=parser.get_format_instructions())
    logger.info(f"参数查询prompt: {prompt.messages}")
    chain = prompt | get_lc_ali_model_client(streaming=False) | parser
    data = chain.invoke({"query": query,"api_key": YUANFENJU_API_KEY})
    logger.info(f"大模型返回参数抽取结果: {data}")
    result = requests.post(NAME_PAIR, data=data)
    if result.status_code == 200:
        logger.info(f"缘分居接口返回JSON: {result.json()}")
        try:
            json = result.json()
            returnstring = "匹配情况:" + json["data"]["score"] + "--" + json["data"]["description"]["title"] + json["data"]["description"]["description"]
            return returnstring
        except Exception as e:
            return "匹配情况查询失败,可能是你忘记询问男女双方姓名"
    else:
        return "今日天机之门已闭，请改日再来。"

@tool
def phone_luck(query: str):
    """
    只有用户说要根据手机号测吉凶的时候才会使用这个工具,需要输入用户手机号，
    如果缺少用户手机号时则不可用.自动检查用户输入手机号是否为大陆合法手机号格式。
    """
    logger.info(f"-------- tool calling:【phone_luck】--------")
    if YUANFENJU_API_KEY is None:
        return "今日天机之门已闭，请改日再来。"
    prompt = ChatPromptTemplate.from_template(
        """
        你是一个参数查询助手，根据用户输入内容找出相关的参数并按json格式返回。
        JSON字段如下： 
        -"api_key":"{api_key}", 
        - "shouji":"手机号", 
        如果没有找到相关参数，则需要提醒用户告诉你这些内容，只返回数据结构，不要有其他的评论，用户输入:{query}
        """)
    parser = JsonOutputParser()
    prompt = prompt.partial(format_instructions=parser.get_format_instructions())
    logger.info(f"参数查询prompt: {prompt.messages}")
    chain = prompt | get_lc_ali_model_client(streaming=False) | parser
    data = chain.invoke({"query": query,"api_key": YUANFENJU_API_KEY})
    logger.info(f"大模型返回参数抽取结果: {data}")
    result = requests.post(PHONE_LUCK, data=data)
    if result.status_code == 200:
        logger.info(f"缘分居接口返回JSON: {result.json()}")
        try:
            json = result.json()
            returnstring = "吉凶情况:" + json["data"]["xiongji"] + ":" + json["data"]["score"] + "---" + json["data"]["desc"] + json["data"]["desc1"]
            return returnstring
        except Exception as e:
            return "吉凶情况查询失败,可能是你忘记询问用户手机号"
    else:
        return "今日天机之门已闭，请改日再来。"

@tool
def yaoyigua():
    """
    只有用户想要占卜抽签的时候才会使用这个工具。
    """
    logger.info(f"-------- tool calling:【yaoyigua】--------")
    api_key = YUANFENJU_API_KEY
    result = requests.post(ZHANBU_URL, data={"api_key": api_key})
    logger.info(f"缘分居meiri接口返回: {result}")
    if result.status_code == 200:
        logger.info(f"缘分居meiri接口返回JSON: {result.json()}")
        return_string = json.loads(result.text)
        image = return_string["data"]["description"]["卦曰"]
        logger.info(f"每日一占: {image}")
        return image
    else:
        return "技术错误，请告诉用户稍后再试。"

@tool
def jiemeng(query: str):
    """
    只有用户想要解梦的时候才会使用这个工具,需要输入用户梦境的内容，如果缺少用户梦境的内容则不可用。
    """
    logger.info(f"-------- tool calling:【jiemeng】--------")
    api_key = YUANFENJU_API_KEY
    LLM = get_lc_ali_model_client(streaming=False)
    prompt = PromptTemplate.from_template("根据内容提取1个关键词，只返回关键词，内容为:{topic}")
    prompt_value = prompt.invoke({"topic": query})
    keyword = LLM.invoke(prompt_value)
    logger.info(f"提取的关键词: {keyword}")
    result = requests.post(ZHOUGONG_URL, data={"api_key": api_key, "title_zhougong": keyword})
    if result.status_code == 200:
        logger.info(f"缘分居zhougong接口返回JSON: {result.json()}--{api_key}")
        returnstring = json.loads(result.text)
        return returnstring
    else:
        return "技术错误，请告诉用户稍后再试。"

