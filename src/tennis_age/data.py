
import re

import pandas as pd
import requests

from .cleaning import clean_career_matches


BASE_URL = "https://www.tennisabstract.com"


def _player_slug(name):
    if not isinstance(name, str) or not name.strip():
        raise ValueError("Player name must be a non-empty string.")
    name = re.sub(r"([a-z])([A-Z])", r"\1 \2", name.strip())
    words = re.findall(r"[A-Za-z]+", name)
    if not words:
        raise ValueError("Invalid player name.")
    return "".join(word[0].upper() + word[1:] for word in words)


def _download_text(url):
    try:
        response = requests.get(url, timeout=15)
        if response.status_code == 404:
            return None
        response.raise_for_status()
        return response.text
    except requests.RequestException as exc:
        raise ConnectionError(f"Could not retrieve data from {url}") from exc


def _get_birth_date(slug):
    url = f"{BASE_URL}/jsmatches/{slug}.js"
    js_text = _download_text(url)

    if not js_text:
        raise ValueError(f"Player '{slug}' was not found.")

    match = re.search(r"\bvar\s+dob\s*=\s*['\"]?(\d{8})", js_text)
    if not match:
        raise ValueError(f"Birth date not found for '{slug}'.")

    birth_date = match.group(1)
    if pd.isna(pd.to_datetime(
        birth_date, format="%Y%m%d", errors="coerce"
    )):
        raise ValueError(f"Invalid birth date for '{slug}'.")

    return birth_date


def get_player_data(name):
    slug = _player_slug(name)
    birth_date = _get_birth_date(slug)
    url = f"{BASE_URL}/jsmatches/{slug}Career.js"
    js_text = _download_text(url)
    if not js_text or not re.search(r"\bmorematchmx\s*=", js_text):
        raise ValueError(f"No career match data found for '{name}'.")
    return clean_career_matches(js_text, birth_date)