import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
# 中文支持
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 设置页面
st.set_page_config(page_title="销售数据分析看板", layout="wide")
st.title("📈 销售数据分析看板")

# 使用Pandas创建示例数据
@st.cache_data  # 使用缓存避免每次交互都重新加载数据
def load_data():
    data = {
        "年份": [2018, 2019, 2020, 2021, 2022, 2023],
        "销售额_产品A": [1000, 1500, 1300, 1800, 2200, 2500],
        "销售额_产品B": [600, 900, 1200, 1100, 1500, 1900],
        "成本": [800, 1000, 1100, 1200, 1400, 1500]
    }
    df = pd.DataFrame(data)
    df['总销售额'] = df['销售额_产品A'] + df['销售额_产品B']
    df['利润'] = df['总销售额'] - df['成本']
    return df

df = load_data()

# 在侧边栏添加交互控件
st.sidebar.header("控制面板")
selected_years = st.sidebar.slider(
    "选择年份范围:",
    min_value=2018,
    max_value=2023,
    value=(2018, 2023)  # 默认值
)
show_profit = st.sidebar.checkbox("显示利润", value=True)

# 根据用户选择过滤数据
filtered_df = df[(df['年份'] >= selected_years[0]) & (df['年份'] <= selected_years[1])]

# 显示数据
st.subheader("数据概览")
st.dataframe(filtered_df, use_container_width=True)  # 使用Pandas DataFrame，Streamlit自动渲染为交互表格

# 使用两列布局展示图表
col1, col2 = st.columns(2)

with col1:
    st.write("#### 销售额趋势")
    # 使用Matplotlib创建图表
    fig, ax = plt.subplots()
    ax.plot(filtered_df['年份'], filtered_df['销售额_产品A'], label='产品A', marker='o')
    ax.plot(filtered_df['年份'], filtered_df['销售额_产品B'], label='产品B', marker='s')
    if show_profit:
        ax.plot(filtered_df['年份'], filtered_df['利润'], label='利润', linestyle='--', marker='^')
    ax.set_xlabel("年份")
    ax.set_ylabel("金额 (万元)")
    ax.set_title("产品销售额与利润趋势")
    ax.legend()
    ax.grid(True, linestyle='--', alpha=0.7)
    # 将Matplotlib图表嵌入Streamlit应用
    st.pyplot(fig)

with col2:
    st.write("#### 年度销售额占比")
    # 也可以直接使用Streamlit内置的快捷图表方法，其底层通常与Pandas DataFrame集成
    chart_data = filtered_df.set_index('年份')[['销售额_产品A', '销售额_产品B']]
    st.bar_chart(chart_data)  # Streamlit 直接绘制Pandas数据

# 显示一些统计指标
st.subheader("关键指标")
col1, col2, col3, col4 = st.columns(4)
col1.metric("平均总销售额", f"{filtered_df['总销售额'].mean():.0f} 万元")
col2.metric("平均利润", f"{filtered_df['利润'].mean():.0f} 万元")
col3.metric("利润最高年份", int(filtered_df.loc[filtered_df['利润'].idxmax(), '年份']))
col4.metric("总销售额增长率", f"{(filtered_df['总销售额'].iloc[-1] / filtered_df['总销售额'].iloc[0] - 1) * 100:.1f}%")
