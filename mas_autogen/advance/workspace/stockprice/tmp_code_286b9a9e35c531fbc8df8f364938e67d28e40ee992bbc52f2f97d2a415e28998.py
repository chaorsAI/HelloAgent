# 使用 mplfinance 绘制真实 K 线图（即使数据是模拟的）
import pandas as pd
import mplfinance as mpf
from datetime import datetime

# 创建符合 mplfinance 要求的 DataFrame（索引为 DatetimeIndex）
dates = pd.date_range(end=datetime.today(), periods=5, freq='B')
df = pd.DataFrame({
    'Open': [85.0, 87.5, 86.2, 88.0, 89.5],
    'High': [88.0, 89.0, 87.5, 90.0, 91.0],
    'Low': [84.5, 86.0, 85.0, 87.0, 88.5],
    'Close': [87.5, 86.2, 88.0, 89.5, 90.2],
    'Volume': [1000000, 1200000, 950000, 1100000, 1300000]
}, index=dates)

# 绘制 K 线图
mpf.plot(df, type='candle', volume=True, style='charles', 
         title='美团最近一周K线图', ylabel='价格 (HKD)',
         savefig='meituan_kline.png')
