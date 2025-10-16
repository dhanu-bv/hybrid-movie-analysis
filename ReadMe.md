# 🎬 Hybrid Movie Analysis Dashboard

[![Python](https://img.shields.io/badge/Python-3.10-blue)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30-orange)](https://streamlit.io/)


A **hybrid movie analysis platform** combining **precomputed Spark results** with **live TMDb data** to provide rich insights into movies by genre, ratings, and sentiment analysis of reviews.

---

## 📌 Overview
Hybrid Movie Analysis is designed to provide:
- **Top 10 movies by genre** from historical Spark analysis.
- **Live enrichment from TMDb API** including movie posters, ratings, and reviews.
- **Sentiment analysis** of reviews using TextBlob.
- **Interactive Streamlit dashboard** for a seamless visual experience.

---

## 🌟 Key Features
- Display **Top Movies per Genre** with ratings and counts.
- **Filter movies** by minimum rating.
- **Live TMDb Popular Movies** with poster, rating, and sentiment.
- **Live Top Movies by Genre** with up-to-date TMDb data.
- **Review sentiment analysis**: Positive ✅, Neutral ➖, Negative ❌.
- SVG placeholder for movies without posters.
- Clean, responsive, and interactive dashboard UI.

---

## 🛠 Technologies Used
- **Backend:** Python, Pandas, TextBlob, Requests
- **Frontend / Dashboard:** Streamlit
- **Data Processing:** Apache Spark (precomputed CSV/Parquet results)
- **APIs:** TMDb (The Movie Database)
- **Others:** HTML for rendering reviews safely, glob & os for file handling

---

## 🗂 Project Structure
Hybrid-Movie-Analysis/
├── app.py # Main Streamlit application
├── process_data.py # Data processing script
├── generate_static_site.py # Optional static site generation
├── analysis_results/ # Precomputed Spark CSV/Parquet results
├── ml-latest-small/ # Raw movie dataset files
├── debug_spark.py # Spark debugging utilities
├── debug_spark_run.txt # Spark run logs
├── requirements.txt # Python dependencies
└── README.md # Project documentation


## Installation
1. Clone the repo: `git clone https://github.com/dhanu-bv/hybrid-movie-analysis.git`
2. Install dependencies: `pip install -r requirements.txt`
3. Add your TMDb API key in `app.py`
4. Run: `streamlit run app.py`
