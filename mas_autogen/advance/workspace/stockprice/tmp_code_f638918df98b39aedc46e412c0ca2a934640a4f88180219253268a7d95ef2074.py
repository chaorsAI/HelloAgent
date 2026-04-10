import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import mplfinance as mpf
from datetime import datetime, timedelta

# 获取当前日期
today = datetime.today()
current_year_month = today.strftime("%Y-%m")

# 美团在港交所的股票代码为 3690.HK
stock_symbol = "3690.HK"

# 下载本月至今的数据
start_date = f"{current_year_month}-01"
end_date = today.strftime("%Y-%m-%d")

# 获取数据
df_month = yf.download(stock_symbol, start=start_date, end=end_date)
df_week = yf.download(stock_symbol, start=today - timedelta(days=7), end=end_date)

# 分析本月股价变化
if not df_month.empty:
    start_price = df_month['Open'][0]
    end_price = df_month['Close'][-1]
    change = end_price - start_price
    change_percent = (change / start_price) * 100
    analysis = (
        f"美团公司（股票代码：3690.HK）本月（{current_year_month}）至今股价从 {start_price:.2f} 港元 "
        f"变动至 {end_price:.2f} 港元，变动幅度为 {change:+.2f} 港元（{change_percent:+.2f}%）。"
    )
else:
    analysis = "未能获取本月美团公司的股价数据。"

print("=== 股票变化分析 ===")
print(analysis)

# 绘制最近一周的K线图
if not df_week.empty and len(df_week) >= 2:
    # 使用mplfinance绘制K线图
    mpf.plot(
        df_week,
        type='candle',
        style='charles',
        title='美团最近一周K线图',
        ylabel='价格 (HKD)',
        volume=True,
        savefig='meituan_kline.png'
    )
    print("K线图已保存为 meituan_kline.png")
else:
    print("数据不足，无法绘制最近一周的K线图。")
