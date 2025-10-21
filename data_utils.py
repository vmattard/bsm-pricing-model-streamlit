from datetime import date
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd
import yfinance as yf

from black_scholes_merton import BlackScholesMerton
from enums import OptionType


def round_value(value: Optional[float], precision: int = 4) -> Optional[float]:
    """Rounds a float to a given precision, returning None if the input is None."""
    return round(value, precision) if value is not None else value


def get_stock_metadata(ticker: str) -> Dict[str, Any]:
    stock = yf.Ticker(ticker)
    metadata = {
        "spotPrice": stock.info.get("regularMarketPrice", 0) or 0,
        "dividendYield": stock.info.get("dividendYield", 0) or 0,
    }
    return metadata


def get_option_chains(ticker: str, target_date: date) -> Dict[OptionType, pd.DataFrame]:
    try:
        stock = yf.Ticker(ticker)
        chain = stock.option_chain(date=target_date.isoformat())
        return {OptionType.CALL: chain.calls, OptionType.PUT: chain.puts}
    except ValueError:
        return {OptionType.CALL: pd.DataFrame(), OptionType.PUT: pd.DataFrame()}


def get_option_expiration_dates(ticker: str) -> List[date]:
    stock = yf.Ticker(ticker)
    return [date.fromisoformat(dt) for dt in stock.options]


def process_option_chains(
    chains: Dict[OptionType, pd.DataFrame],
    expiration_date: date,
    stock_metadata: Dict[str, Any],
) -> pd.DataFrame:
    target_columns = [
        "contractSymbol",
        "strike",
        "bid",
        "ask",
        "impliedVolatility",
        "spread",
        "inTheMoney",
        "price",
        "delta",
    ]

    S = stock_metadata.get("spotPrice")
    t = (abs(expiration_date - date.today())).days / 365
    r = 4.25 / 100  # risk free rate
    q = stock_metadata.get("dividendYield") / 100

    calls = chains[OptionType.CALL].copy()
    puts = chains[OptionType.PUT].copy()

    for col in ["price", "delta", "gamma", "vega", "theta", "rho"]:
        calls[col] = np.nan
        puts[col] = np.nan

    for idx, c_row in calls.iterrows():
        bsm_model = BlackScholesMerton(
            S=S, K=c_row["strike"], t=t, r=r, sigma=c_row["impliedVolatility"], q=q
        )
        data_call = bsm_model.call()
        calls.loc[idx, data_call.keys()] = data_call.values()

    calls["spread"] = calls["ask"] - calls["bid"]

    for idx, p_row in puts.iterrows():
        bsm_model = BlackScholesMerton(
            S=S, K=p_row["strike"], t=t, r=r, sigma=p_row["impliedVolatility"], q=q
        )
        data_put = bsm_model.put()
        puts.loc[idx, data_put.keys()] = data_put.values()

    puts["spread"] = puts["ask"] - puts["bid"]

    calls_final = calls.reindex(columns=target_columns)
    puts_final = puts.reindex(columns=target_columns)

    return calls_final.merge(
        puts_final, how="outer", on="strike", suffixes=("_call", "_put")
    )
