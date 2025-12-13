import importlib.resources
import os
import traceback
from datetime import datetime

from jinja2 import Environment, FileSystemLoader

import flask_monitoringdashboard
from flask_monitoringdashboard.core.config import Config

template_root = os.path.join(importlib.resources.files(flask_monitoringdashboard).__str__(), 'templates', 'alert')
template_env = Environment(loader=FileSystemLoader(template_root))
template = template_env.get_template('report.html')


class AlertContent:

    def __init__(self, exception: BaseException, config: Config, url: str):
        self._exception = exception

        self.created_at = datetime.now(config.timezone)
        self.created_at_str = self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        self.send_at = None  # When was the alert sent, None if not sent yet

        self.exception_type = exception.__class__.__name__

        self.title = self._create_title()
        self.stack_trace = ''.join(traceback.format_exception(type(exception), exception, exception.__traceback__))

        self.url = url

    def _create_title(self) -> str:
        return f"[{self.exception_type}] Uncaught exception at {self.created_at_str}"

    def get_limited_stack_trace(self, char_limit: int | None) -> str:
        if not char_limit:
            return self.stack_trace
        return self.stack_trace[:char_limit] + ('...' if len(self.stack_trace) > char_limit else '')

    def create_body_text(self, char_limit: int | None) -> str:
        return f"An exception of type {self.exception_type} \n\nStack Trace: {self.get_limited_stack_trace(char_limit)}"

    def create_body_markdown(self, char_limit: int | None) -> str:
        return (
            f"**Type:** `{self.exception_type}`\n"
            f"**Timestamp:** `{self.created_at_str}`\n"
            f"**Stack Trace:**\n```\n{self.get_limited_stack_trace(char_limit)}\n```"
        )

    def create_body_mrkdwn(self, char_limit: int | None) -> str:
        return (
            f"*Type:* `{self.exception_type}`\n"
            f"*Timestamp:* `{self.created_at_str}`\n"
            f"*Stack Trace:*\n```\n{self.get_limited_stack_trace(char_limit)}\n```"
        )

    def create_body_html(self, char_limit: int | None) -> str:
        return template.render(
            exc_type=self.exception_type,
            timestamp=self.created_at_str,
            stacktrace=self.get_limited_stack_trace(char_limit)
        )
