# import pandas as pd
# import seaborn as sns
# import matplotlib.pyplot as plt

# # Step 1: Load combined stock data
# df = pd.read_csv(r"C:\Users\91902\Desktop\Vs_code\Data-Driven Stock Analysis\new\combined.csv")
# df['date'] = pd.to_datetime(df['date'])
# df = df.sort_values(by=['Ticker', 'date'])

# # Step 2: Pivot data so that each stock's close price is a separate column
# pivot_df = df.pivot(index='date', columns='Ticker', values='close')

# # Step 3: Calculate percentage change to normalize data (daily return)
# pct_change_df = pivot_df.pct_change().dropna()

# # Step 4: Compute correlation matrix
# correlation_matrix = pct_change_df.corr()

# # Optional: Save correlation matrix to CSV
# correlation_matrix.to_csv(r"C:\Users\91902\Desktop\Vs_code\Data-Driven Stock Analysis\correlation_matrix.csv")
# print("✅ Correlation matrix saved to CSV")

# # Step 5: Plot the heatmap
# plt.figure(figsize=(14, 10))
# sns.heatmap(correlation_matrix, cmap='coolwarm', annot=False, fmt=".2f", linewidths=0.5)

# plt.title("Stock Price Correlation Heatmap (Based on Daily % Change)")
# plt.xticks(rotation=45, ha='right')
# plt.yticks(rotation=0)
# plt.tight_layout()
# plt.show()



import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from itertools import combinations

# Step 1: Load combined stock price data
stock_df = pd.read_csv(r"C:\Users\91902\Desktop\Vs_code\Data-Driven Stock Analysis\new\combined.csv")
stock_df['date'] = pd.to_datetime(stock_df['date'])
stock_df = stock_df.sort_values(by=['Ticker', 'date'])

# Step 2: Pivot data: rows = date, columns = ticker, values = close
pivot_df = stock_df.pivot(index='date', columns='Ticker', values='close')

# Step 3: Compute percentage change and correlation matrix
returns_df = pivot_df.pct_change().dropna()
correlation_matrix = returns_df.corr()

# Step 4: Load sector data
sector_df = pd.read_csv(r"C:\Users\91902\Desktop\Vs_code\Data-Driven Stock Analysis\sector_data - Sheet1.csv")
sector_df = sector_df.rename(columns={"COMPANY": "Ticker", "sector": "Sector"})

# Step 5: Merge to get Ticker-Sector mapping
ticker_sector_map = dict(zip(sector_df['Ticker'], sector_df['Sector']))

# Step 6: Count strong correlations per sector
correlation_summary = {}

tickers = correlation_matrix.columns.tolist()
for t1, t2 in combinations(tickers, 2):
    corr_value = correlation_matrix.loc[t1, t2]

    sector1 = ticker_sector_map.get(t1)
    sector2 = ticker_sector_map.get(t2)

    if pd.isna(sector1) or pd.isna(sector2):
        continue

    if sector1 not in correlation_summary:
        correlation_summary[sector1] = {'Positive': 0, 'Negative': 0}

    # Count strong correlations only
    if corr_value >= 0.5:
        correlation_summary[sector1]['Positive'] += 1
    elif corr_value <= -0.5:
        correlation_summary[sector1]['Negative'] += 1

# Step 7: Convert summary to DataFrame
summary_df = pd.DataFrame.from_dict(correlation_summary, orient='index').reset_index()
summary_df = summary_df.rename(columns={'index': 'Sector'})

# Ensure both columns exist
if 'Positive' not in summary_df.columns:
    summary_df['Positive'] = 0
if 'Negative' not in summary_df.columns:
    summary_df['Negative'] = 0

# Save result
output_csv = r"C:\Users\91902\Desktop\Vs_code\Data-Driven Stock Analysis\sectorwise_correlation_summary.csv"
summary_df.to_csv(output_csv, index=False)
print(f"✅ Sector-wise correlation summary saved to: {output_csv}")

# Step 8: Plot stacked bar chart
plot_df = summary_df.set_index('Sector')[['Positive', 'Negative']]
plot_df.plot(kind='bar', stacked=True, figsize=(12, 6), color=['green', 'red'], edgecolor='black')

plt.title("Sector-wise Positive and Negative Correlations (One Year)")
plt.xlabel("Sector")
plt.ylabel("Number of Strong Correlations")
plt.xticks(rotation=45)
plt.grid(axis='y')
plt.legend(title="Correlation Type")
plt.tight_layout()
plt.show()
