import traceback
from datetime import datetime
from flask_monitoringdashboard.core.config import Config


class NotificationContent:

    def __init__(self, exception: BaseException, config: Config):
        self._exception = exception

        self.created_at = datetime.now(config.timezone)
        self.send_at = None # When was the notification sent, None if not sent yet

        self.notification_type = None
        self.exception_type = exception.__class__.__name__
        
        self.title = self._create_title(exception)
        self.stack_trace = ''.join(traceback.format_exception(type(exception), exception, exception.__traceback__))
        self.body_text = self._create_body_text(exception)
        self.body_markdown = self._create_body_markdown(exception)
        self.body_html = self._create_body_html(exception)


    def _create_title(self, exception: BaseException) -> str:
        # This is going to be in the 
        return f"[{exception.__class__.__name__}] Uncaught exception at {self.created_at.strftime("%Y-%m-%d %H:%M:%S")}"

    def _create_body_text(self, exception: BaseException) -> str:
        return f"An exception of type {exception.__class__.__name__} \n\nStack Trace: {self.stack_trace}"
    
    def _create_body_markdown(self, exception: BaseException) -> str:
        return f"""**Type:** `{exception.__class__.__name__}`
                   **Timestamp:** `{self.created_at.strftime("%Y-%m-%d %H:%M:%S")}`
                   **Stack Trace:** {self.stack_trace}"""

    def _create_body_html(self, exception: BaseException) -> str:
        import html

        # TODO this is not nice, should be in a separate template file
        return f"""<!doctype html>
        <html lang='en'>
        <head>
        <meta charset='utf-8'>
        <meta name='viewport' content='width=device-width, initial-scale=1.0'>
        <title>Exception Report</title>
        <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; margin: 0; padding: 20px; color: #111; }}
        .card {{ border: 1px solid #e1e1e1; border-radius: 6px; padding: 16px; background: #ffffff; max-width: 700px; }}
        .row {{ margin-bottom: 12px; }}
        .label {{ font-weight: 600; display: inline-block; width: 110px; vertical-align: top; }}
        .value {{ display: inline-block; max-width: 560px; }}
        code.inline {{ background: #f5f5f5; padding: 2px 6px; border-radius: 4px; font-family: monospace; }}
        pre.trace {{ background: #0f1720; color: #e6eef8; padding: 12px; border-radius: 6px; overflow-x: auto; white-space: pre-wrap; font-family: Menlo, Monaco, monospace; font-size: 13px; }}
        </style>
        </head>
        <body>
        <div class='card'>
        <div class='row'>
        <span class='label'>Type:</span>
        <span class='value'><code class='inline'>{html.escape(exception.__class__.__name__)}</code></span>
        </div>
    
    
        <div class='row'>
        <span class='label'>Timestamp:</span>
        <span class='value'><code class='inline'>{html.escape(self.created_at.strftime('%Y-%m-%d %H:%M:%S'))}</code></span>
        </div>
    
    
        <div class='row'>
        <span class='label'>Stack Trace:</span>
        <div class='value'>
        <pre class='trace'>{html.escape(self.stack_trace)}</pre>
        </div>
        </div>
        </div>
        </body>
        </html>"""