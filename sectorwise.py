import pandas as pd
import matplotlib.pyplot as plt

# Load the stock data
stock_df = pd.read_csv(r"C:\Users\91902\Desktop\Vs_code\Data-Driven Stock Analysis\new\combined.csv")

# Load sector mapping and rename the column
sector_df = pd.read_csv(r"C:\Users\91902\Desktop\Vs_code\Data-Driven Stock Analysis\sector_data - Sheet1.csv")
sector_df = sector_df.rename(columns={"COMPANY": "Ticker"})

# Ensure date is in datetime format and sort
stock_df['date'] = pd.to_datetime(stock_df['date'])
stock_df = stock_df.sort_values(by=['Ticker', 'date'])

# Calculate yearly return for each stock
first_close = stock_df.groupby('Ticker').first()['close']
last_close = stock_df.groupby('Ticker').last()['close']
yearly_return = ((last_close - first_close) / first_close).reset_index()
yearly_return.columns = ['Ticker', 'Yearly_Return']

# Merge with sector data
merged_df = pd.merge(yearly_return, sector_df, on='Ticker', how='left')
merged_df = merged_df.dropna(subset=['sector'])

# Calculate average yearly return per sector
sector_returns = merged_df.groupby('sector')['Yearly_Return'].mean().sort_values(ascending=False)

# Find High and Low sectors
high_sector = sector_returns.idxmax()
low_sector = sector_returns.idxmin()

# Find Stable sector (excluding high & low) — closest to 0
remaining_sectors = sector_returns.drop([high_sector, low_sector])
stable_sector = remaining_sectors.abs().idxmin()

# Create final result DataFrame
result_df = pd.DataFrame({
    'Sector': [high_sector, low_sector, stable_sector],
    'Avg_Yearly_Return': [
        sector_returns[high_sector],
        sector_returns[low_sector],
        sector_returns[stable_sector]
    ],
    'Performance': ['High', 'Low', 'Stable']
})

# Save result to CSV
output_csv = r"C:\Users\91902\Desktop\Vs_code\Data-Driven Stock Analysis\sector_classification.csv"
result_df.to_csv(output_csv, index=False)
print(f"✅ Sector classification saved to: {output_csv}")

# Plotting
plt.figure(figsize=(8, 5))
colors = result_df['Performance'].map({'High': 'green', 'Low': 'red', 'Stable': 'gray'})
plt.bar(result_df['Sector'], result_df['Avg_Yearly_Return'], color=colors, edgecolor='black')

# Annotate bars
for i, val in enumerate(result_df['Avg_Yearly_Return']):
    plt.text(i, val, f"{val:.2%}", ha='center', va='bottom', fontsize=10)

plt.title("High, Low, and Stable Performing Sectors (Corrected)")
plt.xlabel("Sector")
plt.ylabel("Average Yearly Return")
plt.grid(axis='y')
plt.tight_layout()
plt.show()
