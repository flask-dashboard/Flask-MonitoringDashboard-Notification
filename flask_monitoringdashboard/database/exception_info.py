"""
Contains all functions that access an ExceptionInfo object.
"""
from sqlalchemy import desc
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

def get_exceptions_with_timestamps(session, offset, per_page):
    """
    Gets the requests of an endpoint sorted by request time, together with the stack lines.
    :param session: session for the database
    :param endpoint_id: filter profiled requests on this endpoint
    :param offset: number of items to skip
    :param per_page: number of items to return
    :return: A list with tuples. Each tuple consists first of a Request-object, and the second part
    of the tuple is a list of StackLine-objects.
    """
    result = (
        session.query(
            ExceptionInfo.exception_type,
            ExceptionInfo.exception_msg,
            Request.time_requested,
            Endpoint.name
        )
        .join(Request, ExceptionInfo.request_id == Request.id).join(Endpoint, Request.endpoint_id == Endpoint.id)
        .order_by(desc(Request.time_requested))
        .offset(offset)
        .limit(per_page)
        .all()
    )
    session.expunge_all()
    return result
