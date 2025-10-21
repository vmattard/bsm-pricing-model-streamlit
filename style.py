from typing import Any, Dict

import pandas as pd
import streamlit as st
from matplotlib.colors import LinearSegmentedColormap
from pandas.io.formats.style import Styler

# This creates a gradient from transparent to a translucent light green
light_green_cmap = LinearSegmentedColormap.from_list(
    "light_green",
    ["#ffffff00", "#90ee90"],  # Hex codes for transparent -> light green
    N=256,
)

# This creates a gradient from transparent to a translucent light red
light_red_cmap = LinearSegmentedColormap.from_list(
    "light_red",
    ["#ffffff00", "#f08080"],  # Hex codes for transparent -> light coral/red
    N=256,
)


def style_option_chain(df: pd.DataFrame) -> Styler:
    """
    Styles an options chain DataFrame, including price and delta columns, for display in Streamlit.

    Returns:
        A pandas Styler object with the applied styles.
    """

    column_order = [
        "contractSymbol_call",
        "price_call",
        "bid_call",
        "ask_call",
        "spread_call",
        "impliedVolatility_call",
        "delta_call",
        "inTheMoney_call",
        "strike",
        "contractSymbol_put",
        "price_put",
        "bid_put",
        "ask_put",
        "spread_put",
        "impliedVolatility_put",
        "delta_put",
        "inTheMoney_put",
    ]

    rename_map = {
        "contractSymbol_call": "Call Symbol",
        "price_call": "Call Price",
        "bid_call": "Call Bid",
        "ask_call": "Call Ask",
        "spread_call": "Call Spread",
        "impliedVolatility_call": "Call IV",
        "delta_call": "Call Δ",
        "inTheMoney_call": "ITM Call",
        "strike": "Strike",
        "contractSymbol_put": "Put Symbol",
        "price_put": "Put Price",
        "bid_put": "Put Bid",
        "ask_put": "Put Ask",
        "spread_put": "Put Spread",
        "impliedVolatility_put": "Put IV",
        "delta_put": "Put Δ",
        "inTheMoney_put": "ITM Put",
    }

    df_styled = df.copy().reindex(columns=column_order).rename(columns=rename_map)

    def highlight_itm(row):
        style = [""] * len(row)
        if row.get("ITM Call"):
            style[0:7] = ["background-color: rgba(144, 238, 144, 0.5)"] * 7
        if row.get("ITM Put"):
            style[9:16] = ["background-color: rgba(173, 216, 230, 0.5)"] * 7
        return style

    call_cols = [
        "Call Symbol",
        "Call Price",
        "Call Bid",
        "Call Ask",
        "Call Spread",
        "Call IV",
        "Call Δ",
    ]
    put_cols = [
        "Put Symbol",
        "Put Price",
        "Put Bid",
        "Put Ask",
        "Put Spread",
        "Put IV",
        "Put Δ",
    ]

    return (
        df_styled.style.set_properties(
            subset=call_cols, **{"background-color": "rgba(144, 238, 144, 0.2)"}
        )
        .set_properties(
            subset=put_cols, **{"background-color": "rgba(173, 216, 230, 0.2)"}
        )
        .set_properties(subset=["Strike"], **{"font-weight": "bold"})
        .apply(highlight_itm, axis=1)
        .format(
            {
                "Call Price": "{:.2f}",
                "Call Bid": "{:.2f}",
                "Call Ask": "{:.2f}",
                "Call Spread": "{:.2f}",
                "Call IV": "{:.4f}",
                "Call Δ": "{:.3f}",
                "Strike": "{:.2f}",
                "Put Price": "{:.2f}",
                "Put Bid": "{:.2f}",
                "Put Ask": "{:.2f}",
                "Put Spread": "{:.2f}",
                "Put IV": "{:.4f}",
                "Put Δ": "{:.3f}",
            },
            na_rep="-",
        )
    )


def get_option_chain_column_config() -> Dict[str, Any]:
    """Returns the column configuration dictionary for the option chain DataFrame."""
    return {
        "Call Symbol": st.column_config.TextColumn(
            "Call Symbol",
            help="The unique ticker for the call option.",
            width="medium",
        ),
        "Call Price": st.column_config.NumberColumn(
            "Call Price",
            help="The theoretical price of the call option from the pricing model.",
            format="%.2f",
            width="small",
        ),
        "Call Bid": st.column_config.NumberColumn(
            "Call Bid",
            help="The highest price a buyer is willing to pay for the call option.",
            format="%.2f",
            width="small",
        ),
        "Call Ask": st.column_config.NumberColumn(
            "Call Ask",
            help="The lowest price a seller is willing to accept for the call option.",
            format="%.2f",
            width="small",
        ),
        "Call Spread": st.column_config.NumberColumn(
            "Call Spread",
            help="The difference between the Ask and the Bid prices (Ask - Bid).",
            format="%.2f",
            width="small",
        ),
        "Call IV": st.column_config.NumberColumn(
            "Call IV",
            help="Implied Volatility of the call option.",
            format="percent",
            width="small",
        ),
        "Call Δ": st.column_config.NumberColumn(
            "Call Δ",
            help="Rate of change of the option price with respect to the underlying stock price.",
            format="%.3f",
            width="small",
        ),
        "ITM Call": None,  # Hides the 'ITM Call' column
        "Strike": st.column_config.NumberColumn(
            "Strike Price",
            help="The price at which the option can be exercised.",
            format="%.2f",
            width="small",
        ),
        "Put Symbol": st.column_config.TextColumn(
            "Put Symbol",
            help="The unique ticker for the put option.",
            width="medium",
        ),
        "Put Price": st.column_config.NumberColumn(
            "Put Price",
            help="The theoretical price of the put option from the pricing model.",
            format="%.2f",
            width="small",
        ),
        "Put Bid": st.column_config.NumberColumn(
            "Put Bid",
            help="The highest price a buyer is willing to pay for the put option.",
            format="%.2f",
            width="small",
        ),
        "Put Ask": st.column_config.NumberColumn(
            "Put Ask",
            help="The lowest price a seller is willing to accept for the put option.",
            format="%.2f",
            width="small",
        ),
        "Put Spread": st.column_config.NumberColumn(
            "Put Spread",
            help="The difference between the Ask and the Bid prices (Ask - Bid).",
            format="%.2f",
            width="small",
        ),
        "Put IV": st.column_config.NumberColumn(
            "Put IV",
            help="Implied Volatility of the put option.",
            format="percent",
            width="small",
        ),
        "Put Δ": st.column_config.NumberColumn(
            "Put Δ",
            help="Rate of change of the option price with respect to the underlying stock price.",
            format="%.3f",
            width="small",
        ),
        "ITM Put": None,  # Hides the 'ITM Put' column
    }
