from sqlalchemy.orm import Session

from flask_monitoringdashboard.core.config import Config
from . import chat, email, issue
from .alert_content import AlertContent


def send_alert(
        exception: BaseException,
        session: Session,
        config: Config):
    from flask_monitoringdashboard.database.exception_occurrence import (
        check_if_stack_trace_exists,
    )

    if not check_if_stack_trace_exists(session, exception, exception.__traceback__):
        # Create alert content
        alert_content = AlertContent(exception, config)
        types = config.alert_type

        if 'email' in types:
            email.send_email(alert_content)
        if 'issue' in types:
            # Send Post Request to repository to create issue
            issue.create_issue(config.github_token, config.repository_owner, config.repository_name, alert_content)
        if 'chat' in types:
            chat.send_message(alert_content)
    else:
        print('Stack trace already exists in DB, no alert sent.')
