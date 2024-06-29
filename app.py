import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from folium.plugins import HeatMap
from folium.map import Popup
import matplotlib.pyplot as plt
import os

plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False

# 获取当前脚本文件的绝对路径
script_dir = os.path.dirname(os.path.abspath(__file__))

# 构建数据文件的绝对路径
file_path = os.path.join(script_dir, 'data/query.csv')

# 确保文件路径正确
print("Data file path: ", file_path)

# 加载地震数据
data = pd.read_csv(file_path, encoding='latin1')

# 将时间列转换为日期时间格式
data['time'] = pd.to_datetime(data['time'])

# 获取唯一国家列表，并处理空值
data['place'] = data['place'].astype(str)
data['country'] = data['place'].apply(lambda x: x.split(",")[-1].strip())
countries = data['country'].unique()
countries = list(countries)
countries.insert(0, 'All countries or regions')  # 在国家列表中添加一个“所有国家”选项


# 绘制地图的函数
def plot_map(data, country=None):
    if country and country != 'All countries or regions':
        data = data[data['country'] == country]

    m = folium.Map(location=[0, 0], zoom_start=2)

    for idx, row in data.iterrows():
        popup_content = f"""
        <div style="width: 200px;">
        <strong>位置:</strong> {row['place']}<br>
        <strong>震级:</strong> {row['mag']}<br>
        <strong>震源深度:</strong> {row['depth']} km<br>
        <strong>时间:</strong> {row['time']}
    </div>
    """
        folium.CircleMarker(
            location=[row['latitude'], row['longitude']],
            radius=3,
            popup=Popup(popup_content, max_width=250),
            color='blue',
            fill=True,
            fill_color='blue'
        ).add_to(m)

    return m


# Streamlit 应用
st.title("2018-2023年中国及其附近国家或地区地震数据查询、可视化与热点分析")

selected_country = st.selectbox("Select Country", countries)

st.header(f"{selected_country}的地震地图")
earthquake_map = plot_map(data, selected_country)
st_folium(earthquake_map, width=700)

st.header("地震数据")
if selected_country == 'All countries or regions':
    country_data = data[(data['time'].dt.year >= 2018) & (data['time'].dt.year <= 2023)]
else:
    country_data = data[
        (data['country'] == selected_country) & (data['time'].dt.year >= 2018) & (data['time'].dt.year <= 2023)]
st.dataframe(country_data)

# 显示地震点数量
num_earthquakes = country_data.shape[0]
st.write(f"2018-2023年{selected_country}有{num_earthquakes}个地震点")

# 添加地震数据的柱状图分析
st.header("地震数据逐年统计柱状图")
country_data['year'] = country_data['time'].dt.year
earthquake_counts = country_data['year'].value_counts().sort_index()

plt.figure(figsize=(10, 6))
plt.bar(earthquake_counts.index, earthquake_counts.values, color='skyblue')
plt.xlabel('年份')
plt.ylabel('地震点数量')
plt.title(f'2018-2023年{selected_country}的地震点数量')
st.pyplot(plt)

# 热点分析
st.header("热点分析")
heat_data = [[row['latitude'], row['longitude']] for index, row in data.iterrows()]
m_heat = folium.Map(location=[0, 0], zoom_start=2)
HeatMap(heat_data).add_to(m_heat)
st_folium(m_heat, width=700)

# 使用 markdown 来控制间距
st.markdown("<style> div.row-widget.stRadio > div {flex-direction:row;} </style>", unsafe_allow_html=True)
