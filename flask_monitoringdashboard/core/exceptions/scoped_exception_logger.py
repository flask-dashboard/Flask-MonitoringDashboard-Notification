from typing import Union

class ScopedExceptionLogger:
    """
    This class is for logging user captured exceptions, in the scope of the current request.
    It is just a DTO for transmitting the user captured exceptions and uncaught exceptions to the exception logger.
    """
    def __init__(self) -> None:
        self.user_captured_exceptions: list[BaseException] = []
        self.uncaught_exception: Union[BaseException, None] = None

    def add_exc(self, e: BaseException):
        self.user_captured_exceptions.append(e)
