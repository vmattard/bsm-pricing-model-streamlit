import streamlit as st

import charts as c
import data_utils as du
import style as s
from enums import OptionType
from event_manager import (
    Event,
    EventManager,
    event_calculate_bsm,
    event_fetch_option_chains,
    event_fetch_option_expiration_dates,
    event_simulate_bsm,
)

# --- App Setup ---
event_manager = EventManager()


def build_greek_table(option_type: OptionType) -> None:
    """
    Builds and displays a row of metrics for the option price and Greeks.
    """
    bsm_calculation_data = EventManager.get(Event.DATA_BSM_CALCULATION).get(option_type)
    metrics_config = [
        {"key": "price", "label": "Price ($)"},
        {"key": "delta", "label": "Delta (Δ)"},
        {"key": "gamma", "label": "Gamma (Γ)"},
        {"key": "vega", "label": "Vega (v)"},
        {"key": "theta", "label": "Theta (θ)"},
        {"key": "rho", "label": "Rho (ρ)"},
    ]

    if bsm_calculation_data:
        cols = st.columns(len(metrics_config))
        for col, metric in zip(cols, metrics_config):
            with col:
                value = bsm_calculation_data.get(metric["key"])
                display_value = (
                    du.round_value(value) if isinstance(value, (int, float)) else "N/A"
                )
                st.metric(label=metric["label"], value=display_value)


def build_greek_chart(option_type: OptionType) -> None:
    """
    Builds and displays a 3x2 grid of Greek charts using Altair.
    """
    bsm_simulation_data = EventManager.get(Event.DATA_BSM_SIMULATION).get(option_type)
    strike_price = EventManager.get(Event.INPUT_STRIKE_PRICE)

    if bsm_simulation_data is None or bsm_simulation_data.empty:
        # Don't show a warning on initial load, only if simulation was attempted and failed
        if EventManager.get(Event.BUTTON_SIMULATE):
            st.warning(f"No simulation data available for {option_type.value} options.")
        return

    charts_config = [
        {"y_col": "price", "title": "Price ($)"},
        {"y_col": "delta", "title": "Delta (Δ)"},
        {"y_col": "gamma", "title": "Gamma (Γ)"},
        {"y_col": "vega", "title": "Vega (v)"},
        {"y_col": "theta", "title": "Theta (θ)"},
        {"y_col": "rho", "title": "Rho (ρ)"},
    ]

    row1 = st.columns(3)
    row2 = st.columns(3)
    all_columns = row1 + row2

    for i, config in enumerate(charts_config):
        with all_columns[i]:
            st.subheader(config["title"])
            if config["y_col"] in bsm_simulation_data.columns:
                chart = c.create_altair_chart(
                    data=bsm_simulation_data,
                    y_col=config["y_col"],
                    y_title=config["title"],
                    strike_price=strike_price,
                )
                st.altair_chart(chart, use_container_width=True)
            else:
                st.warning(f"Column '{config['y_col']}' not found in data.")


def build_bsm_tab_content() -> None:
    """
    Builds the content for the Black-Scholes-Merton tab, containing sub-tabs for Call and Put options.
    """
    call_tab, put_tab = st.tabs(OptionType.values())
    with call_tab:
        build_greek_table(OptionType.CALL)
        build_greek_chart(OptionType.CALL)
    with put_tab:
        build_greek_table(OptionType.PUT)
        build_greek_chart(OptionType.PUT)


def build_option_expiration_dates_content():
    """
    Builds the dropdown for selecting option expiration dates.
    """
    stock_option_expiration_dates_data = EventManager.get(
        Event.DATA_STOCK_OPTION_EXPIRATION_DATES
    )
    if not stock_option_expiration_dates_data:
        # Don't show a warning on initial load
        if EventManager.get(Event.BUTTON_FETCH):
            st.warning("No option expiration dates found.")
        return

    st.selectbox(
        label="Expiration dates",
        options=stock_option_expiration_dates_data,
        key=Event.INPUT_STOCK_OPTION_EXPIRATION_DATE,
        on_change=event_fetch_option_chains,
    )


def build_option_chains_content():
    """
    Builds the dataframe display for the stock option chains.
    """
    stock_option_chains_data = EventManager.get(Event.DATA_STOCK_OPTION_CHAINS)
    if not stock_option_chains_data:
        # Don't show a warning on initial load
        if EventManager.get(Event.BUTTON_FETCH):
            st.warning("No option chains found.")
        return

    stock_ticker = EventManager.get(Event.INPUT_STOCK_OPTION_TICKER)
    expiration_date = EventManager.get(Event.INPUT_STOCK_OPTION_EXPIRATION_DATE)
    stock_metadata = EventManager.get(Event.DATA_STOCK)

    if (
        OptionType.CALL not in stock_option_chains_data
        or OptionType.PUT not in stock_option_chains_data
        or stock_option_chains_data[OptionType.CALL].empty
        or stock_option_chains_data[OptionType.PUT].empty
    ):
        st.warning(f"No option chains found for {stock_ticker} on the selected date.")
        return

    df = du.process_option_chains(
        stock_option_chains_data, expiration_date, stock_metadata
    )
    df_styled = s.style_option_chain(df)
    column_config = s.get_option_chain_column_config()

    st.subheader(f"Option Chain for {stock_ticker}")
    details = f"""
    :gray[**Expires:** {expiration_date.isoformat()} &nbsp;&nbsp;|&nbsp;&nbsp; **Spot Price:** ${stock_metadata.get('spotPrice'):.2f} &nbsp;&nbsp;|&nbsp;&nbsp; **Dividend Yield:** {stock_metadata.get('dividendYield'):.2f}%]
    """
    st.markdown(details)
    st.dataframe(
        df_styled,
        column_config=column_config,
        use_container_width=True,
        hide_index=True,
    )


def build_sidebar() -> None:
    """
    Builds the combined sidebar with expandable sections for each tool.
    """
    with st.sidebar:
        st.title("Options Analysis Tool")
        st.caption(
            """
            Created by: Vincent Mattard 
            <a href="https://www.linkedin.com/in/vincentmattard/" target="_blank" style="display: inline-flex; align-items: center; text-decoration: none; margin-left: 6px;">
                <img src="https://cdn-icons-png.flaticon.com/512/174/174857.png" alt="LinkedIn" width="16" height="16" style="vertical-align: middle;">
            </a>
            """,
            unsafe_allow_html=True,
        )
        st.title("Parameters")

        with st.expander("Option Calculator", expanded=True):
            st.number_input(
                label="Underlying Asset Price ($)",
                format="%.2f",
                min_value=0.01,
                key=Event.INPUT_UNDERLYING_ASSET_PRICE,
            )
            st.number_input(
                label="Strike Price ($)",
                format="%.2f",
                min_value=0.01,
                key=Event.INPUT_STRIKE_PRICE,
            )
            st.date_input(
                label="Expiration Date",
                format="YYYY-MM-DD",
                min_value="today",
                key=Event.INPUT_EXPIRATION_DATE,
            )
            st.number_input(
                label="Interest Rate (%)",
                format="%.2f",
                min_value=0.01,
                key=Event.INPUT_INTEREST_RATE,
            )
            st.number_input(
                label="Volatility (%)",
                format="%.2f",
                min_value=0.01,
                key=Event.INPUT_VOLATILITY,
            )
            st.number_input(
                label="Dividend Yield (%)",
                format="%.2f",
                min_value=0.0,
                key=Event.INPUT_DIVIDEND_YIELD,
            )
            c_btn, s_btn = st.columns(2)
            with c_btn:
                st.button(
                    label="Calculate",
                    on_click=event_calculate_bsm,
                    key=Event.BUTTON_CALCULATE,
                )
            with s_btn:
                st.button(
                    label="Simulate",
                    on_click=event_simulate_bsm,
                    key=Event.BUTTON_SIMULATE,
                )

        with st.expander("Option Viewer", expanded=True):
            st.text_input(label="Stock Ticker", key=Event.INPUT_STOCK_OPTION_TICKER)
            st.button(
                label="Fetch",
                on_click=event_fetch_option_expiration_dates,
                key=Event.BUTTON_FETCH,
            )


def main() -> None:
    """
    Main function to run the Streamlit app.
    """
    st.set_page_config(
        page_title="Options Analysis Tool",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    if not EventManager.get(Event.STATE_INITIALIZE):
        event_manager.initialize()

    build_sidebar()

    # Main content organized into tabs
    bsm_tab, option_chain_tab = st.tabs(["Calculator", "Viewer"])

    with bsm_tab:
        st.subheader("Black-Scholes-Merton")
        build_bsm_tab_content()

    with option_chain_tab:
        st.subheader("Stock Option Chain")
        build_option_expiration_dates_content()
        build_option_chains_content()


if __name__ == "__main__":
    main()
