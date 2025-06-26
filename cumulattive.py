import pandas as pd
import matplotlib.pyplot as plt

# Load combined data
df = pd.read_csv(r"C:\Users\91902\Desktop\Vs_code\Data-Driven Stock Analysis\new\combined.csv")

# Ensure date is datetime format
df['date'] = pd.to_datetime(df['date'])

# Sort by ticker and date
df = df.sort_values(by=['Ticker', 'date'])

# Calculate daily returns
df['prev_close'] = df.groupby('Ticker')['close'].shift(1)
df['daily_return'] = (df['close'] - df['prev_close']) / df['prev_close']

# Drop first row for each ticker (because of NaN daily return)
df.dropna(subset=['daily_return'], inplace=True)

# Calculate cumulative return for each day
df['cumulative_return'] = df.groupby('Ticker')['daily_return'].transform(lambda x: (1 + x).cumprod() - 1)

# Get the last cumulative return for each stock
latest_returns = df.groupby('Ticker').apply(lambda x: x.sort_values('date').iloc[-1])[['Ticker', 'cumulative_return']]
latest_returns = latest_returns.reset_index(drop=True)

# Save to CSV
output_csv = r"C:\Users\91902\Desktop\Vs_code\Data-Driven Stock Analysis\cumulative_returns.csv"
latest_returns.to_csv(output_csv, index=False)
print(f"✅ Cumulative return CSV saved at: {output_csv}")

# Get top 5 performers for plotting
top5 = latest_returns.sort_values('cumulative_return', ascending=False).head(5)['Ticker'].tolist()
top5_df = df[df['Ticker'].isin(top5)]

# Plot line chart
plt.figure(figsize=(12, 6))
for ticker in top5:
    ticker_df = top5_df[top5_df['Ticker'] == ticker]
    plt.plot(ticker_df['date'], ticker_df['cumulative_return'], label=ticker)

plt.title("Cumulative Return Over Time (Top 5 Performing Stocks)")
plt.xlabel("Date")
plt.ylabel("Cumulative Return")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
