# Apex Retail - End-to-End Data Analysis Case Study

[![Python 3.14](https://img.shields.io/badge/Python-3.14-blue.svg)](https://www.python.org/)
[![SQLite](https://img.shields.io/badge/Database-SQLite-003B57.svg)](https://www.sqlite.org/)
[![Pandas](https://img.shields.io/badge/Data_Analysis-Pandas-150458.svg)](https://pandas.pydata.org/)
[![Power BI](https://img.shields.io/badge/BI_Tool-Power_BI-F2C811.svg)](https://powerbi.microsoft.com/)
[![Excel](https://img.shields.io/badge/Spreadsheet-Excel-1D6F42.svg)](https://www.microsoft.com/excel)

A comprehensive, production-grade **End-to-End Data Analytics Case Study** focusing on **Apex Retail**, a multi-channel e-commerce enterprise. The project covers data generation/extraction, data cleaning & exploratory analysis in Python, analytical deep-dives using SQL & Pandas, executive dashboard modeling in Excel, DAX metric engineering for Power BI/Tableau, and strategic business recommendations.

---

## 📊 Project Overview

- **Timeframe Analyzed**: 2 Years (January 1, 2024 – December 31, 2025)
- **Completed Orders**: 4,914 Gross Orders
- **Gross Revenue**: \$1,287,915.12
- **Net Realized Revenue**: \$1,169,014.40
- **Net Realized Profit**: \$605,382.86 (**51.79% Net Margin**)
- **Overall Return Rate**: **9.34%** (\$118.9K refunded)

---

## 🛠️ Tech Stack & Skills Demonstrated

1. **Python (Pandas, NumPy, Matplotlib, Seaborn)**:
   - Automated data cleaning, deduplication, missing value imputation, date parsing, string standardization, and high-resolution chart exports.
2. **SQL (SQLite / DuckDB)**:
   - Window functions (`NTILE`, `LAG`), aggregations, CTEs, and relational database schema modeling.
3. **Excel (`openpyxl`)**:
   - Executive dashboard design, KPI summary cards, dynamic formulas (`SUMIFS`, `AVERAGEIFS`, `XLOOKUP`), conditional formatting, and native charts.
4. **Power BI / Tableau (DAX & Star Schema)**:
   - Star schema dimension modeling (`DimCustomer`, `DimProduct`, `DimDate`, `FactOrders`, `FactReturns`) and 20+ production-grade DAX measures.

---

## 📁 Repository Structure

```text
e2e-data-analysis-case-study/
│
├── data/
│   ├── raw/                       # Initial raw CSV files with dirty data
│   │   ├── raw_customers.csv
│   │   ├── raw_products.csv
│   │   ├── raw_orders.csv
│   │   └── raw_returns.csv
│   └── cleaned/                   # Sanitized datasets & SQLite DB
│       ├── apex_retail.db         # SQLite Relational Database
│       ├── cleaned_master_orders.csv
│       ├── rfm_summary.csv
│       ├── category_profitability.csv
│       └── monthly_performance.csv
│
├── scripts/
│   ├── 01_generate_raw_data.py    # Raw multi-table dataset synthesizer
│   ├── 02_data_cleaning_eda.py    # Data cleaning & exploratory data analysis
│   ├── 03_sql_pandas_analysis.py  # SQL window queries & Pandas transformations
│   ├── 04_build_excel_workbook.py # Excel workbook generator (Apex_Retail_Analysis.xlsx)
│   └── 05_bi_export.py            # High-res visualization charts & DAX library generator
│
├── visualizations/                # Exported PNG charts for report
│   ├── monthly_revenue_trend.png
│   ├── rfm_distribution.png
│   ├── category_profitability.png
│   ├── return_rate_by_category.png
│   └── regional_channel_heatmap.png
│
├── power_bi/
│   └── power_bi_dax_measures.dax  # Formatted DAX measures library
│
├── Apex_Retail_Analysis.xlsx       # Formatted Executive Excel Workbook
└── README.md                      # Project documentation
```

---

## 🚀 How to Run the Pipeline

### 1. Prerequisites
Ensure Python 3.9+ is installed along with required packages:

```bash
pip install pandas numpy matplotlib seaborn openpyxl xlsxwriter
```

### 2. Execution Steps
Run the pipeline scripts in sequential order:

```bash
# Step 1: Synthesize raw transactional data with intentional dirty data
python scripts/01_generate_raw_data.py

# Step 2: Clean data, handle nulls/outliers, and execute EDA
python scripts/02_data_cleaning_eda.py

# Step 3: Execute SQL window queries & Pandas analytical deep-dives
python scripts/03_sql_pandas_analysis.py

# Step 4: Programmatically generate Executive Excel Workbook
python scripts/04_build_excel_workbook.py

# Step 5: Export visual charts & Power BI DAX metrics
python scripts/05_bi_export.py
```

---

## 📌 Key Insights & Strategic Recommendations

1. **At-Risk Customer Retention Opportunity**:
   - **35.2% of repeat buyers (352 customers)** are currently At-Risk (> 230 days idle), representing **\$416.9K in historical revenue**.
   - *Action*: Launch automated 3-stage win-back email sequences with personalized 15% promotional incentives to capture **+\$104K in net revenue**.
2. **Product Return Rate Mitigation**:
   - Return rate of **9.34%** cost **\$118.9K in refunded sales** and \$7.3K in reverse shipping. **44.01% of returns** were due to *"Item Not as Described"* and *"Wrong Size/Fit"*.
   - *Action*: Enhance product specifications and 3D sizing charts to lower return rates to 6.8%, saving **+\$32K/year**.
3. **Category Profit Margin Optimization**:
   - Beauty & Care (**56.96% margin**) and Apparel (**56.76% margin**) significantly outperform Electronics (**48.71% margin**).
   - *Action*: Reallocate 15% of marketing ad spend toward high-margin Beauty & Apparel categories.

---

## 📄 License
This repository is open source and available under the [MIT License](LICENSE).
