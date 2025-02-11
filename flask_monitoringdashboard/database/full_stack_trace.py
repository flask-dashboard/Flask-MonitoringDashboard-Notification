from flask_monitoringdashboard.database import FullStackTrace

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