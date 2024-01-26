This repo includes the python code for building a web app that serves as a demonstration of how to retrieve
historical stock data via the Yahoo Finance API. Users can input a list of stock tickers, or use a default
ten-stock list. The app then plots the price and cumulative return time series for each ticker, providing a
statistical summary for each.

Furthermore, the app constructs two portfolios: an **equal-weighted** portfolio and an **optimal**
portfolio. The **optimal** portfolio is generated using the PyPortfolioOpt library with a max_sharpe
objective. A backtest of their performance is conducted, and a statistical summary of the backtest
results is provided.

### Code Structure
```bash
simple_portfolio_app             Project Name
    |_src                            Source Directory
        |_app.py                         The entry point and the main body of this app. 
        |_app_data.py                    The collection of helper fuctions for retrieving data.
        |_app_utils.py                   The utility functions
    |_test                           Unit Test Directory
        |_test_app_utils.py              Unit test files for app_utils.py
```

### Python Packages
There are specifically 3 python packages are used for this app: 
1) Yahoo! Finance's API (https://pypi.org/project/yfinance/)
Undoubtedly, it can be said that this is one of the most popular open-source libraries efficiently downloading market data from Yahoo Finance.

2) PyPortfolioOpt (https://pypi.org/project/pyportfolioopt/)
It's a user-friendly library that implements various portfolio optimization methods.

3) Streamlit (https://streamlit.io/)
It's a lightweight yet powerful tool designed to streamline the rapid development and seamless sharing of data applications.

   
Please follow the steps below to clone, install required packages and start running and enjoying this app.

### Clone
Clone this repo to your local machine using https://github.com/yanpeng-wu/simple_portfolio_app/

### Install Package Requirements
To install the required python packages, enter your local directory for the above clone and run the following command:
```bash
pip install -r requirements.txt
```

### Start the App!
To start the web app, run:
```bash
python -m streamlit run [YOUR_LOCAL_PATH_OF_PROJECT]\src\app.py
```
Once you see the following lines, it should pop your browser and launch the home page of this app!
```bash
C:\Windows\System32>python -m streamlit run C:\Users\pengf\PycharmProjects\simple_portfolio_app\src\app.py

  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.1.30:8501
```
