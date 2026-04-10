# server_agent.py：提供加法服务的智能体

import os
import asyncio
import uvicorn
from flask import Flask, jsonify, request

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from mcp.client.stdio import stdio_client
from mcp import ClientSession


app = FastAPI(title=__name__)

# A2A核心：Agent Card（服务说明书）A2A Server计算实现
AGENT_CARD = {
    "agent_id": "math_mixed_orchestrator_v1",
    "name": "混合运算编排智能体",
    "description": "支持本地加法和MCP减法运算",
    "endpoint": "http://localhost:8888/a2a",
    "capabilities": [
        {
            "method": "add",  # 本地加法方法
            "params": ["a", "b"],
            "returns": "sum"
        },
        {
            "method": "minus",  # MCP减法方法
            "params": ["a", "b"],
            "returns": "difference"
        }
    ]
}

# 暴露Agent Card的端点（供客户端发现）
# @app.route("/agent_card", methods=["GET"])
@app.get("/agent_card")
async def get_agent_card(request: Request):
    return AGENT_CARD


# A2A通信的核心端点（处理客户端请求）
# @app.route("/a2a", methods=["POST"])
@app.post("/a2a")
async def handle_a2a_request(request: Request):
    # 解析A2A标准请求（JSON-RPC简化版）
    try:
        # ✅ 正确：在异步函数内用 await 调用 request.json()
        req_data = await request.json()
    except Exception as e:
        return JSONResponse(
            content={"error": f"解析请求失败: {str(e)}", "id": None},
            status_code=400
        )

    method = req_data.get("method")
    params = req_data.get("params", {})
    req_id = req_data.get("id")

    # A2A 服务端自行计算
    if method == "add":
        # 本地直接计算加法（无需MCP）
        try:
            a, b = params["a"], params["b"]
            result = a + b
            return {
                "jsonrpc": "2.0",
                "result": {"sum": result},
                "id": req_id
            }
        except KeyError:
            return {"error": "Missing 'a' or 'b' parameter", "id": req_id}, 400
    elif method == "minus":
        # 调用MCP工具（减法计算）
        try:
            difference = await call_mcp_minus_tool(
                tool_name="calculate_minus",
                tool_params={"a": params["a"], "b": params["b"]},
                mcp_server_cmd=["python", "mcp_minus_server.py"]  # 启动MCP服务端
            )
            return {
                "jsonrpc": "2.0",
                "result": {"difference": difference},
                "id": req_id
            }
        except Exception as e:
            return {"error": f"MCP调用失败: {str(e)}", "id": req_id}, 500
    else:
        return {"error": f"不支持的方法: {method}", "id": req_id}, 400


# MCP客户端封装：调用减法工具（stdio传输）
# ------------------------------
async def call_mcp_minus_tool(tool_name: str, tool_params: dict, mcp_server_cmd: list) -> int:
    """
    用MCP客户端连接stdio服务端，调用工具并返回结果
    """
    # 1. 启动MCP服务端进程，用stdio_client创建流（连接stdin/stdout）
    async with stdio_client(mcp_server_cmd) as (read_stream, write_stream):
        # 2. 初始化MCP会话（完成协议握手）
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()  # 必须：握手确认
            # 3. 调用MCP工具（calculate_minus）
            result = await session.call_tool(tool_name, tool_params)
            # 4. 提取结果（根据fastmcp返回结构调整，此处假设result.output是工具返回值）
            # 若返回结构是{"output": 66}，则改为result["output"]
            return result.output


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8888)