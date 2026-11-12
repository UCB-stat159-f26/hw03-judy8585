import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd
import pytest

from tennis_age import plot_player_matches


@pytest.fixture
def sample_matches():
    return pd.DataFrame({
        "player_age": [18, 20, 22, 24, 26],
        "age_difference": [4, -2, 0, 3, -5],
        "result": ["W", "L", "W", "L", "W"]
    })


def test_plot_creation(sample_matches):
    fig = plot_player_matches(sample_matches)
    assert isinstance(fig, plt.Figure)
    assert len(fig.axes) == 1
    assert len(fig.axes[0].collections) == 2
    plt.close(fig)


def test_number_of_points(sample_matches):
    fig = plot_player_matches(sample_matches)
    points = sum(len(c.get_offsets()) for c in fig.axes[0].collections)
    assert points == len(sample_matches)
    plt.close(fig)


def test_only_wins():
    df = pd.DataFrame({
        "player_age": [18, 20],
        "age_difference": [2, -3],
        "result": ["W", "W"]
    })
    fig = plot_player_matches(df)
    assert len(fig.axes[0].collections) == 1
    plt.close(fig)


def test_empty_dataframe():
    df = pd.DataFrame(columns=["player_age", "age_difference", "result"])
    with pytest.raises(ValueError, match="empty DataFrame"):
        plot_player_matches(df)


def test_missing_columns():
    df = pd.DataFrame({"player_age": [20], "result": ["W"]})
    with pytest.raises(ValueError, match="missing required columns"):
        plot_player_matches(df)


def test_invalid_results(sample_matches):
    sample_matches.loc[0, "result"] = "X"
    with pytest.raises(ValueError, match="Results must be W or L"):
        plot_player_matches(sample_matches)


def test_age_difference_direction(sample_matches):
    fig = plot_player_matches(sample_matches)
    ax = fig.axes[0]

    for collection, result in zip(ax.collections, ["W", "L"]):
        expected = sample_matches.loc[
            sample_matches["result"] == result, "age_difference"
        ]
        actual = collection.get_offsets()[:, 1]
        assert list(actual) == pytest.approx((-expected).tolist())

    plt.close(fig)
