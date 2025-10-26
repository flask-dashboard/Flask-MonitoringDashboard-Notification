import traceback
from datetime import datetime, timezone

class NotificationContent:

    def __init__(self, exception: BaseException):
        self._exception = exception
        self.created_at = datetime.now(timezone.utc) # TODO: make timezone configurable or at least the printed format
        self.send_at = None # When was the notification sent, None if not sent yet

        self.notification_type = None
        self.exception_type = exception.__class__.__name__
        
        self.title = self._create_title(exception)
        self.body = self._create_body_markdown(exception)


    def _create_title(self, exception: BaseException) -> str:
        # This is going to be in the 
        return f"[{exception.__class__.__name__}] Uncaught exception at {self.created_at.strftime("%Y-%m-%d %H:%M:%S")}"

    def _create_body(self, exception: BaseException) -> str:
        return f"An exception of type {exception.__class__.__name__} \n\nStack Trace: {''.join(traceback.format_exception(type(exception), exception, exception.__traceback__))}"
    
    def _create_body_markdown(self, exception: BaseException) -> str:
        return f"""**Type:** `{exception.__class__.__name__}`
                   **Timestamp:** `{self.created_at.strftime("%Y-%m-%d %H:%M:%S")}`
                   **Stack Trace:** {''.join(traceback.format_exception(type(exception), exception, exception.__traceback__))}"""