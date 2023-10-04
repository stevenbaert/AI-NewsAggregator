import csv
import subprocess
import time
from dotenv import load_dotenv
from initialize import log_message, get_current_timestamp, initialize_log_file
import pandas as pd
import os
from azureopenaicall import call_azureopenai  # Assuming you have this module

log_file = os.getenv("LOG_FILE")
if not log_file:
    log_file, _ = initialize_log_file()
    os.environ["LOG_FILE"] = log_file

def main():
    new_table = []
    token_usage_table = []

    log_message("Initializing the program...", log_file)

    try:
        with open("./data/tokenusage.csv", "r") as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                token_usage_table.append(row)
    except FileNotFoundError:
        log_message("Token usage file not found. Creating a new one.", log_file)
        token_usage_table.append(["Script Name", "Token Usage"])

    num_items_enabled = False
    num_items = 3

    log_message("Reading the existing news CSV file...", log_file)

    start_total_time = time.time()

    try:
        with open("./data/news-scraped.csv", "r") as csvfile:
            reader = csv.reader(csvfile)
            next(reader)
            total_items = sum(1 for row in reader)
            csvfile.seek(0)
            next(reader)

            for i, row in enumerate(reader):
                if num_items_enabled and i >= num_items:
                    break

                start_time = time.time()
                title, description, publishedat, url, urltoimage, search_term, scraped_data = row

                log_message(f"Processing item {i+1}/{total_items} - {title}...", log_file)

                user_instruction = "Summarize only the relevant part of this text in a Summary section, put short summary in one or two lines,then add two blank spaces then add **Takeaways:** under that in few bullet points but don't put the text Further takeaways, make sure each bullet point starts on new line: "

                result = call_azureopenai(user_instruction, scraped_data)

                # Added exception handling and key checking here
                try:
                    aisummary = result.get("choices", [{}])[0].get("message", {}).get("content", None)
                    token_usage = result.get("usage", {}).get("total_tokens", None)

                    if aisummary is None or not isinstance(aisummary, str) or len(aisummary) < 10:
                        log_message(f"Summary not generated or too short for {title}. Skipping.", log_file)
                        continue

                except Exception as e:
                    log_message(f"Exception: {e}", log_file)
                    continue

                end_time = time.time()
                elapsed_time = end_time - start_time

                log_message(f"Processed item {i+1}/{total_items} in {elapsed_time:.2f} seconds.", log_file)

                new_row = {
                    "title": title,
                    "aisummary": aisummary,
                    "description": description,
                    "publishedat": publishedat,
                    "url": url,
                    "urltoimage": urltoimage,
                    "search_term": search_term,
                }

                new_table.append(new_row)
                token_usage_table.append(["ai-summarizer.py", token_usage])

        end_total_time = time.time()
        total_elapsed_time = end_total_time - start_total_time
        log_message(f"Total time: {total_elapsed_time:.2f} seconds.", log_file)

    except FileNotFoundError:
        log_message("CSV file not found. Check the path.", log_file)
        return

    try:
        with open("./data/aisummary.csv", "w", newline="") as csvfile:
            fieldnames = ["title", "aisummary", "description", "publishedat", "url", "urltoimage", "search_term"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for row in new_table:
                writer.writerow(row)

        with open("./data/tokenusage.csv", "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            for row in token_usage_table:
                writer.writerow(row)

        log_message("CSV files updated.", log_file)

    except PermissionError:
        log_message("Permission error. Close the file if it's open.", log_file)

    try:
        log_message("Running aisummary-to-html.py...", log_file)
        subprocess.run(["python3", "aisummary-to-html.py"], check=True)
        log_message("Successfully ran aisummary-to-html.py.", log_file)
    except subprocess.CalledProcessError as e:
        log_message(f"Failed to run aisummary-to-html.py. Error: {e}", log_file)
        raise e

    log_message("Program completed.", log_file)

if __name__ == "__main__":
    main()
