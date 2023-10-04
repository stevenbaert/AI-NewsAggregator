import csv
import os
import pandas as pd
from dotenv import load_dotenv
from initialize import log_message, get_current_timestamp, initialize_log_file
from azureopenaicall import call_azureopenai

# Load environment variables
load_dotenv()

log_file = os.getenv("LOG_FILE")
if not log_file:
    log_file, _ = initialize_log_file()
    os.environ["LOG_FILE"] = log_file

search_terms = os.getenv("SEARCH_TERMS")

# Initialize token and cost counters
total_tokens_used = 0
total_cost_input = 0
total_cost_output = 0

# Get token costs from environment variables and convert them to float
token_cost_input = float(os.getenv("TokenCostGPT432KInput").replace(",", "."))
token_cost_output = float(os.getenv("TokenCostGPT432KOutput").replace(",", "."))


def main():
    global total_tokens_used, total_cost_input, total_cost_output
    new_table = []
    log_message(f"Starting the ai-filtering script.", log_file)

    try:
        no_count = 0
        with open("./data/news.csv", "r") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                title, description, publishedAt, url, urltoimage, search_term = (
                    row["title"],
                    row["description"],
                    row["publishedAt"],
                    row["url"],
                    row["urlToImage"],
                    row["search_term"],
                )

                text_to_check = f"{title}\n{description}"
                user_instruction = f"Is this input related to one of these subjects: {search_terms} . Only output yes or no without any bracket or formatting."

                resultplain = call_azureopenai(user_instruction, text_to_check)
                result = resultplain["choices"][0]["message"]["content"]

                log_message(f"{result} :: for {title}.", log_file)

                if result == "No":
                    no_count += 1
                    continue

                new_table.append(row)

                prompt_tokens = resultplain["usage"]["prompt_tokens"]
                completion_tokens = resultplain["usage"]["completion_tokens"]

                cost_input = prompt_tokens * token_cost_input / 1000
                cost_output = completion_tokens * token_cost_output / 1000

                total_cost_input += cost_input
                total_cost_output += cost_output

                total_tokens_used += prompt_tokens + completion_tokens

                log_message(
                    f"    // Tokens used for this query: {total_tokens_used}.", log_file
                )

        log_message(
            f"Total number of items with 'No', so being filtered from news is: {no_count}.",
            log_file,
        )

    except FileNotFoundError:
        log_message(f"File not found. Make sure the path is correct.", log_file)
        return

    csv_path = "./data/ai-filtered-news.csv"
    with open(csv_path, "w", newline="") as csvfile:
        fieldnames = [
            "title",
            "description",
            "publishedAt",
            "url",
            "urlToImage",
            "search_term",
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in new_table:
            writer.writerow(row)

    df = pd.read_csv(csv_path)
    html_path = "./html/ai-filtered-news.html"
    df.to_html(html_path, index=False)

    log_message(f"ai-filtered-news.html created in the html folder.", log_file)

    log_message(f"TOTAL TOKENS USED: {total_tokens_used}", log_file)

    token_usage_file = "./data/TokenUsage.csv"
    current_timestamp = get_current_timestamp()
    num_queries = len(new_table)

    if not os.path.exists(token_usage_file):
        with open(token_usage_file, "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(
                [
                    "Date",
                    "Script",
                    "Number of Queries",
                    "Prompt Tokens",
                    "Completion Tokens",
                    "Total Tokens",
                    "Cost Input",
                    "Cost Output",
                    "Total Cost",
                ]
            )

    with open(token_usage_file, "a", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(
            [
                current_timestamp,
                "ai-filtering script",
                num_queries,
                prompt_tokens,
                completion_tokens,
                total_tokens_used,
                total_cost_input,
                total_cost_output,
                total_cost_input + total_cost_output,
            ]
        )

    # Convert TokenUsage.csv to TokenUsage.html


# Convert TokenUsage.csv to TokenUsage.html
# # BEGIN: ed8c6549bwf9
# def convert_csv_to_html():
#     csv_path = "./data/TokenUsage.csv"
#     html_path = "./html/TokenUsage.html"

#     try:
#         # Read the CSV into a DataFrame, skipping bad lines
#         df = pd.read_csv(csv_path, error_bad_lines=False)

#         # Write the DataFrame to HTML
#         df.to_html(html_path, index=False)

#         log_message(
#             f"Successfully converted TokenUsage.csv to TokenUsage.html.", log_file
#         )

#     except Exception as e:
#         log_message(f"Error while converting TokenUsage.csv to HTML: {e}", log_file)

# # END: ed8c6549bwf9

if __name__ == "__main__":
    main()
    # convert_csv_to_html()
