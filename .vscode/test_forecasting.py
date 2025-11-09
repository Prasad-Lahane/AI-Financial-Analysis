from modules.data_loader import load_screener_data
from modules.models.forecasting_model import train_forecast_model

file_path = "data/raw/Jio_Financial.xlsx"
df = load_screener_data(file_path)

if df is not None:
    forecast_df, model = train_forecast_model(df, metric='net profit')
else:
    print("❌ Cannot forecast due to data load failure.")
