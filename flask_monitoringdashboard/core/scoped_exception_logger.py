from types import TracebackType
from typing import Union

ExcInfo = tuple[type[BaseException], BaseException, TracebackType]


class ScopedExceptionLogger:
    """
    This class is for logging user captured exceptions, in the scope of the current request.
    It is just a DTO for transmitting the user captured exceptions and uncaught exceptions to the exception logger.
    """
    def __init__(self) -> None:
        self.user_captured_exceptions: list[BaseException] = []
        self.uncaught_exception_info: Union[ExcInfo, None] = None

    def add_exc(self, e: BaseException):
        self.user_captured_exceptions.append(e)
