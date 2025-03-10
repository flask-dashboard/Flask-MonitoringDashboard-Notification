
"""
This file contains all unit tests of exception stack line in the database.
(Corresponding to the file: 'flask_monitoringdashboard/database/exception_stack_line.py')
"""
from flask_monitoringdashboard.database import ExceptionStackLine
from flask_monitoringdashboard.database.exception_stack_line import add_exception_stack_line

def test_add_exception_stack_line(session, stack_trace_snapshot, function_definition, code_line):
    assert session.query(ExceptionStackLine).filter(ExceptionStackLine.stack_trace_snapshot_id == stack_trace_snapshot.id).one_or_none() is None
    add_exception_stack_line(session, stack_trace_snapshot_id=stack_trace_snapshot.id, position=0, code_line=code_line, function_defintion_id=function_definition.id, relative_lineno=1)
    session.commit()
    assert session.query(ExceptionStackLine).filter(ExceptionStackLine.stack_trace_snapshot_id == stack_trace_snapshot.id).one()
