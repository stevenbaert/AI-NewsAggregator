from dotenv import load_dotenv
import os
import subprocess
from initialize import (
    log_message,
    get_current_timestamp,
    cleanup_old_logs,
    initialize_log_file,
    log_dir,
)

load_dotenv()

# Load email subjects from .env file
StandardNewsMailSubject = os.getenv("StandardNewsMailSubject")
AIGeneratedNewsMailSubject = os.getenv("AIGeneratedNewsMailSubject")
SendAlsoStandardMail = os.getenv("SendAlsoStandardMail")
# os.getenv("LOG_DIR")

log_file = os.getenv("LOG_FILE")

if not log_file:
    log_file, _ = initialize_log_file()
    os.environ["LOG_FILE"] = log_file

# Append a log entry
with open(log_file, "a") as file:
    file.write("Log entry\n")

with open(log_file, "w") as f:
    log_message(f"Starting the script.", log_file)

    # Run the fetchnews.py script and log its output
    log_message(f"*** RUNNING *** fetchnews.py.", log_file)
    process = subprocess.run(["python3", "fetchnews.py"], stdout=subprocess.PIPE)
    if process.returncode == 0:
        log_message(f"*** SUCCESSFULLY *** ran fetchnews.py.", log_file)
        log_message(process.stdout.decode("utf-8"), log_file)

        # Continue with ai-filterfetchnews.py
        log_message(f"*** RUNNING *** ai-filterfetchnews.py.", log_file)
        process = subprocess.run(
            ["python3", "ai-filterfetchnews.py"], stdout=subprocess.PIPE
        )
        if process.returncode == 0:
            log_message(f"*** SUCCESSFULLY *** ran ai-filterfetchnews.py.", log_file)
            log_message(process.stdout.decode("utf-8"), log_file)

            # Continue with news-scraper.py
            log_message(f"*** RUNNING *** news-scraper.py.", log_file)
            process = subprocess.run(
                ["python3", "news-scraper.py"], stdout=subprocess.PIPE
            )
            if process.returncode == 0:
                log_message(f"*** SUCCESSFULLY *** ran news-scraper.py.", log_file)
                log_message(process.stdout.decode("utf-8"), log_file)

                # Continue with ai-summarizer.py
                log_message(f"*** RUNNING *** ai-summarizer.py.", log_file)
                process = subprocess.run(
                    ["python3", "ai-summarizer.py"], stdout=subprocess.PIPE
                )
                if process.returncode == 0:
                    log_message(f"*** SUCCESSFULLY *** ran ai-summarizer.py.", log_file)
                    log_message(process.stdout.decode("utf-8"), log_file)

                    # Continue with sendmail.py
                    log_message(f"*** RUNNING *** sendmail.py.", log_file)
                    if SendAlsoStandardMail == "1":
                        process1 = subprocess.run(
                            [
                                "python3",
                                "sendmail.py",
                                "html/news.html",
                                log_file,
                                StandardNewsMailSubject,
                            ],
                            stdout=subprocess.PIPE,
                        )
                        if process1.returncode == 0:
                            log_message(
                                f"Email sent *** SUCCESSFULLY *** with subject {StandardNewsMailSubject}.",
                                log_file,
                            )
                        else:
                            log_message(
                                f"Failed to send email with subject {StandardNewsMailSubject}.",
                                log_file,
                            )

                    process2 = subprocess.run(
                        [
                            "python3",
                            "sendmail.py",
                            "html/aisummary.html",
                            log_file,
                            AIGeneratedNewsMailSubject,
                        ],
                        stdout=subprocess.PIPE,
                    )
                    if process2.returncode == 0:
                        log_message(
                            f"Email sent *** SUCCESSFULLY *** with subject {AIGeneratedNewsMailSubject}.",
                            log_file,
                        )
                    else:
                        log_message(
                            f"Failed to send email with subject {AIGeneratedNewsMailSubject}.",
                            log_file,
                        )
                else:
                    log_message(f"Failed to run ai-summarizer.py.", log_file)
            else:
                log_message(f"Failed to run news-scraper.py.", log_file)
        else:
            log_message(f"Failed to run ai-filterfetchnews.py.", log_file)
    else:
        log_message(f"Failed to run fetchnews.py.", log_file)

    # Cleanup old log files
    log_message(f"Cleaning up old log files.", log_file)
    cleanup_old_logs(log_dir)

    log_message(f"Finished running the script.", log_file)
