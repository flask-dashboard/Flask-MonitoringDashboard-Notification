import smtplib

from email.message import EmailMessage


def send_email(subject, body):
    from flask_monitoringdashboard import config

    message = EmailMessage()
    message.set_content(body)

    message['Subject'] = subject
    message['From'] = config.smtp_user
    message['To'] = config.smtp_to

    with smtplib.SMTP(config.smtp_host, int(config.smtp_port)) as smtp:
        smtp.starttls()
        smtp.login(config.smtp_user, config.smtp_password)
        smtp.send_message(message)