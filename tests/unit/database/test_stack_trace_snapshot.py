
"""
This file contains all unit tests of full stack trace in the database.
(Corresponding to the file: 'flask_monitoringdashboard/database/stack_trace_snapshot.py')
"""
import pytest
from flask_monitoringdashboard.database import StacktraceSnapshot
from flask_monitoringdashboard.database.stack_trace_snapshot import get_stack_trace_by_hash, add_stack_trace_snapshot, get_stacklines_from_stack_trace_snapshot_id

def test_add_stack_trace_snapshot(session):
    stack_trace_snapshot_count = session.query(StacktraceSnapshot).count()
    chained_stack_trace_hash = "test_hash"
    stack_trace_snapshot_id = add_stack_trace_snapshot(session, chained_stack_trace_hash)
    f_stack_trace = session.query(StacktraceSnapshot).filter(StacktraceSnapshot.chained_stack_trace_hash == chained_stack_trace_hash).one()
    assert stack_trace_snapshot_id == f_stack_trace.id
    assert stack_trace_snapshot_count + 1 == session.query(StacktraceSnapshot).count()

def test_add_existing_stack_trace_snapshot(session, stack_trace_snapshot):
    stack_trace_snapshot_id = add_stack_trace_snapshot(session, stack_trace_snapshot.chained_stack_trace_hash)
    stack_trace_snapshot_count = session.query(StacktraceSnapshot).count()
    stack_trace_snapshot_id_2 = add_stack_trace_snapshot(session, stack_trace_snapshot.chained_stack_trace_hash)
    assert stack_trace_snapshot_count == session.query(StacktraceSnapshot).count()
    assert stack_trace_snapshot_id == stack_trace_snapshot_id_2

def test_get_stack_trace_by_hash(session, stack_trace_snapshot):
    f_stack_trace = get_stack_trace_by_hash(session, stack_trace_snapshot.chained_stack_trace_hash)
    assert f_stack_trace.id == stack_trace_snapshot.id

def test_get_stack_trace_by_invalid_hash(session):
    f_stack_trace = get_stack_trace_by_hash(session, 'invalid')
    assert f_stack_trace is None

def test_get_stacklines_from_stack_trace_snapshot_id(session, exception_stack_line):
    stacklines = get_stacklines_from_stack_trace_snapshot_id(session, exception_stack_line.stack_trace_snapshot_id)
    assert len(stacklines) == 1
    assert stacklines[0].stack_trace_snapshot_id == exception_stack_line.stack_trace_snapshot_id
    assert stacklines[0].code_id == exception_stack_line.code_id
    assert stacklines[0].position == exception_stack_line.position
    assert stacklines[0].function_definition_id == exception_stack_line.function_definition_id
    assert stacklines[0].relative_line_number == exception_stack_line.relative_line_number
