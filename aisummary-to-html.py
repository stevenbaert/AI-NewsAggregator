import pandas as pd
import os
from initialize import get_current_timestamp, log_message, initialize_log_file

# Initialize log directory

log_file = os.getenv("LOG_FILE")
if not log_file:
    log_file, _ = initialize_log_file()
    os.environ["LOG_FILE"] = log_file


def load_css(file_path):
    with open(file_path, "r") as f:
        return f.read()


def format_summary(summary):
    if summary:
        log_message(f"Formatting summary.", log_file)

        parts = summary.split("**Takeaways:**")
        main_summary = parts[0].replace("**Summary:**", "").strip()
        takeaways = parts[1].strip() if len(parts) > 1 else ""

        takeaways_list = takeaways.split("\n- ")
        takeaways_html = "<ul>"
        for i, takeaway in enumerate(takeaways_list):
            if i == 0:
                takeaways_html += f"<li>{takeaway.lstrip('- ').strip()}</li>"
            else:
                takeaways_html += f"<li>{takeaway.strip()}</li>"
        takeaways_html += "</ul>"

        formatted_summary = (
            f"{main_summary}<br><br><strong>Takeaways:</strong>{takeaways_html}"
        )
        return formatted_summary
    else:
        log_message(f"No summary available.", log_file)
        return "No summary available"


def main(image_size=200):
    log_message(
        f"Starting aisummarizertohtml script.",
        log_file,
    )

    log_message(f"Reading CSV file.", log_file)
    data = pd.read_csv("./data/aisummary.csv")

    log_message(f"Loading CSS.", log_file)
    css_content = load_css("./aisummary.css")

    log_message(f"Initializing HTML content.", log_file)

    html_content = f"""<html>
    <head>
        <title>AI Summary</title>
        <style>
        {css_content}
        </style>
    </head>
    <body>
    <h1 class="centered">Here is your AI-generated newsletter</h1>"""

    for index, row in data.iterrows():
        log_message(
            f"Formatting summary for row {index}.",
            log_file,
        )

        formatted_summary = format_summary(row["aisummary"])

        if pd.isna(row["urltoimage"]):
            image_url = (
                "https://www.stevenbaert.ai/wp-content/uploads/2023/08/image-31.png"
            )
        elif ".jpg?" in row["urltoimage"]:
            image_url = (
                "https://www.stevenbaert.ai/wp-content/uploads/2023/08/image-31.png"
            )
        else:
            image_url = row["urltoimage"]

        html_content += f'<h2 class="centered">{row["title"]}</h2>'
        html_content += f'<h6 class="centered">Published At: {row["publishedat"]}</h6>'
        html_content += f'<div class="centered"><img src="{image_url}" width="{image_size}"></div><br>'
        html_content += '<table id="customers">'
        html_content += f"<tr><th>Description</th><td>{row['description']}</td></tr>"
        html_content += f"<tr><th>AISummary</th><td>{formatted_summary}</td></tr>"
        html_content += (
            f"<tr><th>URL</th><td><a href='{row['url']}'>{row['url']}</a></td></tr>"
        )
        html_content += "</table><br>"

    html_content += "</body></html>"

    log_message(f"Writing HTML content to file.", log_file)

    with open("./html/aisummary.html", "w") as html_file:
        html_file.write(html_content)

    log_message(f"HTML file created successfully.", log_file)


if __name__ == "__main__":
    main(image_size=200)
