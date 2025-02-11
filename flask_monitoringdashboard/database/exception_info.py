"""
Contains all functions that access an ExceptionInfo object.
"""

from flask_monitoringdashboard.database import ExceptionInfo, Request, Endpoint

def get_exception_info(session, request_id: int):
    """
    Retrieve an ExceptionInfo record by request_id.
    """
    return session.query(ExceptionInfo).filter_by(request_id=request_id).first()
    
def add_exception_info(session, request_id: int, trace_id: int, exception_type: str, exception_msg: str):
    """
    Add a new ExceptionInfo record.
    """
    exception_info = ExceptionInfo(
        request_id=request_id,
        exception_type=exception_type,
        exception_msg=exception_msg,
        full_stack_trace_id=trace_id
    )
    session.add(exception_info)
    session.commit()
    return exception_info

def get_exceptions_with_timestamps(session):
    results = session.query(
        ExceptionInfo.exception_type,
        ExceptionInfo.exception_msg,
        Request.time_requested,
        Endpoint.name
    ).join(Request, ExceptionInfo.request_id == Request.id).join(Endpoint, Request.endpoint_id == Endpoint.id).all()
    
    return results