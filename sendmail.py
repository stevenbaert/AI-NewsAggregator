import smtplib
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os
import sys

load_dotenv()

from_address = os.getenv("FROM_ADDRESS")
to_address = os.getenv("TO_ADDRESS")

# Read the HTML content
# sys.argv[1]: Specifies the HTML file to be sent as the email body.
# Example: "html/news.html"
with open(sys.argv[1], "r") as file:
    html_content = file.read()

# Create the email
msg = MIMEMultipart()
msg["Subject"] = sys.argv[3]  # Email title from command-line argument
msg["From"] = from_address
msg["To"] = to_address

# Attach the HTML content
part1 = MIMEText(html_content, "html")
msg.attach(part1)

# Attach the logfile
with open(sys.argv[2], "rb") as file:
    part2 = MIMEBase("application", "octet-stream")
    part2.set_payload(file.read())
encoders.encode_base64(part2)
part2.add_header(
    "Content-Disposition", f'attachment; filename="{os.path.basename(sys.argv[2])}"'
)
msg.attach(part2)

username = os.getenv("GMAIL_USERNAME")
password = os.getenv("GMAIL_PASSWORD")

try:
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.ehlo()
    server.starttls()
    server.login(username, password)
    server.sendmail(from_address, to_address, msg.as_string())
    server.quit()
except Exception as e:
    print(f"Failed to send email: {e}")
