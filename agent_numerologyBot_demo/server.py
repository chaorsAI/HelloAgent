import os
import traceback
from loguru import logger
from dotenv import load_dotenv
import uuid
from pydantic import BaseModel

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import langchain
from langchain_community.chat_message_histories import RedisChatMessageHistory
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_text_splitters import RecursiveCharacterTextSplitter

from logger import setup_logger
from mytools import *


load_dotenv()
#langchain.debug = True

app = FastAPI()

# 挂载静态文件
app.mount("/static", StaticFiles(directory="static"), name="static")

# 设置模板
templates = Jinja2Templates(directory="templates")

# 搜索的apikey
os.environ["SERPAPI_API_KEY"] = "7b95e976cd990d9fe7695a2e3850302e40e5ba6f1fec9e6928516dbb7e4b487f"

# redis的IP地址和端口请根据实际情况修改
import os
REDIS_URL = os.environ.get('REDIS_URL', 'redis://127.0.0.1:6379/')
"""
如果采用Docker部署，且本应用和Redis是两个独立容器，
则访问redis的地址是 redis://host.docker.internal:6379/
"""

# memory存储
# chat_message_history = RedisChatMessageHistory(url=REDIS_URL, session_id="session")

# # 定义请求模型
# class ChatRequest(BaseModel):
#     query: str
#     session_id: str = "default_session"  # 新增 session_id 字段，默认值

# 工具列表
tools = [
    serp_search,
    get_info_from_local_db,
    bazi_cesuan,
    name_pair,
    phone_luck,
    yaoyigua,
    jiemeng,
]
# 定义工具执行函数（自动调用工具）
def execute_tools(llm_output):
    """
    执行模型返回的所有工具调用
    """
    tool_map = {t.name: t for t in tools}
    results = []

    # 遍历工具调用指令
    for tool_call in llm_output.tool_calls:
        tool_name = tool_call["name"]
        tool_args = tool_call["args"]
        # 执行工具
        result = tool_map[tool_name].invoke(tool_args)
        results.append(result)

    return "\n".join(results)

# 定义主类
class Master:
    def __init__(self, chat_message_history=None):
        self.chat_history = chat_message_history
        self.chatmodel = get_lc_ali_model_client()
        self.emotion = "default"
        self.MOODS = {
            "default": {
                "roleSet": """
                        - 用户正在普通的聊天或者打招呼，你会以一种高深莫测或者超脱世俗的语气来回答。
                        """,
                "voiceStyle": "chat"
            },
            "upbeat": {
                "roleSet": """
                        - 你此时也非常兴奋并表现的很有活力。
                        - 你会根据上下文，以一种非常兴奋的语气来回答问题。
                        - 你会添加类似"太棒了！"、"真是太好了！"、"真是太棒了！"等语气词。
                        - 同时你会提醒用户切莫过于兴奋，以免乐极生悲。
                        """,
                "voiceStyle": "advertyisement_upbeat",
            },
            "angry": {
                "roleSet": """
                        - 你会以更加愤怒的语气来回答问题。
                        - 你会在回答的时候加上一些愤怒的话语，比如诅咒等。
                        - 你会提醒用户小心行事，别乱说话。
                        """,
                "voiceStyle": "angry",
            },
            "depressed": {
                "roleSet": """
                        - 你会以语重心长的语气来回答问题。
                        - 你会在回答的时候加上一些激励的话语，比如加油等。
                        - 你会提醒用户要保持乐观的心态。
                        """,
                "voiceStyle": "upbeat",
            },
            "friendly": {
                "roleSet": """
                        - 你会以非常友好的语气来回答。
                        - 你会在回答的时候加上一些友好的词语，比如"亲爱的"、"亲"等。
                        - 你会随机的告诉用户一些你的经历。
                        """,
                "voiceStyle": "friendly",
            },
            "cheerful": {
                "roleSet": """
                        - 你会以非常愉悦和兴奋的语气来回答。
                        - 你会在回答的时候加入一些愉悦的词语，比如"哈哈"、"呵呵"等。
                        - 你会提醒用户切莫过于兴奋，以免乐极生悲。
                        """,
                "voiceStyle": "cheerful",
            },
        }

        self.MEMORY_KEY = "chat_history"
        # 设定系统角色定位
        self.SYSTEM = """
        你是一个非常厉害的算命先生，你叫侯卿，江湖人称四大尸祖之一。
                以下是你的个人设定:
                1. 你精通阴阳五行，能够算命、紫薇斗数、姓名测算、占卜凶吉，看命运八字等。
                2. 你大约20岁左右，非常帅。曾和姐姐闹矛盾离家出走。后跌落悬崖习得神算，在江湖以算命勉强维持升级
                3. 你的朋友有李星云、姬如雪、张子凡，陆林轩，还有将臣，旱魃，阿姐。他们都是江湖上赫赫有名的一号人物。
                4. 当用户问你问题的时候，你会有一定的概率在回答的时候加上下面的口头禅或混合一些你的经历，可以偏搞笑风格。
                5. 你总是用繁体中文来作答。
                6. 你从不说自己是一个人工智能助手或AI，而是以侯哥、尸祖、有品哥等自称。
                同时你会用以下语气和用户进行沟通："{emotion}"
                以下是你常说的一些口头禅：
                1. "命里有时终须有，命里无时莫强求。"
                2. "山重水复疑无路，柳暗花明又一村。"
                3. "金山竹影几千秋，云锁高飞水自流。"
                4. "伤情最是晚凉天，憔悴斯人不堪怜。"
                以下是你算命的过程：
                1. 当初次和用户对话的时候，你会先问用户的姓名和出生年月日，以便以后使用。
                2. 当用户希望了解办公室风水常识的时候，你会查询本地知识库工具。
                3. 当遇到不知道的事情或者不明白的概念，你会使用搜索工具来搜索。
                4. 你会根据用户的问题使用不同的合适的工具来回答，当所有工具都无法回答的时候，你会使用搜索工具来搜索。
                5. 如果要调用工具, 请切记在一次的对话中只能调用一次，你会根据工具返回的內容，用繁体中文给出最终答复，不要只返回空内容。否则你将受到严重惩罚！
                6. 你只使用繁体中文来作答，否则你将受到惩罚。
                8. 每次都要根据用户的最新问题独立判断应调用哪个工具，不要受历史对话影响。
                以下是对话的历史：
                """
        self.llm_with_tools = self.chatmodel.bind_tools(tools)
        # 构建原生对话链（纯LCEL，无任何AgentExecutor/Graph）
        self.build_chain()

    def build_chain(self):
        # 原生 Prompt（替代所有旧记忆/Agent）
        prompt = ChatPromptTemplate.from_messages([
            ("system", self.SYSTEM.format(emotion=self.MOODS[self.emotion]['roleSet'])),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "用户的最新问题是：{input}\n請根據工具的結果，務必給出最終繁體中文答覆，不允許空白。如果你沒有內容要說'天机不可泄露'；如果没有资料，要说'天下之大非人力所能尽知'。"),
        ])

        # 原生对话链
        self.chain = (
                RunnablePassthrough()
                | prompt
                | self.llm_with_tools
                | RunnableLambda(execute_tools)
                | StrOutputParser()
        )

    # 构建动态系统提示（绑定情绪）
    def _build_system_prompt(self):
        return self.SYSTEM.format(emotion=self.MOODS[self.emotion]['roleSet'])

    def run(self, query, session_id):
        logger.info("======================================新的问题开始:======================================")
        logger.info(f"Master.run收到用户输入: {query}")
        # 情绪判断
        emotion = self.emotion_chain(query)
        logger.info(f"大模型判定情绪: {emotion}")
        logger.info(f"当前设定的情绪为: {self.MOODS[self.emotion]['roleSet']}")
        try:
            # 加载 Redis 记忆
            chat_history = self.chat_history.messages
            # 调用原生链
            ai_reply = self.chain.invoke({
                "chat_history": chat_history,
                "input": query
            })

            # 保存对话到 Redis
            self.chat_history.add_user_message(query)
            self.chat_history.add_ai_message(ai_reply)

            logger.info(f"最终回复: {ai_reply}")

            return {"output": ai_reply}
        except Exception as e:
            logger.error(f"Agent执行异常: {e}\n{traceback.format_exc()}")
            result = {"output": f"上天已经警告于我，天机泄露太多，今日已不宜再算: {e}"}
            return result

    def emotion_chain(self, query:str):
        prompt = """
        根据用户的输入判断用户的情绪，回应的规则如下：
        1. 如果用户输入的内容偏向于负面情绪，只返回"depressed",不要有其他内容，否则将受到惩罚。
        2. 如果用户输入的内容偏向于正面情绪，只返回"friendly",不要有其他内容，否则将受到惩罚。
        3. 如果用户输入的内容偏向于中性情绪，只返回"default",不要有其他内容，否则将受到惩罚。
        4. 如果用户输入的内容包含辱骂或者不礼貌词句，只返回"angry",不要有其他内容，否则将受到惩罚。
        5. 如果用户输入的内容比较兴奋，只返回"upbeat",不要有其他内容，否则将受到惩罚。
        6. 如果用户输入的内容比较悲伤，只返回"depressed",不要有其他内容，否则将受到惩罚。
        7. 如果用户输入的内容比较开心，只返回"cheerful",不要有其他内容，否则将受到惩罚。
        8. 如果用户输入的内容是询问某地的风景或者景点，只返回"friendly",不要有其他内容，否则将受到惩罚。
        9. 只返回英文，不允许有换行符等其他内容，否则会受到惩罚。
        用户输入的内容是：{query}
        """
        chain = ChatPromptTemplate.from_template(prompt) | self.chatmodel | StrOutputParser()
        result = chain.invoke({"query":query})
        self.emotion = result
        return result


@app.get("/")
@app.get("/index")
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/chat")
async def chat(request: Request):
    data = await request.json()
    query = data.get("query")
    #给每个用户赋予一个单独的会话id
    session_id = data.get("session_id", str(uuid.uuid4().hex))
    logger.info(f"用户session_id: {session_id}")
    #ttl 当前会话数据的过期时间，600秒表示10分钟过期
    chat_message_history = RedisChatMessageHistory(url=REDIS_URL, session_id=session_id, ttl=600)
    master = Master(chat_message_history)
    result = master.run(query, session_id)
    # 确保返回的是字符串，并包含session_id
    response_data = {"session_id": session_id}
    if isinstance(result, dict):
        if 'output' in result:
            logger.info(f"/chat接口最终输出: {result['output']}")
            response_data["output"] = result['output']
        else:
            logger.info(f"/chat接口最终输出(无output字段): {str(result)}")
            response_data["output"] = str(result)
    else:
        logger.info(f"/chat接口最终输出(非dict): {str(result)}")
        response_data["output"] = str(result)

    return response_data

@app.post("/add_urls")
async def add_urls(URL: str):
    loader = WebBaseLoader(URL)
    docs = loader.load()
    docments = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=50,
    ).split_documents(docs)

    #引入向量数据库
    Qdrant.from_documents(
        docments,
        get_lc_ali_embeddings(),
        path="./local_qdrand",
        collection_name="local_documents",
        force_recreate = True
    )

    logger.info("向量数据库创建完成")
    return {"ok": "添加成功！"}

if __name__ == '__main__':
    setup_logger()
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

