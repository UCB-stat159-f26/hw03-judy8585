import matplotlib.pyplot as plt
import pandas as pd


def _validate_matches(df):
    required = {"player_age", "age_difference", "result"}
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input must be a pandas DataFrame.")
    if not required.issubset(df.columns):
        raise ValueError("DataFrame is missing required columns.")
    if df.empty:
        raise ValueError("Cannot plot an empty DataFrame.")
    if not df["result"].isin(["W", "L"]).all():
        raise ValueError("Results must be W or L.")


def plot_player_matches(df):
    _validate_matches(df)
    fig, ax = plt.subplots(figsize=(10, 6))
    colors = {"W": "#2878B5", "L": "#8E63AD"}

    for result, label in [("W", "Won"), ("L", "Lost")]:
        matches = df[df["result"] == result]
        if not matches.empty:
            ax.scatter(matches["player_age"], -matches["age_difference"],
					   color=colors[result], s=18, alpha=0.7, label=label)

    ax.axhline(0, color="gray", linestyle="--", linewidth=1)
    ax.set_xlabel("Player Age (years)")
    ax.set_ylabel("Player Age - Opponent Age (years)")
    ax.set_title("Age Differences in Career Matches")
    ax.legend()
    fig.tight_layout()
    return fig
