import pandas as pd 
import datetime as dt
import matplotlib.pyplot as plt
import numpy as np

def download_stock_data(ticker,timestamp_start,timestamp_end):
    url=f"https://query1.finance.yahoo.com/v7/finance/download/{ticker}?period1={timestamp_start}&period2={timestamp_end}&interval\
=1d&events=history&includeAdjustedClose=true"
    df = pd.read_csv(url)
    return df

# set time period to use
datetime_start=dt.datetime(2022, 1, 1, 7, 35, 51)
datetime_end=dt.datetime.today()
timestamp_start=int(datetime_start.timestamp()) 
timestamp_end=int(datetime_end.timestamp()) 

# load data
ticker='AAPL'
df = download_stock_data(ticker,timestamp_start,timestamp_end)
df = df.set_index('Date')
df.head()

# get moving average of past 20 days
window = 20
df["ma_20"] = df["Adj Close"].rolling(window=window).mean()

# set signal as -1 if price above ma, and vice versa
df["diff"] = df["Adj Close"] - df["ma_20"]
df['signal'] = np.where(df["diff"] > 0, -1, 1)

# plot moving average
figs=(8,4)
df[['Adj Close',"ma_20"]].plot(figsize=figs)
plt.title("Mean Reversion")
plt.show()

# plot diff with (amplified) signal 
df['diff'].plot(figsize=figs)
(10*df['signal']).plot(figsize=figs, linestyle='--') 
plt.title("Diff vs Signal")
plt.legend()
plt.show()

# plot ratio of price to ma
(df["Adj Close"]/df["ma_20"] ).plot(figsize=figs)
plt.title("Ratio=Close/ma_20")
plt.show()

# calculate the daily returns
df['returns'] = df['Adj Close'].pct_change()

# calculate the strategy returns
df['strategy_returns'] = df['signal'] .shift(1) * df['returns']

# calculate the cumulative returns
df=df.dropna()
df['cumulative_returns'] = (1 + df['strategy_returns']).cumprod()

# plot the cumulative returns
figs = (8,4)
df['cumulative_returns'].plot(figsize = figs)
plt.title("Cumulative Return")
plt.show()