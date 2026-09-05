import os
import sqlite3
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as bg
import streamlit as st

st.set_page_config(
    page_title="Apex Retail - Interactive Analytics Demo",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load Data
base_dir = os.path.dirname(os.path.abspath(__file__))
clean_dir = os.path.join(base_dir, "data", "cleaned")
db_path = os.path.join(clean_dir, "apex_retail.db")

@st.cache_data
def load_master_data():
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query("SELECT * FROM master_orders", conn)
    conn.close()
    return df

@st.cache_data
def load_rfm_data():
    conn = sqlite3.connect(db_path)
    df_sum = pd.read_sql_query("SELECT * FROM rfm_summary", conn)
    df_det = pd.read_sql_query("SELECT * FROM rfm_customer_segments", conn)
    conn.close()
    return df_sum, df_det

df_master = load_master_data()
df_rfm_sum, df_rfm_det = load_rfm_data()

# Custom CSS Styling
st.markdown("""
    <style>
    .main { background-color: #F8F9FA; }
    .kpi-card {
        background-color: #FFFFFF;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        text-align: center;
        border-left: 5px solid #1F4E78;
    }
    .kpi-title { font-size: 14px; color: #6C757D; font-weight: 600; text-transform: uppercase; }
    .kpi-value { font-size: 26px; color: #1F4E78; font-weight: 700; margin-top: 5px; }
    </style>
""", unsafe_allow_html=True)

# Sidebar Filter
st.sidebar.title("📌 Navigation & Filters")
page = st.sidebar.radio("Go to Page:", [
    "📈 Executive Dashboard",
    "👥 Customer RFM Segments",
    "🏷️ Category Profitability",
    "💻 Live SQL Query Console"
])

st.sidebar.markdown("---")
st.sidebar.subheader("Filter Master Data")

all_regions = ["All"] + list(df_master["region"].unique())
selected_region = st.sidebar.selectbox("Region:", all_regions)

all_categories = ["All"] + list(df_master["category"].unique())
selected_category = st.sidebar.selectbox("Category:", all_categories)

# Apply Filter
df_filtered = df_master.copy()
if selected_region != "All":
    df_filtered = df_filtered[df_filtered["region"] == selected_region]
if selected_category != "All":
    df_filtered = df_filtered[df_filtered["category"] == selected_category]

# -------------------------------------------------------------
# PAGE 1: Executive Dashboard
# -------------------------------------------------------------
if page == "📈 Executive Dashboard":
    st.title("🚀 Apex Retail - Executive Performance Dashboard")
    st.markdown("Interactive analytical view of realized revenue, net profitability, order volume, and return rates.")
    
    # KPI Row
    total_sales = df_filtered["net_sales"].sum()
    total_rev = df_filtered["net_revenue"].sum()
    total_profit = df_filtered["net_profit_final"].sum()
    total_orders = df_filtered["order_id"].nunique()
    aov = total_sales / total_orders if total_orders > 0 else 0
    return_rate = (df_filtered["is_returned"].sum() / total_orders * 100) if total_orders > 0 else 0

    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.markdown(f'<div class="kpi-card"><div class="kpi-title">Net Sales</div><div class="kpi-value">${total_sales:,.2f}</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="kpi-card"><div class="kpi-title">Realized Revenue</div><div class="kpi-value">${total_rev:,.2f}</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="kpi-card"><div class="kpi-title">Net Profit</div><div class="kpi-value">${total_profit:,.2f}</div></div>', unsafe_allow_html=True)
    with col4:
        st.markdown(f'<div class="kpi-card"><div class="kpi-title">Average Order Value</div><div class="kpi-value">${aov:,.2f}</div></div>', unsafe_allow_html=True)
    with col5:
        st.markdown(f'<div class="kpi-card"><div class="kpi-title">Return Rate</div><div class="kpi-value">{return_rate:.2f}%</div></div>', unsafe_allow_html=True)

    st.markdown("---")

    # Monthly Trend Plotly Chart
    st.subheader("Monthly Revenue & Profit Growth Trend")
    monthly_df = df_filtered.groupby("order_year_month")[["net_revenue", "net_profit_final"]].sum().reset_index()
    monthly_df.rename(columns={"net_revenue": "Net Revenue", "net_profit_final": "Net Profit"}, inplace=True)

    fig_monthly = px.line(
        monthly_df, x="order_year_month", y=["Net Revenue", "Net Profit"],
        markers=True, line_shape="spline",
        labels={"value": "Amount ($)", "order_year_month": "Month"},
        color_discrete_map={"Net Revenue": "#1F4E78", "Net Profit": "#2E75B6"}
    )
    fig_monthly.update_layout(hovermode="x unified", legend_title_text="Metric", height=420)
    st.plotly_chart(fig_monthly, use_container_width=True)

    # Regional & Channel Matrix
    col_left, col_right = st.columns(2)
    with col_left:
        st.subheader("Revenue by Acquisition Channel")
        chan_df = df_filtered.groupby("acquisition_channel")["net_revenue"].sum().reset_index()
        fig_chan = px.pie(chan_df, names="acquisition_channel", values="net_revenue", hole=0.4, color_discrete_sequence=px.colors.sequential.Blues_r)
        st.plotly_chart(fig_chan, use_container_width=True)
    
    with col_right:
        st.subheader("Regional Performance ($)")
        reg_df = df_filtered.groupby("region")["net_revenue"].sum().reset_index()
        fig_reg = px.bar(reg_df, x="region", y="net_revenue", text_auto=".2s", color="region", color_discrete_sequence=px.colors.qualitative.Prism)
        st.plotly_chart(fig_reg, use_container_width=True)

# -------------------------------------------------------------
# PAGE 2: Customer RFM Segments
# -------------------------------------------------------------
elif page == "👥 Customer RFM Segments":
    st.title("👥 Customer RFM Segmentation Analysis")
    st.markdown("Recency, Frequency, and Monetary Value segmentation of 1,000 active customers.")

    st.subheader("RFM Segment Revenue Impact")
    fig_rfm = px.bar(
        df_rfm_sum, x="rfm_segment", y="total_segment_revenue",
        color="rfm_segment", text="total_customers",
        labels={"total_segment_revenue": "Total Revenue ($)", "rfm_segment": "RFM Segment", "total_customers": "Customers"},
        color_discrete_sequence=px.colors.sequential.Darkmint_r
    )
    fig_rfm.update_traces(texttemplate='%{text} Customers', textposition='outside')
    st.plotly_chart(fig_rfm, use_container_width=True)

    st.subheader("Customer Recency vs Monetary Value Scatter Plot")
    fig_scatter = px.scatter(
        df_rfm_det, x="recency_days", y="monetary", size="frequency", color="rfm_segment",
        hover_name="customer_name", labels={"recency_days": "Recency (Days Idle)", "monetary": "Lifetime Monetary Value ($)"},
        color_discrete_map={"Champions": "#1F4E78", "Loyal Customers": "#2E75B6", "Potential Loyalists": "#5B9BD5", "At-Risk": "#ED7D31", "Lost Customers": "#C00000"}
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

    st.subheader("Customer Directory")
    st.dataframe(df_rfm_det, use_container_width=True)

# -------------------------------------------------------------
# PAGE 3: Category Profitability
# -------------------------------------------------------------
elif page == "🏷️ Category Profitability":
    st.title("🏷️ Category Profitability & Return Diagnostics")

    cat_summary = df_master.groupby("category").agg(
        total_orders=("order_id", "nunique"),
        gross_sales=("gross_sales", "sum"),
        net_sales=("net_sales", "sum"),
        gross_profit=("gross_profit", "sum"),
        returns=("is_returned", "sum")
    ).reset_index()

    cat_summary["profit_margin_pct"] = (cat_summary["gross_profit"] / cat_summary["net_sales"]) * 100
    cat_summary["return_rate_pct"] = (cat_summary["returns"] / cat_summary["total_orders"]) * 100

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Category Profit Margins (%)")
        fig_margin = px.bar(cat_summary, x="category", y="profit_margin_pct", color="profit_margin_pct", text_auto=".1f", color_continuous_scale="Viridis")
        st.plotly_chart(fig_margin, use_container_width=True)
    
    with col2:
        st.subheader("Category Return Rates (%)")
        fig_ret = px.bar(cat_summary, x="category", y="return_rate_pct", color="return_rate_pct", text_auto=".1f", color_continuous_scale="Reds")
        st.plotly_chart(fig_ret, use_container_width=True)

    st.subheader("Return Reasons Breakdown")
    ret_reasons = df_master[df_master["is_returned"] == 1]["return_reason"].value_counts().reset_index()
    ret_reasons.columns = ["Return Reason", "Count"]
    fig_reasons = px.bar(ret_reasons, x="Count", y="Return Reason", orientation="h", color="Count", color_continuous_scale="Oranges")
    st.plotly_chart(fig_reasons, use_container_width=True)

# -------------------------------------------------------------
# PAGE 4: Live SQL Query Console
# -------------------------------------------------------------
elif page == "💻 Live SQL Query Console":
    st.title("💻 Live SQL Database Console (`apex_retail.db`)")
    st.markdown("Execute custom analytical SQL queries against SQLite database tables: `master_orders`, `customers`, `products`, `orders`, `returns`.")

    default_sql = """SELECT 
    category,
    COUNT(order_id) AS orders,
    ROUND(SUM(net_sales), 2) AS net_sales,
    ROUND(SUM(gross_profit), 2) AS gross_profit,
    ROUND(AVG(profit_margin_pct), 2) AS avg_margin_pct
FROM master_orders
GROUP BY category
ORDER BY net_sales DESC;"""

    query_input = st.text_area("Write SQL Query:", default_sql, height=150)
    
    if st.button("Execute SQL Query 🚀"):
        try:
            conn = sqlite3.connect(db_path)
            res_df = pd.read_sql_query(query_input, conn)
            conn.close()
            st.success(f"Query returned {len(res_df)} rows successfully!")
            st.dataframe(res_df, use_container_width=True)
        except Exception as e:
            st.error(f"SQL Execution Error: {e}")
