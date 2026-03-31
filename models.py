
import os
from openai import OpenAI
import inspect
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI

from langsmith import Client

from autogen_ext.models.openai import OpenAIChatCompletionClient

from Constant import *


# 加载环境变量
load_dotenv()

def get_ag_ali_model_client():
    return OpenAIChatCompletionClient(
        model=ALI_TONGYI_MAX1_MODEL,
        api_key=os.getenv(ALI_TONGYI_API_KEY_OS_VAR_NAME),
        base_url=ALI_TONGYI_URL,
        model_info={
            "vision": True,           # 支持多模态（图片+文本）输入
            "function_calling": True, # 支持工具/函数调用（核心Agent能力）
            "json_output": True,      # 支持返回JSON格式数据
            "family": "unknown",      # 模型所属系列（未分类），由于AutoGen最开始是兼容OpenAI的，这里除了OpenAI到的几个类型就都填"unknown"
            "structured_output": True # 支持严格结构化输出
        })

def get_lc_o_model_client(api_key=os.getenv(ALI_TONGYI_API_KEY_OS_VAR_NAME),
                          base_url=ALI_TONGYI_URL,
                          model=ALI_TONGYI_MAX_MODEL, temperature = 0.7, verbose=False, debug=False):
    '''
    以OpenAI兼容的方式，通过LangChain获得指定平台和模型的客户端
    可以通过传入api_key，base_url，model，temperature四个参数来覆盖默认值
    verbose，debug两个参数，分别控制是否输出调试信息，是否输出详细调试信息，默认不打印
    :return: 指定平台和模型的客户端，默认平台和模型为阿里百炼qwen-max-latest，温度=0.7
    '''
    function_name = inspect.currentframe().f_code.co_name
    if(verbose):
        print(f"{function_name}-平台：{base_url},模型：{model},温度：{temperature}")
    if(debug):
        print(f"{function_name}-平台：{base_url},模型：{model},温度：{temperature},key：{api_key}")
    return ChatOpenAI(api_key=api_key, base_url=base_url,model=model,temperature=temperature)

def get_lc_o_ali_model_client(model=ALI_TONGYI_PLUS_MODEL, temperature = 0.7, verbose=False, debug=False):
    '''
    以OpenAI兼容的方式，通过LangChain获得阿里大模型的客户端
    可以通过传入model，temperature 两个参数来覆盖默认值
    verbose，debug两个参数，分别控制是否输出调试信息，是否输出详细调试信息，默认不打印
    :return: 指定平台和模型的客户端，默认模型为阿里百炼里的qwen-plus，温度=0.7
    '''
    return get_lc_o_model_client(api_key=os.getenv(ALI_TONGYI_API_KEY_OS_VAR_NAME), base_url=ALI_TONGYI_URL
                                 , model=model, temperature =temperature, verbose=verbose, debug=debug)

def get_lc_o_ds_model_client(model=DEEPSEEK_CHAT_MODEL, temperature = 0.7, verbose=False, debug=False):
    '''
    以OpenAI兼容的方式，通过LangChain获得DeepSeek大模型的客户端
    可以通过传入model，temperature 两个参数来覆盖默认值
    verbose，debug两个参数，分别控制是否输出调试信息，是否输出详细调试信息，默认不打印
    :return: 指定平台和模型的客户端，默认模型为DeepSeek的deepseek-chat，温度=0.7
    '''
    return get_lc_o_model_client(api_key=os.getenv(DEEPSEEK_API_KEY_OS_VAR_NAME), base_url=DEEPSEEK_URL
                                 , model=model, temperature =temperature, verbose=verbose, debug=debug)

def get_normal_client(api_key=os.getenv(ALI_TONGYI_API_KEY_OS_VAR_NAME), base_url=ALI_TONGYI_URL,
                      verbose=False, debug=False):
    """
    使用原生api获得指定平台的客户端，但未指定具体模型，缺省平台为阿里云百炼
    也可以通过传入api_key，base_url两个参数来覆盖默认值
    verbose，debug两个参数，分别控制是否输出调试信息，是否输出详细调试信息，默认不打印
    """
    function_name = inspect.currentframe().f_code.co_name
    if (verbose):
        print(f"{function_name}-平台：{base_url}")
    if (debug):
        print(f"{function_name}-平台：{base_url},key：{api_key}")
    return OpenAI(api_key=api_key, base_url=base_url)

def get_langsimth_client():
    return Client(
        api_key=os.getenv(LANGSMITH_API_KEY_OS_VAR_NAME),  # 如果传入，会覆盖环境变量
        api_url=LANGSMITH_API_URL,  # 覆盖端点
)
