import json
import requests
import inspect
import pandas as pd
from datetime import datetime


def check_tick1(date, start, end):
    print('=== 开始完整诊断流程 ===')

    # 1. 构建请求
    url = 'https://kyfw.12306.cn/otn/leftTicket/queryG?leftTicketDTO.train_date={}&leftTicketDTO.from_station={}&leftTicketDTO.to_station={}&purpose_codes=ADULT'.format(
        date, start, end)
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
    home_res = session.get(home_url, headers=headers, timeout=10)
    print(f'     首页状态: {home_res.status_code}, Cookie数量: {len(session.cookies)}')

    # 6.2 检查当前Cookie
    print('   当前会话Cookie:')
    for cookie in session.cookies:
        print(f'     {cookie.name}: {cookie.value[:30]}...' if len(
            cookie.value) > 30 else f'     {cookie.name}: {cookie.value}')

    # 6.3 重新尝试查询
    print('\n   2. 使用获取的Cookie重新查询...')
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