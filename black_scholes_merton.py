from typing import Dict, Tuple

import numpy as np
import pandas as pd
from scipy.stats import norm

from enums import OptionType


class BlackScholesMerton:

    def __init__(
        self, S: float, K: float, t: float, r: float, sigma: float, q: float = 0.0
    ):
        """
        Initializes the Black-Scholes-Merton option pricing model.

        Parameters:
        S (float): Spot price of the underlying asset.
        K (float): Strike price.
        t (float): Time to maturity (in years).
        r (float): Risk-free interest rate (annualized, e.g., 0.05 for 5%).
        sigma (float): Volatility of the underlying asset (annualized, e.g., 0.2 for 20%).
        q (float): Continuous dividend yield (annualized, defaults to 0).
        """
        self.S = S
        self.K = K
        self.t = t
        self.r = r
        self.sigma = sigma
        self.q = q

        self._validate_variables()

        self.d1, self.d2 = self._calculate_d1_d2()

    def _validate_variables(self) -> None:
        """Validates the input parameters to ensure they are positive/non-negative."""
        if self.S <= 0:
            raise ValueError("Spot price (S) must be positive.")
        if self.K <= 0:
            raise ValueError("Strike price (K) must be positive.")
        if self.t <= 0:
            raise ValueError("Time to maturity (t) must be positive.")
        if self.sigma <= 0:
            raise ValueError("Volatility (sigma) must be positive.")
        if self.q < 0:
            raise ValueError("Dividend yield (q) cannot be negative.")

    def _calculate_d1_d2(self) -> Tuple[float, float]:
        """
        Calculates and returns the d1 and d2 parameters.
        """
        d1 = (
            np.log(self.S / self.K) + (self.r - self.q + 0.5 * self.sigma**2) * self.t
        ) / (self.sigma * np.sqrt(self.t))
        d2 = d1 - self.sigma * np.sqrt(self.t)
        return d1, d2

    def call(self) -> Dict[str, float]:
        """
        Calculates the price and Greeks for a European Call option.
        """
        price = self.S * np.exp(-self.q * self.t) * norm.cdf(self.d1) - self.K * np.exp(
            -self.r * self.t
        ) * norm.cdf(self.d2)

        return {
            "price": price,
            "delta": self.delta(OptionType.CALL),
            "gamma": self.gamma(),
            "vega": self.vega(),
            "theta": self.theta(OptionType.CALL),
            "rho": self.rho(OptionType.CALL),
        }

    def put(self) -> Dict[str, float]:
        """
        Calculates the price and Greeks for a European Put option.
        """
        price = self.K * np.exp(-self.r * self.t) * norm.cdf(
            -self.d2
        ) - self.S * np.exp(-self.q * self.t) * norm.cdf(-self.d1)

        return {
            "price": price,
            "delta": self.delta(OptionType.PUT),
            "gamma": self.gamma(),
            "vega": self.vega(),
            "theta": self.theta(OptionType.PUT),
            "rho": self.rho(OptionType.PUT),
        }

    def delta(self, option_type: OptionType) -> float:
        """Calculates the Delta of the option."""
        if option_type == OptionType.CALL:
            delta = np.exp(-self.q * self.t) * norm.cdf(self.d1)
        elif option_type == OptionType.PUT:
            delta = np.exp(-self.q * self.t) * (norm.cdf(self.d1) - 1)
        else:
            raise ValueError("Invalid option type.")
        return delta

    def gamma(self) -> float:
        """Calculates the Gamma of the option."""
        denominator = self.S * self.sigma * np.sqrt(self.t)
        if denominator == 0:
            return np.nan
        return (norm.pdf(self.d1) * np.exp(-self.q * self.t)) / denominator

    def vega(self) -> float:
        """Calculates the Vega of the option (per 1% change in volatility)."""
        return (
            self.S * np.exp(-self.q * self.t) * norm.pdf(self.d1) * np.sqrt(self.t)
        ) / 100

    def theta(self, option_type: OptionType) -> float:
        """Calculates the Theta of the option (per day)."""
        term1 = -(
            self.S * np.exp(-self.q * self.t) * norm.pdf(self.d1) * self.sigma
        ) / (2 * np.sqrt(self.t))

        if option_type == OptionType.CALL:
            term2 = self.q * self.S * np.exp(-self.q * self.t) * norm.cdf(self.d1)
            term3 = -self.r * self.K * np.exp(-self.r * self.t) * norm.cdf(self.d2)
            theta = term1 + term2 + term3
        elif option_type == OptionType.PUT:
            term2 = -self.q * self.S * np.exp(-self.q * self.t) * norm.cdf(-self.d1)
            term3 = self.r * self.K * np.exp(-self.r * self.t) * norm.cdf(-self.d2)
            theta = term1 + term2 + term3
        else:
            raise ValueError("Invalid option type.")

        return theta / 365

    def rho(self, option_type: OptionType) -> float:
        """Calculates the Rho of the option (per 1% change in risk-free rate)."""
        term = self.K * self.t * np.exp(-self.r * self.t)

        if option_type == OptionType.CALL:
            rho = term * norm.cdf(self.d2)
        elif option_type == OptionType.PUT:
            rho = -term * norm.cdf(-self.d2)
        else:
            raise ValueError("Invalid option type.")

        return rho / 100


def simulate_bsm(
    S: float,
    K: float,
    t: float,
    r: float,
    sigma: float,
    q: float,
    option_type: OptionType,
    range_percent: float = 0.30,
    steps: int = 50,
) -> pd.DataFrame:
    """
    Calculates Black-Scholes-Merton metrics for a range of spot prices
    centered around the current spot price S.

    Args:
        S (float): The current spot price, used as the center of the range.
        K (float): Strike price.
        t (float): Time to maturity (in years).
        r (float): Risk-free interest rate.
        sigma (float): Volatility.
        q (float): Continuous dividend yield.
        option_type (OptionType): The type of option (CALL or PUT).
        range_percent (float): The +/- percentage to define the spot price range.
        steps (int): The number of data points to generate.

    Returns:
        pd.DataFrame: A DataFrame with spot prices and corresponding Greeks.
    """

    lower_bound = min(S, K)
    upper_bound = max(S, K)

    s_start = lower_bound * (1 - range_percent)
    s_end = upper_bound * (1 + range_percent)

    spot_prices = np.linspace(s_start, s_end, steps)

    results = []
    for spot_price in spot_prices:
        try:
            bs_model = BlackScholesMerton(S=spot_price, K=K, t=t, r=r, sigma=sigma, q=q)
            if option_type == OptionType.CALL:
                greeks = bs_model.call()
            else:
                greeks = bs_model.put()

            greeks["S"] = spot_price
            results.append(greeks)

        except ValueError as e:
            print(f"Could not calculate for S={spot_price:.2f}: {e}")

    return pd.DataFrame(results)


def calculate_bsm(
    S: float,
    K: float,
    t: float,
    r: float,
    sigma: float,
    q: float,
    option_type: OptionType,
) -> Dict[str, float]:
    bsm_model = BlackScholesMerton(S, K, t, r, sigma, q)
    match option_type:
        case OptionType.CALL:
            return bsm_model.call()
        case OptionType.PUT:
            return bsm_model.put()
    raise ValueError("Invalid option type. Must be OptionType.CALL or OptionType.PUT.")
