from types import TracebackType
from typing import TypeAlias, Union

ExcInfo: TypeAlias = tuple[type[BaseException], BaseException, TracebackType]

class ScopedExceptionLogger():
    def __init__(self) -> None:
        self.user_captured_exceptions: list[BaseException] = []
        self.uncaught_exception_info: Union[ExcInfo, None] = None

    def add_exc(self, e: BaseException):
        self.user_captured_exceptions.append(e)

