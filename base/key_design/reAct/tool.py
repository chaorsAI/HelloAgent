# tool.python
# 共用的 tool 工具



from dotenv import load_dotenv
import numexpr
import math

from langchain_community.tools import tool

@tool
def calculator(expression: str) -> str:
    """使用Python的numexpr库计算表达式。表达式应该是解决问题的单行数学表达式。.
    例子:
        "37593 * 67"
        "37593**(1/5)"
        "37593^(1/5)"
    """
    local_dict = {"pi": math.pi, "e": math.e}
    return str(
        numexpr.evaluate(
            expression.strip(),
            global_dict={},
            local_dict=local_dict,  # 添加常用数学函数
        )
    )