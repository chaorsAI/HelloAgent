# client_agent.py：调用加法服务的智能体
import requests


def call_a2a_agent(agent_card_url, method, params):
    """
    按A2A协议调用智能体
    """
    # 1. 发现：获取Agent Card（可选，这里假设已知端点）
    agent_card = requests.get(agent_card_url).json()

    # 2. 构造A2A请求（JSON-RPC格式）
    a2a_request = {
        "jsonrpc": "2.0",
        "method": method,
        "params": params,
        "id": 1  # 请求ID，用于匹配响应
    }

    # 3. 发送请求到服务端点
    endpoint = agent_card["endpoint"]   # 从Agent Card中获取
    # endpoint = "http://localhost:8888/a2a"
    response = requests.post(endpoint, json=a2a_request)

    return response.json()


if __name__ == "__main__":
    # 调用加法服务：计算1+2
    result = call_a2a_agent(
        agent_card_url="http://localhost:8888/agent_card",  # Agent Card地址
        method="add",
        params={"a": 1, "b": 2}
    )
    print(f"A2A调用结果：{result['result']['sum']}")  # 输出：3

    # 调用减法服务：计算700-34
    result = call_a2a_agent(
        agent_card_url="http://localhost:8888/agent_card",  # Agent Card地址
        method="minus",
        params={"a": 1, "b": 2}
    )
    print(f"A2A调用结果：{result['result']['difference']}")  # 输出：666