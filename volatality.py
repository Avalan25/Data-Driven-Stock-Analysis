import pandas as pd
import matplotlib.pyplot as plt

# Step 1: Load combined stock data
combined_df = pd.read_csv(r"C:\Users\91902\Desktop\Vs_code\Data-Driven Stock Analysis\new\combined.csv")
combined_df['date'] = pd.to_datetime(combined_df['date'])
combined_df = combined_df.sort_values(by=['Ticker', 'date'])

# Step 2: Calculate daily return
combined_df['prev_close'] = combined_df.groupby('Ticker')['close'].shift(1)
combined_df['daily_return'] = (combined_df['close'] - combined_df['prev_close']) / combined_df['prev_close']
combined_df.dropna(subset=['daily_return'], inplace=True)

# Step 3: Calculate volatility (standard deviation of daily returns)
volatility_df = combined_df.groupby('Ticker')['daily_return'].std().reset_index()
volatility_df.columns = ['Ticker', 'Volatility']

# Step 4: Load the symbol mapping file
sector_df = pd.read_csv(r"C:\Users\91902\Desktop\Vs_code\Data-Driven Stock Analysis\Sector_data - Sheet1.csv")

# Step 5: Merge volatility data with symbols using Ticker and COMPANY
merged_df = pd.merge(volatility_df, sector_df, left_on='Ticker', right_on='COMPANY', how='left')

# Step 6: Keep only necessary columns and drop rows without symbols
final_df = merged_df[['Symbol', 'Volatility']].dropna()

# Step 7: Save the final data to a CSV
output_csv = r"C:\Users\91902\Desktop\Vs_code\Data-Driven Stock Analysis\volatility_with_symbols.csv"
final_df.to_csv(output_csv, index=False)
print(f"✅ Volatility CSV saved at: {output_csv}")

# Step 8: Plot bar chart of top 10 most volatile stocks
top10_volatile = final_df.sort_values(by='Volatility', ascending=False).head(10)

plt.figure(figsize=(10, 6))
plt.bar(top10_volatile['Symbol'], top10_volatile['Volatility'], color='orange', edgecolor='black')
plt.title("Top 10 Most Volatile Stocks (Standard Deviation of Daily Returns)")
plt.xlabel("Symbol")
plt.ylabel("Volatility")
plt.xticks(rotation=45)
plt.grid(axis='y')
plt.tight_layout()
plt.show()