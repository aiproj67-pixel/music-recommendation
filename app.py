
# ------------------------- Data loading -------------------------
from pathlib import Path

import pandas as pd
import streamlit as st

# Locate songs.csv in the same directory as app.py
BASE_DIR = Path(__file__).resolve().parent
CSV_FILE = BASE_DIR / "songs.csv"

REQUIRED_COLUMNS = ["Song", "Artist", "Genre", "Language"]


@st.cache_data
def load_songs(file_path: str, modified_time: float):
    path = Path(file_path)

    if not path.is_file():
        return None, "songs.csv was not found in the app directory."

    df = pd.read_csv(path, encoding="utf-8-sig")

    # Remove extra spaces from CSV column names
    df.columns = df.columns.astype(str).str.strip()

    missing = [
        column for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    if missing:
        return None, (
            "Missing CSV columns: " + ", ".join(missing)
        )

    df = df.dropna(subset=REQUIRED_COLUMNS).copy()

    for column in REQUIRED_COLUMNS:
        df[column] = df[column].astype(str).str.strip()

    df = df[(df[REQUIRED_COLUMNS] != "").all(axis=1)]

    return df.reset_index(drop=True), None


if not CSV_FILE.is_file():
    st.error(
        "Could not find songs.csv. Make sure it is uploaded "
        "to the same GitHub folder as app.py."
    )
    st.stop()

try:
    songs, data_error = load_songs(
        str(CSV_FILE),
        CSV_FILE.stat().st_mtime,
    )
except Exception as exc:
    st.error(f"Unable to load songs.csv: {exc}")
    st.stop()

if data_error:
    st.error(data_error)
    st.stop()

if songs is None or songs.empty:
    st.warning("The CSV file contains no valid song records.")
    st.stop()
