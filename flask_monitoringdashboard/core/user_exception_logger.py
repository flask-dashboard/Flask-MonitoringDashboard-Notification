from types import TracebackType
from typing import Union

ExcInfo = tuple[type[BaseException], BaseException, TracebackType]


class ScopedExceptionLogger:
    def __init__(self) -> None:
        self.user_captured_exceptions: list[BaseException] = []
        self.uncaught_exception_info: Union[ExcInfo, None] = None

    def add_exc(self, e: BaseException):
        self.user_captured_exceptions.append(e)
