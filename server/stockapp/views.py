from rest_framework.decorators import api_view
from rest_framework.response import Response
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import statsmodels.tsa.stattools as ts 
from statsmodels.tsa.stattools import adfuller
import datetime as dt
import numpy as np
import seaborn as sns
import io
import base64

matplotlib.use('Agg')
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = 'Helvetica'

def plot_to_base64(plt_figure, dpi=150):
    """Converts a matplotlib plot to a base64 encoded string."""
    buffer = io.BytesIO()
    plt_figure.savefig(buffer, format='png', dpi=dpi)
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    return base64.b64encode(image_png).decode('utf-8')

def download_stock_data(ticker,start_date_str,end_date_str):
    try:
        datetime_start = dt.datetime.strptime(start_date_str, '%Y-%m-%d')
    except ValueError:
        datetime_start = dt.datetime(2022, 1, 8, 7, 35, 51) 

    try:
        datetime_end = dt.datetime.strptime(end_date_str, '%Y-%m-%d')
    except ValueError:
        datetime_end = dt.datetime.today() - dt.timedelta(days=365)

    # Convert datetime objects to timestamps
    timestamp_start = int(datetime_start.timestamp())
    timestamp_end = int(datetime_end.timestamp())
    url=f"https://query1.finance.yahoo.com/v7/finance/download/{ticker}?period1={timestamp_start}&period2={timestamp_end}&interval\=1d&events=history&includeAdjustedClose=true"
    df = pd.read_csv(url)
    return df

def coint_testing(df_stocks, ticker_long, ticker_short):
    result = ts.coint(df_stocks[ticker_long], df_stocks[ticker_short])
    coint_p = result[1]
    adf_p = adfuller(df_stocks[ticker_long] - df_stocks[ticker_short])[1]
    return coint_p, adf_p

def plot_stock_prices(df_stocks, ticker_long, ticker_short):
    plt.figure(figsize = (10, 6))
    df_stocks[ticker_long].plot(label=ticker_long+' Price')
    df_stocks[ticker_short].plot(label=ticker_short+' Price')
    plt.title("Prices of {0} and {1}".format(ticker_long,ticker_short))
    plt.legend()
    return plot_to_base64(plt)

def plot_spread(df_stocks, ticker_long, ticker_short):
    spread = df_stocks[ticker_long] - df_stocks[ticker_short]
    plt.figure(figsize = (8,5))
    spread.plot(label='Spread = '+ticker_long+' - '+ ticker_short,linestyle='--')
    plt.title("Spread of Prices")
    plt.legend()
    return plot_to_base64(plt)

def plot_ratio_static(ratio, ticker_long, ticker_short, n_std, ratio_mean, ratio_std):
    plt.figure(figsize = (8,5))
    ratio.plot(label='Ratio = '+ticker_long+' / '+ ticker_short,linestyle='-')
    plt.axhline(ratio_mean - n_std * ratio_std, color='green')
    plt.axhline(ratio_mean + n_std * ratio_std, color='green')
    plt.axhline(ratio_mean, color='red')
    plt.title("Price Ratio of " + ticker_long + " and " + ticker_short + " (Static)")
    plt.legend()
    return plot_to_base64(plt)

def plot_ratio_bollinger(df_stocks, ratio, ticker_long, ticker_short, n_std, ratio_rolling_mean, ratio_rolling_std, window):
    upper_band = ratio_rolling_mean + n_std * ratio_rolling_std
    lower_band = ratio_rolling_mean - n_std * ratio_rolling_std
    plt.figure(figsize = (8,5))
    upper_band.plot(label='Upper_band')
    lower_band.plot(label='Lower_band')
    ratio.plot(label = 'Ratio = '+ticker_long+' - '+ ticker_short,linestyle='--', color='r')
    ratio_rolling_mean.plot(label = 'Price Ratio ' + str(window) + '-day MA', linestyle = '-.')
    plt.fill_between(df_stocks.index,lower_band, upper_band, alpha=0.2)
    plt.title("Price Ratio of " + ticker_long + " and " + ticker_short + " (Bands)")
    plt.legend()
    return plot_to_base64(plt)

def plot_returns(df_stocks, ticker_long, ticker_short, zscore, n_std, method):
    # enter long position if z-score is less than -n_std
    # enter short position if z-score is greater than n_std
    signal = np.where(zscore < -n_std, 1, np.where(zscore > n_std, -1, 0))
    signal = pd.Series(signal, index=df_stocks.index)

    # get and plot cumulative returns
    returns = df_stocks[ticker_long].pct_change() - df_stocks[ticker_short].pct_change()
    strategy_returns = signal.shift(1) * returns
    cumulative_returns = (1 + strategy_returns).cumprod()
    plt.figure(figsize=(8,5))
    cumulative_returns.plot()
    plt.title("Cumulative Returns ({0})".format(method))
    return plot_to_base64(plt) 
    
def plot_stock_prices_with_signals(df_stocks, ticker_long, ticker_short, zscore, n_std):
    plt.figure(figsize=(10, 6))

    # Plot the stock prices
    df_stocks[ticker_long].plot(label=ticker_long + ' Price')
    df_stocks[ticker_short].plot(label=ticker_short + ' Price')

    # Identify and plot buy signals (z-score < -n_std)
    buy_long = df_stocks[ticker_long].copy()
    sell_long = df_stocks[ticker_long].copy()
    buy_long[zscore>-n_std] = np.nan
    sell_long[zscore<n_std] = np.nan
    buy_long.plot(color='g', linestyle='None', marker='^', label="_nolegend_")
    sell_long.plot(color='r', linestyle='None', marker='v', label="_nolegend_")

    buy_short = df_stocks[ticker_short].copy()
    sell_short = df_stocks[ticker_short].copy()
    buy_short[zscore<n_std] = np.nan
    sell_short[zscore>-n_std] = np.nan
    buy_short.plot(color='g', linestyle='None', marker='^', label="_nolegend_")
    sell_short.plot(color='r', linestyle='None', marker='v', label="_nolegend_")

    plt.title("Prices of {0} and {1} with Buy/Sell Signals".format(ticker_long, ticker_short))
    plt.legend()

    return plot_to_base64(plt)

@api_view(['POST'])
def stock_api(request):
    # plot formatting
    figs=(8,4.5)
    plt.figure(figsize = figs)

    # process data
    ticker_long = request.data.get('ticker1') or 'AAPL' 
    ticker_short = request.data.get('ticker2') or 'MSFT' 
    start_date_str = request.data.get('startDate')
    end_date_str = request.data.get('endDate')
    window = request.data.get('window') or 20
    n_std = request.data.get('std') or 2

    df_stocks = pd.DataFrame()
    for ticker in [ticker_long, ticker_short]:
        df_temp = download_stock_data(ticker, start_date_str, end_date_str)[['Date', 'Adj Close']]
        df_temp = df_temp.set_index('Date')
        df_temp.columns = [ticker]
        df_stocks = pd.concat((df_stocks, df_temp), axis=1)

    # cointegration and adfuller testing
    coint_p, adf_p = coint_testing(df_stocks, ticker_long, ticker_short)
    print('P value for the augmented Engle-Granger two-step cointegration test is', coint_p)
    print('P value for the Augmented Dickey-Fuller Test is', adf_p)

    ratio = df_stocks[ticker_long] / df_stocks[ticker_short]
    zscore = (ratio - ratio.mean()) / ratio.std()
    ratio_mean = ratio.mean()
    ratio_std = ratio.std()
    
    ratio_rolling_mean = ratio.rolling(window=window).mean()
    ratio_rolling_std = ratio.rolling(window=window).std()
    rolling_zscore = (ratio - ratio_rolling_mean) / ratio_rolling_std

    # plot stock prices
    prices_base64 = plot_stock_prices(df_stocks, ticker_long, ticker_short)

    # plot ratio with static
    static_base64 = plot_ratio_static(ratio, ticker_long, ticker_short, n_std, ratio_mean, ratio_std)

    # plot ratio with bands
    bands_base64 = plot_ratio_bollinger(df_stocks, ratio, ticker_long, ticker_short, n_std, ratio_rolling_mean, ratio_rolling_std, window)

    # plot static returns
    static_returns_base64 = plot_returns(df_stocks, ticker_long, ticker_short, zscore, n_std, "Static")

    # plot bands returns
    bands_returns_base64 = plot_returns(df_stocks, ticker_long, ticker_short, rolling_zscore, n_std, "Bands")

    # plot prices with buy and sell signals
    prices_signals_base64 = plot_stock_prices_with_signals(df_stocks, ticker_long, ticker_short, zscore, n_std)
    plt.close()

    return Response({'coint_p': coint_p, 'adf_p': adf_p, 'prices': prices_base64, 'static': static_base64, 'bands': bands_base64, 'static_returns': static_returns_base64, 'bands_returns': bands_returns_base64, 'prices_signals': prices_signals_base64})