import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import os
from supabase import create_client

# 尝试加载项目中的中文字体
font_path = os.path.join("fonts", "NotoSansSC-Regular.otf")
# font_path = os.path.join("fonts", "SimHei.ttf")
if os.path.exists(font_path):
    fm.fontManager.addfont(font_path)
    plt.rcParams['font.sans-serif'] = ['Noto Sans SC']
    # plt.rcParams['font.sans-serif'] = ['SimHei']
else:
    # 如果没有找到字体，就用系统默认字体
    # plt.rcParams['font.sans-serif'] = ['DejaVu Sans']
    pass
plt.rcParams['axes.unicode_minus'] = False

# ====================================================================================
# ======================
# 初始化 Supabase 客户端
# ======================
@st.cache_resource
def get_supabase():
    url = st.secrets["supabase"]["url"]
    key = st.secrets["supabase"]["key"]
    return create_client(url, key)

supabase = get_supabase()

# ======================
# 初始化 session_state
# ======================
if "watchlist" not in st.session_state:
    # 从 Supabase 读取自选股
    data = supabase.table("watchlist").select("*").order("id").execute().data
    st.session_state.watchlist = [row["code"] for row in data]

# ======================
# 页面标题
# ======================
st.title("📈 自选股管理")

# ======================
# 添加股票
# ======================
new_stock = st.text_input("输入股票代码（如 sh600519）")

if st.button("添加股票"):
    if new_stock and new_stock not in st.session_state.watchlist:
        # 写入 Supabase
        try:
            supabase.table("watchlist").insert({"code": new_stock}).execute()
            # 更新 session_state
            st.session_state.watchlist.append(new_stock)
            st.success(f"✅ 已添加 {new_stock}")
        except Exception as e:
            st.error(f"❌ 添加失败: {e}")

# ======================
# 删除股票
# ======================
if st.session_state.watchlist:
    delete_stock = st.selectbox("选择要删除的股票", [""] + st.session_state.watchlist)
    if st.button("删除选中股票") and delete_stock:
        try:
            supabase.table("watchlist").delete().eq("code", delete_stock).execute()
            st.session_state.watchlist.remove(delete_stock)
            st.success(f"❌ 已删除 {delete_stock}")
        except Exception as e:
            st.error(f"❌ 删除失败: {e}")

# ======================
# 显示当前自选股
# ======================
st.subheader("🗂 当前自选股列表")
st.table(pd.DataFrame(st.session_state.watchlist, columns=["股票代码"]))
# ====================================================================================
# ====================================================================================
st.markdown("---")

# test file read on server
df = pd.read_excel('t1.xlsx', sheet_name='ths_lr1',header=0, index_col=0)
st.table(df.iloc[0:5, 0:5])

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
st.dataframe(filtered_df, width="stretch")  # 使用Pandas DataFrame，Streamlit自动渲染为交互表格

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















