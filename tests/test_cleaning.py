import pytest

from tennis_age.cleaning import clean_career_matches


FEMALE_JS = '''
var morematchmx = [
["19951030", "Canadian Open", "Carpet", "W", "L",
"", "", "WC", "Q1", "6-1 6-1", "3",
"Anne Miller", "149", "7", "", "R", "19770119"]
];
'''

MALE_JS = '''
var morematchmx = [
["20010910", "Spain F10", "Hard", "S", "L",
"", "", "WC", "R32", "2-6 7-5 6-2", "3",
"Guillermo Platel", "731", "", "", "R", "22.264202601"]
];
'''


def test_female_opponent_age():
    df = clean_career_matches(FEMALE_JS, "1981-09-26")
    assert len(df) == 1
    assert df["opponent_age"].iloc[0] == pytest.approx(18.7766, abs=0.001)
    assert df["result"].iloc[0] == "L"


def test_male_opponent_age():
    df = clean_career_matches(MALE_JS, "1986-06-03")
    assert len(df) == 1
    assert df["opponent_age"].iloc[0] == pytest.approx(22.2642, abs=0.001)
    assert df["result"].iloc[0] == "L"


def test_age_difference():
    df = clean_career_matches(FEMALE_JS, "1981-09-26")
    expected = df["opponent_age"] - df["player_age"]
    assert df["age_difference"].iloc[0] == pytest.approx(expected.iloc[0])


def test_invalid_js():
    with pytest.raises(ValueError, match="Could not find career match data"):
        clean_career_matches("invalid data", "1981-09-26")


def test_invalid_birth_date():
    with pytest.raises(ValueError, match="Invalid player birth date"):
        clean_career_matches(FEMALE_JS, "not-a-date")


def test_empty_matches():
    with pytest.raises(ValueError, match="No career matches found"):
        clean_career_matches("var morematchmx = [];", "1981-09-26")
