import hashlib
import traceback
from types import TracebackType
from typing import Union

from flask_monitoringdashboard.core.exceptions.stack_frame_parsing import (
    get_function_definition_from_frame,
)


def hash_stack_trace(exc, tb):
    """
    Hashes the stack trace of an exception including the function definition of each frame in the traceback.
    """
    stack_trace_string = "".join(traceback.format_exception(exc))
    chained_stack_trace_hash = stack_trace_hasher(stack_trace_string)
    return _hash_traceback_object(chained_stack_trace_hash, tb)


def stack_trace_hasher(s: str):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def _hash_traceback_object(h: str, tb: Union[TracebackType, None]):
    if tb is None:
        return h

    f_def = get_function_definition_from_frame(tb.tb_frame)
    new_hash = stack_trace_hasher(h + f_def.function_hash)

    return _hash_traceback_object(new_hash, tb.tb_next)
