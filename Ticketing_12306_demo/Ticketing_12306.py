# Ticketing_12306_demo.py
# 12306 铁路智能订票小助手


import json
import requests
import inspect
import pandas as pd
from datetime import datetime
import time, random

from models import get_normal_client, ALI_TONGYI_MAX_MODEL, ALI_TONGYI_PLUS_MODEL


client = get_normal_client()

#根据实际的业务接口，做数据的获取和分析
def check_tick(date, start, end):
    print('=== 开始完整诊断流程 ===')

    # 1. 构建请求
    url = 'https://kyfw.12306.cn/lcquery/queryG?train_date={}&from_station_telecode={}&to_station_telecode={}&result_index=0&can_query=Y&isShowWZ=Y&sort_type=2&purpose_codes=00&is_loop_transfer=S&channel=E&_json_att='.format(
        date, start, end
    )
    # url = 'https://kyfw.12306.cn/otn/leftTicket/queryG?leftTicketDTO.train_date={}&leftTicketDTO.from_station={}&leftTicketDTO.to_station={}&purpose_codes=ADULT'.format(
    #     date, start, end)
    print(f'目标URL: {url}')

    # 2. 使用精简但必要的headers
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": "https://kyfw.12306.cn/otn/leftTicket/init",
        "X-Requested-With": "XMLHttpRequest",
        "Connection": "keep-alive",
    }

    # 3. 关键：记录但没有cookies的初始请求
    time.sleep(random.uniform(1, 3))
    session = requests.Session()
    print('\n[阶段1] 测试无Cookie的直接访问...')

    try:
        res = session.get(url, headers=headers, timeout=10)
        print(f'状态码: {res.status_code}')
        print(f'内容类型: {res.headers.get("Content-Type")}')
        print(f'响应长度: {len(res.text)} 字符')
        print(f'前200字符: {res.text[:200]}')

        # 保存完整响应用于分析
        with open('response_no_cookie.html', 'w', encoding='utf-8') as f:
            f.write(res.text)

    except Exception as e:
        print(f'请求异常: {e}')
        return None

    # 4. 如果有重定向，跟踪重定向链
    if res.history:
        print(f'\n发生重定向，历史记录:')
        for i, resp in enumerate(res.history):
            print(f'  重定向{i + 1}: {resp.status_code} -> {resp.url}')

    # 5. 如果返回的是HTML，分析其内容
    if 'text/html' in res.headers.get('Content-Type', ''):
        print('\n[分析] 服务器返回了HTML页面，可能的原因:')
        print('   1. 需要登录验证')
        print('   2. 触发了反爬机制')
        print('   3. 参数格式错误')

        # 检查常见错误页面关键词
        html_lower = res.text.lower()
        if 'login' in html_lower or '登录' in html_lower:
            print('   → 检测到登录页面，需要有效会话')
        if '验证码' in html_lower or 'captcha' in html_lower:
            print('   → 检测到验证码要求')
        if '繁忙' in html_lower or 'busy' in html_lower:
            print('   → 服务器繁忙或访问频率受限')

    # 6. 尝试模拟完整浏览器流程
    print('\n[阶段2] 模拟浏览器完整流程...')

    # 6.1 首先访问首页获取基础cookies
    print('   1. 访问首页获取初始Cookie...')
    home_url = 'https://kyfw.12306.cn/otn/leftTicket/init'
    time.sleep(random.uniform(1, 3))
    home_res = session.get(home_url, headers=headers, timeout=10)
    print(f'     首页状态: {home_res.status_code}, Cookie数量: {len(session.cookies)}')

    # 6.2 检查当前Cookie
    print('   当前会话Cookie:')
    for cookie in session.cookies:
        print(f'     {cookie.name}: {cookie.value[:30]}...' if len(
            cookie.value) > 30 else f'     {cookie.name}: {cookie.value}')

    # 6.3 重新尝试查询
    print('\n   2. 使用获取的Cookie重新查询...')
    # time.sleep(random.uniform(1, 3))
    res2 = session.get(url, headers=headers, timeout=10)
    print(f'     查询状态: {res2.status_code}')
    print(f'     内容类型: {res2.headers.get("Content-Type")}')

    # 7. 最终诊断
    print('\n=== 诊断摘要 ===')
    print(f'1. 初始请求状态: {res.status_code}')
    print(f'2. 带Cookie请求状态: {res2.status_code if "res2" in locals() else "N/A"}')
    print(f'3. 最终响应长度: {len(res2.text) if "res2" in locals() else len(res.text)}')

    # 保存最终响应
    with open('response_final.html', 'w', encoding='utf-8') as f:
        f.write(res2.text if 'res2' in locals() else res.text)

    print('\n诊断完成。请检查生成的response_*.html文件，特别是response_final.html的内容。')
    print('如果文件是HTML，请在浏览器中打开查看具体是什么页面。')

    return None

    data = res.json()
    print('12306接口返回，并准备后续处理:', data)

    # 这是一个列表
    result = data["data"]["result"]

    lis = []
    for index in result:
        index_list = index.replace('有', 'Yes').replace('无', 'No').split('|')
        # print(index_list)
        train_number = index_list[3]  # 车次

        if 'G' in train_number:
            time_1 = index_list[8]  # 出发时间
            time_2 = index_list[9]  # 到达时间
            prince_seat = index_list[25]  # 特等座
            first_class_seat = index_list[31]  # 一等座
            second_class = index_list[30]  # 二等座
            dit = {
                '车次': train_number,
                '出发时间': time_1,
                '到站时间': time_2,
                "是否可以预定": index_list[11],

            }
            lis.append(dit)
        else:
            # print(index_list)
            time_1 = index_list[8]  # 出发时间
            time_2 = index_list[9]  # 到达时间

            dit = {
                '车次': train_number,
                '出发时间': time_1,
                '到站时间': time_2,
                "是否可以预定": index_list[11],

            }
            lis.append(dit)
    # print(lis)
    content = pd.DataFrame(lis)
    # print(content)

    return content

def check_date():
    today = datetime.now().date()
    return today

# 定义函数映射字典
function_map = {
    "check_tick": check_tick,
    "check_date": check_date
}
tools=[
            {
                "type": "function",
                "function": {
                    "name": "check_tick",
                    "description": "给定日期查询有没有票",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "date": {
                                "type": "string",
                                "description": "日期",
                            },
                            "start": {
                                "type": "string",
                                "description": "出发站的地址编码",
                            },
                            "end": {
                                "type": "string",
                                "description": "终点站的地址编码",
                            }

                        },

                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "check_date",
                    "description": "返回当前的日期",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "str": {
                                "type": "string",
                                "description": "返回今天的日期",
                            }
                        }
                    }
                }
            }
        ]

def get_completion(messages, model=ALI_TONGYI_PLUS_MODEL):
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0,
        max_tokens=1024,
        tools=tools
    )
    return response.choices[0].message


prompt = "查询明天下午北京到上海的票？并列出车次信息"

messages = [
    {"role": "system", "content": "你是一个地图通，你可以找到任何地址，找到地址后可以参考的地址编码有<北京：BJP；上海：SHH；天津：TJP；长沙：CSQ；>"},
    {"role": "user", "content": prompt}
]
response = get_completion(messages)

messages.append(response)  # 把大模型的回复加入到对话中
print("=====大模型回复=====")
print(response)

# 用户的请求需要多次函数调用，如果返回的是函数调用结果，则打印出来
while (response.tool_calls is not None):
    for tool_call in response.tool_calls:
        args = json.loads(tool_call.function.arguments)
        print("参数：", args)

        # if (tool_call.function.name == "check_tick"):
        #     print("Call: check_tick")
        #     result = check_tick(**args)
        # elif (tool_call.function.name == "check_date"):
        #     print("Call: check_date")
        #     result = check_date()
        function_name = tool_call.function.name
        if function_name in function_map:
            print(f"Call: {function_name}")
            func = function_map[function_name]
            # 获取函数签名，python内置内省库inspect
            sig = inspect.signature(func)
            params = sig.parameters
            # 根据函数参数决定如何调用
            if params:  # 函数有参数
                if args:
                    result = func(**args)
                else:
                    # 可以提供默认值或抛出错误
                    result = func()
            else:  # 函数无参数
                result = func()
        print(f"=====函数{function_name}返回=====")
        print(result)

        messages.append({
            "tool_call_id": tool_call.id,  # 用于标识函数调用的 ID
            "role": "tool",
            "name": tool_call.function.name,
            "content": str(result)  # 数值result 必须转成字符串
        })

    response = get_completion(messages)
    print("=====大模型回复2=====")
    print(response)
    messages.append(response)  # 把大模型的回复加入到对话中

print("=====最终回复=====")
print(response.content)