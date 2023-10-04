import os
import requests
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import time
import random
from initialize import log_message, get_current_timestamp, initialize_log_file

log_file = os.getenv("LOG_FILE")
if not log_file:
    log_file, _ = initialize_log_file()
    os.environ["LOG_FILE"] = log_file


def get_random_user_agent():
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    ]
    return random.choice(user_agents)


log_message(f"Starting the newsscraper script.", log_file)
log_message(f"Loading environment variables...", log_file)

load_dotenv()

news_csv_path = "data/ai-filtered-news.csv"

log_message(f"Reading the news.csv file...", log_file)
try:
    news_df = pd.read_csv(news_csv_path)
    log_message(
        f"Successfully read the news.csv file. Found {len(news_df)} articles.",
        log_file,
    )
except FileNotFoundError:
    log_message(f"File {news_csv_path} not found.", log_file)
    exit()

log_message(
    f"Adding a new column for scraped data...",
    log_file,
)
news_df["scraped_data"] = np.nan
news_df["scraped_data"] = news_df["scraped_data"].astype("object")
log_message(f"New column added.", log_file)

log_message(f"Starting to scrape URLs...", log_file)
for i, row in news_df.iterrows():
    url = row["url"]
    if pd.notna(url):
        log_message(
            f"Scraping {i+1} of {len(news_df)}: {url}",
            log_file,
        )
        for _ in range(3):
            try:
                headers = {"User-Agent": get_random_user_agent()}
                response = requests.get(url, headers=headers)

                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, "lxml")
                    all_text = soup.get_text()
                    news_df.at[i, "scraped_data"] = all_text
                    log_message(
                        f"Successfully scraped {i+1} of {len(news_df)}.",
                        log_file,
                    )
                    break
                else:
                    log_message(
                        f"Received status code {response.status_code}. Retrying...",
                        log_file,
                    )
                time.sleep(random.uniform(1, 3))
            except Exception as e:
                log_message(
                    f"An error occurred while scraping {i+1} of {len(news_df)}: {url}. Error: {e}",
                    log_file,
                )

log_message(
    f"Saving the DataFrame to a new CSV file...",
    log_file,
)
try:
    news_df.to_csv("data/news-scraped.csv", index=False, encoding="utf-8-sig")
    log_message(
        f"Scraping completed. The data has been saved to 'data/news-scraped.csv'.",
        log_file,
    )

    # Save the DataFrame to an HTML file
    html_file_path = "html/news-scraped.html"
    log_message(
        f"Attempting to save the DataFrame to {html_file_path}...",
        log_file,
    )
    news_df.to_html(html_file_path)
    log_message(
        f"The DataFrame has been successfully saved as an HTML file in {html_file_path}.",
        log_file,
    )
except Exception as e:
    log_message(
        f"An error occurred while saving the CSV or HTML file: {e}",
        log_file,
    )

log_message(
    f"Finished running the newsscraper script.",
    log_file,
)
