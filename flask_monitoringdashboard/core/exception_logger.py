import inspect
import traceback
import hashlib

from types import FrameType, TracebackType
from typing import Union

from sqlalchemy.orm import Session
from flask_monitoringdashboard.core.scoped_exception_logger import (
    ExcInfo,
    ScopedExceptionLogger,
)
from flask_monitoringdashboard.database import CodeLine, FunctionDefinition
from flask_monitoringdashboard.database.exception_info import add_exception_info
from flask_monitoringdashboard.database.stack_trace_snapshot import (
    add_stack_trace_snapshot,
    get_stack_trace_by_hash,
)
from flask_monitoringdashboard.database.exception_stack_line import (
    add_exception_stack_line,
)
from flask_monitoringdashboard.database.function_definition import (
    add_function_definition,
)
from flask_monitoringdashboard.database.exception_message import add_exception_message
from flask_monitoringdashboard.database.exception_type import add_exception_type


class ExceptionLogger:

    def __init__(self, scoped_logger: ScopedExceptionLogger):
        self.user_captured_exceptions: list[BaseException] = (
            scoped_logger.user_captured_exceptions
        )

        # These gymnastics are required as otherwise it will save a lot of unneeded stuff to the traceback
        # i.e. The __traceback__ object that is attached to the Exception object will get written to if we do not do this trick
        # This means that stack frames from when we reraise the execption later will be included which has no value to the user
        raised_exc_info: Union[ExcInfo, None] = scoped_logger.uncaught_exception_info
        self.uncaught_exception_info: Union[BaseException, None] = None
        self.uncaught_exception_traceback: Union[TracebackType, None] = None
        if raised_exc_info is not None:
            self.uncaught_exception_info = raised_exc_info[1]
            self.uncaught_exception_traceback = raised_exc_info[2]

    def _save_to_db(
        self,
        request_id: int,
        session: Session,
        exc: BaseException,
        typ: type[BaseException],
        tb: Union[TracebackType, None],
    ):
        """
        Save exception info to DB
        """
        hashed_trace = hash_stack_trace(exc, tb)
        existing_trace = get_stack_trace_by_hash(session, hashed_trace)

        if existing_trace:
            trace_id = int(existing_trace.id)
        else:
            trace_id = add_stack_trace_snapshot(session, hashed_trace)
            idx = 0
            while tb:
                # iterate over traceback lines
                # i.e. the object representation of the following traceback
                # Traceback (most recent call last):
                #   File "example.py", line 9, in <module>
                #     calculate()
                #   File "example.py", line 6, in calculate
                #     return divide(10, 0)
                #   File "example.py", line 2, in divide
                #     return a / b
                # ZeroDivisionError: division by zero
                f_def = get_function_definition_from_frame(tb.tb_frame)
                function_id = add_function_definition(session, f_def)
                c_line = create_codeline_from_frame(tb.tb_frame, tb.tb_lineno)
                add_exception_stack_line(
                    session,
                    trace_id,
                    idx,
                    c_line,
                    function_id,
                    c_line.line_number - tb.tb_frame.f_code.co_firstlineno,
                )
                tb = tb.tb_next
                idx += 1

        exc_msg_id = add_exception_message(session, str(exc))
        exc_type_id = add_exception_type(session, typ.__name__)
        add_exception_info(session, request_id, trace_id, exc_type_id, exc_msg_id)

    def save_to_db(self, request_id: int, session: Session):
        """
        Iterates over all the exceptions and save each exception info to DB
        """
        for e in self.user_captured_exceptions:
            self._save_to_db(request_id, session, e, type(e), e.__traceback__)
        if (
            self.uncaught_exception_info is not None
            and self.uncaught_exception_traceback is not None
        ):
            e = self.uncaught_exception_info
            # We have to choose the next frame as else it will include the evaluate function
            self._save_to_db(
                request_id,
                session,
                e,
                type(e),
                self.uncaught_exception_traceback.tb_next,
            )


def _hash(s: str):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def _hash_traceback_object(h: str, tb: Union[TracebackType, None]):
    if tb is None:
        return h

    f_def = get_function_definition_from_frame(tb.tb_frame)
    new_hash = _hash(h + f_def.function_hash)

    return _hash_traceback_object(new_hash, tb.tb_next)


def get_function_definition_from_frame(frame: FrameType) -> FunctionDefinition:
    f_def = FunctionDefinition()
    f_def.function_code = inspect.getsource(frame.f_code)
    f_def.function_hash = _hash(f_def.function_code)
    return f_def


def create_codeline_from_frame(frame: FrameType, lineno):
    c_line = CodeLine()
    c_line.filename = frame.f_code.co_filename
    c_line.line_number = lineno
    c_line.function_name = frame.f_code.co_name
    code_context = inspect.getframeinfo(frame).code_context
    if code_context is not None and len(code_context) > 0:
        c_line.code = code_context[0]
    return c_line


def hash_stack_trace(exc, tb):
    """
    Hashes the stack trace of an exception including the function definition of each frame in the traceback.
    """
    stack_trace_string = "".join(traceback.format_exception(exc))
    chained_stack_trace_hash = _hash(stack_trace_string)
    return _hash_traceback_object(chained_stack_trace_hash, tb)
