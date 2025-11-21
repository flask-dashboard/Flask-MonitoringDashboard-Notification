import html
import traceback
from datetime import datetime

from flask import render_template

from flask_monitoringdashboard.core.config import Config


class AlertContent:

    def __init__(self, exception: BaseException, config: Config):
        self._exception = exception

        self.created_at = datetime.now(config.timezone)
        self.send_at = None  # When was the alert sent, None if not sent yet

        self.exception_type = exception.__class__.__name__

        self.title = self._create_title(exception)
        self.stack_trace = ''.join(traceback.format_exception(type(exception), exception, exception.__traceback__))
        self.body_text = self._create_body_text(exception)
        self.body_markdown = self._create_body_markdown(exception)
        self.body_html = self._create_body_html(exception)

    def _create_title(self, exception: BaseException) -> str:
        return f"[{exception.__class__.__name__}] Uncaught exception at {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}"

    def _create_body_text(self, exception: BaseException) -> str:
        return f"An exception of type {exception.__class__.__name__} \n\nStack Trace: {self.stack_trace}"

    def _create_body_markdown(self, exception: BaseException) -> str:
        return (
            f"**Type:** `{exception.__class__.__name__}`\n"
            f"**Timestamp:** `{self.created_at.strftime('%Y-%m-%d %H:%M:%S')}`\n"
            f"**Stack Trace:**\n```\n{self.stack_trace}\n```"
        )

    def _create_body_html(self, exception):
        return render_template(
            "alert/report.html",
            exc_type=exception.__class__.__name__,
            timestamp=self.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            stacktrace=self.stack_trace
        )
