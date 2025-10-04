

import traceback
import os
import sys
import shutil
import time

def java_available():
    """Return True if a java executable is available in PATH or JAVA_HOME."""
    if shutil.which('java'):
        return True
    java_home = os.environ.get('JAVA_HOME') or os.environ.get('JDK_HOME')
    if java_home:
        java_path = os.path.join(java_home, 'bin', 'java.exe' if sys.platform == 'win32' else 'java')
        return os.path.exists(java_path)
    return False


def pandas_pipeline(movies_csv='ml-latest-small/movies.csv', ratings_csv='ml-latest-small/ratings.csv', output_dir='analysis_results'):
    """Compute the same top-10-per-genre analysis using pandas only (no Java/PySpark required)."""
    import pandas as pd
    print('Running pandas fallback pipeline...')
    movies = pd.read_csv(movies_csv)
    ratings = pd.read_csv(ratings_csv)

    
    movies['genres'] = movies['genres'].fillna('')
    movies = movies.assign(genre=movies['genres'].str.split('|'))
    movies = movies.explode('genre')

    
    merged = ratings.merge(movies[['movieId', 'title', 'genre']], on='movieId', how='left')

   
    agg = merged.groupby(['genre', 'title']).rating.agg(['count', 'mean']).reset_index()
    agg = agg.rename(columns={'count': 'rating_count', 'mean': 'avg_rating'})
    agg = agg[agg['rating_count'] > 50]

   
    agg['rank'] = agg.groupby('genre')['avg_rating'].rank(method='first', ascending=False)
    top10 = agg[agg['rank'] <= 10].sort_values(['genre', 'rank'])

    os.makedirs(output_dir, exist_ok=True)
    out_path = os.path.join(output_dir, 'top10_movies_per_genre.csv')
    top10[['genre', 'title', 'rating_count', 'avg_rating']].to_csv(out_path, index=False)
    print(f'Pandas CSV results saved to: {out_path}')


def main():
    
    if java_available():
        try:
            from pyspark.sql import SparkSession
            from pyspark.sql.functions import col, avg, count, split, explode, rank
            from pyspark.sql.window import Window

            spark = SparkSession.builder.appName("MovieAnalysis").master("local[*]").getOrCreate()
            print("Spark session created. Loading data...")

            movies_df = spark.read.csv("ml-latest-small/movies.csv", header=True, inferSchema=True)
            ratings_df = spark.read.csv("ml-latest-small/ratings.csv", header=True, inferSchema=True)

            print("Starting data analysis with Spark...")

            movies_with_genres_df = movies_df.withColumn("genre", explode(split(col("genres"), "\\|")))
            full_df = ratings_df.join(movies_with_genres_df, "movieId")

            genre_movie_stats = full_df.groupBy("genre", "title") \
                .agg(
                    count("rating").alias("rating_count"),
                    avg("rating").alias("avg_rating")
                )

            popular_genre_movies = genre_movie_stats.filter(col("rating_count") > 50)

            window_spec = Window.partitionBy("genre").orderBy(col("avg_rating").desc())
            ranked_movies = popular_genre_movies.withColumn("rank", rank().over(window_spec))

            top_10_movies_per_genre = ranked_movies.filter(col("rank") <= 10) \
                .select("genre", "title", "rating_count", "avg_rating") \
                .orderBy("genre", "rank")

            top_10_movies_per_genre.show(50)

            output_path = "analysis_results"
            print(f"Saving results to '{output_path}'...")
            
            os.makedirs(output_path, exist_ok=True)

            
            try:
                top_10_movies_per_genre.coalesce(1) \
                    .write \
                    .option("header", "true") \
                    .mode("overwrite") \
                    .parquet(output_path)
                print("Parquet results saved successfully.")
            except Exception:
                print("Parquet write failed  falling back to writing CSV via pandas. Error:")
                traceback.print_exc()
                try:
                    df_pd = top_10_movies_per_genre.toPandas()
                    csv_path = os.path.join(output_path, "top10_movies_per_genre.csv")
                    df_pd.to_csv(csv_path, index=False)
                    print(f"CSV results saved successfully to '{csv_path}'")
                except Exception:
                    print("Failed to write CSV fallback as well:")
                    traceback.print_exc()

            spark.stop()
            return
        except Exception:
            print('Spark path failed; falling back to pandas. Error:')
            traceback.print_exc()

    
    try:
        pandas_pipeline()
    except Exception:
        print('Pandas fallback also failed:')
        traceback.print_exc()


if __name__ == '__main__':
    try:
        main()
    except Exception:
        print('An exception occurred while running process_data.py')
        traceback.print_exc()
        raise
