import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from flask_monitoringdashboard.core.notification.notification_content import NotificationContent


def send_email(notification_content: NotificationContent):
    from flask_monitoringdashboard import config

    message = MIMEMultipart('alternative')

    message['Subject'] = notification_content.title
    message['From'] = config.smtp_user
    message['To'] = ', '.join(config.smtp_to)

    message.attach(MIMEText(notification_content.body_text, 'plain'))
    message.attach(MIMEText(notification_content.body_html, 'html'))

    with smtplib.SMTP(config.smtp_host, int(config.smtp_port)) as smtp:
        smtp.starttls()
        smtp.login(config.smtp_user, config.smtp_password)
        smtp.sendmail(config.smtp_user, config.smtp_to, message.as_string())
        smtp.quit()
