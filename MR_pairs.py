import pandas as pd
import matplotlib.pyplot as plt
import datetime as dt
import numpy as np

def download_stock_data(ticker,timestamp_start,timestamp_end):
    url=f"https://query1.finance.yahoo.com/v7/finance/download/{ticker}?period1={timestamp_start}&period2={timestamp_end}&interval\
=1d&events=history&includeAdjustedClose=true"
    df = pd.read_csv(url)
    return df

# set time period to use
datetime_start=dt.datetime(2022, 2, 8, 7, 35, 51)
datetime_end=dt.datetime.today()
timestamp_start=int(datetime_start.timestamp()) 
timestamp_end=int(datetime_end.timestamp()) 

# load data
tickers=['BRK-B','MSFT']
df_global=pd.DataFrame()
for ticker in tickers:
    df_temp = download_stock_data(ticker,timestamp_start,timestamp_end)[['Date','Adj Close']]
    df_temp = df_temp.set_index('Date')
    df_temp.columns=[ticker]
    df_global=pd.concat((df_global, df_temp),axis=1)
df_global.head()

# get spread between two stocks:
ticker_long = tickers[0]
ticker_short = tickers[1]
spread = df_global[ticker_long] - df_global[ticker_short]

# get rolling mean and sd of spread
window = 20
n_std = 1.5
rolling_mean = spread.rolling(window=window).mean()
rolling_std = spread.rolling(window=window).std()

# get z-score of spread and lower and upper bands
zscore = (spread - rolling_mean) / rolling_std
upper_band = rolling_mean + n_std * rolling_std
lower_band = rolling_mean - n_std * rolling_std

# plot stock prices and spread
figs=(8,4)
plt.figure(figsize = figs)
spread.plot(label='Spread = '+ticker_long+' - '+ ticker_short,linestyle='--')
df_global[ticker_long].plot(label=ticker_long+'_price')
df_global[ticker_short].plot(label=ticker_short+'_price')
plt.title("Spread and Prices of {0} and {1}".format(ticker_long,ticker_short))
plt.legend()
plt.show()

# plot lower and upper bands with spread and ma
plt.figure(figsize = figs)
upper_band.plot(label='Upper_band')
lower_band.plot(label='Lower_band')
spread.plot(label = 'Spread = '+ticker_long+' - '+ ticker_short,linestyle='--', color='r')
rolling_mean.plot(label = 'ma_30days_spread', linestyle = '-.')
plt.fill_between(df_global.index,lower_band, upper_band, alpha=0.2)
plt.legend()
plt.show()

# enter long position if z-score is less than -n_std
# enter short position if z-score is greater than n_std
signal = np.where(zscore < -n_std, 1, np.where(zscore > n_std, -1, 0))
signal = pd.Series(signal, index=df_global.index)

# get daily returns
returns = df_global[ticker_long].pct_change() - df_global[ticker_short].pct_change()

# get strategy returns
strategy_returns = signal.shift(1) * returns

# get and plot cumulative returns
cumulative_returns = (1 + strategy_returns).cumprod()
cumulative_returns.plot(figsize = figs)
plt.title("Cumulative Return with n_std={0}".format(n_std))
plt.show()