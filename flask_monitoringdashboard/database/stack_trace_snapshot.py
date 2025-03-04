from typing import Union
from sqlalchemy.orm import Session
from flask_monitoringdashboard.database import ExceptionStackLine, StacktraceSnapshot
from sqlalchemy import desc

def get_stack_trace_by_hash(session: Session, stack_trace_snapshot_hash: str) -> Union[StacktraceSnapshot, None]:
    """
    Get StacktraceSnapshot record by its chained_stack_trace_hash.
    """
    result = (
        session.query(StacktraceSnapshot)
        .filter_by(chained_stack_trace_hash=stack_trace_snapshot_hash)
        .first()
    )
    return result

def add_stack_trace_snapshot(session: Session, stack_trace_snapshot_hash: str) -> int:
    """
    Add a new StacktraceSnapshot record. Returns the id.
    """
    result = StacktraceSnapshot(
        chained_stack_trace_hash = stack_trace_snapshot_hash
    )
    session.add(result)
    session.flush()

    return int(result.id)


def get_stacklines_from_stacktrace_snapshot_id(session: Session, stacktrace_snapshot_id: int) -> list[ExceptionStackLine]:
    """
    Gets all the stack lines referred to by a stacktrace.
    :param session: session for the database
    :param stacktrace_snapshot_id: Filter ExceptionStackLines on this stack trace id
    :return: A list of ExceptionStackLine objects of a specific stack trace
    """
    result = (
        session.query(
            ExceptionStackLine
        )
        .filter(ExceptionStackLine.stacktrace_snapshot_id == stacktrace_snapshot_id)
        .order_by(desc(ExceptionStackLine.position))
        .all()
    )
    return result

