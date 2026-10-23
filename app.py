
from pathlib import Path

import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Music Recommendation System",
    page_icon="🎵",
    layout="wide",
)

st.title("🎵 Music Recommendation System")
st.write("Discover songs based on your favourite genre, artist, or song.")

# Load the CSV file from the same folder as app.py
CSV_FILE = Path(__file__).resolve().parent / "songs.csv"


@st.cache_data
def load_songs():
    if not CSV_FILE.exists():
        return None

    df = pd.read_csv(CSV_FILE, encoding="utf-8-sig")

    required_columns = ["Song", "Artist", "Genre", "Language"]
    missing = [col for col in required_columns if col not in df.columns]

    if missing:
        raise ValueError(
            f"Missing required CSV columns: {', '.join(missing)}"
        )

    df = df.dropna(subset=required_columns).copy()

    for col in required_columns:
        df[col] = df[col].astype(str).str.strip()

    return df[
        (df[required_columns] != "").all(axis=1)
    ].reset_index(drop=True)


try:
    songs = load_songs()
except Exception as error:
    st.error(f"Could not read songs.csv: {error}")
    st.stop()

if songs is None:
    st.error(
        "songs.csv was not found. Upload it to the same "
        "GitHub folder as app.py."
    )
    st.stop()

if songs.empty:
    st.warning("Your songs.csv file has no valid song records.")
    st.stop()

st.success(f"Loaded {len(songs)} songs successfully!")

mode = st.selectbox(
    "How would you like recommendations?",
    [
        "Recommend by genre",
        "Recommend by artist",
        "Recommend by favourite song",
        "Display all songs",
    ],
)


def show_recommendations(results):
    if results.empty:
        st.info("No matching songs found. Try another selection.")
        return

    st.subheader(f"🎧 Recommended Songs ({len(results)})")
    st.dataframe(
        results[["Song", "Artist", "Genre", "Language"]],
        use_container_width=True,
        hide_index=True,
    )


if mode == "Recommend by genre":
    genres = sorted(songs["Genre"].unique())

    genre = st.selectbox("Choose your favourite genre", genres)

    if st.button("Find Songs", type="primary"):
        results = songs[
            songs["Genre"].str.casefold() == genre.casefold()
        ]
        show_recommendations(results)

elif mode == "Recommend by artist":
    artists = sorted(songs["Artist"].unique())

    artist = st.selectbox("Choose your favourite artist", artists)

    if st.button("Find Songs", type="primary"):
        results = songs[
            songs["Artist"].str.casefold() == artist.casefold()
        ]
        show_recommendations(results)

elif mode == "Recommend by favourite song":
    titles = sorted(songs["Song"].unique())

    title = st.selectbox("Choose a song you like", titles)

    if st.button("Find Similar Songs", type="primary"):
        selected = songs[
            songs["Song"].str.casefold() == title.casefold()
        ]

        genres = selected["Genre"].str.casefold().unique()

        results = songs[
            songs["Genre"].str.casefold().isin(genres)
            & (songs["Song"].str.casefold() != title.casefold())
        ]

        st.caption(
            "These suggestions share the same genre as your selected song."
        )
        show_recommendations(results)

else:
    st.subheader("📚 All Songs")
    st.dataframe(
        songs[["Song", "Artist", "Genre", "Language"]],
        use_container_width=True,
        hide_index=True,
    )
