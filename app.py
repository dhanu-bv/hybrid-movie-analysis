import streamlit as st
import pandas as pd
import requests
import glob
import os
from textblob import TextBlob
import html  

st.set_page_config(page_title="Hybrid Movie Analysis", layout="wide")


LOCAL_TMDB_API_KEY = "950bfd8ed97bddbdefae65f6ac103b3c"

def _get_tmdb_api_key():
    if LOCAL_TMDB_API_KEY:
        return LOCAL_TMDB_API_KEY
    env_key = os.environ.get('TMDB_API_KEY')
    if env_key:
        return env_key
    try:
        if hasattr(st, 'secrets') and st.secrets is not None:
            try:
                return st.secrets.get('TMDB_API_KEY')
            except Exception:
                try:
                    return st.secrets['TMDB_API_KEY']
                except Exception:
                    return None
    except Exception:
        return None

API_KEY = _get_tmdb_api_key()

@st.cache_data
def load_spark_results():
    csv_files = glob.glob(os.path.join("analysis_results", "*.csv"))
    parquet_files = glob.glob(os.path.join("analysis_results", "*.parquet"))
    if csv_files:
        df = pd.read_csv(csv_files[0])
    elif parquet_files:
        try:
            df = pd.read_parquet(parquet_files[0])
        except Exception:
            return None
    else:
        return None
    if 'avg_rating' in df.columns:
        df['avg_rating'] = pd.to_numeric(df['avg_rating'], errors='coerce').round(2)
    if 'rating_count' in df.columns:
        df['rating_count'] = pd.to_numeric(df['rating_count'], errors='coerce').fillna(0).astype(int)
    return df

@st.cache_data
def tmdb_search_movie(title: str):
    if not API_KEY:
        return None
    try:
        url = f"https://api.themoviedb.org/3/search/movie?api_key={API_KEY}&query={requests.utils.quote(title)}"
        r = requests.get(url, timeout=8)
        r.raise_for_status()
        data = r.json()
        return data.get('results', [])[0] if data.get('results') else None
    except Exception:
        return None

@st.cache_data
def tmdb_get_reviews(movie_id: int):
    if not API_KEY or not movie_id:
        return []
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}/reviews?api_key={API_KEY}"
        r = requests.get(url, timeout=8)
        r.raise_for_status()
        return r.json().get('results', [])
    except Exception:
        return []

def analyze_sentiment(text: str) -> str:
    analysis = TextBlob(text or "")
    if analysis.sentiment.polarity > 0.1:
        return "Positive ✅"
    if analysis.sentiment.polarity < -0.1:
        return "Negative ❌"
    return "Neutral ➖"

def svg_placeholder(width=300, height=450, text='No image'):
    svg = f"<svg xmlns='http://www.w3.org/2000/svg' width='{width}' height='{height}' viewBox='0 0 {width} {height}'>"
    svg += "<rect width='100%' height='100%' fill='%23f3f3f3'/>"
    svg += f"<text x='50%' y='50%' dominant-baseline='middle' text-anchor='middle' fill='%23777' font-size='20'>{text}</text>"
    svg += "</svg>"
    return 'data:image/svg+xml;utf8,' + svg


st.markdown("<h1 style='text-align:center'>🎬 Hybrid Movie Analysis Dashboard</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center'>Precomputed Spark results + live TMDb enrichment.</p>", unsafe_allow_html=True)
st.markdown("---")


results_df = load_spark_results()
if results_df is None:
    st.error("Analysis results not found. Run process_data.py and ensure analysis_results/top10_movies_per_genre.csv exists.")
    st.stop()


col1, col2 = st.columns([1, 3])

with col1:
    
    st.markdown(
        """
        <div style='padding:15px; border:1px solid #eee; border-radius:10px; background:#fafafa;'>
        <h4 style='color:black;'>🎯 Insights Dashboard</h4>
        <p style='color:black;'>Select Genre and optional filters</p>
        </div>
        """, unsafe_allow_html=True
    )

    genres = sorted(results_df['genre'].dropna().unique())
    selected_genre = st.selectbox("Select Genre:", options=genres)

    min_rating = st.slider("Minimum Avg Rating:", 0.0, 5.0, 0.0, 0.1)

with col2:
    st.header(f"Top 10 Movies for: {selected_genre}")
    filtered_df = results_df[results_df['genre'] == selected_genre]
    filtered_df = filtered_df[filtered_df['avg_rating'] >= min_rating]
    display_df = filtered_df.sort_values(['avg_rating', 'rating_count'], ascending=[False, False]).head(10)

    st.dataframe(
        display_df[['title', 'avg_rating', 'rating_count']].reset_index(drop=True),
        use_container_width=True
    )


st.markdown("---")
st.header("⚡ Live TMDb Panel")

@st.cache_data
def fetch_tmdb_popular():
    if not API_KEY:
        return []
    try:
        url = f"https://api.themoviedb.org/3/movie/popular?api_key={API_KEY}&language=en-US&page=1"
        r = requests.get(url, timeout=8)
        r.raise_for_status()
        return r.json().get('results', [])
    except Exception:
        return []

popular = fetch_tmdb_popular() if API_KEY else []
st.subheader("🌟 Currently Popular Movies")
if popular:
    cols_p = st.columns(5)
    for i, mv in enumerate(popular[:10]):
        with cols_p[i % 5]:
            poster = f"https://image.tmdb.org/t/p/w342{mv.get('poster_path')}" if mv.get('poster_path') else None
            if poster:
                st.image(poster, use_container_width=True)
            else:
                st.image(svg_placeholder(220, 220, 'No image'), use_container_width=True)
            st.caption(f"{mv.get('title')} — ⭐ {mv.get('vote_average')}")
else:
    st.info("Popular movies not available (no TMDb key or an error occurred).")


st.subheader("🎬 Top Movies by Genre (live)")
genres_live = {
    'Action': 28, 'Adventure': 12, 'Animation': 16, 'Comedy': 35,
    'Crime': 80, 'Drama': 18, 'Fantasy': 14, 'Horror': 27,
    'Science Fiction': 878, 'Thriller': 53, 'Romance': 10749
}
selected_genre_name_live = st.selectbox("Choose a genre (live):", options=list(genres_live.keys()))
if selected_genre_name_live:
    gid = genres_live[selected_genre_name_live]

    @st.cache_data
    def fetch_tmdb_genre_top(genre_id):
        if not API_KEY:
            return []
        try:
            url = f"https://api.themoviedb.org/3/discover/movie?api_key={API_KEY}&language=en-US&sort_by=vote_average.desc&vote_count.gte=500&with_genres={genre_id}"
            r = requests.get(url, timeout=8)
            r.raise_for_status()
            return r.json().get('results', [])
        except Exception:
            return []

    genre_movies = fetch_tmdb_genre_top(gid) if API_KEY else []
    if genre_movies:
        cols_g = st.columns(5)
        for i, mv in enumerate(genre_movies[:10]):
            with cols_g[i % 5]:
                poster = f"https://image.tmdb.org/t/p/w342{mv.get('poster_path')}" if mv.get('poster_path') else None
                if poster:
                    st.image(poster, use_container_width=True)
                else:
                    st.image(svg_placeholder(220, 220, 'No image'), use_container_width=True)
                st.caption(f"{mv.get('title')} — ⭐ {mv.get('vote_average')}")
                
               
                with st.expander("Reviews"):
                    
                    with st.spinner("Fetching live reviews..."):
                        reviews = tmdb_get_reviews(mv.get('id'))
                    if not reviews:
                        st.write("No recent reviews found.")
                    else:
                       
                        for r in reviews[:3]:
                            author = html.escape(r.get('author', 'unknown'))
                            content = r.get('content', '') or ''
                            sentiment = analyze_sentiment(content)
                            snippet = html.escape(content[:300])
                            full = html.escape(content)
                            st.markdown(f"**{author}** — {sentiment}")
                            st.markdown(
                                f"<div style='padding:8px; margin-bottom:6px; border-radius:6px; background:#f7f7f7; border:1px solid #eee; color:black;'>{snippet}{'...' if len(content)>300 else ''}</div>",
                                unsafe_allow_html=True
                            )
                            if len(content) > 300:
                                st.markdown(
                                    f"<details><summary style='color:blue; cursor:pointer;'>Read full review</summary><p style='white-space:pre-wrap; color:black; background:#f7f7f7; padding:5px; border-radius:4px;'>{full}</p></details>",
                                    unsafe_allow_html=True
                                )
    else:
        st.info("No live movies found for this genre (or TMDb key missing).")
