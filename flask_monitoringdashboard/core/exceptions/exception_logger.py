from types import TracebackType
from typing import Union

from sqlalchemy.orm import Session
from flask_monitoringdashboard.core.exceptions.scoped_exception_logger import (
    ScopedExceptionLogger,
)
from flask_monitoringdashboard.core.exceptions.stack_frame_parsing import (
    get_function_definition_from_frame,
    create_codeline_from_frame,
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
        self.uncaught_exception_info: Union[BaseException, None] = scoped_logger.uncaught_exception_info
        
        if self.uncaught_exception_info is not None:
            # The uncaught_exception_info is set in the evaluate_() function,
            # which causes stack frames from evaluate_() to appear in the traceback.
            # These frames are not relevant for the user, so we skip the first frame 
            traceback_without_reraise = self.uncaught_exception_info.__traceback__.tb_next
            self.uncaught_exception_info = self.uncaught_exception_info.with_traceback(traceback_without_reraise)
    
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
        Iterates over all the user captured exceptions but also the uncaught ones and saves each exception info to DB
        """

        # User Captured Exceptions
        for e in self.user_captured_exceptions:
            self._save_to_db(request_id, session, e, type(e), e.__traceback__)

        # Uncaught exception
        e = self.uncaught_exception_info
        if (
            e is not None and e.__traceback__ is not None
        ):
            self._save_to_db(
                request_id,
                session,
                e,
                type(e),
                e.__traceback__
            )
            
    def get_copy_of_uncaught_exception(self):
        """
        Helper function to reraise the uncaught exception with its original traceback, 
        The copy is made in order to preserve the original exception's stack trace
        """
        exc = self.uncaught_exception_info
        if exc is not None:
            return exc.__class__(exc.args).with_traceback(exc.__traceback__)
