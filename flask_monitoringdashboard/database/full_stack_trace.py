from flask_monitoringdashboard.database import CodeLine, ExceptionStackLine, FullStackTrace, code_line

def get_stack_trace_by_hash(session, full_stack_trace):
    """
    Get FullStackTrace record by its stack_trace_hash.
    """
    result = (
        session.query(FullStackTrace)
        .filter_by(stack_trace_hash=full_stack_trace)
        .first()
    )
    return result

def add_full_stack_trace(session, full_stack_trace: str):
    """
    Add a new FullStackTrace record.
    """
    result = FullStackTrace(
        stack_trace_hash = full_stack_trace
    )
    session.add(result)
    session.flush()

    return result.id


def get_code_from_stacktrace_id(session, stack_trace_id):
    """
    Gets all the code lines referred to by a stacktrace.
    """
    result = (
        session.query(
            ExceptionStackLine
        )
        .filter(ExceptionStackLine.stack_trace_id == stack_trace_id)
        .order_by(ExceptionStackLine.position)
        .all()
    )
    return result
