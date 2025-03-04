from typing import Union
from sqlalchemy.orm import Session
from flask_monitoringdashboard.database import ExceptionStackLine, StacktraceSnapshot
from sqlalchemy import desc

def get_stack_trace_by_hash(session: Session, full_stack_trace: str) -> Union[StacktraceSnapshot, None]:
    """
    Get StacktraceSnapshot record by its chained_stacktrace_hash.
    """
    result = (
        session.query(StacktraceSnapshot)
        .filter_by(chained_stacktrace_hash=full_stack_trace)
        .first()
    )
    return result

def add_full_stack_trace(session: Session, full_stack_trace: str) -> int:
    """
    Add a new StacktraceSnapshot record. Returns the id.
    """
    result = StacktraceSnapshot(
        chained_stacktrace_hash = full_stack_trace
    )
    session.add(result)
    session.flush()

    return int(result.id)


def get_stacklines_from_full_stacktrace_id(session: Session, stacktrace_snapshot_id: int) -> list[ExceptionStackLine]:
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

