import os
import pandas as pd
import xlsxwriter
from modules.data_loader import load_screener_data
from modules.models.forecasting_model import forecast_net_profit
from modules.models.valuation_model import calculate_dcf

# Step 1: Load and clean financial data
df_clean = load_screener_data()

if df_clean is None:
    print("❌ Pipeline aborted due to data loading error.")
    exit()

# Step 2: Forecast future net profits
future_df = forecast_net_profit(df_clean)

if future_df is None:
    print("❌ Pipeline aborted due to forecasting error.")
    exit()

# Step 3: Calculate company valuation
valuation = calculate_dcf(future_df['predicted_net profit'].tolist())

# Step 4: Save Results with Charts
os.makedirs("results", exist_ok=True)
output_path = "results/output_forecast_valuation.xlsx"

with pd.ExcelWriter(output_path, engine='xlsxwriter') as writer:
    df_clean.to_excel(writer, sheet_name='Cleaned Financials')
    future_df.to_excel(writer, sheet_name='Forecast')
    pd.DataFrame([{'Valuation (in Cr)': valuation}]).to_excel(writer, sheet_name='Valuation')

    workbook = writer.book
    forecast_sheet = writer.sheets['Forecast']
    clean_sheet = writer.sheets['Cleaned Financials']
    valuation_sheet = writer.sheets['Valuation']

    # 📈 Line Chart: Forecasted Net Profit
    line_chart = workbook.add_chart({'type': 'line'})
    line_chart.add_series({
        'name': 'Forecasted Net Profit',
        'categories': ['Forecast', 1, 0, len(future_df), 0],
        'values': ['Forecast', 1, 1, len(future_df), 1],
    })
    line_chart.set_title({'name': 'Net Profit Forecast (Next 3 Years)'})
    line_chart.set_x_axis({'name': 'Year'})
    line_chart.set_y_axis({'name': 'Net Profit (₹ Cr)'})
    forecast_sheet.insert_chart('E2', line_chart)

    # 📊 Bar Chart: Historical vs Forecasted Net Profit
    bar_chart = workbook.add_chart({'type': 'column'})
    bar_chart.add_series({
        'name': 'Historical Net Profit',
        'categories': ['Cleaned Financials', 1, 0, len(df_clean), 0],
        'values': ['Cleaned Financials', 1, 2, len(df_clean), 2],
    })
    bar_chart.add_series({
        'name': 'Forecasted Net Profit',
        'categories': ['Forecast', 1, 0, len(future_df), 0],
        'values': ['Forecast', 1, 1, len(future_df), 1],
    })
    bar_chart.set_title({'name': 'Net Profit: Historical vs Forecast'})
    bar_chart.set_x_axis({'name': 'Year'})
    bar_chart.set_y_axis({'name': 'Net Profit (₹ Cr)'})
    forecast_sheet.insert_chart('E20', bar_chart)

    # 💰 Highlight Valuation
    valuation_sheet.write('C2', '✅ DCF Valuation (in ₹ Cr):')
    valuation_sheet.write('D2', valuation)

print(f"\n📊 Charts and results saved to {output_path}")
