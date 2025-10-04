"""
generate_static_site.py

Create a single static HTML page showing the top-10 movies per genre using
analysis_results/top10_movies_per_genre.csv.

Optional poster embedding: set TMDB_API_KEY environment variable before running
so the script will fetch posters and save them under static/posters/ and link
locally in the generated page. If no API key is set, the page will render with
placeholder images and links that perform a TMDb search when clicked.

Usage:
    # Without posters
    python generate_static_site.py

    # With posters (recommended if you want images):
    $env:TMDB_API_KEY = "your_key_here"
    python generate_static_site.py

Output:
    analysis_results/top10_movies_per_genre.html
    static/posters/ (optional, when TMDB_API_KEY is provided)

"""
import os
import sys
import csv
import pandas as pd
import requests
import pathlib
import html
from urllib.parse import quote_plus

ROOT = pathlib.Path(__file__).parent.resolve()
CSV_PATH = ROOT / 'analysis_results' / 'top10_movies_per_genre.csv'
OUT_HTML = ROOT / 'analysis_results' / 'top10_movies_per_genre.html'
POSTER_DIR = ROOT / 'static' / 'posters'
TMDB_KEY = os.environ.get('TMDB_API_KEY')
TMDB_IMAGE_BASE = 'https://image.tmdb.org/t/p/w342'

PLACEHOLDER_SVG = (
    "data:image/svg+xml;utf8,"
    "<svg xmlns='http://www.w3.org/2000/svg' width='300' height='450' viewBox='0 0 300 450'>"
    "<rect width='100%' height='100%' fill='%23e8e8e8'/>"
    "<text x='50%' y='50%' dominant-baseline='middle' text-anchor='middle' fill='%23666' font-size='18'>No Image</text>"
    "</svg>"
)


def slugify(text: str) -> str:
    keep = []
    for c in text.lower():
        if c.isalnum():
            keep.append(c)
        elif c in (' ', '-', '_'):
            keep.append('-')
    s = ''.join(keep)
    
    while '--' in s:
        s = s.replace('--', '-')
    return s.strip('-')[:120]


def fetch_tmdb_poster(title: str):
    """Search TMDb for the movie title and return local poster path if downloaded.
    Returns None if not found or TMDB_KEY is not set.
    """
    if not TMDB_KEY:
        return None
   
    try:
        url = f'https://api.themoviedb.org/3/search/movie?api_key={TMDB_KEY}&query={quote_plus(title)}'
        r = requests.get(url, timeout=8)
        r.raise_for_status()
        data = r.json()
        if not data.get('results'):
            return None
        
        poster_path = data['results'][0].get('poster_path')
        if not poster_path:
            return None
        image_url = TMDB_IMAGE_BASE + poster_path
        
        POSTER_DIR.mkdir(parents=True, exist_ok=True)
        filename = slugify(title) + (pathlib.Path(poster_path).suffix or '.jpg')
        out_file = POSTER_DIR / filename
        
        if not out_file.exists():
            with requests.get(image_url, stream=True, timeout=10) as ir:
                ir.raise_for_status()
                with open(out_file, 'wb') as f:
                    for chunk in ir.iter_content(1024 * 8):
                        if chunk:
                            f.write(chunk)
        return out_file.relative_to(ROOT).as_posix()
    except Exception as e:
       
        return None


def generate_html(df: pd.DataFrame):
    genres = sorted(df['genre'].dropna().unique())

    nav_items = []
    sections = []
    for genre in genres:
        subset = df[df['genre'] == genre].sort_values(['avg_rating', 'rating_count'], ascending=[False, False]).head(10)
        if subset.empty:
            continue
        section_id = slugify(genre) or 'genre'
        nav_items.append((genre, section_id))

        cards = []
        for _, row in subset.iterrows():
            title = row['title']
            rating = round(float(row['avg_rating']), 2) if not pd.isna(row['avg_rating']) else ''
            count = int(row['rating_count']) if not pd.isna(row['rating_count']) else 0
            poster_local = None
            if TMDB_KEY:
                poster_local = fetch_tmdb_poster(title)
            if poster_local:
                img_src = poster_local
            else:
               
                tmdb_search = f'https://www.themoviedb.org/search?query={quote_plus(title)}'
                img_src = PLACEHOLDER_SVG
            escaped_title = html.escape(title)
            tmdb_search = f'https://www.themoviedb.org/search?query={quote_plus(title)}'
            card_html = f"""
            <div class="card">
                <a href="{tmdb_search}" target="_blank">
                    <img src="{img_src}" alt="{escaped_title}"/>
                </a>
                <div class="meta">
                    <div class="title">{escaped_title}</div>
                    <div class="rating">⭐ {rating} — {count} ratings</div>
                </div>
            </div>
            """
            cards.append(card_html)

        section_html = f"""
        <section id="{section_id}">
            <h2>{html.escape(genre)}</h2>
            <div class="grid">
                {''.join(cards)}
            </div>
        </section>
        """
        sections.append(section_html)

    # build final page
    nav_html = ''.join([f'<a href="#{sid}">{html.escape(name)}</a>' for name, sid in nav_items])

    page = f"""
    <!doctype html>
    <html lang="en">
    <head>
      <meta charset="utf-8">
      <meta name="viewport" content="width=device-width,initial-scale=1">
      <title>Top 10 Movies per Genre</title>
      <style>
        body {{ font-family: Arial, sans-serif; padding: 20px; }}
        header {{ display:flex; align-items:center; justify-content:space-between; gap:20px; }}
        nav a {{ margin-right: 10px; text-decoration:none; color:#0366d6; }}
        .grid {{ display:grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap:16px; margin-bottom:40px; }}
        .card {{ background:#fff; border:1px solid #eee; padding:8px; border-radius:6px; box-shadow:0 1px 2px rgba(0,0,0,0.04); }}
        .card img {{ width:100%; height:270px; object-fit:cover; border-radius:4px; }}
        .meta {{ padding:6px 4px; }}
        .title {{ font-weight:600; font-size:14px; margin-bottom:4px; }}
        .rating {{ color:#666; font-size:13px; }}
        section h2 {{ margin-top:36px; margin-bottom:12px; border-bottom:1px solid #eee; padding-bottom:6px; }}
      </style>
    </head>
    <body>
      <header>
        <h1>Top 10 Movies per Genre</h1>
        <nav>{nav_html}</nav>
      </header>
      <main>
        {''.join(sections)}
      </main>
    </body>
    </html>
    """
    return page


def main():
    if not CSV_PATH.exists():
        print(f'CSV not found at {CSV_PATH}. Run process_data.py first.')
        sys.exit(1)
    df = pd.read_csv(CSV_PATH)
    html_text = generate_html(df)
    OUT_HTML.parent.mkdir(parents=True, exist_ok=True)
    OUT_HTML.write_text(html_text, encoding='utf-8')
    print(f'Generated static site: {OUT_HTML}')
    if TMDB_KEY:
        print(f'Posters (if found) saved under: {POSTER_DIR}')


if __name__ == '__main__':
    main()
