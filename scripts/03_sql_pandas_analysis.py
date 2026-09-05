import os
import sqlite3
import pandas as pd
import numpy as np

def main():
    base_dir = r"C:\Users\91984\.gemini\antigravity\scratch\e2e-data-analysis-case-study"
    clean_dir = os.path.join(base_dir, "data", "cleaned")
    db_path = os.path.join(clean_dir, "apex_retail.db")

    # Load Clean Datasets
    df_cust = pd.read_csv(os.path.join(clean_dir, "cleaned_customers.csv"))
    df_prod = pd.read_csv(os.path.join(clean_dir, "cleaned_products.csv"))
    df_ord = pd.read_csv(os.path.join(clean_dir, "cleaned_orders.csv"))
    df_ret = pd.read_csv(os.path.join(clean_dir, "cleaned_returns.csv"))
    df_master = pd.read_csv(os.path.join(clean_dir, "cleaned_master_orders.csv"))

    # Connect to SQLite DB and load tables
    conn = sqlite3.connect(db_path)
    df_cust.to_sql("customers", conn, if_exists="replace", index=False)
    df_prod.to_sql("products", conn, if_exists="replace", index=False)
    df_ord.to_sql("orders", conn, if_exists="replace", index=False)
    df_ret.to_sql("returns", conn, if_exists="replace", index=False)
    df_master.to_sql("master_orders", conn, if_exists="replace", index=False)

    print("=" * 70)
    print("EXECUTING SQL & PANDAS ANALYTICAL DEEP-DIVES")
    print("=" * 70)

    # -------------------------------------------------------------
    # QUERY 1: RFM Customer Segmentation (SQL)
    # -------------------------------------------------------------
    rfm_summary_sql = """
    WITH customer_metrics AS (
        SELECT 
            c.customer_id,
            c.customer_name,
            c.region,
            c.customer_segment,
            COUNT(m.order_id) AS frequency,
            SUM(m.net_revenue) AS monetary,
            MAX(m.order_date) AS last_order_date,
            CAST(JULIANDAY('2025-12-31') - JULIANDAY(MAX(m.order_date)) AS INTEGER) AS recency_days
        FROM customers c
        JOIN master_orders m ON c.customer_id = m.customer_id
        GROUP BY c.customer_id, c.customer_name, c.region, c.customer_segment
    ),
    rfm_scores AS (
        SELECT *,
            CASE 
                WHEN recency_days <= 60 AND frequency >= 5 AND monetary >= 1500 THEN 'Champions'
                WHEN recency_days <= 120 AND frequency >= 3 THEN 'Loyal Customers'
                WHEN recency_days <= 90 AND frequency < 3 THEN 'Potential Loyalists'
                WHEN recency_days > 120 AND frequency >= 3 THEN 'At-Risk'
                ELSE 'Lost Customers'
            END AS rfm_segment
        FROM customer_metrics
    )
    SELECT 
        rfm_segment,
        COUNT(customer_id) AS total_customers,
        ROUND(AVG(recency_days), 1) AS avg_recency_days,
        ROUND(AVG(frequency), 2) AS avg_frequency,
        ROUND(AVG(monetary), 2) AS avg_monetary_val,
        ROUND(SUM(monetary), 2) AS total_segment_revenue
    FROM rfm_scores
    GROUP BY rfm_segment
    ORDER BY total_segment_revenue DESC;
    """
    
    print("\n--- 1. RFM Customer Segmentation Summary (SQL) ---")
    df_rfm_summary = pd.read_sql_query(rfm_summary_sql, conn)
    print(df_rfm_summary.to_string(index=False))
    df_rfm_summary.to_csv(os.path.join(clean_dir, "rfm_summary.csv"), index=False)

    rfm_detail_sql = """
    WITH customer_metrics AS (
        SELECT 
            c.customer_id,
            c.customer_name,
            c.region,
            c.customer_segment,
            COUNT(m.order_id) AS frequency,
            SUM(m.net_revenue) AS monetary,
            MAX(m.order_date) AS last_order_date,
            CAST(JULIANDAY('2025-12-31') - JULIANDAY(MAX(m.order_date)) AS INTEGER) AS recency_days
        FROM customers c
        JOIN master_orders m ON c.customer_id = m.customer_id
        GROUP BY c.customer_id, c.customer_name, c.region, c.customer_segment
    )
    SELECT *,
        CASE 
            WHEN recency_days <= 60 AND frequency >= 5 AND monetary >= 1500 THEN 'Champions'
            WHEN recency_days <= 120 AND frequency >= 3 THEN 'Loyal Customers'
            WHEN recency_days <= 90 AND frequency < 3 THEN 'Potential Loyalists'
            WHEN recency_days > 120 AND frequency >= 3 THEN 'At-Risk'
            ELSE 'Lost Customers'
        END AS rfm_segment
    FROM customer_metrics;
    """
    df_rfm_detail = pd.read_sql_query(rfm_detail_sql, conn)
    df_rfm_detail.to_csv(os.path.join(clean_dir, "rfm_customer_segments.csv"), index=False)

    # -------------------------------------------------------------
    # QUERY 2: Product Category Profitability & Returns (SQL)
    # -------------------------------------------------------------
    cat_sql = """
    SELECT 
        category,
        COUNT(order_id) AS total_orders,
        SUM(quantity) AS total_units_sold,
        ROUND(SUM(gross_sales), 2) AS gross_sales,
        ROUND(SUM(discount_amount), 2) AS total_discounts,
        ROUND(SUM(net_sales), 2) AS net_sales,
        ROUND(SUM(total_cost), 2) AS total_cogs,
        ROUND(SUM(gross_profit), 2) AS gross_profit,
        ROUND((SUM(gross_profit) / SUM(net_sales)) * 100, 2) AS profit_margin_pct,
        SUM(is_returned) AS return_count,
        ROUND((CAST(SUM(is_returned) AS FLOAT) / COUNT(order_id)) * 100, 2) AS return_rate_pct,
        ROUND(SUM(net_revenue), 2) AS net_realized_revenue
    FROM master_orders
    GROUP BY category
    ORDER BY net_realized_revenue DESC;
    """
    print("\n--- 2. Product Category Profitability & Return Analysis (SQL) ---")
    df_cat_summary = pd.read_sql_query(cat_sql, conn)
    print(df_cat_summary.to_string(index=False))
    df_cat_summary.to_csv(os.path.join(clean_dir, "category_profitability.csv"), index=False)

    # -------------------------------------------------------------
    # QUERY 3: Monthly Revenue & YoY Growth (SQL)
    # -------------------------------------------------------------
    monthly_sql = """
    WITH monthly_sales AS (
        SELECT 
            order_year_month,
            order_year,
            order_month,
            COUNT(order_id) AS order_count,
            SUM(net_sales) AS gross_revenue,
            SUM(net_revenue) AS net_revenue,
            SUM(net_profit_final) AS net_profit
        FROM master_orders
        GROUP BY order_year_month, order_year, order_month
    )
    SELECT 
        order_year_month,
        order_year,
        order_month,
        order_count,
        ROUND(net_revenue, 2) AS net_revenue,
        ROUND(net_profit, 2) AS net_profit,
        ROUND(
            (net_revenue - LAG(net_revenue, 1) OVER (ORDER BY order_year_month)) / 
            NULLIF(LAG(net_revenue, 1) OVER (ORDER BY order_year_month), 0) * 100, 2
        ) AS mom_growth_pct,
        ROUND(
            (net_revenue - LAG(net_revenue, 12) OVER (ORDER BY order_year_month)) / 
            NULLIF(LAG(net_revenue, 12) OVER (ORDER BY order_year_month), 0) * 100, 2
        ) AS yoy_growth_pct
    FROM monthly_sales
    ORDER BY order_year_month;
    """
    print("\n--- 3. Monthly Revenue Trend & Growth Rates (SQL) ---")
    df_monthly = pd.read_sql_query(monthly_sql, conn)
    print(df_monthly.to_string(index=False))
    df_monthly.to_csv(os.path.join(clean_dir, "monthly_performance.csv"), index=False)

    # -------------------------------------------------------------
    # QUERY 4: Regional & Acquisition Channel Matrix
    # -------------------------------------------------------------
    print("\n--- 4. Regional Revenue by Acquisition Channel (Pandas Pivot) ---")
    df_region_channel = df_master.pivot_table(
        index="region",
        columns="acquisition_channel",
        values="net_revenue",
        aggfunc="sum",
        fill_value=0
    ).round(2)
    print(df_region_channel)
    df_region_channel.to_csv(os.path.join(clean_dir, "regional_channel_matrix.csv"))

    # -------------------------------------------------------------
    # QUERY 5: Return Reasons Analysis (SQL)
    # -------------------------------------------------------------
    returns_sql = """
    SELECT 
        return_reason,
        COUNT(order_id) AS return_count,
        ROUND(SUM(net_sales), 2) AS refunded_value,
        ROUND((COUNT(order_id) * 100.0 / (SELECT COUNT(*) FROM master_orders WHERE is_returned = 1)), 2) AS pct_of_returns
    FROM master_orders
    WHERE is_returned = 1
    GROUP BY return_reason
    ORDER BY return_count DESC;
    """
    print("\n--- 5. Return Reasons Breakdown (SQL) ---")
    df_returns_breakdown = pd.read_sql_query(returns_sql, conn)
    print(df_returns_breakdown.to_string(index=False))
    df_returns_breakdown.to_csv(os.path.join(clean_dir, "returns_breakdown.csv"), index=False)

    conn.close()
    print("\nSQL & Pandas analysis executed and exported to CSV/DB successfully!")

if __name__ == "__main__":
    main()
