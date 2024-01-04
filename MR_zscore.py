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
datetime_start=dt.datetime(2023, 1, 1, 7, 35, 51)
datetime_end=dt.datetime.today()
timestamp_start=int(datetime_start.timestamp()) 
timestamp_end=int(datetime_end.timestamp()) 

# load data
ticker='MSFT'
df = download_stock_data(ticker,timestamp_start,timestamp_end)
df = df.set_index('Date')
df.head()

# get 20-day moving average
window=60
df['ma_20'] = df['Adj Close'].rolling(window=window).mean()

# get sd of 20-day ma and z-score of price
df['std_20']  = df['Adj Close'].rolling(window=window).std()
df['zscore']  = (df['Adj Close'] - df['ma_20']) / df['std_20'] 

# buy if z-score less than n_std, sell if z-score is more than n_std
# hold if between -1 and 1
n_std=1.5
df['signal'] = np.where(df['zscore'] < -n_std, 1, np.where(df['zscore'] > n_std, -1, 0))

# plot z-score and signal
figs=(8,4)
df['signal'].plot(figsize=figs, linestyle="--")   
df['zscore'].plot(figsize=figs)          
plt.title("Mean Reversion with z-score")
plt.legend()
plt.show()

# set lower and upper bands according to n_std
upper_band=df['ma_20']+n_std*df['std_20']
lower_band=df['ma_20']-n_std*df['std_20']

# plot price and bands, buy when below lower band and selll when above upper band
figs=(10,6)
df['Adj Close'].plot(figsize=figs)
df['ma_20'].plot(figsize=figs,linestyle='-.', color="w")
upper_band.plot(linestyle='--',label='upper_band')
lower_band.plot(linestyle=':',label='lower_band')
plt.fill_between(df.index,lower_band, upper_band, alpha=0.3)
plt.title("Upper and Lower Band")
plt.legend()
plt.show()

# calculate daily returns
df['returns'] = df['Adj Close'].pct_change()

# calculate strategy returns
df['strategy_returns'] = df['signal'].shift(1) * df['returns']

# calculate cumulative returns
df=df.dropna()
df['cumulative_returns'] = (1 + df['strategy_returns']).cumprod()

# plot the cumulative returns
df['cumulative_returns'].plot(figsize=figs)
plt.title ("Cumulative Return")
plt.show()