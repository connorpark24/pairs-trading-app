from rest_framework.decorators import api_view
from rest_framework.response import Response
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import datetime as dt
import numpy as np
import seaborn as sns
import io
import base64

matplotlib.use('Agg')
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = 'Helvetica'

@api_view(['POST'])
def stock_api(request):
    ticker1 = request.data.get('ticker1') or 'AAPL' 
    ticker2 = request.data.get('ticker2') or 'MSFT' 

    datetime_start=dt.datetime(2022, 1, 8, 7, 35, 51)
    datetime_end=dt.datetime.today()    
    timestamp_start=int(datetime_start.timestamp()) 
    timestamp_end=int(datetime_end.timestamp()) 

    def download_stock_data(ticker,timestamp_start,timestamp_end):
        url=f"https://query1.finance.yahoo.com/v7/finance/download/{ticker}?period1={timestamp_start}&period2={timestamp_end}&interval\=1d&events=history&includeAdjustedClose=true"
        df = pd.read_csv(url)
        return df

    def find_most_correlated_stocks(df):
        corr_matrix = df.corr()
        corr_matrix = corr_matrix.unstack()
        sorted_corr = corr_matrix.sort_values(kind="quicksort", ascending=False)
        most_correlated_pair = sorted_corr.index[sorted_corr != 1][0]
        return most_correlated_pair
    
    def plot_to_base64(plt_figure, dpi=150):
        """Converts a matplotlib plot to a base64 encoded string."""
        buffer = io.BytesIO()
        plt_figure.savefig(buffer, format='png', dpi=dpi)
        buffer.seek(0)
        image_png = buffer.getvalue()
        buffer.close()
        return base64.b64encode(image_png).decode('utf-8')

    tickers = [
    "AAPL",
    "MSFT",
    "AMZN",
    "NVDA",
    "GOOGL",
    "META",
    "TSLA",
    "BRK-B",
    "AVGO",
    "UNH",
    "JPM",
    "LLY",
    "V",
    "XOM",
    "JNJ",
    "HD",
    "MA",
    "PG",
    "COST",
    "ABBV",
    "MRK",
    "ADBE",
    "CVX",
    "CRM"
    ]

    df_global = pd.DataFrame()
    for ticker in tickers:
        df_temp = download_stock_data(ticker, timestamp_start, timestamp_end)[['Date', 'Adj Close']]
        df_temp = df_temp.set_index('Date')
        df_temp.columns = [ticker]
        df_global = pd.concat((df_global, df_temp), axis=1)

    # show correlation heatmap
    corr = df_global.corr()
    plt.figure(figsize=(16, 7))
    sns.heatmap(corr, annot=True, cmap='coolwarm', fmt=".2f", linewidths=.5)
    plt.title('Correlation Matrix Heatmap of Selected Stocks')
    heatmap_base64 = plot_to_base64(plt)

    # Find the two most correlated stocks
    # ticker_long, ticker_short = find_most_correlated_stocks(df_global)
    ticker_long = ticker1
    ticker_short = ticker2

    # get spread between two stocks:
    spread = df_global[ticker_long] - df_global[ticker_short]

    # get rolling mean and sd of spread
    window = 20
    n_std = 1.75
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
    spread_base64 = plot_to_base64(plt)

    # plot lower and upper bands with spread and ma
    plt.figure(figsize = figs)
    upper_band.plot(label='Upper_band')
    lower_band.plot(label='Lower_band')
    spread.plot(label = 'Spread = '+ticker_long+' - '+ ticker_short,linestyle='--', color='r')
    rolling_mean.plot(label = 'ma_30days_spread', linestyle = '-.')
    plt.fill_between(df_global.index,lower_band, upper_band, alpha=0.2)
    plt.legend()
    bands_base64 = plot_to_base64(plt)

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
    plt.figure(figsize=figs)  # Start a new figure
    cumulative_returns.plot()
    plt.title("Cumulative Return with n_std={0}".format(n_std))
    returns_base64 = plot_to_base64(plt)  # Encode the plot
    plt.close()  # Close the plot context

    return Response({'heatmap': heatmap_base64, 'spread': spread_base64, 'bands': bands_base64, 'returns': returns_base64})