from types import TracebackType
from typing import Union

from sqlalchemy.orm import Session
from flask_monitoringdashboard.core.exceptions.scoped_exception_logger import (
    ExcInfo,
    ScopedExceptionLogger,
)
from flask_monitoringdashboard.core.exceptions.stack_frame_parsing import (
    get_function_definition_from_frame,
)
from flask_monitoringdashboard.core.exceptions.stack_trace_hashing import (
    hash_stack_trace,
)
from flask_monitoringdashboard.database.exception_info import add_exception_info
from flask_monitoringdashboard.database.stack_trace_snapshot import (
    add_stack_trace_snapshot,
    get_stack_trace_by_hash,
)
from flask_monitoringdashboard.database.exception_stack_line import (
    add_exception_stack_line,
)
from flask_monitoringdashboard.database.exception_frame import add_exception_frame
from flask_monitoringdashboard.database.function_location import add_function_location
from flask_monitoringdashboard.database.file_path import add_file_path
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
        is_user_captured: bool,
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
                file_path = add_file_path(session, tb.tb_frame.f_code.co_filename)
                f_location_id = add_function_location(
                    session,
                    file_path,
                    function_id,
                    tb.tb_frame.f_code.co_firstlineno,
                )
                frame_id = add_exception_frame(session, f_location_id, tb.tb_lineno)
                add_exception_stack_line(
                    session,
                    trace_id,
                    frame_id,
                    idx,
                )
                tb = tb.tb_next
                idx += 1

        exc_msg_id = add_exception_message(session, str(exc))
        exc_type_id = add_exception_type(session, typ.__name__)
        add_exception_info(session, request_id, trace_id, exc_type_id, exc_msg_id, is_user_captured)

    def save_to_db(self, request_id: int, session: Session):
        """
        Iterates over all the user captured exceptions but also the uncaught ones and saves each exception info to DB
        """

        # User Captured Exceptions
        for e in self.user_captured_exceptions:
            self._save_to_db(request_id, session, e, type(e), e.__traceback__, True)

        # Uncaught exception
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
                False,
            )
