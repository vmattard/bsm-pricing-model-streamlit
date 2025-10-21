import altair as alt
import pandas as pd


def create_altair_chart(
    data: pd.DataFrame, y_col: str, y_title: str, strike_price: float
) -> alt.Chart:
    """
    Creates a standardized Altair line chart for a given option metric.

    Args:
        data (pd.DataFrame): The DataFrame containing simulation results.
                             Must have an 'S' column for the x-axis.
        y_col (str): The name of the column to use for the y-axis (e.g., 'delta').
        y_title (str): The display title for the y-axis (e.g., 'Delta (Δ)').
        strike_price (float): The strike price, used to draw a vertical line.

    Returns:
        alt.Chart: A layered Altair chart object ready for display.
    """
    line = (
        alt.Chart(data)
        .mark_line()
        .encode(
            x=alt.X("S", title="Spot Price ($)"),
            y=alt.Y(y_col, title=y_title, scale=alt.Scale(zero=False)),
            tooltip=[
                alt.Tooltip("S", title="Spot Price", format="$.2f"),
                alt.Tooltip(y_col, title=y_title, format=".4f"),
            ],
        )
        .interactive()
    )

    rule = (
        alt.Chart(pd.DataFrame({"strike": [strike_price]}))
        .mark_rule(color="red", strokeDash=[4, 4])
        .encode(x="strike")
    )

    return line + rule
