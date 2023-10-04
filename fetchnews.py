# fetchnews.py
import os
from dotenv import load_dotenv
import datetime
import requests

from initialize import log_message, get_current_timestamp, initialize_log_file
import pandas as pd

# Load environment variables
load_dotenv()

log_file = os.getenv("LOG_FILE")
if not log_file:
    log_file, _ = initialize_log_file()
    os.environ["LOG_FILE"] = log_file

fetchnewarticles = os.getenv("fetchnewarticles")

NUM_ARTICLES = int(os.getenv("FETCH_NUM_ARTICLES"))
SEARCH_TERMS = os.getenv("SEARCH_TERMS").split(",")


def get_articles(api_keys, from_date, to_date, log_file):
    all_articles = []
    for api_key in api_keys:
        for idx, term in enumerate(SEARCH_TERMS):
            log_message(
                f"Fetching articles for search term {idx+1}/{len(SEARCH_TERMS)}: {term}",
                log_file,
            )

            url = "https://newsapi.org/v2/everything"
            parameters = {
                "q": term,
                "pageSize": NUM_ARTICLES,
                "apiKey": api_key,
                "language": "en",
                "from": from_date,
                "to": to_date,
                "sortBy": "publishedAt",
            }
            try:
                response = requests.get(url, params=parameters)
                if response.status_code == 429:
                    log_message(
                        "API key rate limit reached. Switching keys...", log_file
                    )
                    break
                response.raise_for_status()
            except Exception as e:
                log_message(f"An error occurred: {e}", log_file)
                return []

            articles = response.json().get("articles", [])
            log_message(
                f"Fetched {len(articles)} articles for search term: {term}", log_file
            )

            for article in articles:
                article["search_term"] = term
            all_articles.extend(articles)
        else:
            return all_articles
    log_message("All API keys have too many requests. Exiting...", log_file)
    exit(1)


if __name__ == "__main__":
    log_message(f"Starting fetchnews.py script.", log_file)

    if fetchnewarticles == "1":
        now = datetime.datetime.now()
        two_days_ago = now - datetime.timedelta(days=2)

        api_keys = os.getenv("NEWS_API_KEY").split(",")
        articles = get_articles(
            api_keys,
            two_days_ago.strftime("%Y-%m-%dT%H:%M:%S"),
            now.strftime("%Y-%m-%dT%H:%M:%S"),
            log_file,
        )

        df = pd.DataFrame(
            [article for article in articles if article["content"] is not None]
        )

        original_count = len(df)
        df.drop_duplicates(subset=["url"], inplace=True)
        new_count = len(df)

        log_message(
            f"Removed {original_count - new_count} duplicate articles based on URL.",
            log_file,
        )

        df["publishedAt"] = pd.to_datetime(df["publishedAt"])
        df.sort_values(by="publishedAt", ascending=False, inplace=True)
        df["publishedAt"] = df["publishedAt"].dt.strftime("%d-%m-%y")

        df.to_csv(
            "data/news.csv",
            index=False,
            columns=[
                "title",
                "description",
                "publishedAt",
                "url",
                "urlToImage",
                "search_term",
            ],
            encoding="utf-8",
        )

        log_message(f"Processed {len(df)} articles and saved to CSV.", log_file)
    else:
        df = pd.read_csv("data/news.csv", encoding="utf-8")

    # Generate HTML
    html = '<table id="customers">'
    html += "<thead><tr>"
    for col in ["Title", "Description", "PublishedAt", "URL", "Image", "Search Term"]:
        html += f"<th>{col}</th>"
    html += "</tr></thead><tbody>"

    for i, row in df.iterrows():
        html += "<tr>"
        html += (
            f'<td style="white-space: nowrap; font-weight: bold;">{row["title"]}</td>'
        )
        html += f'<td>{row["description"]}</td>'
        html += f'<td>{row["publishedAt"]}</td>'
        html += f'<td>{row["url"]}</td>'
        html += f'<td>{row["urlToImage"]}</td>'
        html += f'<td>{row.get("search_term", "N/A")}</td>'
        html += "</tr>"

    html += "</tbody></table>"

    with open("html/news.html", "w") as f:
        f.write(
            f"""<html><head><style>
        #customers {{
          font-family: Arial, Helvetica, sans-serif;
          border-collapse: collapse;
          width: 100%;
        }}
        #customers td, #customers th {{
          border: 1px solid #ddd;
          padding: 8px;
        }}
        #customers tr:nth-child(even){{background-color: #f2f2f2;}}
        #customers tr:hover {{background-color: #ddd;}}
        #customers th {{
          padding-top: 12px;
          padding-bottom: 12px;
          text-align: left;
          background-color: #333333;
          color: white;
        }}
        </style></head><body><h1>Here is your overview:</h1>{html}</body></html>"""
        )

    log_message(f"HTML file generated.", log_file)
