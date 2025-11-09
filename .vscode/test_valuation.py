from modules.models.valuation_model import discounted_cash_flow
import pandas as pd

# Simulate using forecasted profits (from previous forecast output)
profits = [1620.63, 1628.67, 1636.71]  # Could also load from forecast CSV

# Call DCF function
valuation = discounted_cash_flow(profits, discount_rate=0.1, terminal_growth_rate=0.03)

if valuation:
    print(f"\n💰 Estimated Company Valuation (DCF): ₹{valuation} Cr")
else:
    print("❌ Valuation could not be calculated.")
