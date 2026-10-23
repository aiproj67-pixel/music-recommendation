from pathlib import Path

import pandas as pd
import streamlit as st

# ------------------------- Page setup -------------------------
st.set_page_config(
    page_title="MelodyMatch | Music Recommender",
    page_icon="🎧",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ------------------------- Styling -------------------------
st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(135deg, #101322 0%, #17172b 48%, #20203a 100%);
        color: #f5f5fb;
    }
    [data-testid="stSidebar"] {
        background: #111321;
        border-right: 1px solid rgba(255,255,255,.08);
    }
    .hero {
        padding: 1.6rem 1.8rem;
        border-radius: 22px;
        background: linear-gradient(120deg, rgba(130,87,229,.28), rgba(33,197,181,.13));
        border: 1px solid rgba(255,255,255,.12);
        margin-bottom: 1.2rem;
    }
    .hero h1 { margin: 0; font-size: clamp(2rem, 4vw, 3.2rem); }
    .hero p { color: #c8c9dc; margin: .55rem 0 0; font-size: 1.05rem; }
    .metric-card {
        background: rgba(255,255,255,.055);
        border: 1px solid rgba(255,255,255,.10);
        border-radius: 16px;
        padding: 1rem 1.15rem;
    }
    .metric-label { color: #b6b8d0; font-size: .9rem; }
    .metric-value { color: #fff; font-size: 1.7rem; font-weight: 700; }
    div.stButton > button {
        border-radius: 12px;
        min-height: 2.8rem;
        font-weight: 650;
    }
    .song-card {
        border: 1px solid rgba(255,255,255,.12);
        background: rgba(255,255,255,.045);
        border-radius: 14px;
        padding: 1rem;
        margin: .45rem 0;
    }
    .song-title { font-weight: 700; font-size: 1.05rem; color: #fff; }
    .song-meta { color: #c2c4d8; font-size: .9rem; margin-top: .25rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ------------------------- Data loading -------------------------
CSV_FILE = Path(__file__).resolve().parent / "songs.csv"
REQUIRED_COLUMNS = ["Song", "Artist", "Genre", "Language"]


@st.cache_data
def load_songs(file_path: str, modified_time: float):
    path = Path(file_path)

    if not path.exists():
        return None, None

    df = pd.read_csv(path, encoding="utf-8-sig")

    missing = [
        column
        for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    if missing:
        return None, (
            f"Missing required CSV columns: {', '.join(missing)}"
        )

    df = df.dropna(subset=REQUIRED_COLUMNS).copy()

    for column in REQUIRED_COLUMNS:
        df[column] = df[column].astype(str).str.strip()

    df = df[(df[REQUIRED_COLUMNS] != "").all(axis=1)]

    return df.reset_index(drop=True), None


st.sidebar.markdown("## 🎧 MelodyMatch")
st.sidebar.caption("Your personal music discovery space")
st.sidebar.divider()

if not CSV_FILE.exists():
    st.error(
        "**Could not find `songs.csv`.** Place it in the same "
        "GitHub folder as `app.py`.\n\n"
        f"Expected location: `{CSV_FILE}`"
    )
    st.stop()

try:
    songs, data_error = load_songs(
        str(CSV_FILE),
        CSV_FILE.stat().st_mtime,
    )
except Exception as exc:
    st.error(f"Could not read `songs.csv`: {exc}")
    st.info(
        "Check that the file is a valid CSV saved with UTF-8 encoding."
    )
    st.stop()

if data_error:
    st.error(data_error)
    st.info(
        "Required column names: Song, Artist, Genre, Language."
    )
    st.stop()

if songs is None or songs.empty:
    st.warning("No valid song records were found in `songs.csv`.")
    st.stop()

# ------------------------- Header and overview -------------------------
st.markdown(
    """
    <div class="hero">
      <h1>Find your next favourite 🎶</h1>
      <p>Explore tracks by genre, artist, or a song you already love.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

metric1, metric2, metric3 = st.columns(3)

with metric1:
    st.markdown(
        f'<div class="metric-card">'
        f'<div class="metric-label">Songs in library</div>'
        f'<div class="metric-value">{len(songs):,}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

with metric2:
    st.markdown(
        f'<div class="metric-card">'
        f'<div class="metric-label">Genres</div>'
        f'<div class="metric-value">{songs["Genre"].nunique():,}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

with metric3:
    st.markdown(
        f'<div class="metric-card">'
        f'<div class="metric-label">Artists</div>'
        f'<div class="metric-value">{songs["Artist"].nunique():,}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

st.write("")

page = st.sidebar.radio(
    "Navigate",
    ["Discover", "Browse library", "About"],
    index=0,
)

# ------------------------- Discover -------------------------
if page == "Discover":
    st.subheader("✨ Discover music")

    mode = st.radio(
        "Choose your discovery method",
        ["By genre", "By artist", "By favourite song"],
        horizontal=True,
    )

    if mode == "By genre":
        options = sorted(
            songs["Genre"].unique(),
            key=str.casefold,
        )

        choice = st.selectbox(
            "What genre are you in the mood for?",
            options,
        )

        results = songs[
            songs["Genre"].str.casefold() == choice.casefold()
        ]

        st.caption(f"Showing tracks in **{choice}**.")

        st.dataframe(
            results[["Song", "Artist", "Genre", "Language"]],
            use_container_width=True,
            hide_index=True,
        )

    elif mode == "By artist":
        options = sorted(
            songs["Artist"].unique(),
            key=str.casefold,
        )

        choice = st.selectbox(
            "Choose an artist",
            options,
        )

        results = songs[
            songs["Artist"].str.casefold() == choice.casefold()
        ]

        st.caption(f"Tracks by **{choice}**.")

        st.dataframe(
            results[["Song", "Artist", "Genre", "Language"]],
            use_container_width=True,
            hide_index=True,
        )

    else:
        options = sorted(
            songs["Song"].unique(),
            key=str.casefold,
        )

        title = st.selectbox(
            "Choose a song you already enjoy",
            options,
        )

        selected = songs[
            songs["Song"].str.casefold() == title.casefold()
        ]

        selected_genres = selected["Genre"].str.casefold().unique()

        results = songs[
            songs["Genre"].str.casefold().isin(selected_genres)
            & (songs["Song"].str.casefold() != title.casefold())
        ]

        if not results.empty:
            st.caption(
                f"Because you like **{title}**, here are other "
                "tracks in the same genre."
            )

            st.dataframe(
                results[["Song", "Artist", "Genre", "Language"]],
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info(
                "No other songs in the same genre were found. "
                "Try another song."
            )

    if not results.empty:
        csv_bytes = results[
            ["Song", "Artist", "Genre", "Language"]
        ].to_csv(index=False).encode("utf-8")

        st.download_button(
            "⬇️ Download these recommendations as CSV",
            data=csv_bytes,
            file_name="music_recommendations.csv",
            mime="text/csv",
        )

# ------------------------- Browse library -------------------------
elif page == "Browse library":
    st.subheader("📚 Browse the music library")

    search = st.text_input(
        "Search songs, artists, genres, or languages",
        placeholder="Try a song title, artist, genre...",
    )

    filtered = songs.copy()

    if search.strip():
        term = search.strip()
        mask = pd.Series(False, index=filtered.index)

        for column in REQUIRED_COLUMNS:
            mask |= filtered[column].str.contains(
                term,
                case=False,
                na=False,
                regex=False,
            )

        filtered = filtered[mask]

    c1, c2 = st.columns(2)

    with c1:
        genre_filter = st.multiselect(
            "Filter by genre",
            sorted(
                songs["Genre"].unique(),
                key=str.casefold,
            ),
        )

    with c2:
        language_filter = st.multiselect(
            "Filter by language",
            sorted(
                songs["Language"].unique(),
                key=str.casefold,
            ),
        )

    if genre_filter:
        filtered = filtered[
            filtered["Genre"].isin(genre_filter)
        ]

    if language_filter:
        filtered = filtered[
            filtered["Language"].isin(language_filter)
        ]

    st.caption(
        f"{len(filtered):,} song(s) match your filters."
    )

    st.dataframe(
        filtered[["Song", "Artist", "Genre", "Language"]],
        use_container_width=True,
        hide_index=True,
    )

# ------------------------- About -------------------------
else:
    st.subheader("About MelodyMatch")

    st.write(
        "MelodyMatch is a simple music discovery app powered by "
        "your `songs.csv` dataset. It recommends songs by matching "
        "genre or artist, and suggests tracks from the same genre "
        "as a selected song."
    )

    st.info(
        "This version uses rule-based matching, not a trained "
        "machine-learning model. Recommendations depend on the "
        "songs and metadata in your CSV file."
    )

st.sidebar.divider()
st.sidebar.caption("Made with Streamlit · Keep discovering 🎵")
