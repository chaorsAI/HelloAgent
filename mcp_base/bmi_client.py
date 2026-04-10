import asyncio
import os
import logging

from mcp.client.stdio import stdio_client
from mcp import ClientSession, StdioServerParameters

# 配置日志级别
logging.getLogger('mcp').setLevel(logging.WARNING)

async def main():
    # 1. 配置MCP Server启动参数
    bmi_params = StdioServerParameters(
        # 启动服务器的命令
        command="python",
        # 服务器脚本路径（需绝对路径或相对工作目录）
        args=["./bmi_server.py"],
        # 可选：设置服务器的工作目录（默认当前目录）
        env=None
    )

    # 2. 用stdio_client创建封装流（关键修复：不再手动创建子进程）
    async with stdio_client(bmi_params) as (read_stream, write_stream):
        # 3. 用封装流初始化ClientSession
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()  # 必须：完成协议握手
            print("✅ 会话初始化完成，成功连接到MCP服务器！")

            # 4. 调用工具（正常执行）
            bmi = await session.call_tool(
                "calculate_bmi",
                {"weight_kg": 70.0, "height_m": 1.75}
            )
            print(f"\n📊 BMI结果：{bmi}")  # 输出：{"bmi": 22.86, "category": "正常"}

            # 5. 获取资源
            info = await session.read_resource("server://info")
            print(f"\n⏰ 服务器信息：{info}")

            # 6. 调用Prompt
            prompt = await session.get_prompt(
                "health_prompt",
                {"name": "张三"}
            )
            print(f"\n💡 健康提示：\n{prompt}")


if __name__ == "__main__":
    # 运行异步主函数（Python 3.7+）
    asyncio.run(main())