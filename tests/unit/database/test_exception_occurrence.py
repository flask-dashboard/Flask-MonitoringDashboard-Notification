"""
This file contains all unit tests of exception info in the database.
(Corresponding to the file: 'flask_monitoringdashboard/database/exception_occurrence.py')
"""

from flask_monitoringdashboard.database import ExceptionOccurrence
from flask_monitoringdashboard.database.exception_occurrence import (
    get_first_exception_occurrence,
    add_exception_occurrence,
    count_grouped_exceptions,
    count_endpoint_grouped_exceptions,
    get_exceptions_with_timestamps,
    delete_exception_occurrence,
    get_exceptions_with_timestamps_and_stack_trace_id,
)


def test_get_exception_occurrence(session, exception_occurrence: ExceptionOccurrence):
    e_info = get_first_exception_occurrence(session, exception_occurrence.request_id)
    assert e_info.request_id == exception_occurrence.request_id
    assert e_info.exception_type_id == exception_occurrence.exception_type_id
    assert e_info.exception_msg_id == exception_occurrence.exception_msg_id
    assert (
        e_info.stack_trace_snapshot_id == exception_occurrence.stack_trace_snapshot_id
    )
    assert e_info.is_user_captured == exception_occurrence.is_user_captured
