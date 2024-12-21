import os
import aiosmtplib
from email.message import EmailMessage

# Чтение переменных окружения
ETHEREAL_HOST = os.getenv("ETHEREAL_HOST")
ETHEREAL_PORT = int(os.getenv("ETHEREAL_PORT", 587))
ETHEREAL_USER = os.getenv("ETHEREAL_USER")
ETHEREAL_PASS = os.getenv("ETHEREAL_PASS")

async def send_email(to_email: str, subject: str, html_content: str):
    """
    Отправляет email через Ethereal SMTP.
    """
    message = EmailMessage()
    message["From"] = ETHEREAL_USER
    message["To"] = to_email
    message["Subject"] = subject
    message.set_content(html_content, subtype='frontend')

    try:
        await aiosmtplib.send(
            message,
            hostname=ETHEREAL_HOST,
            port=ETHEREAL_PORT,
            username=ETHEREAL_USER,
            password=ETHEREAL_PASS,
            start_tls=True,
        )
        print(f"Email sent to {to_email}")
    except Exception as e:
        print(f"Failed to send email to {to_email}: {e}")
        raise e
