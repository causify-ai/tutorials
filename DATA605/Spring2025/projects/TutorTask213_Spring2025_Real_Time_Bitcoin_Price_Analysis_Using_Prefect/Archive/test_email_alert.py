import os
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv

# Load .env variables
load_dotenv()

# ✅ Define variables AFTER loading
sender = os.getenv("ALERT_EMAIL")
password = os.getenv("EMAIL_APP_PASSWORD")
receiver = sender  # Send to self

# 🔍 Debug: Print loaded values
print(f"Sender: {sender}")
print(f"Password: {password}")

# Compose email
subject = "✅ Test Email from Bitcoin Prefect Project"
body = "This is a test email to confirm your Gmail alert configuration is working."

msg = MIMEText(body)
msg["Subject"] = subject
msg["From"] = sender
msg["To"] = receiver

# Send email
try:
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender, password)
        server.sendmail(sender, receiver, msg.as_string())
    print("✅ Test email sent successfully!")
except Exception as e:
    print(f"❌ Failed to send email: {e}")
