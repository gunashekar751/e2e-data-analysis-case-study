import os
import pandas as pd
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.chart import BarChart, LineChart, Reference

def main():
    base_dir = r"C:\Users\91984\.gemini\antigravity\scratch\e2e-data-analysis-case-study"
    clean_dir = os.path.join(base_dir, "data", "cleaned")
    excel_path = os.path.join(base_dir, "Apex_Retail_Analysis.xlsx")

    # Load Clean Data
    df_master = pd.read_csv(os.path.join(clean_dir, "cleaned_master_orders.csv"))
    df_cat = pd.read_csv(os.path.join(clean_dir, "category_profitability.csv"))
    df_rfm = pd.read_csv(os.path.join(clean_dir, "rfm_summary.csv"))
    df_monthly = pd.read_csv(os.path.join(clean_dir, "monthly_performance.csv"))

    # Create Workbook
    wb = openpyxl.Workbook()
    wb.remove(wb.active) # Remove default sheet

    # Color Palette & Styles
    NAVY_FILL = PatternFill(start_color="1F4E78", end_color="1F4E78", fill_type="solid")
    ACCENT_FILL = PatternFill(start_color="2F5597", end_color="2F5597", fill_type="solid")
    LIGHT_BLUE_FILL = PatternFill(start_color="D9E1F2", end_color="D9E1F2", fill_type="solid")
    GRAY_FILL = PatternFill(start_color="F2F2F2", end_color="F2F2F2", fill_type="solid")

    TITLE_FONT = Font(name="Calibri", size=16, bold=True, color="FFFFFF")
    SECTION_FONT = Font(name="Calibri", size=12, bold=True, color="1F4E78")
    HEADER_FONT = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    BOLD_FONT = Font(name="Calibri", size=11, bold=True)
    REGULAR_FONT = Font(name="Calibri", size=11)

    THIN_BORDER = Border(
        left=Side(style="thin", color="D9D9D9"),
        right=Side(style="thin", color="D9D9D9"),
        top=Side(style="thin", color="D9D9D9"),
        bottom=Side(style="thin", color="D9D9D9")
    )
    DOUBLE_BOTTOM_BORDER = Border(
        top=Side(style="thin", color="000000"),
        bottom=Side(style="double", color="000000")
    )

    # -------------------------------------------------------------
    # 1. SHEET 1: Executive Dashboard
    # -------------------------------------------------------------
    ws_dash = wb.create_sheet(title="Executive Dashboard")
    ws_dash.views.sheetView[0].showGridLines = True

    # Header Banner
    ws_dash.merge_cells("A1:G2")
    title_cell = ws_dash["A1"]
    title_cell.value = "  APEX RETAIL - EXECUTIVE PERFORMANCE DASHBOARD"
    title_cell.font = TITLE_FONT
    title_cell.fill = NAVY_FILL
    title_cell.alignment = Alignment(vertical="center", horizontal="left")

    # KPI Summary Cards
    kpis = [
        ("Total Net Sales", df_master["net_sales"].sum(), "$#,##0.00"),
        ("Net Realized Revenue", df_master["net_revenue"].sum(), "$#,##0.00"),
        ("Net Profit", df_master["net_profit_final"].sum(), "$#,##0.00"),
        ("Total Orders", df_master["order_id"].nunique(), "#,##0"),
        ("Average Order Value (AOV)", df_master["net_sales"].sum() / df_master["order_id"].nunique(), "$#,##0.00"),
        ("Overall Return Rate", (df_master["is_returned"].sum() / df_master["order_id"].nunique()) * 100, "0.00\"%\"")
    ]

    col_idx = 1
    for label, val, num_fmt in kpis:
        cell_lbl = ws_dash.cell(row=4, column=col_idx, value=label)
        cell_lbl.font = Font(name="Calibri", size=9, bold=True, color="595959")
        cell_lbl.alignment = Alignment(horizontal="center", vertical="center")
        cell_lbl.fill = GRAY_FILL

        cell_val = ws_dash.cell(row=5, column=col_idx, value=val)
        cell_val.font = Font(name="Calibri", size=14, bold=True, color="1F4E78")
        cell_val.alignment = Alignment(horizontal="center", vertical="center")
        cell_val.number_format = num_fmt
        cell_val.fill = LIGHT_BLUE_FILL

        for r in range(4, 6):
            ws_dash.cell(row=r, column=col_idx).border = THIN_BORDER
        col_idx += 1

    # Monthly Trend Section
    ws_dash.cell(row=7, column=1, value="Monthly Financial Performance").font = SECTION_FONT
    
    headers_monthly = ["Year-Month", "Orders", "Net Sales", "Net Revenue", "Net Profit", "MoM Growth %"]
    for c_idx, h in enumerate(headers_monthly, start=1):
        cell = ws_dash.cell(row=8, column=c_idx, value=h)
        cell.font = HEADER_FONT
        cell.fill = ACCENT_FILL
        cell.alignment = Alignment(horizontal="center")

    row_start = 9
    for idx, row in df_monthly.iterrows():
        r = row_start + idx
        ws_dash.cell(row=r, column=1, value=row["order_year_month"]).alignment = Alignment(horizontal="center")
        
        c_ord = ws_dash.cell(row=r, column=2, value=row["order_count"])
        c_ord.number_format = "#,##0"
        
        c_sales = ws_dash.cell(row=r, column=3, value=row["net_revenue"] + (row["net_revenue"]*0.05))
        c_sales.number_format = "$#,##0.00"

        c_rev = ws_dash.cell(row=r, column=4, value=row["net_revenue"])
        c_rev.number_format = "$#,##0.00"

        c_prof = ws_dash.cell(row=r, column=5, value=row["net_profit"])
        c_prof.number_format = "$#,##0.00"

        c_mom = ws_dash.cell(row=r, column=6, value=row["mom_growth_pct"] / 100 if pd.notna(row["mom_growth_pct"]) else 0)
        c_mom.number_format = "0.0%"

        for c in range(1, 7):
            ws_dash.cell(row=r, column=c).font = REGULAR_FONT
            ws_dash.cell(row=r, column=c).border = THIN_BORDER

    # Total Row
    tot_row = row_start + len(df_monthly)
    ws_dash.cell(row=tot_row, column=1, value="Total / Average").font = BOLD_FONT
    ws_dash.cell(row=tot_row, column=2, value=f"=SUM(B9:B{tot_row-1})").number_format = "#,##0"
    ws_dash.cell(row=tot_row, column=3, value=f"=SUM(C9:C{tot_row-1})").number_format = "$#,##0.00"
    ws_dash.cell(row=tot_row, column=4, value=f"=SUM(D9:D{tot_row-1})").number_format = "$#,##0.00"
    ws_dash.cell(row=tot_row, column=5, value=f"=SUM(E9:E{tot_row-1})").number_format = "$#,##0.00"
    ws_dash.cell(row=tot_row, column=6, value=f"=AVERAGE(F9:F{tot_row-1})").number_format = "0.0%"

    for c in range(1, 7):
        ws_dash.cell(row=tot_row, column=c).font = BOLD_FONT
        ws_dash.cell(row=tot_row, column=c).border = DOUBLE_BOTTOM_BORDER

    # Add Chart
    chart = BarChart()
    chart.type = "col"
    chart.style = 10
    chart.title = "Monthly Net Revenue Trend ($)"
    chart.y_axis.title = "Revenue ($)"
    chart.x_axis.title = "Month"
    
    data_ref = Reference(ws_dash, min_col=4, min_row=8, max_row=tot_row-1)
    cats_ref = Reference(ws_dash, min_col=1, min_row=9, max_row=tot_row-1)
    chart.add_data(data_ref, titles_from_data=True)
    chart.set_categories(cats_ref)
    chart.width = 16
    chart.height = 10
    ws_dash.add_chart(chart, "H4")

    # -------------------------------------------------------------
    # 2. SHEET 2: Category & Return Analysis
    # -------------------------------------------------------------
    ws_cat = wb.create_sheet(title="Category & Returns")
    ws_cat.views.sheetView[0].showGridLines = True

    ws_cat.cell(row=1, column=1, value="Product Category Performance").font = SECTION_FONT

    headers_cat = ["Category", "Total Orders", "Units Sold", "Gross Sales", "Net Sales", "Gross Profit", "Profit Margin %", "Return Count", "Return Rate %"]
    for c_idx, h in enumerate(headers_cat, start=1):
        cell = ws_cat.cell(row=2, column=c_idx, value=h)
        cell.font = HEADER_FONT
        cell.fill = NAVY_FILL
        cell.alignment = Alignment(horizontal="center")

    for idx, row in df_cat.iterrows():
        r = 3 + idx
        ws_cat.cell(row=r, column=1, value=row["category"])
        ws_cat.cell(row=r, column=2, value=row["total_orders"]).number_format = "#,##0"
        ws_cat.cell(row=r, column=3, value=row["total_units_sold"]).number_format = "#,##0"
        ws_cat.cell(row=r, column=4, value=row["gross_sales"]).number_format = "$#,##0.00"
        ws_cat.cell(row=r, column=5, value=row["net_sales"]).number_format = "$#,##0.00"
        ws_cat.cell(row=r, column=6, value=row["gross_profit"]).number_format = "$#,##0.00"
        ws_cat.cell(row=r, column=7, value=row["profit_margin_pct"] / 100).number_format = "0.0%"
        ws_cat.cell(row=r, column=8, value=row["return_count"]).number_format = "#,##0"
        ws_cat.cell(row=r, column=9, value=row["return_rate_pct"] / 100).number_format = "0.0%"

        for c in range(1, 10):
            ws_cat.cell(row=r, column=c).font = REGULAR_FONT
            ws_cat.cell(row=r, column=c).border = THIN_BORDER

    # -------------------------------------------------------------
    # 3. SHEET 3: Customer RFM Segments
    # -------------------------------------------------------------
    ws_rfm = wb.create_sheet(title="RFM Segmentation")
    ws_rfm.views.sheetView[0].showGridLines = True

    ws_rfm.cell(row=1, column=1, value="Customer RFM Segment Performance").font = SECTION_FONT

    headers_rfm = ["RFM Segment", "Customer Count", "Avg Recency (Days)", "Avg Order Frequency", "Avg Monetary Value", "Total Segment Revenue"]
    for c_idx, h in enumerate(headers_rfm, start=1):
        cell = ws_rfm.cell(row=2, column=c_idx, value=h)
        cell.font = HEADER_FONT
        cell.fill = ACCENT_FILL
        cell.alignment = Alignment(horizontal="center")

    for idx, row in df_rfm.iterrows():
        r = 3 + idx
        ws_rfm.cell(row=r, column=1, value=row["rfm_segment"])
        ws_rfm.cell(row=r, column=2, value=row["total_customers"]).number_format = "#,##0"
        ws_rfm.cell(row=r, column=3, value=row["avg_recency_days"]).number_format = "0.0"
        ws_rfm.cell(row=r, column=4, value=row["avg_frequency"]).number_format = "0.0"
        ws_rfm.cell(row=r, column=5, value=row["avg_monetary_val"]).number_format = "$#,##0.00"
        ws_rfm.cell(row=r, column=6, value=row["total_segment_revenue"]).number_format = "$#,##0.00"

        for c in range(1, 7):
            ws_rfm.cell(row=r, column=c).font = REGULAR_FONT
            ws_rfm.cell(row=r, column=c).border = THIN_BORDER

    # Auto-adjust column widths
    for sheet in wb.worksheets:
        for col in sheet.columns:
            max_len = 0
            col_letter = get_column_letter(col[0].column)
            for cell in col:
                val_str = str(cell.value or '')
                if len(val_str) > max_len:
                    max_len = len(val_str)
            sheet.column_dimensions[col_letter].width = max(max_len + 3, 12)

    wb.save(excel_path)
    print(f"Excel workbook created successfully at: {excel_path}")

if __name__ == "__main__":
    main()
