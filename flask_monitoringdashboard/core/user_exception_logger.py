from types import TracebackType
from typing import TypeAlias, Union

ExcInfo: TypeAlias = tuple[type[BaseException], BaseException, TracebackType]

class ScopedExceptionLogger():
    def __init__(self) -> None:
        self.exc_list: list[BaseException] = []
        self.raised_exc_info: Union[ExcInfo, None] = None

    def add_exc(self, e: BaseException):
        self.exc_list.append(e)

