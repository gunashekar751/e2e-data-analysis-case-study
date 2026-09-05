import os
import random
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

def main():
    base_dir = r"C:\Users\91984\.gemini\antigravity\scratch\e2e-data-analysis-case-study"
    raw_dir = os.path.join(base_dir, "data", "raw")
    os.makedirs(raw_dir, exist_ok=True)

    np.random.seed(42)
    random.seed(42)

    # -------------------------------------------------------------
    # 1. Customers Dataset (~1,000 customers)
    # -------------------------------------------------------------
    num_customers = 1000
    first_names = ["James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda", "William", "Elizabeth",
                   "David", "Barbara", "Richard", "Susan", "Joseph", "Jessica", "Thomas", "Sarah", "Charles", "Karen",
                   "Christopher", "Nancy", "Daniel", "Lisa", "Matthew", "Betty", "Anthony", "Margaret", "Donald", "Sandra"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez",
                  "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin"]

    dirty_regions = ["North", "  NORTH ", "South", "south", "East", " EAST", "West", "west", "Midwest", "MIDWEST", None]
    channels = ["Organic Search", "Paid Ads", "Social Media", "Email Campaign", "Referral", None]
    segments = ["Consumer", "Corporate", "Small Business"]

    start_date = datetime(2024, 1, 1)
    
    cust_records = []
    for i in range(1, num_customers + 1):
        cid = f"CUST-{1000 + i}"
        fname = random.choice(first_names)
        lname = random.choice(last_names)
        name = f"{fname} {lname}"
        email = f"{fname.lower()}.{lname.lower()}{random.randint(1,99)}@example.com" if random.random() > 0.03 else None
        reg = random.choice(dirty_regions)
        chan = random.choice(channels)
        seg = random.choice(segments)
        days_offset = random.randint(0, 700)
        signup_dt = (start_date + timedelta(days=days_offset)).strftime("%Y-%m-%d")

        cust_records.append({
            "customer_id": cid,
            "customer_name": name,
            "email": email,
            "region": reg,
            "acquisition_channel": chan,
            "customer_segment": seg,
            "signup_date": signup_dt
        })

    # Add 15 duplicate customer records with minor variances
    for i in range(15):
        dup_idx = random.randint(0, num_customers - 1)
        dup_rec = cust_records[dup_idx].copy()
        cust_records.append(dup_rec)

    df_cust = pd.DataFrame(cust_records)
    cust_csv = os.path.join(raw_dir, "raw_customers.csv")
    df_cust.to_csv(cust_csv, index=False)
    print(f"Generated raw_customers.csv with {len(df_cust)} rows.")

    # -------------------------------------------------------------
    # 2. Products Dataset (~50 products across 5 categories)
    # -------------------------------------------------------------
    dirty_categories = [
        "Electronics", "Electrnoics", "ELECTRONICS",
        "Apparel", "apparel", "  Apparel ",
        "Home & Kitchen", "Home and Kitchen", "HOME & KITCHEN",
        "Beauty & Care", "Beauty & care",
        "Sports & Outdoors", "Sports & outdoors"
    ]

    products_data = [
        ("Wireless Noise-Canceling Headphones", "Electronics", 120.00, 249.99),
        ("Smart 4K Ultra HD TV 55\"", "Electronics", 350.00, 699.99),
        ("Mechanical Gaming Keyboard", "Electronics", 45.00, 99.99),
        ("Ergonomic Wireless Mouse", "Electronics", 20.00, 49.99),
        ("Portable Bluetooth Speaker", "Electronics", 30.00, 79.99),
        ("Smart Watch Series V", "Electronics", 110.00, 229.99),
        ("USB-C Multi-Port Hub", "Electronics", 15.00, 39.99),
        ("High-Speed Wi-Fi Router", "Electronics", 50.00, 119.99),
        ("Noise Isolating Earbuds", "Electronics", 25.00, 59.99),
        ("HD Webcam 1080p", "Electronics", 30.00, 69.99),
        
        ("Men's Lightweight Running Jacket", "Apparel", 25.00, 65.00),
        ("Women's High-Waist Yoga Pants", "Apparel", 18.00, 48.00),
        ("Classic Cotton Crewneck T-Shirt", "Apparel", 8.00, 24.00),
        ("All-Weather Waterproof Boots", "Apparel", 45.00, 110.00),
        ("Unisex Fleece Pullover Hoodie", "Apparel", 20.00, 55.00),
        ("Slim-Fit Denim Jeans", "Apparel", 28.00, 68.00),
        ("Thermal Base Layer Top", "Apparel", 15.00, 38.00),
        ("Breathable Athletic Socks (6-Pack)", "Apparel", 6.00, 18.00),
        ("Casual Canvas Sneakers", "Apparel", 22.00, 52.00),
        ("Winter Insulated Gloves", "Apparel", 12.00, 32.00),

        ("Stainless Steel Espresso Machine", "Home & Kitchen", 140.00, 299.99),
        ("Non-Stick Ceramic Cookware Set", "Home & Kitchen", 80.00, 189.99),
        ("Smart Robot Vacuum Cleaner", "Home & Kitchen", 160.00, 349.99),
        ("Digital Air Fryer Oven 6Qt", "Home & Kitchen", 50.00, 119.99),
        ("High-Speed Blender 1200W", "Home & Kitchen", 40.00, 89.99),
        ("Memory Foam Queen Mattress Topper", "Home & Kitchen", 65.00, 139.99),
        ("Electric Kettle Temperature Control", "Home & Kitchen", 22.00, 49.99),
        ("Chef's Knife Japanese Steel 8\"", "Home & Kitchen", 30.00, 74.99),
        ("Automatic Drip Coffee Maker", "Home & Kitchen", 25.00, 59.99),
        ("Air Purifier for Large Room", "Home & Kitchen", 75.00, 159.99),

        ("Hydrating Facial Serum Vitamin C", "Beauty & Care", 12.00, 34.00),
        ("Sonic Electric Toothbrush", "Beauty & Care", 28.00, 69.99),
        ("Organic Argan Hair Oil Repair", "Beauty & Care", 9.00, 26.00),
        ("Deep Cleansing Charcoal Scrub", "Beauty & Care", 7.00, 19.99),
        ("Gentle Daily Face Moisturizer", "Beauty & Care", 10.00, 28.00),
        ("Anti-Aging Retinol Night Cream", "Beauty & Care", 15.00, 42.00),
        ("Professional Hair Dryer 1875W", "Beauty & Care", 25.00, 59.99),
        ("Natural Sunscreen SPF 50", "Beauty & Care", 8.00, 22.00),
        ("Exfoliating Body Wash Lavender", "Beauty & Care", 5.00, 14.99),
        ("Beard Grooming & Trimming Kit", "Beauty & Care", 14.00, 35.00),

        ("Adjustable Dumbbell Set 50lbs", "Sports & Outdoors", 110.00, 249.99),
        ("Waterproof 4-Person Camping Tent", "Sports & Outdoors", 60.00, 149.99),
        ("Insulated Stainless Hydration Bottle", "Sports & Outdoors", 10.00, 29.99),
        ("Ultra-Thick Non-Slip Yoga Mat", "Sports & Outdoors", 14.00, 36.00),
        ("Folding Camping Chair Set", "Sports & Outdoors", 22.00, 54.99),
        ("Trekking Poles Aluminum Pair", "Sports & Outdoors", 16.00, 39.99),
        ("Resistance Exercise Bands (Set of 5)", "Sports & Outdoors", 7.00, 19.99),
        ("High-Performance Bicycle Helmet", "Sports & Outdoors", 25.00, 64.99),
        ("Outdoor Hydration Backpack 2L", "Sports & Outdoors", 18.00, 44.99),
        ("Compact LED Camping Lantern", "Sports & Outdoors", 8.00, 21.99),
    ]

    prod_records = []
    for idx, (pname, cat, cost, price) in enumerate(products_data, start=1):
        pid = f"PROD-{idx:02d}"
        dirty_cat_choice = random.choice([cat, cat, cat, random.choice(dirty_categories)])
        prod_records.append({
            "product_id": pid,
            "product_name": pname,
            "category": dirty_cat_choice,
            "unit_cost": cost,
            "unit_price": price
        })

    df_prod = pd.DataFrame(prod_records)
    prod_csv = os.path.join(raw_dir, "raw_products.csv")
    df_prod.to_csv(prod_csv, index=False)
    print(f"Generated raw_products.csv with {len(df_prod)} rows.")

    # -------------------------------------------------------------
    # 3. Orders Dataset (~5,200 order lines over 2024-2025)
    # -------------------------------------------------------------
    num_orders = 5200
    valid_cids = [f"CUST-{1000 + i}" for i in range(1, num_customers + 1)]
    valid_pids = [f"PROD-{i:02d}" for i in range(1, 51)]
    
    pay_methods = ["Credit Card", "PayPal", "Debit Card", "Store Credit", None]

    order_records = []
    order_id_counter = 10001
    
    order_start = datetime(2024, 1, 1)
    
    for i in range(num_orders):
        oid = f"ORD-{order_id_counter}"
        order_id_counter += 1

        days_offset = random.randint(0, 729)
        dt = order_start + timedelta(days=days_offset)
        
        fmt_rand = random.random()
        if fmt_rand < 0.70:
            dt_str = dt.strftime("%Y-%m-%d")
        elif fmt_rand < 0.88:
            dt_str = dt.strftime("%m/%d/%Y")
        else:
            dt_str = dt.strftime("%d-%m-%Y")

        cid_rand = random.random()
        if cid_rand < 0.96:
            cid = random.choice(valid_cids)
        elif cid_rand < 0.98:
            cid = None
        else:
            cid = "CUST-9999" # invalid non-existent ID

        pid = random.choice(valid_pids)
        
        qty_rand = random.random()
        if qty_rand < 0.01:
            qty = -2  # negative anomaly
        elif qty_rand < 0.015:
            qty = 500 # extreme outlier
        else:
            qty = random.randint(1, 5)

        discount = round(random.choice([0.0, 0.0, 0.05, 0.10, 0.15, 0.20]), 2)
        pmt = random.choice(pay_methods)
        ship_cost = round(random.uniform(3.99, 19.99), 2)

        order_records.append({
            "order_id": oid,
            "order_date": dt_str,
            "customer_id": cid,
            "product_id": pid,
            "quantity": qty,
            "discount": discount,
            "payment_method": pmt,
            "shipping_cost": ship_cost
        })

    # Inject 80 duplicate order rows
    for _ in range(80):
        dup_row = random.choice(order_records).copy()
        order_records.append(dup_row)

    df_orders = pd.DataFrame(order_records)
    orders_csv = os.path.join(raw_dir, "raw_orders.csv")
    df_orders.to_csv(orders_csv, index=False)
    print(f"Generated raw_orders.csv with {len(df_orders)} rows.")

    # -------------------------------------------------------------
    # 4. Returns Dataset (~480 returns)
    # -------------------------------------------------------------
    valid_order_ids = [r["order_id"] for r in order_records if r["quantity"] > 0]
    returned_order_ids = random.sample(valid_order_ids, min(480, len(valid_order_ids)))

    reasons = ["Defective Item", "Wrong Size / Fit", "Item Not as Described", "Changed Mind", "Late Delivery"]
    
    return_records = []
    ret_id_counter = 5001

    for oid in returned_order_ids:
        ord_info = next((r for r in order_records if r["order_id"] == oid), None)
        if not ord_info:
            continue
            
        try:
            raw_dt = ord_info["order_date"]
            if "/" in raw_dt:
                ord_dt = datetime.strptime(raw_dt, "%m/%d/%Y")
            elif "-" in raw_dt and len(raw_dt.split("-")[0]) == 4:
                ord_dt = datetime.strptime(raw_dt, "%Y-%m-%d")
            else:
                ord_dt = datetime.strptime(raw_dt, "%d-%m-%Y")
        except Exception:
            ord_dt = datetime(2024, 6, 15)

        ret_dt = ord_dt + timedelta(days=random.randint(3, 25))
        reason = random.choice(reasons)

        return_records.append({
            "return_id": f"RET-{ret_id_counter}",
            "order_id": oid,
            "return_date": ret_dt.strftime("%Y-%m-%d"),
            "return_reason": reason
        })
        ret_id_counter += 1

    df_returns = pd.DataFrame(return_records)
    returns_csv = os.path.join(raw_dir, "raw_returns.csv")
    df_returns.to_csv(returns_csv, index=False)
    print(f"Generated raw_returns.csv with {len(df_returns)} rows.")

if __name__ == "__main__":
    main()
