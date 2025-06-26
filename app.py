import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import calendar

st.set_page_config(layout='wide', page_title='Data-Driven Stock Analysis')

st.title("📊 Data-Driven Stock Analysis Dashboard")

menu = st.sidebar.selectbox(
    "Select Analysis",
    [
        "Top 10 Most Volatile Stocks",
        "Top 5 Performing Stocks",
        "High, Low, Stable Sectors",
        "Sector-wise Correlation Summary",
        "Monthly Gainers and Losers"
    ]
)

# Common file paths
combined_csv = "new/combined.csv"
sector_csv = "Sector_data - Sheet1.csv"

@st.cache_data
def load_data():
    df = pd.read_csv(combined_csv)
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values(by=['Ticker', 'date'])
    return df

@st.cache_data
def load_sector():
    return pd.read_csv(sector_csv)

df = load_data()
sector_df = load_sector()

if menu == "Top 10 Most Volatile Stocks":
    st.subheader("📈 Top 10 Most Volatile Stocks (Standard Deviation of Daily Returns)")
    df['prev_close'] = df.groupby('Ticker')['close'].shift(1)
    df['daily_return'] = (df['close'] - df['prev_close']) / df['prev_close']
    volatility_df = df.groupby('Ticker')['daily_return'].std().reset_index()
    volatility_df.columns = ['Ticker', 'Volatility']
    merged = pd.merge(volatility_df, sector_df, left_on='Ticker', right_on='COMPANY', how='left')
    top10 = merged[['Symbol', 'Volatility']].dropna().sort_values(by='Volatility', ascending=False).head(10)

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(top10['Symbol'], top10['Volatility'], color='orange', edgecolor='black')
    ax.set_title("Top 10 Most Volatile Stocks")
    ax.set_ylabel("Volatility")
    ax.set_xlabel("Symbol")
    plt.xticks(rotation=45)
    st.pyplot(fig)

elif menu == "Top 5 Performing Stocks":
    st.subheader("🚀 Top 5 Performing Stocks (Cumulative Return)")
    df['prev_close'] = df.groupby('Ticker')['close'].shift(1)
    df['daily_return'] = (df['close'] - df['prev_close']) / df['prev_close']
    df.dropna(subset=['daily_return'], inplace=True)
    df['cumulative_return'] = df.groupby('Ticker')['daily_return'].transform(lambda x: (1 + x).cumprod() - 1)
    latest_returns = df.groupby('Ticker').apply(lambda x: x.sort_values('date').iloc[-1])[['Ticker', 'cumulative_return']]
    latest_returns = latest_returns.reset_index(drop=True)
    top5 = latest_returns.sort_values('cumulative_return', ascending=False).head(5)['Ticker'].tolist()

    fig, ax = plt.subplots(figsize=(12, 6))
    for ticker in top5:
        temp_df = df[df['Ticker'] == ticker]
        ax.plot(temp_df['date'], temp_df['cumulative_return'], label=ticker)
    ax.set_title("Cumulative Return Over Time")
    ax.set_xlabel("Date")
    ax.set_ylabel("Cumulative Return")
    ax.legend()
    ax.grid(True)
    st.pyplot(fig)

elif menu == "High, Low, Stable Sectors":
    st.subheader("📊 Sector Classification by Performance")
    first = df.groupby('Ticker').first()['close']
    last = df.groupby('Ticker').last()['close']
    yearly_return = ((last - first) / first).reset_index()
    yearly_return.columns = ['Ticker', 'Yearly_Return']
    sector_df = sector_df.rename(columns={'COMPANY': 'Ticker'})
    merged = pd.merge(yearly_return, sector_df, on='Ticker', how='left')
    sector_returns = merged.groupby('sector')['Yearly_Return'].mean().sort_values(ascending=False)

    high = sector_returns.idxmax()
    low = sector_returns.idxmin()
    stable = sector_returns.drop([high, low]).abs().idxmin()

    result_df = pd.DataFrame({
        'Sector': [high, low, stable],
        'Avg_Yearly_Return': [sector_returns[high], sector_returns[low], sector_returns[stable]],
        'Performance': ['High', 'Low', 'Stable']
    })

    color_map = {'High': 'green', 'Low': 'red', 'Stable': 'gray'}
    colors = result_df['Performance'].map(color_map)

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(result_df['Sector'], result_df['Avg_Yearly_Return'], color=colors, edgecolor='black')
    for i, val in enumerate(result_df['Avg_Yearly_Return']):
        ax.text(i, val, f"{val:.2%}", ha='center', va='bottom')
    ax.set_title("Sector Performance: High, Low, Stable")
    ax.set_ylabel("Average Yearly Return")
    ax.grid(axis='y')
    st.pyplot(fig)

elif menu == "Sector-wise Correlation Summary":
    st.subheader("🔁 Sector-wise Correlation (Strong Positive & Negative)")
    pivot_df = df.pivot(index='date', columns='Ticker', values='close')
    returns_df = pivot_df.pct_change().dropna()
    correlation_matrix = returns_df.corr()

    sector_df = sector_df.rename(columns={"COMPANY": "Ticker", "sector": "Sector"})
    ticker_sector_map = dict(zip(sector_df['Ticker'], sector_df['Sector']))
    from itertools import combinations
    summary = {}

    for t1, t2 in combinations(correlation_matrix.columns, 2):
        corr = correlation_matrix.loc[t1, t2]
        sector = ticker_sector_map.get(t1)
        if not sector: continue
        if sector not in summary:
            summary[sector] = {'Positive': 0, 'Negative': 0}
        if corr >= 0.5:
            summary[sector]['Positive'] += 1
        elif corr <= -0.5:
            summary[sector]['Negative'] += 1

    plot_df = pd.DataFrame.from_dict(summary, orient='index').reset_index().rename(columns={'index': 'Sector'})
    fig, ax = plt.subplots(figsize=(12, 6))
    plot_df.set_index('Sector')[['Positive', 'Negative']].plot(kind='bar', stacked=True, color=['green', 'red'], ax=ax)
    ax.set_title("Sector-wise Correlation Summary")
    ax.set_ylabel("Number of Strong Correlations")
    ax.grid(axis='y')
    st.pyplot(fig)

elif menu == "Monthly Gainers and Losers":
    st.subheader("📅 Monthly Top 5 Gainers and Losers")
    df['Month'] = df['date'].dt.to_period('M')
    first_close = df.groupby(['Ticker', 'Month']).first()['close']
    last_close = df.groupby(['Ticker', 'Month']).last()['close']
    monthly_return = ((last_close - first_close) / first_close).reset_index()
    monthly_return.columns = ['Ticker', 'Month', 'Monthly_Return']
    monthly_return['MonthDisplay'] = pd.to_datetime(monthly_return['Month'].astype(str)).dt.strftime('%b')

    months_order = monthly_return['Month'].sort_values().unique()
    fig, axs = plt.subplots(4, 3, figsize=(18, 14))
    plt.subplots_adjust(hspace=0.7)

    for idx, month in enumerate(months_order):
        ax = axs[idx // 3, idx % 3]
        data = monthly_return[monthly_return['Month'] == month]
        top5 = data.sort_values('Monthly_Return', ascending=False).head(5)
        bottom5 = data.sort_values('Monthly_Return').head(5)
        combined = pd.concat([top5, bottom5])
        colors = ['green'] * 5 + ['red'] * 5

        sns.barplot(x='Ticker', y='Monthly_Return', data=combined, palette=colors, ax=ax)
        ax.set_title(f"{calendar.month_name[month.month]}")
        ax.set_xticklabels(combined['Ticker'], rotation=35, ha='right', fontsize=8)
        ax.axhline(0, color='black', linestyle='--', linewidth=0.7)

    st.pyplot(fig)
