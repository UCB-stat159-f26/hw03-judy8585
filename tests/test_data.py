import json

import pytest

from tennis_age import data


def _career(result, opponent_age, date="19951030"):
    row = [
        date, "Event", "Hard", "W", result,
        "", "", "WC", "R32", "6-4 6-4", "3",
        "Example Opponent", "100", "", "", "R", opponent_age
    ]
    return "var morematchmx = " + json.dumps([row]) + ";"


def _mock_player(monkeypatch, slug, dob, career):
    def fake_download(url):
        if url.endswith(f"/{slug}.js"):
            return f"var dob={dob};"
        if url.endswith(f"/{slug}Career.js"):
            return career
        return None

    monkeypatch.setattr(data, "_download_text", fake_download)


@pytest.mark.parametrize("name", [
    "serena williams",
    "Serena Williams",
    "SerenaWilliams"
])
def test_female_names_and_age(monkeypatch, name):
    career = _career("L", "19770119")
    _mock_player(monkeypatch, "SerenaWilliams", "19810926", career)
    df = data.get_player_data(name)

    assert len(df) == 1
    assert df["player_age"].iloc[0] == pytest.approx(14.092, abs=0.01)
    assert df["opponent_age"].iloc[0] == pytest.approx(18.777, abs=0.01)
    assert df["result"].iloc[0] == "L"


def test_male_player(monkeypatch):
    career = _career("W", "22.264202601", "20010910")
    _mock_player(monkeypatch, "RafaelNadal", "19860603", career)
    df = data.get_player_data("Rafael Nadal")

    assert len(df) == 1
    assert df["player_age"].iloc[0] == pytest.approx(15.272, abs=0.01)
    assert df["opponent_age"].iloc[0] == pytest.approx(22.2642)
    assert df["result"].iloc[0] == "W"


def test_invalid_player(monkeypatch):
    monkeypatch.setattr(data, "_download_text", lambda url: None)

    with pytest.raises(ValueError, match="not found"):
        data.get_player_data("GastonSanchez")


def test_empty_player_name():
    with pytest.raises(ValueError, match="non-empty string"):
        data.get_player_data("")


def test_invalid_birth_date(monkeypatch):
    career = _career("L", "19770119")
    _mock_player(monkeypatch, "SerenaWilliams", "19811399", career)

    with pytest.raises(ValueError, match="Invalid birth date"):
        data.get_player_data("Serena Williams")


def test_missing_career_data(monkeypatch):
    _mock_player(
        monkeypatch, "SerenaWilliams",
        "19810926", "var other_data = [];"
    )

    with pytest.raises(ValueError, match="No career match data"):
        data.get_player_data("Serena Williams")



def test_prefers_complete_career(monkeypatch):
    old = _career("L", "19790606", "20010910")
    recent = _career("W", "19951004", "20241119")

    def get_rows(js):
        return json.loads(js.split("=", 1)[1].strip().rstrip(";"))

    rows = get_rows(old) + get_rows(recent)
    complete = "var matchmx = " + json.dumps(rows) + ";"

    def fake_download(url):
        if url.endswith("/RafaelNadal.js"):
            return "var dob=19860603;"
        if url.endswith("/RafaelNadalCareer.js"):
            return old
        if "player-classic.cgi?p=RafaelNadal" in url:
            return complete
        return None

    monkeypatch.setattr(data, "_download_text", fake_download)
    df = data.get_player_data("Rafael Nadal")

    assert len(df) == 2
    assert df["date"].max().strftime("%Y-%m-%d") == "2024-11-19"
    assert df["player_age"].max() == pytest.approx(38.46, abs=0.02)
