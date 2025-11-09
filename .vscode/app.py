import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from modules.data_loader import load_screener_data
from modules.models.forecasting_model import forecast_net_profit
from modules.models.valuation_model import calculate_dcf
import os
import tempfile

# ---------- PAGE CONFIG ----------
st.set_page_config(page_title="AI Based FMVA", layout="wide")

# ---------- SIDEBAR ----------
with st.sidebar:
    st.title("📊 AI Valuation Tool")
    st.markdown("Upload your Excel file to get:")
    st.markdown("- 📈 Forecasted Net Profit\n- 💰 Company Valuation (DCF + PE)\n- 📉 Visualizations\n- 📁 Downloadable Report")
    st.markdown("---")
    st.subheader("📌 Assumptions")
    discount_rate = st.slider("Discount Rate (WACC)", 5.0, 15.0, 10.0)
    growth_rate = st.slider("Terminal Growth Rate (%)", 2.0, 10.0, 5.0)
    pe_ratio = st.slider("Industry PE Ratio", 5, 50, 20)
    st.markdown("---")
    st.caption("Made by Prasad Lahane © 2025")

# ---------- MAIN TITLE ----------
st.title("📊 AI-Powered Financial Modeling & Valuation Tool")
st.markdown("Upload your Excel file to generate forecasts and valuation.")

# ---------- FILE UPLOADER ----------
uploaded_file = st.file_uploader("📂 Upload Or Drag Excel File Here", type=["xlsx"])

if uploaded_file is not None:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx", dir="sample_data") as tmp:
        tmp.write(uploaded_file.read())
        temp_path = tmp.name

    # ---------- DATA LOADING ----------
    df_clean = load_screener_data(file_path=temp_path)

    if df_clean is not None:
        st.subheader("✅ Cleaned Financial Data")
        st.dataframe(df_clean, use_container_width=True)

        # ---------- BASIC METRICS ----------
        if 'sales' in df_clean.columns and 'net profit' in df_clean.columns:
            recent_years = df_clean.tail(2)
            revenue_growth = ((recent_years['sales'].iloc[1] - recent_years['sales'].iloc[0]) / recent_years['sales'].iloc[0]) * 100
            net_profit_margin = (recent_years['net profit'].iloc[1] / recent_years['sales'].iloc[1]) * 100

            col1, col2 = st.columns(2)
            col1.metric("📈 YoY Revenue Growth", f"{revenue_growth:.2f} %")
            col2.metric("💰 Net Profit Margin", f"{net_profit_margin:.2f} %")

        # ---------- FORECAST ----------
        future_df = forecast_net_profit(df_clean)
        if future_df is not None:
            st.markdown("### 🔮 3-Year Net Profit Forecast")
            
            # ---------- VISUALIZATION ----------
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df_clean.index.astype(str), y=df_clean['net profit'],
                mode='lines+markers', name='Historical Net Profit'
            ))
            fig.add_trace(go.Scatter(
                x=future_df['year'].astype(str), y=future_df['predicted_net profit'],
                mode='lines+markers', name='Forecasted Net Profit',
                line=dict(dash='dash')
            ))
            fig.update_layout(title="Net Profit Forecast (Historical vs Predicted)",
                              xaxis_title="Year", yaxis_title="Net Profit (in ₹ Cr)",
                              template="plotly_white", height=400)
            st.plotly_chart(fig, use_container_width=True)

            # ---------- KEY METRICS ----------
            st.markdown("### 📌 Quick Stats")
            col1, col2, col3 = st.columns(3)
            col1.metric("📅 Last Year", f"{df_clean.index[-1]}")
            col2.metric("💼 Last Net Profit", f"{df_clean['net profit'].iloc[-1]:,.2f} Cr")
            col3.metric("📊 Next Year Forecast", f"{future_df['predicted_net profit'].iloc[0]:,.2f} Cr")

            # ---------- VALUATION ----------
            dcf_valuation = calculate_dcf(future_df['predicted_net profit'].tolist(), discount_rate, growth_rate)
            last_net_profit = df_clean['net profit'].iloc[-1]
            pe_valuation = last_net_profit * pe_ratio

            st.subheader("💰 Estimated Company Valuation")
            col1, col2 = st.columns(2)
            col1.success(f"DCF Valuation: ₹ {dcf_valuation:,.2f} Cr")
            col2.info(f"PE Valuation: ₹ {pe_valuation:,.2f} Cr")

            # ---------- EXPANDERS ----------
            with st.expander("🔍 View Full Forecast Table"):
                st.table(future_df)

            with st.expander("📁 Cleaned Raw Financials"):
                st.dataframe(df_clean)

            # ---------- DOWNLOAD RESULTS ----------
            os.makedirs("results", exist_ok=True)
            output_path = f"results/output_{os.path.basename(temp_path)}".replace(".xlsx", "_report.xlsx")
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                df_clean.to_excel(writer, sheet_name='Cleaned Financials')
                future_df.to_excel(writer, sheet_name='Forecast')
                pd.DataFrame([
                    {'Valuation Method': 'DCF', 'Value (in Cr)': dcf_valuation},
                    {'Valuation Method': 'PE', 'Value (in Cr)': pe_valuation}
                ]).to_excel(writer, sheet_name='Valuation')

            with open(output_path, "rb") as f:
                st.download_button(
                    label="📥 Download Valuation Report",
                    data=f,
                    file_name=os.path.basename(output_path),
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        else:
            st.error("❌ Forecasting failed.")
    else:
        st.error("❌ Failed to load or clean the uploaded file.")
else:
    st.info("📂 Please upload a Screener Excel file to continue.")
