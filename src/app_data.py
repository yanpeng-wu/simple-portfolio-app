from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import streamlit as st
import yfinance as yfin
from pypfopt import expected_returns
from pypfopt import risk_models
from pypfopt.efficient_frontier import EfficientFrontier

from app_utils import max_drawdown


@st.cache_data
def get_hist_adj_close(tickers: list, start_date: datetime, end_date: datetime):
    """
    Helper function to retrieve adjusted close price for the given tickers and the date range.

    Parameters:
      - tickers (list): A list of stock tickers.
      - start_date (datetime): Start date of the requested date range.
      - end_date (datetime): End date of the requested date range.

    Returns:
      - DataFrame: columns are the adj close time series for each ticker.

    Example:
      ```python
        df = get_hist_adj_close(tickers=['AAPL','IBM'], start_date=datetime(2024,1,1), end_date=datetime(2024,1,25))
      ```
    """
    start_date_rev = (start_date - timedelta(days=365)).strftime("%Y-%m-%d")
    end_date = end_date.strftime("%Y-%m-%d")

    data = yfin.download(tickers=tickers, start=start_date_rev, end=end_date, group_by='ticker')

    df = pd.DataFrame()
    for tkr in tickers:
        df[tkr] = data[tkr]['Adj Close']

    return df

@st.cache_data
def get_price_return_data(tickers, start_date, end_date):
    """
    Helper function to retrieve both adjusted close price and close-to-close price returns for the
    given tickers and the date range.

    Parameters:
      - tickers (list): A list of stock tickers.
      - start_date (datetime): Start date of the requested date range.
      - end_date (datetime): End date of the requested date range.

    Returns:
      - df_price (DataFrame): columns are the adj close time series for each ticker.
      - df_return (DataFrame): columns are the close-to-close return time series for each ticker.

    Example:
      ```python
        df_px, df_rt = get_price_return_data(tickers=['AAPL','IBM'], start_date=datetime(2024,1,1), end_date=datetime(2024,1,25))
      ```
    """
    df_price = get_hist_adj_close(tickers, start_date, end_date)
    df_return = df_price.pct_change()

    return df_price, df_return

@st.cache_data
def get_stats(df_return):
    """
    Helper function to generate a statistical summary of the backtest results.

    Parameters:
      - df_return (DataFrame): The daily close-to-close return time series data frame returned from get_price_return_data().

    Returns:
      - stats (DataFrame): The statistical summary of the daily returns for either individual stock or a portfolio.

    Example:
      ```python
        df_stats = get_stats(df_rt)
      ```
    """
    stats = df_return.agg(['count', 'sum', 'mean', 'std', max_drawdown]).transpose()
    stats = stats.reset_index().rename(columns={
        'count': 'N Days',
        'sum': 'Cum Return',
        'mean': 'Avg Dly Return',
        'std': 'Stdev',
        'max_drawdown': 'Max Drawdown'
    })
    stats['Ann Volatility'] = stats['Stdev'] * np.sqrt(252)
    stats['Sharpe Ratio'] = stats['Avg Dly Return'] * 252 / stats['Ann Volatility']
    stats = stats[['index', 'N Days', 'Cum Return', 'Avg Dly Return', 'Ann Volatility', 'Sharpe Ratio', 'Max Drawdown']]

    return stats

@st.cache_data
def get_eqw_pf_returns(df_return):
    """
    Helper function to calculate the daily return for an equal-weight portfolio.

    Parameters:
      - df_return (DataFrame): The daily close-to-close return time series data frame returned from get_price_return_data().

    Returns:
      - DataFrame: The portfolio daily return time series.

    Example:
      ```python
        return_eqw_pf = get_eqw_pf_returns(df_rt)
      ```
    """
    return df_return.mean(axis=1)[252:]

@st.cache_data
def get_opt_weights(df_price):
    """
    Helper function to get the daily weight of stocks in the optimal portfolio. The optimal portfolio is generated
    using the PyPortfolioOpt library with a max_sharpe objective.

    Parameters:
      - df_price (DataFrame): The daily adj-close time series data frame returned from get_price_return_data().

    Returns:
      - wt (Series): The weights of stocks for "current" date of optimization.

    Example:
      ```python
        wt = get_opt_weights(df_px)
      ```
    """
    mu = expected_returns.mean_historical_return(df_price)
    cov_mx = risk_models.sample_cov(df_price)

    # optimize for max sharpe ratio
    ef = EfficientFrontier(mu, cov_mx)
    weights = ef.max_sharpe()

    wt = pd.DataFrame(list(weights.items()), columns=['Ticker', 'Weight'])
    wt.set_index('Ticker', drop=True, inplace=True)

    return wt

@st.cache_data
def get_opt_pf_returns(df_price, df_return):
    """
    Helper function to calculate the daily return for an optimal portfolio.

    Parameters:
      - df_price (DataFrame): The daily adj-close time series data frame returned from get_price_return_data().
      - df_return (DataFrame): The daily close-to-close return time series data frame returned from get_price_return_data().

    Returns:
      - returns_opt_pf (DataFrame): The optimal portfolio daily return time series.
      - weights_opt_pf (DataFrame): The daily weights of the stocks in the optimal portfolio.

    Example:
      ```python
        return_opt_pf, weight_opt_pf = get_opt_pf_returns(df_px, df_rt)
      ```
    """
    returns_opt_pf, weights_opt_pf = pd.DataFrame(), pd.DataFrame()

    # Use the trailing 1 year data for mean return and covariance matrix calculations, hence 252 (days)
    for i in range(252, len(df_price)):
        prices = df_price.iloc[i - 252:i]
        wt = get_opt_weights(prices)
        rt = df_return.iloc[i].to_frame('Return')

        wt_rt = wt.join(rt, how='left')
        pf_return = pd.DataFrame({'Return': [sum(wt_rt['Weight'] * wt_rt['Return'])]}, index=[df_return.iloc[i].name])
        returns_opt_pf = pd.concat([returns_opt_pf, pf_return])

        wt = wt.transpose()
        wt['Date'] = prices.index[-1]
        wt.set_index('Date', inplace=True)
        weights_opt_pf = pd.concat([weights_opt_pf, wt])

    return returns_opt_pf['Return'], weights_opt_pf




