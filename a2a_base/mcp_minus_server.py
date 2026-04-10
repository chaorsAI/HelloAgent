from mcp.server.fastmcp import FastMCP


# 创建一个MCP服务器
mcp = FastMCP("减法计算工具")

# 使用装饰器定义一个工具（Tool）
@mcp.tool()
# 原有工具：计算BMI
def calculate_minus(a: int, b: int) -> int:
    """
    计算两个数的减法
    """
    return a - b


if __name__ == "__main__":
    # 启动 MCP 服务，使用标准输入输出方式
    mcp.run(transport='stdio')