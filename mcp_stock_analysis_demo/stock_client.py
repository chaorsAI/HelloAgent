import asyncio
import os
from dotenv import load_dotenv
from loguru import logger
import requests
import json

from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent
from mcp import ClientSession


from models import get_lc_o_ali_model_client, ALI_TONGYI_API_KEY_OS_VAR_NAME
from utils.logger import logger

load_dotenv()
api_key=os.getenv(ALI_TONGYI_API_KEY_OS_VAR_NAME)

# 服务端MCP地址（关键：带/mcp路径）
MCP_BASE = "http://localhost:8888/mcp"

async def main():
    client = MultiServerMCPClient(
        {
            "Stock": {
                "url": "http://localhost:8888/mcp",
                "transport": "sse",
            }
        }
    )

    tools = await client.get_tools()
    for index, tool in enumerate(tools):
        logger.info(f"第{index + 1}个工具：{tool.name}")

    llm = get_lc_o_ali_model_client()
    logger.info(f"=================准备实际的业务工作=================")

    agent = create_agent(
        model=llm,
        tools=tools
    )

    math_response = await agent.ainvoke(
        {"messages": [{"role": "user", "content": "分析一下 03690 这个怎么样？啥时候值得买"}]}
    )
    logger.info(f"大模型返回参数抽取结果: {math_response}")

    # math_response = await agent.ainvoke(
    #     {"messages": [{"role": "user", "content": "长沙的景点有哪些"}]}
    # )
    # print("分析结果为:", math_response)

# 运行异步主函数
if __name__ == "__main__":
    asyncio.run(main())