
def max_drawdown(return_ts):
    cum_return_ts = (1 + return_ts).cumprod()[1:]
    high_watermarks = cum_return_ts.cummax()
    drawdowns = 1 - cum_return_ts.div(high_watermarks)
    max_drawdown = - max(drawdowns)
    return max_drawdown