import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import calendar
from matplotlib.gridspec import GridSpec

# Load and prepare data
df = pd.read_csv(r"C:\Users\91902\Desktop\Vs_code\Data-Driven Stock Analysis\new\combined.csv")
df['date'] = pd.to_datetime(df['date'])
df = df.sort_values(by=['Ticker', 'date'])
df['Month'] = df['date'].dt.to_period('M')

# Monthly returns
first_close = df.groupby(['Ticker', 'Month']).first()['close']
last_close = df.groupby(['Ticker', 'Month']).last()['close']
monthly_return = ((last_close - first_close) / first_close).reset_index()
monthly_return.columns = ['Ticker', 'Month', 'Monthly_Return']
monthly_return['MonthName'] = monthly_return['Month'].astype(str)
monthly_return['MonthDisplay'] = pd.to_datetime(monthly_return['Month'].astype(str)).dt.strftime('%b')

# Plotting setup
months_order = monthly_return['Month'].sort_values().unique()
fig = plt.figure(figsize=(16, 14))  # Smaller and wider for clearer plots
gs = GridSpec(4, 3, figure=fig)
plt.subplots_adjust(hspace=0.7)

for idx, month in enumerate(months_order):
    ax = fig.add_subplot(gs[idx // 3, idx % 3])
    
    # Top and bottom 5
    month_data = monthly_return[monthly_return['Month'] == month]
    top5 = month_data.sort_values('Monthly_Return', ascending=False).head(5)
    bottom5 = month_data.sort_values('Monthly_Return').head(5)
    combined = pd.concat([top5, bottom5])
    colors = ['green'] * 5 + ['red'] * 5
    
    # Plot
    sns.barplot(x='Ticker', y='Monthly_Return', data=combined, palette=colors, ax=ax)
    ax.set_title(f"{calendar.month_name[month.month]}", fontsize=10)
    ax.set_ylabel("")
    ax.set_xlabel("")
    ax.set_xticklabels(combined['Ticker'], rotation=35, ha='right', fontsize=8)
    ax.tick_params(axis='y', labelsize=8)
    ax.axhline(0, color='black', linestyle='--', linewidth=0.7)

# Main title
plt.suptitle("Top 5 Gainers and Losers by Month (1-Year Breakdown)", fontsize=14)
plt.tight_layout(rect=[0, 0, 1, 0.96])
plt.show()
