import os
import pandas as pd
import numpy as np

def main():
    base_dir = r"C:\Users\91984\.gemini\antigravity\scratch\e2e-data-analysis-case-study"
    raw_dir = os.path.join(base_dir, "data", "raw")
    clean_dir = os.path.join(base_dir, "data", "cleaned")
    os.makedirs(clean_dir, exist_ok=True)

    print("=" * 60)
    print("STARTING DATA CLEANING & EDA PIPELINE")
    print("=" * 60)

    # 1. Load Raw Datasets
    df_cust_raw = pd.read_csv(os.path.join(raw_dir, "raw_customers.csv"))
    df_prod_raw = pd.read_csv(os.path.join(raw_dir, "raw_products.csv"))
    df_ord_raw = pd.read_csv(os.path.join(raw_dir, "raw_orders.csv"))
    df_ret_raw = pd.read_csv(os.path.join(raw_dir, "raw_returns.csv"))

    print(f"Raw Customers shape: {df_cust_raw.shape}")
    print(f"Raw Products shape:  {df_prod_raw.shape}")
    print(f"Raw Orders shape:    {df_ord_raw.shape}")
    print(f"Raw Returns shape:   {df_ret_raw.shape}\n")

    # -------------------------------------------------------------
    # 2. Clean Customers Dataset
    # -------------------------------------------------------------
    print("--- Cleaning Customers Dataset ---")
    df_cust = df_cust_raw.copy()
    
    # Deduplicate
    before_cust_len = len(df_cust)
    df_cust = df_cust.drop_duplicates(subset=["customer_id"])
    print(f"Removed {before_cust_len - len(df_cust)} duplicate customer IDs.")

    # Standardize String Fields
    df_cust["region"] = df_cust["region"].astype(str).str.strip().str.title()
    region_map = {
        "North": "North", "South": "South", "East": "East", "West": "West", "Midwest": "Midwest", "Nan": "Unknown"
    }
    df_cust["region"] = df_cust["region"].map(lambda x: region_map.get(x, "Unknown"))
    
    df_cust["acquisition_channel"] = df_cust["acquisition_channel"].fillna("Direct / Organic")
    df_cust["email"] = df_cust["email"].fillna("missing_email@apexretail.com")

    # -------------------------------------------------------------
    # 3. Clean Products Dataset
    # -------------------------------------------------------------
    print("\n--- Cleaning Products Dataset ---")
    df_prod = df_prod_raw.copy()

    # Standardize Category Typos
    category_clean_map = {
        "Electronics": "Electronics", "Electrnoics": "Electronics", "ELECTRONICS": "Electronics",
        "Apparel": "Apparel", "apparel": "Apparel", "  Apparel ": "Apparel",
        "Home & Kitchen": "Home & Kitchen", "Home and Kitchen": "Home & Kitchen", "HOME & KITCHEN": "Home & Kitchen",
        "Beauty & Care": "Beauty & Care", "Beauty & care": "Beauty & Care",
        "Sports & Outdoors": "Sports & Outdoors", "Sports & outdoors": "Sports & Outdoors"
    }
    df_prod["category"] = df_prod["category"].astype(str).str.strip().map(lambda x: category_clean_map.get(x, x))
    
    # Calculate product margin
    df_prod["unit_margin"] = df_prod["unit_price"] - df_prod["unit_cost"]
    df_prod["target_margin_pct"] = round((df_prod["unit_margin"] / df_prod["unit_price"]) * 100, 2)

    # -------------------------------------------------------------
    # 4. Clean Orders Dataset
    # -------------------------------------------------------------
    print("\n--- Cleaning Orders Dataset ---")
    df_ord = df_ord_raw.copy()

    # Deduplicate Order Rows
    before_ord_len = len(df_ord)
    df_ord = df_ord.drop_duplicates(subset=["order_id"])
    print(f"Removed {before_ord_len - len(df_ord)} duplicate order IDs.")

    # Parse Inconsistent Order Dates
    def parse_mixed_dates(val):
        if pd.isna(val):
            return pd.NaT
        val_str = str(val).strip()
        for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%d-%m-%Y"):
            try:
                return pd.to_datetime(val_str, format=fmt)
            except ValueError:
                pass
        return pd.to_datetime(val_str, errors="coerce")

    df_ord["order_date"] = df_ord["order_date"].apply(parse_mixed_dates)
    df_ord = df_ord.dropna(subset=["order_date"])

    # Filter Invalid / Non-existent Customer IDs
    valid_cids = set(df_cust["customer_id"])
    df_ord = df_ord[df_ord["customer_id"].isin(valid_cids)]

    # Handle Outlier & Negative Quantities
    invalid_qty_mask = (df_ord["quantity"] <= 0) | (df_ord["quantity"] > 50)
    print(f"Filtered out {invalid_qty_mask.sum()} invalid/outlier quantity records.")
    df_ord = df_ord[~invalid_qty_mask].copy()

    # Impute missing payment methods
    df_ord["payment_method"] = df_ord["payment_method"].fillna("Credit Card")

    # -------------------------------------------------------------
    # 5. Clean Returns Dataset
    # -------------------------------------------------------------
    print("\n--- Cleaning Returns Dataset ---")
    df_ret = df_ret_raw.copy()
    df_ret["return_date"] = pd.to_datetime(df_ret["return_date"], errors="coerce")
    valid_order_ids_clean = set(df_ord["order_id"])
    df_ret = df_ret[df_ret["order_id"].isin(valid_order_ids_clean)].copy()

    # -------------------------------------------------------------
    # 6. Merge Master Analytics Dataset & Feature Engineering
    # -------------------------------------------------------------
    print("\n--- Creating Clean Master Orders Dataset ---")
    
    # Merge Orders + Products
    df_master = df_ord.merge(df_prod, on="product_id", how="inner")
    
    # Merge + Customers
    df_master = df_master.merge(df_cust, on="customer_id", how="inner")

    # Merge + Returns flag
    ret_order_ids = set(df_ret["order_id"])
    df_master["is_returned"] = df_master["order_id"].isin(ret_order_ids).astype(int)
    
    # Merge return reason
    df_master = df_master.merge(df_ret[["order_id", "return_reason"]], on="order_id", how="left")
    df_master["return_reason"] = df_master["return_reason"].fillna("No Return")

    # Financial Feature Engineering
    df_master["gross_sales"] = df_master["quantity"] * df_master["unit_price"]
    df_master["discount_amount"] = df_master["gross_sales"] * df_master["discount"]
    df_master["net_sales"] = df_master["gross_sales"] - df_master["discount_amount"]
    df_master["total_cost"] = df_master["quantity"] * df_master["unit_cost"]
    df_master["gross_profit"] = df_master["net_sales"] - df_master["total_cost"]
    df_master["profit_margin_pct"] = (df_master["gross_profit"] / df_master["net_sales"]) * 100

    # Net Revenue after returns
    df_master["net_revenue"] = np.where(df_master["is_returned"] == 1, 0.0, df_master["net_sales"])
    df_master["net_profit_final"] = np.where(df_master["is_returned"] == 1, -df_master["shipping_cost"], df_master["gross_profit"])

    # Time Attributes
    df_master["order_year"] = df_master["order_date"].dt.year
    df_master["order_month"] = df_master["order_date"].dt.month
    df_master["order_year_month"] = df_master["order_date"].dt.to_period("M").astype(str)
    df_master["order_quarter"] = df_master["order_date"].dt.to_period("Q").astype(str)
    df_master["day_of_week"] = df_master["order_date"].dt.day_name()

    print(f"Final Clean Master Orders Shape: {df_master.shape}")
    print("\nMaster Dataset Columns:")
    print(list(df_master.columns))

    # Save cleaned files
    df_cust.to_csv(os.path.join(clean_dir, "cleaned_customers.csv"), index=False)
    df_prod.to_csv(os.path.join(clean_dir, "cleaned_products.csv"), index=False)
    df_ord.to_csv(os.path.join(clean_dir, "cleaned_orders.csv"), index=False)
    df_ret.to_csv(os.path.join(clean_dir, "cleaned_returns.csv"), index=False)
    df_master.to_csv(os.path.join(clean_dir, "cleaned_master_orders.csv"), index=False)

    print("\n--- Summary KPIs ---")
    total_net_sales = df_master["net_sales"].sum()
    total_net_revenue = df_master["net_revenue"].sum()
    total_profit = df_master["net_profit_final"].sum()
    total_orders = df_master["order_id"].nunique()
    total_returns = df_master["is_returned"].sum()
    overall_return_rate = (total_returns / total_orders) * 100

    print(f"Total Gross Orders:   {total_orders:,}")
    print(f"Total Net Sales:      ${total_net_sales:,.2f}")
    print(f"Net Realized Revenue: ${total_net_revenue:,.2f}")
    print(f"Net Realized Profit:  ${total_profit:,.2f}")
    print(f"Overall Return Rate:  {overall_return_rate:.2f}%\n")

    print("Data cleaning & EDA pipeline completed successfully!")

if __name__ == "__main__":
    main()
