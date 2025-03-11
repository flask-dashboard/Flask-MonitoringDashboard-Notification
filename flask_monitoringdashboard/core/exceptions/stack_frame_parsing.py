import inspect
from types import FrameType

from flask_monitoringdashboard.core.exceptions.text_hash import text_hash
from flask_monitoringdashboard.database import FunctionDefinition, CodeLine


def get_function_definition_from_frame(frame: FrameType) -> FunctionDefinition:

    f_def = FunctionDefinition()
    f_def.function_code = inspect.getsource(frame.f_code)
    f_def.function_hash = text_hash(f_def.function_code)
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
