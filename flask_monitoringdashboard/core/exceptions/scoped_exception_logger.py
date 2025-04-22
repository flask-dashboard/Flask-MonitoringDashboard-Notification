from typing import Union
import copy


class ScopedExceptionLogger:
    """
    This class is for logging user captured exceptions, in the scope of the current request.
    It is just a DTO for transmitting the user captured exceptions and uncaught exceptions to the exception logger.
    """

    def __init__(self) -> None:
        self.user_captured_exceptions: list[BaseException] = []
        self.uncaught_exception: Union[BaseException, None] = None

    def add_user_captured_exc(self, e: BaseException):
        e_copy = _get_copy_of_exception(e)
        self.user_captured_exceptions.append(e_copy)

    def set_uncaught_exc(self, e: BaseException):
        e_copy = _get_copy_of_exception(e)
        self.uncaught_exception = e_copy


def _get_copy_of_exception(e: BaseException):
    """
    Helper function to reraise the uncaught exception with its original traceback,
    The copy is made in order to preserve the original exception's stack trace
    """
    if e is None:
        return None

    try:
        new_exc = e.__class__(*e.args)
    except Exception:
        try:
            new_exc = copy.deepcopy(e)
        except Exception:
            new_exc = e.__class__()

    if e.__traceback__:
        return new_exc.with_traceback(e.__traceback__)
    return new_exc
