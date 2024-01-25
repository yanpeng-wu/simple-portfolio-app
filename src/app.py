#pip install yfinance
#pip install streamlit
#pip install PyPortfolioOpt
#>pip install plotly_express

#python -m streamlit run C:\Users\pengf\PycharmProjects\simple_portfolio_app\src\app.py

from datetime import datetime

import pandas as pd
import plotly.express as px
import streamlit as st

from app_data import get_price_return_data, get_stats, get_eqw_pf_returns, get_opt_pf_returns

st.write("""
## Simple Portfolio App
Compare the performance of the equal **weighted** and **optimized** portfolios
""")

#######################
# Container: User input
#######################
with st.container():
    st.write('---')
    st.write('#### User inputs')
    user_input = st.text_area(label='Enter a list of tickers (comma-separated):', height=None, max_chars=None, key=None)
    if user_input:
        tickers = user_input.split(',')
        tickers = [t.strip() for t in tickers]
    else:
        tickers = ['NVDA', 'AAPL', 'XOM', 'PFE', 'COST', 'MO', 'O', 'BAC', 'TSLA', 'MCD']
        st.write("Since no input, a default list is applied")

    sdate_col, edate_col = st.columns(2)
    with sdate_col:
        start_date = st.date_input("Start Date", datetime(2022, 1, 1))
    with edate_col:
        end_date = st.date_input("End Date", datetime(2024, 1, 24))

###########################################
# Load all historical price and return data
###########################################
df_price, df_return = get_price_return_data(tickers, start_date, end_date)

format_stats = {
    'N Days':         '{:,.0f}',
    'Cum Return':     '{:,.2%}',
    'Avg Dly Return': '{:,.2%}',
    'Ann Volatility': '{:,.2%}',
    'Sharpe Ratio':   '{:,.2f}',
    'Max Drawdown':   '{:,.2%}'
}

###################################
# Container: Ticker plots and stats
###################################
with st.container():
    st.write('---')
    st.write('#### Ticker')

    selected_tickers = st.multiselect('Show tickers', tickers, tickers, key='ticker')

    # Stock prices
    tkr_price_start_end = df_price.loc[df_price.index >= start_date.strftime('%Y-%m-%d')]
    st.plotly_chart(px.line(tkr_price_start_end[selected_tickers]), use_container_width=True)

    # Stock returns
    tkr_return_start_end = df_return.loc[df_return.index >= start_date.strftime('%Y-%m-%d')]
    tkr_cum_return_start_end = tkr_return_start_end.cumsum()
    st.plotly_chart(px.line(tkr_cum_return_start_end[selected_tickers]), use_container_width=True)

    # Stock stats
    tkr_stats = get_stats(tkr_return_start_end[selected_tickers])
    tkr_stats = tkr_stats.rename(columns={'index': 'Ticker'})
    tkr_stats.set_index(tkr_stats.columns[0], inplace=True)
    st.table(tkr_stats.style.format(format_stats))

######################################
# Container: Portfolio plots and stats
######################################
with st.container():
    st.write('---')
    st.write('#### Portfolio')

    returns_eqw_pf = get_eqw_pf_returns(df_return)
    returns_opt_pf, weights_opt_pf = get_opt_pf_returns(df_price, df_return)
    returns_pf = pd.DataFrame({'Equal Weight': returns_eqw_pf, 'Optimized': returns_opt_pf})

    returns_pf = returns_pf.loc[returns_pf.index >= start_date.strftime('%Y-%m-%d')]
    cum_returns_pf = returns_pf.cumsum()

    st.plotly_chart(px.line(cum_returns_pf), use_container_width=True)

    pf_stats = get_stats(returns_pf)
    pf_stats = pf_stats.rename(columns={'index': 'Portfolio'})
    pf_stats.set_index(pf_stats.columns[0], inplace=True)
    st.table(pf_stats.style.format(format_stats))

    #selected_tickers = st.multiselect('Show tickers', tickers, tickers, key='portfolio')

    # Daily weights
    weights_opt_pf = weights_opt_pf.loc[weights_opt_pf.index >= start_date.strftime('%Y-%m-%d')]
    st.plotly_chart(px.line(weights_opt_pf[selected_tickers]), use_container_width=True)

