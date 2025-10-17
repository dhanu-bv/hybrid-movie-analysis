# 🎬 Hybrid Movie Analysis Dashboard

[![Python](https://img.shields.io/badge/Python-3.10-blue)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30-orange)](https://streamlit.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A **hybrid movie analysis platform** that combines **precomputed Spark results** with **live TMDb data** to provide rich, interactive insights into movies by genre, ratings, and review sentiment.

### 🚀 [**View the Live Demo**](https://hybrid-movie-analysis-fkzbng7lpr7ak2wxdyory5.streamlit.app/)

![Project Demo GIF](link-to-your-screenshot-or.gif)

---

## 📌 Overview

This dashboard solves a common challenge in data analysis: blending large-scale historical analysis with real-time data. It uses pre-processed movie rating data (computed with Apache Spark) for performance and enriches it on-the-fly with live information from the TMDb API, such as movie posters, current ratings, and reviews.

The result is a fast, responsive, and data-rich application for exploring movie trends and sentiment.

---

## 🌟 Key Features

-   **Hybrid Data Model:** Combines static, precomputed movie analytics with live API data for a comprehensive view.
-   **Interactive Genre Analysis:** Displays the top 10 movies for any selected genre based on historical ratings.
-   **Live TMDb Enrichment:** Fetches and displays up-to-date movie posters, ratings, and popular movies.
-   **Sentiment Analysis:** Performs real-time sentiment analysis on TMDb reviews, classifying them as Positive ✅, Neutral ➖, or Negative ❌ using TextBlob.
-   **Dynamic Filtering:** Allows users to filter movies by a minimum rating threshold.
-   **Clean & Responsive UI:** Built with Streamlit for a seamless and intuitive user experience.

---

## 🛠️ Architecture & Tech Stack

The application follows a two-stage data pipeline:

1.  **Offline Processing (Apache Spark):** The raw MovieLens dataset is processed in a Spark environment to compute historical top movies by genre. The results are saved as CSV files for fast loading.
2.  **Online Dashboard (Streamlit):** The Streamlit app loads the precomputed data and enriches it in real-time by making calls to the TMDb API for posters, reviews, and live popularity metrics.

-   **Data Processing:** Apache Spark, Pandas
-   **Backend & Logic:** Python, TextBlob
-   **Frontend / Dashboard:** Streamlit
-   **APIs:** TMDb (The Movie Database)
-   **Data Source:** [MovieLens 25M Dataset](https://grouplens.org/datasets/movielens/latest/)

---

## ⚙️ Getting Started

Follow these instructions to set up and run the project locally.

### Prerequisites

-   Python 3.8+
-   Git

### Installation & Setup

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/dhanu-bv/hybrid-movie-analysis.git](https://github.com/dhanu-bv/hybrid-movie-analysis.git)
    cd hybrid-movie-analysis
    ```

2.  **Install the required dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Set up your TMDb API Key (Securely):**
    * Create a `.streamlit` directory in your project's root folder.
    * Inside `.streamlit`, create a file named `secrets.toml`.
    * Add your TMDb API key to this file like so:
        ```toml
        # .streamlit/secrets.toml
        TMDB_API_KEY = "your_tmdb_api_key_goes_here"
        ```
    * *The `app.py` is already configured to read this secret, so you don't need to paste the key into the main script.*

4.  **Run the Streamlit application:**
    ```bash
    streamlit run app.py
    ```

---
```
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
```

---

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE.md) file for details.
*(**Note:** You'll need to add a `LICENSE.md` file with the MIT license text to your repo for this link to work.)*
