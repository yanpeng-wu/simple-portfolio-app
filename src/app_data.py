import numpy as np
import pandas as pd
import yfinance as yfin
import streamlit as st
from datetime import datetime, timedelta
from app_utils import max_drawdown
from pypfopt.efficient_frontier import EfficientFrontier
from pypfopt import risk_models
from pypfopt import expected_returns

@st.cache_data
def get_hist_adj_close(tickers, start_date, end_date):
    start_date_rev = (start_date - timedelta(days=365)).strftime("%Y-%m-%d")
    end_date = end_date.strftime("%Y-%m-%d")

    data = yfin.download(tickers=tickers, start=start_date_rev, end=end_date, group_by='ticker')

    df = pd.DataFrame()
    for tkr in tickers:
        df[tkr] = data[tkr]['Adj Close']

    return df

@st.cache_data
def get_price_return_data(tickers, start_date, end_date):
    df_price = get_hist_adj_close(tickers, start_date, end_date)
    df_return = df_price.pct_change()
    return df_price, df_return

@st.cache_data
def get_stats(df_return):
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


# Equal weight
@st.cache_data
def get_eqw_pf_returns(df_return):
    return df_return.mean(axis=1)[252:]

# Optimal
@st.cache_data
def get_opt_weights(df_price):
    mu = expected_returns.mean_historical_return(df_price)
    S = risk_models.sample_cov(df_price)

    # optimize for max sharpe ratio
    ef = EfficientFrontier(mu, S)
    weights = ef.max_sharpe()
    cleaned_weights = ef.clean_weights()

    wt = pd.DataFrame(list(cleaned_weights.items()), columns=['Ticker', 'Weight'])
    wt.set_index('Ticker', drop=True, inplace=True)

    return wt

@st.cache_data
def get_opt_pf_returns(df_price, df_return):
    returns_opt_pf, weights_opt_pf = pd.DataFrame(), pd.DataFrame()

    for i in range(252, len(df_price)):
        wt = get_opt_weights(df_price.iloc[i-252:i])
        rt = df_return.iloc[i].to_frame('Return')
        tmp = wt.join(rt, how='left')
        pf_return = pd.DataFrame({'Return': [sum(tmp['Weight'] * tmp['Return'])]}, index=[df_return.iloc[i].name])
        returns_opt_pf = pd.concat([returns_opt_pf, pf_return])
        weights_opt_pf = pd.concat([weights_opt_pf, wt.unstack().unstack()])

    return returns_opt_pf['Return'], weights_opt_pf







