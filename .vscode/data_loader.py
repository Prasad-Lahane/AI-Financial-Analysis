import pandas as pd
import re

def load_screener_data(file_path="sample_data/jio_financial_services.xlsx"):
    try:
        # Read sheet with header at row 0
        pl_df = pd.read_excel(file_path, sheet_name="Profit & Loss", header=0)
        
        # Drop empty rows/columns
        pl_df.dropna(axis=0, how="all", inplace=True)
        pl_df.dropna(axis=1, how="all", inplace=True)

        # Set the first column as index
        pl_df = pl_df.set_index(pl_df.columns[0])
        pl_df.index = pl_df.index.str.strip().str.lower()

        # Extract years from column headers like "31-03-2021"
        def extract_year(col):
            match = re.search(r"\d{4}", str(col))
            return int(match.group()) if match else None

        # Build a new DataFrame with valid years as columns
        year_mapping = {col: extract_year(col) for col in pl_df.columns}
        year_cols = {v: k for k, v in year_mapping.items() if v is not None}

        if not year_cols:
            raise ValueError("❌ No valid year-formatted columns found (e.g., 2021).")

        # Keep only columns with valid years and rename
        pl_df = pl_df[list(year_cols.values())]
        pl_df.columns = list(year_cols.keys())

        # Transpose so years become the index
        pl_df = pl_df.T
        pl_df.index.name = "year"

        # Match and keep financial rows
        metric_aliases = {
            'sales': ['sales', 'total income', 'revenue'],
            'operating profit': ['operating profit', 'ebit'],
            'net profit': ['net profit', 'profit after tax', 'pat'],
        }

        matched_rows = {}
        for key, aliases in metric_aliases.items():
            for alias in aliases:
                if alias in pl_df.columns:
                    matched_rows[key] = alias
                    break

        if not matched_rows:
            raise ValueError("❌ Expected financial rows not found in the file.")

        # Filter and rename columns
        df_clean = pl_df[list(matched_rows.values())].copy()
        df_clean.columns = list(matched_rows.keys())

        # Clean data
        df_clean = df_clean.replace(",", "", regex=True).astype(float)

        print("\n✅ Cleaned Financial Data Preview:")
        print(df_clean.tail())

        return df_clean

    except Exception as e:
        print(f"[ERROR] Failed to load data: {e}")
        return None
