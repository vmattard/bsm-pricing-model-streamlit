from datetime import date
from enum import Enum
from typing import Any

import pandas as pd
import streamlit as st
from dateutil.relativedelta import relativedelta

import data_utils as du
from black_scholes_merton import calculate_bsm, simulate_bsm
from enums import OptionType


class Event(Enum):
    INPUT_UNDERLYING_ASSET_PRICE = "input_underlying_asset_price"
    INPUT_STRIKE_PRICE = "input_strike_price"
    INPUT_VOLATILITY = "input_volatility"
    INPUT_INTEREST_RATE = "input_interest_rate"
    INPUT_EXPIRATION_DATE = "input_expiration_date"
    INPUT_DIVIDEND_YIELD = "input_dividend_yield"

    INPUT_STOCK_OPTION_TICKER = "input_stock_option_ticker"
    INPUT_STOCK_OPTION_EXPIRATION_DATE = "input_stock_option_expiration_date"

    BUTTON_CALCULATE = "btn_calculate"
    BUTTON_SIMULATE = "btn_simulate"

    BUTTON_FETCH = "btn_fetch"

    DATA_BSM_CALCULATION = "data_calculation_bsm"
    DATA_BSM_SIMULATION = "data_simulation_bsm"

    DATA_STOCK_OPTION_CHAINS = "data_stock_option_chains"
    DATA_STOCK_OPTION_EXPIRATION_DATES = "data_stock_option_expiration_dates"
    DATA_STOCK = "data_stock"

    STATE_INITIALIZE = "state_initialize"


class EventManager:

    def initialize(self) -> None:
        today = date.today()
        six_months_ahead = today + relativedelta(months=1)

        self.set(Event.INPUT_UNDERLYING_ASSET_PRICE, 660.0)
        self.set(Event.INPUT_STRIKE_PRICE, 600.0)
        self.set(Event.INPUT_VOLATILITY, 20.0)
        self.set(Event.INPUT_INTEREST_RATE, 4.25)
        self.set(Event.INPUT_EXPIRATION_DATE, six_months_ahead)
        self.set(Event.INPUT_DIVIDEND_YIELD, 0.0)

        self.set(Event.INPUT_STOCK_OPTION_TICKER, "SPY")
        self.set(Event.INPUT_STOCK_OPTION_EXPIRATION_DATE, today)

        self.set(
            Event.DATA_BSM_CALCULATION,
            {OptionType.CALL: {}, OptionType.PUT: {}},
        )
        self.set(
            Event.DATA_BSM_SIMULATION,
            {OptionType.CALL: pd.DataFrame(), OptionType.PUT: pd.DataFrame()},
        )

        self.set(
            Event.DATA_STOCK_OPTION_CHAINS,
            {OptionType.CALL: pd.DataFrame(), OptionType.PUT: pd.DataFrame()},
        )
        self.set(Event.DATA_STOCK_OPTION_EXPIRATION_DATES, [])
        self.set(Event.DATA_STOCK, {})

        self.set(Event.STATE_INITIALIZE, True)

    @staticmethod
    def get(event: Event) -> Any:
        return st.session_state.get(event, None)

    @staticmethod
    def set(event: Event, value: Any) -> None:
        st.session_state[event] = value


def event_calculate_bsm() -> None:
    S = EventManager.get(Event.INPUT_UNDERLYING_ASSET_PRICE)
    K = EventManager.get(Event.INPUT_STRIKE_PRICE)
    t = (abs(EventManager.get(Event.INPUT_EXPIRATION_DATE) - date.today())).days / 365
    r = EventManager.get(Event.INPUT_INTEREST_RATE) / 100
    sigma = EventManager.get(Event.INPUT_VOLATILITY) / 100
    q = EventManager.get(Event.INPUT_DIVIDEND_YIELD) / 100

    bsm_calculation_data = {
        OptionType.CALL: calculate_bsm(S, K, t, r, sigma, q, OptionType.CALL),
        OptionType.PUT: calculate_bsm(S, K, t, r, sigma, q, OptionType.PUT),
    }

    EventManager.set(Event.DATA_BSM_CALCULATION, bsm_calculation_data)


def event_simulate_bsm() -> None:
    S = EventManager.get(Event.INPUT_UNDERLYING_ASSET_PRICE)
    K = EventManager.get(Event.INPUT_STRIKE_PRICE)
    t = (abs(EventManager.get(Event.INPUT_EXPIRATION_DATE) - date.today())).days / 365
    r = EventManager.get(Event.INPUT_INTEREST_RATE) / 100
    sigma = EventManager.get(Event.INPUT_VOLATILITY) / 100
    q = EventManager.get(Event.INPUT_DIVIDEND_YIELD)

    bsm_simulation_data = {
        OptionType.CALL: simulate_bsm(S, K, t, r, sigma, q, OptionType.CALL),
        OptionType.PUT: simulate_bsm(S, K, t, r, sigma, q, OptionType.PUT),
    }

    EventManager.set(Event.DATA_BSM_SIMULATION, bsm_simulation_data)


def event_fetch_option_chains() -> None:
    stock_ticker = EventManager.get(Event.INPUT_STOCK_OPTION_TICKER)
    expiration_date = EventManager.get(Event.INPUT_STOCK_OPTION_EXPIRATION_DATE)
    stock_option_chains_data = du.get_option_chains(stock_ticker, expiration_date)
    stock_data = du.get_stock_metadata(stock_ticker)
    EventManager.set(Event.DATA_STOCK_OPTION_CHAINS, stock_option_chains_data)
    EventManager.set(Event.DATA_STOCK, stock_data)


def event_fetch_option_expiration_dates() -> None:
    stock_ticker = EventManager.get(Event.INPUT_STOCK_OPTION_TICKER)
    stock_option_expiration_dates_data = du.get_option_expiration_dates(stock_ticker)
    EventManager.set(
        Event.DATA_STOCK_OPTION_EXPIRATION_DATES, stock_option_expiration_dates_data
    )
