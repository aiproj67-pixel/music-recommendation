
from pathlib import Path

import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Music Recommendation System",
    page_icon="🎵",
    layout="wide",
)

# ------------------------- Data loading -------------------------

BASE_DIR = Path(__file__).resolve().parent
CSV_FILE = BASE_DIR / "songs.csv"

REQUIRED_COLUMNS = ["Song", "Artist", "Genre", "Language"]


@st.cache_data
def load_songs(file_path, modified_time):
    df = pd.read_csv(file_path, encoding="utf-8-sig")
    df.columns = df.columns.astype(str).str.strip()

    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(
            "Missing CSV columns: " + ", ".join(missing)
        )

    df = df.dropna(subset=REQUIRED_COLUMNS).copy()

    for col in REQUIRED_COLUMNS:
        df[col] = df[col].astype(str).str.strip()

    df = df[(df[REQUIRED_COLUMNS] != "").all(axis=1)]
    return df.reset_index(drop=True)


# ------------------------- Load data -------------------------

st.title("🎵 Music Recommendation System")
st.write("Discover songs based on your favorite genre, language, and artist.")

if not CSV_FILE.is_file():
    st.error("songs.csv was not found beside app.py in your repository.")
    st.stop()

try:
    songs = load_songs(str(CSV_FILE), CSV_FILE.stat().st_mtime)
except Exception as exc:
    st.error(f"Unable to load songs.csv: {exc}")
    st.stop()

if songs.empty:
    st.warning("No valid songs were found in songs.csv.")
    st.stop()

st.success(f"Loaded {len(songs)} songs successfully!")

# ------------------------- Filters -------------------------

st.subheader("Find your music")

col1, col2, col3 = st.columns(3)

with col1:
    genres = ["All"] + sorted(songs["Genre"].unique().tolist())
    selected_genre = st.selectbox("Choose a genre", genres)

with col2:
    languages = ["All"] + sorted(songs["Language"].unique().tolist())
    selected_language = st.selectbox("Choose a language", languages)

with col3:
    artists = ["All"] + sorted(songs["Artist"].unique().tolist())
    selected_artist = st.selectbox("Choose an artist", artists)

filtered = songs.copy()

if selected_genre != "All":
    filtered = filtered[filtered["Genre"] == selected_genre]

if selected_language != "All":
    filtered = filtered[filtered["Language"] == selected_language]

if selected_artist != "All":
    filtered = filtered[filtered["Artist"] == selected_artist]

# ------------------------- Results -------------------------

st.subheader("Recommended songs")
st.write(f"Found **{len(filtered)}** matching songs.")

if filtered.empty:
    st.info("No songs match those filters. Try different selections.")
else:
    st.dataframe(
        filtered,
        use_container_width=True,
        hide_index=True,
    )

st.caption("Recommendations are based on the filters you select.")
