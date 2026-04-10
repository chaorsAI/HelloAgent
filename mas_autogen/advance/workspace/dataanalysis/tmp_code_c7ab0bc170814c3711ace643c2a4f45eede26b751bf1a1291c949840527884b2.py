import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 下载数据
url = "https://raw.githubusercontent.com/vega/vega/main/docs/data/seattle-weather.csv"
data = pd.read_csv(url)

# 打印数据集中的字段
print("数据集中的字段:")
print(data.columns.tolist())

# 统计每种天气的数量
weather_counts = data['weather'].value_counts()

# 打印每种天气的数量
print("\n每种天气的数量:")
print(weather_counts)

# 可视化数据
plt.figure(figsize=(10, 6))
sns.countplot(data=data, x='weather', order=weather_counts.index)
plt.title('Seattle Weather Counts')
plt.xlabel('Weather Type')
plt.ylabel('Count')

# 保存图表到文件
output_file = 'seattle_weather_counts.png'
plt.savefig(output_file)
print(f"\n图表已保存到文件: {output_file}")

# 显示图表
plt.show()

# 接受评论者的反馈以改进代码
# 如果有反馈，请告诉我如何改进代码。
