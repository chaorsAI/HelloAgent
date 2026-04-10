from mcp.server.fastmcp import FastMCP
import ast
import datetime

# 创建一个MCP服务器
mcp = FastMCP("计算器演示")

# 使用装饰器定义一个工具（Tool）
@mcp.tool()
# 原有工具：计算BMI
def calculate_bmi(weight_kg: float, height_m: float) -> dict:
    """
    计算人体BMI
    """
    bmi = weight_kg / (height_m ** 2)
    category = "偏瘦" if bmi < 18.5 else "正常" if bmi < 24 else "超重" if bmi < 28 else "肥胖"
    return {"bmi": round(bmi, 2), "category": category}

# 使用装饰器定义一个资源（Resource）：提供静态或动态数据
@mcp.resource("server://info")
def get_server_info() -> str:
    """
    提供当前服务器的基本信息。
    """
    return f"服务器状态正常。当前时间：{datetime.datetime.now()}"

# Prompt：结合服务器时间和BMI工具的提示模板
@mcp.prompt()
def health_prompt(name: str) -> str:
    """
    生成一个个性化的健康建议提示，结合当前服务器时间和BMI工具用法。

    Args:
        name: 用户姓名（用于个性化称呼）。
    """
    # 调用资源获取当前时间（注意：Prompt函数中可以直接调用其他资源/工具）
    server_info = get_server_info()
    current_time = server_info.split("：")[1]  # 提取时间部分

    # 返回Markdown格式的提示
    return f"""# 健康咨询提示
你好，{name}！当前服务器时间是{current_time}，以下是为你准备的健康建议：
1. 请用`calculate_bmi`工具计算你的BMI（参数：体重kg、身高m）；
2. 根据BMI结果，我会给你对应的健康建议（偏瘦/正常/超重/肥胖）；
3. 提示：BMI正常范围18.5-23.9，超过28需注意饮食和运动。

示例：计算体重70kg、身高1.75m的BMI → `calculate_bmi(weight_kg=70, height_m=1.75)`
"""


if __name__ == "__main__":
    # 启动 MCP 服务，使用标准输入输出方式
    mcp.run(transport='stdio') 