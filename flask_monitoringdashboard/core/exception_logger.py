import inspect
import traceback
import hashlib

from types import FrameType, TracebackType
from typing import Union

from sqlalchemy.orm import Session
from flask_monitoringdashboard.database import CodeLine, FunctionDefinition
from flask_monitoringdashboard.database.exception_info import add_exception_info
from flask_monitoringdashboard.database.full_stack_trace import add_full_stack_trace, get_stack_trace_by_hash
from flask_monitoringdashboard.database.exception_stack_line import add_exception_stack_line
from flask_monitoringdashboard.database.function_definition import add_function_definition
from flask_monitoringdashboard.database.exception_message import add_exception_message
from flask_monitoringdashboard.database.exception_type import add_exception_type


def hash_helper(s: str):
    return hashlib.sha256(s.encode('utf-8')).hexdigest()

def h_chain(h: str, tb: Union[TracebackType, None]):
    if tb is None:
        return h

    f_def = get_function_definition_from_frame(tb.tb_frame)
    new_hash = hash_helper(h+f_def.function_hash)

    return h_chain(new_hash, tb.tb_next)

def get_function_definition_from_frame(frame: FrameType) -> FunctionDefinition:
    f_def = FunctionDefinition()
    f_def.function_code = inspect.getsource(frame.f_code)
    f_def.function_hash = hash_helper(f_def.function_code)
    return f_def

def create_codeline_from_frame(frame: FrameType):
    c_line = CodeLine()
    c_line.filename = frame.f_code.co_filename
    c_line.line_number = frame.f_lineno
    c_line.function_name = frame.f_code.co_name
    code_context = inspect.getframeinfo(frame).code_context
    if code_context is not None and len(code_context) > 0:
        c_line.code = code_context[0]
    return c_line

def hash_stack_trace(self):
    stack_trace_string = ''.join(traceback.format_exception(self.type, self.value, self.tb))
    chained_stacktrace_hash = hash_helper(stack_trace_string)
    return h_chain(chained_stacktrace_hash, self.tb)

class ExceptionLogger():
    def __init__(self, exc_info):
        self.type : type[BaseException] = exc_info[0]
        self.value : BaseException = exc_info[1]
        self.tb : TracebackType = exc_info[2]

    def save_to_db(self, request_id: int, session: Session):
        """
        Save exception info to DB
        """
        hashed_trace = hash_stack_trace(self)
        existing_trace = get_stack_trace_by_hash(session, hashed_trace)
        
        if existing_trace:
            trace_id = int(existing_trace.id)
        else:
            trace_id = add_full_stack_trace(session, hashed_trace)

            tb = self.tb.tb_next
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
                c_line = create_codeline_from_frame(tb.tb_frame)
                add_exception_stack_line(session, trace_id, idx, c_line, function_id, tb.tb_frame.f_lineno-tb.tb_frame.f_code.co_firstlineno)
                tb = tb.tb_next
                idx += 1
        
        exc_msg_id = add_exception_message(session, str(self.value))
        exc_type_id = add_exception_type(session, self.type.__name__)
        add_exception_info(session, request_id, trace_id, exc_type_id, exc_msg_id)
