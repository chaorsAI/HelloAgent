import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import requests
from io import StringIO

# 下载数据
url = "https://raw.githubusercontent.com/uwdata/draco/master/data/cars.csv"
response = requests.get(url)
data = StringIO(response.text)

# 读取数据
df = pd.read_csv(data)

# 打印数据集中的字段
print("数据集中的字段：")
print(df.columns.tolist())
print("\n数据集基本信息：")
print(df.info())
print("\n前几行数据预览：")
print(df.head())

# 检查重量和马力字段的名称
# 根据常见的汽车数据集，重量通常为 'weight' 或 'Weight'，马力通常为 'horsepower' 或 'Horsepower'
print("\n检查可能包含重量和马力的列：")
weight_cols = [col for col in df.columns if 'weight' in col.lower()]
horsepower_cols = [col for col in df.columns if 'horse' in col.lower() or 'power' in col.lower()]

print(f"可能的重量列: {weight_cols}")
print(f"可能的马力列: {horsepower_cols}")

# 确定正确的列名
weight_col = None
horsepower_col = None

# 尝试常见的列名组合
possible_weight_names = ['weight', 'Weight', 'WEIGHT', 'wt']
possible_horsepower_names = ['horsepower', 'Horsepower', 'HORSEPOWER', 'hp', 'HP']

for col in df.columns:
    if col.lower() in [name.lower() for name in possible_weight_names]:
        weight_col = col
    if col.lower() in [name.lower() for name in possible_horsepower_names]:
        horsepower_col = col

if weight_col is None or horsepower_col is None:
    # 如果没有找到标准名称，使用之前找到的可能列
    if weight_cols:
        weight_col = weight_cols[0]
    if horsepower_cols:
        horsepower_col = horsepower_cols[0]

print(f"\n使用的重量列: {weight_col}")
print(f"使用的马力列: {horsepower_col}")

# 检查数据是否有缺失值
print(f"\n重量列缺失值: {df[weight_col].isnull().sum() if weight_col else 'N/A'}")
print(f"马力列缺失值: {df[horsepower_col].isnull().sum() if horsepower_col else 'N/A'}")

# 创建可视化
plt.figure(figsize=(10, 6))
sns.set_style("whitegrid")

# 绘制散点图
if weight_col and horsepower_col:
    # 删除缺失值
    plot_data = df[[weight_col, horsepower_col]].dropna()
    
    # 转换为数值类型（以防有字符串）
    plot_data[weight_col] = pd.to_numeric(plot_data[weight_col], errors='coerce')
    plot_data[horsepower_col] = pd.to_numeric(plot_data[horsepower_col], errors='coerce')
    
    # 再次删除转换后可能产生的NaN值
    plot_data = plot_data.dropna()
    
    plt.scatter(plot_data[weight_col], plot_data[horsepower_col], alpha=0.7)
    plt.xlabel(weight_col)
    plt.ylabel(horsepower_col)
    plt.title(f'{weight_col} vs {horsepower_col}')
    
    # 添加趋势线
    sns.regplot(x=weight_col, y=horsepower_col, data=plot_data, scatter=False, color='red')
    
    # 保存图像
    plt.savefig('weight_vs_horsepower.png', dpi=300, bbox_inches='tight')
    print("\n图像已保存为 'weight_vs_horsepower.png'")
    
    # 显示基本统计信息
    correlation = plot_data[weight_col].corr(plot_data[horsepower_col])
    print(f"\n重量和马力之间的相关系数: {correlation:.3f}")
else:
    print("无法找到合适的重量或马力列进行绘图")

plt.show()
