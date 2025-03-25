"""
This file contains all unit tests of exception info in the database.
(Corresponding to the file: 'flask_monitoringdashboard/database/exception_info.py')
"""

from flask_monitoringdashboard.database import ExceptionInfo
from flask_monitoringdashboard.database.exception_info import (
    get_exception_info,
    add_exception_info,
    count_grouped_exceptions,
    count_endpoint_grouped_exceptions,
    get_exceptions_with_timestamps,
    delete_exception,
    get_exceptions_with_timestamps_and_stack_trace_id,
)


def test_get_exception_info(session, exception_info):
    e_info = get_exception_info(session, exception_info.request_id)
    assert e_info.request_id == exception_info.request_id
    assert e_info.exception_type_id == exception_info.exception_type_id
    assert e_info.exception_msg_id == exception_info.exception_msg_id
    assert e_info.stack_trace_snapshot_id == exception_info.stack_trace_snapshot_id
    assert e_info.is_user_captured == exception_info.is_user_captured
