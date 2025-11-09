from modules.data_loader import load_screener_data

file_path = "data/raw/Jio_Financial.xlsx"
df = load_screener_data(file_path)

if df is not None:
    print("\n✅ Data loaded successfully!")
else:
    print("❌ Could not load or clean the data.")
