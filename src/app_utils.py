
def max_drawdown(return_ts):
    """
    Helper function to calculate the maximum drawdown for the given price return timeseries.

    Parameters:
      - return_ts (Series): The daily close-to-close return time series for a single stock.

    Returns:
      - max_drawdown (float): The maximum drawdown within the time horizon of input series.
    """
    cum_return_ts = (1 + return_ts).cumprod()[1:]
    high_watermarks = cum_return_ts.cummax()
    drawdowns = 1 - cum_return_ts.div(high_watermarks)
    max_drawdown = - max(drawdowns)

    return max_drawdown