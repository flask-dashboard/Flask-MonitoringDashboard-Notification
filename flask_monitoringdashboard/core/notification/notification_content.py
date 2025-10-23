import traceback
from datetime import datetime, timezone

class NotificationContent:

    def __init__(self, exception: BaseException):
        self.title = self._create_title(exception)
        self.body = self._create_body(exception)
        self._exception = exception
        self.create_at = datetime.now(timezone.utc)
        self.send_at = None # When was the notification sent, None if not sent yet

        self.notification_type = None
        self.exception_type = exception.__class__.__name__


    def _create_title(self, exception: BaseException) -> str:
        return f"{exception.__class__.__name__} occurred"

    def _create_body(self, exception: BaseException) -> str:
        return f"An exception of type {exception.__class__.__name__} \n\nStack Trace: {''.join(traceback.format_exception(type(exception), exception, exception.__traceback__))}"