import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

def main():
    base_dir = r"C:\Users\91984\.gemini\antigravity\scratch\e2e-data-analysis-case-study"
    clean_dir = os.path.join(base_dir, "data", "cleaned")
    viz_dir = os.path.join(base_dir, "visualizations")
    bi_dir = os.path.join(base_dir, "power_bi")
    os.makedirs(viz_dir, exist_ok=True)
    os.makedirs(bi_dir, exist_ok=True)

    plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
    plt.rcParams["font.sans-serif"] = "DejaVu Sans"
    plt.rcParams["axes.edgecolor"] = "#D9D9D9"
    plt.rcParams["axes.linewidth"] = 0.8

    # Load Clean Datasets
    df_master = pd.read_csv(os.path.join(clean_dir, "cleaned_master_orders.csv"))
    df_cat = pd.read_csv(os.path.join(clean_dir, "category_profitability.csv"))
    df_rfm = pd.read_csv(os.path.join(clean_dir, "rfm_summary.csv"))
    df_monthly = pd.read_csv(os.path.join(clean_dir, "monthly_performance.csv"))
    df_returns = pd.read_csv(os.path.join(clean_dir, "returns_breakdown.csv"))
    df_matrix = pd.read_csv(os.path.join(clean_dir, "regional_channel_matrix.csv"), index_col=0)

    print("=" * 60)
    print("GENERATING VISUALIZATIONS & BI DASHBOARD ASSETS")
    print("=" * 60)

    # 1. Monthly Revenue & Profit Trend Plot
    fig, ax1 = plt.subplots(figsize=(12, 6))
    ax1.plot(df_monthly["order_year_month"], df_monthly["net_revenue"], marker="o", linewidth=2.5, color="#1F4E78", label="Net Revenue ($)")
    ax1.plot(df_monthly["order_year_month"], df_monthly["net_profit"], marker="s", linewidth=2.5, color="#2E75B6", label="Net Profit ($)")
    ax1.set_title("Apex Retail - Monthly Revenue & Net Profit Trend (2024 - 2025)", fontsize=14, fontweight="bold", pad=15)
    ax1.set_xlabel("Year-Month", fontsize=11, fontweight="bold")
    ax1.set_ylabel("Amount ($)", fontsize=11, fontweight="bold")
    ax1.yaxis.set_major_formatter("${x:,.0f}")
    plt.xticks(rotation=45)
    ax1.legend(loc="upper left", frameon=True)
    plt.tight_layout()
    plt.savefig(os.path.join(viz_dir, "monthly_revenue_trend.png"), dpi=300)
    plt.close()
    print("Saved monthly_revenue_trend.png")

    # 2. RFM Customer Segments Bar Plot
    fig, ax = plt.subplots(figsize=(10, 5))
    palette = ["#1F4E78", "#2E75B6", "#5B9BD5", "#ED7D31", "#C00000"]
    bars = ax.bar(df_rfm["rfm_segment"], df_rfm["total_segment_revenue"] / 1000, color=palette, width=0.55)
    
    ax.set_title("Customer Segmentation Revenue Impact ($ Thousands)", fontsize=14, fontweight="bold", pad=15)
    ax.set_xlabel("RFM Segment", fontsize=11, fontweight="bold")
    ax.set_ylabel("Total Revenue ($K)", fontsize=11, fontweight="bold")
    ax.yaxis.set_major_formatter("${x:,.0f}K")

    for bar, cust_cnt in zip(bars, df_rfm["total_customers"]):
        yval = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2.0, yval + 5, f"${yval:,.1f}K\n({cust_cnt} cust)", ha="center", va="bottom", fontsize=9, fontweight="bold")

    plt.tight_layout()
    plt.savefig(os.path.join(viz_dir, "rfm_distribution.png"), dpi=300)
    plt.close()
    print("Saved rfm_distribution.png")

    # 3. Category Profitability & Margin Dual Axis Plot
    fig, ax1 = plt.subplots(figsize=(10, 5))
    ax2 = ax1.twinx()

    x = np.arange(len(df_cat))
    width = 0.4

    rects1 = ax1.bar(x - width/2, df_cat["net_sales"] / 1000, width, label="Net Sales ($K)", color="#1F4E78")
    rects2 = ax1.bar(x + width/2, df_cat["gross_profit"] / 1000, width, label="Gross Profit ($K)", color="#5B9BD5")
    line = ax2.plot(x, df_cat["profit_margin_pct"], color="#C00000", marker="D", linewidth=2, label="Profit Margin %")

    ax1.set_title("Product Category Sales, Profitability & Margin %", fontsize=14, fontweight="bold", pad=15)
    ax1.set_xticks(x)
    ax1.set_xticklabels(df_cat["category"], rotation=15, ha="right", fontweight="bold")
    ax1.set_ylabel("Sales / Profit ($K)", fontsize=11, fontweight="bold")
    ax2.set_ylabel("Profit Margin %", fontsize=11, fontweight="bold", color="#C00000")
    ax2.yaxis.set_major_formatter("{x:.0f}%")
    ax1.yaxis.set_major_formatter("${x:,.0f}K")

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper right")

    plt.tight_layout()
    plt.savefig(os.path.join(viz_dir, "category_profitability.png"), dpi=300)
    plt.close()
    print("Saved category_profitability.png")

    # 4. Return Rate by Category Plot
    fig, ax = plt.subplots(figsize=(9, 5))
    bars = ax.barh(df_cat["category"], df_cat["return_rate_pct"], color="#ED7D31", height=0.5)
    ax.set_title("Return Rate % by Product Category", fontsize=14, fontweight="bold", pad=15)
    ax.set_xlabel("Return Rate %", fontsize=11, fontweight="bold")
    ax.xaxis.set_major_formatter("{x:.1f}%")

    for bar in bars:
        width = bar.get_width()
        ax.text(width + 0.2, bar.get_y() + bar.get_height()/2.0, f"{width:.2f}%", ha="left", va="center", fontsize=10, fontweight="bold")

    plt.tight_layout()
    plt.savefig(os.path.join(viz_dir, "return_rate_by_category.png"), dpi=300)
    plt.close()
    print("Saved return_rate_by_category.png")

    # 5. Regional & Acquisition Channel Heatmap
    fig, ax = plt.subplots(figsize=(9, 6))
    sns.heatmap(df_matrix / 1000, annot=True, fmt=".1f", cmap="Blues", cbar_kws={"label": "Net Revenue ($K)"}, ax=ax)
    ax.set_title("Net Revenue Heatmap: Region vs Acquisition Channel ($K)", fontsize=13, fontweight="bold", pad=15)
    ax.set_xlabel("Acquisition Channel", fontsize=11, fontweight="bold")
    ax.set_ylabel("Region", fontsize=11, fontweight="bold")
    plt.tight_layout()
    plt.savefig(os.path.join(viz_dir, "regional_channel_heatmap.png"), dpi=300)
    plt.close()
    print("Saved regional_channel_heatmap.png")

    # 6. Generate Power BI DAX Measures File
    dax_content = """// =========================================================================
// APEX RETAIL PERFORMANCE DASHBOARD - DAX MEASURES LIBRARY
// =========================================================================

// --- 1. CORE REVENUE MEASURES ---
Total Gross Sales = SUM(FactOrders[gross_sales])

Total Discounts = SUM(FactOrders[discount_amount])

Total Net Sales = SUM(FactOrders[net_sales])

Total Returns Amount = 
CALCULATE(
    SUM(FactOrders[net_sales]),
    FactOrders[is_returned] = 1
)

Net Realized Revenue = 
SUMX(
    FactOrders,
    IF(FactOrders[is_returned] = 1, 0, FactOrders[net_sales])
)

// --- 2. PROFITABILITY MEASURES ---
Total COGS = SUM(FactOrders[total_cost])

Gross Profit = [Total Net Sales] - [Total COGS]

Gross Profit Margin % = 
DIVIDE([Gross Profit], [Total Net Sales], 0)

Net Profit Final = 
SUMX(
    FactOrders,
    IF(FactOrders[is_returned] = 1, -FactOrders[shipping_cost], FactOrders[gross_profit])
)

Net Profit Margin % = 
DIVIDE([Net Profit Final], [Net Realized Revenue], 0)

// --- 3. VOLUME & ORDER METRICS ---
Total Orders = DISTINCTCOUNT(FactOrders[order_id])

Total Units Sold = SUM(FactOrders[quantity])

Average Order Value (AOV) = 
DIVIDE([Total Net Sales], [Total Orders], 0)

Average Units Per Order = 
DIVIDE([Total Units Sold], [Total Orders], 0)

// --- 4. RETURN ANALYSIS MEASURES ---
Total Returns Count = 
CALCULATE(
    COUNT(FactOrders[order_id]),
    FactOrders[is_returned] = 1
)

Return Rate % = 
DIVIDE([Total Returns Count], [Total Orders], 0)

// --- 5. TIME INTELLIGENCE MEASURES ---
Net Revenue YTD = 
TOTALYTD([Net Realized Revenue], DimDate[Date])

Net Revenue PY = 
CALCULATE([Net Realized Revenue], SAMEPERIODLASTYEAR(DimDate[Date]))

Net Revenue YoY Growth % = 
DIVIDE([Net Realized Revenue] - [Net Revenue PY], [Net Revenue PY], 0)

Net Revenue MoM Growth % = 
VAR PrevMonth = CALCULATE([Net Realized Revenue], DATEADD(DimDate[Date], -1, MONTH))
RETURN DIVIDE([Net Realized Revenue] - PrevMonth, PrevMonth, 0)

// --- 6. CUSTOMER & RFM MEASURES ---
Active Customer Count = DISTINCTCOUNT(FactOrders[customer_id])

Customer Lifetime Value (CLV) = 
DIVIDE([Net Realized Revenue], [Active Customer Count], 0)

Recency Days = 
DATEDIFF(MAX(FactOrders[order_date]), TODAY(), DAY)
"""
    with open(os.path.join(bi_dir, "power_bi_dax_measures.dax"), "w") as f:
        f.write(dax_content)
    print("Saved power_bi_dax_measures.dax")

    print("\nVisualizations and BI dashboard assets completed successfully!")

if __name__ == "__main__":
    main()
