import json
import re

import pandas as pd


def _parse_matches(js_text):
    match = re.search(r"\b(?:morematchmx|matchmx)\s*=\s*", js_text)
    if not match:
        raise ValueError("Could not find career match data.")
    try:
        rows, _ = json.JSONDecoder().raw_decode(js_text[match.end():].lstrip())
    except (json.JSONDecodeError, TypeError) as exc:
        raise ValueError("Invalid career JS data.") from exc
    if not isinstance(rows, list) or not rows:
        raise ValueError("No career matches found.")
    return rows


def _opponent_age(value, match_date):
    value = str(value).strip()
    if re.fullmatch(r"\d{8}", value):
        birth = pd.to_datetime(value, format="%Y%m%d", errors="coerce")
        return (match_date - birth).days / 365.2425 if pd.notna(birth) else float("nan")
    try:
        return float(value)
    except ValueError:
        return float("nan")


def _make_frame(rows):
    if any(not isinstance(row, list) or len(row) < 17 for row in rows):
        raise ValueError("Career match data has missing columns.")
    return pd.DataFrame(
        [[r[0], r[4], r[11], r[16]] for r in rows],
        columns=["date", "result", "opponent", "opponent_age_raw"]
    )


def clean_career_matches(js_text, player_birth_date):
    birth = pd.to_datetime(player_birth_date, errors="coerce")
    if pd.isna(birth):
        raise ValueError("Invalid player birth date.")
    df = _make_frame(_parse_matches(js_text))
    df["date"] = pd.to_datetime(df["date"], format="%Y%m%d", errors="coerce")
    df["player_age"] = (df["date"] - birth).dt.days / 365.2425
    df["opponent_age"] = [
        _opponent_age(v, d)
        for v, d in zip(df["opponent_age_raw"], df["date"])
    ]
    df["age_difference"] = df["opponent_age"] - df["player_age"]
    df["result"] = df["result"].astype("string").str.upper()
    df = df[df["result"].isin(["W", "L"])].dropna(
        subset=["date", "player_age", "opponent_age"]
    )
    return df[
        ["date", "player_age", "opponent_age",
         "age_difference", "result", "opponent"]
    ].reset_index(drop=True)