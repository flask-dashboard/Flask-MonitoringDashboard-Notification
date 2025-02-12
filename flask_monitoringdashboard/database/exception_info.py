"""
Contains all functions that access an ExceptionInfo object.
"""
from sqlalchemy import func, desc
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

def count_grouped_exceptions(session, *where):
    """
    Count the total number of exceptions grouped by endpoint and full stack trace.
    :param session: session for the database
    :param where: filter conditions
    :return: Integer (total number of grouped exceptions)
    """
    return (
        session.query(ExceptionInfo.request_id)
        .join(Request, ExceptionInfo.request_id == Request.id)
        .join(Endpoint, Request.endpoint_id == Endpoint.id)
        .filter(*where)
        .group_by(Endpoint.name, ExceptionInfo.full_stack_trace_id)
        .count()
    )

def get_exceptions_with_timestamps(session, offset, per_page):
    """
    Gets the requests of an endpoint sorted by request time, together with the stack lines.
    :param session: session for the database
    :param endpoint_id: filter profiled requests on this endpoint
    :param offset: number of items to skip
    :param per_page: number of items to return
    :return: A list of tuples. Each tuple contains:
             - exception_type (str)
             - exception_msg (str)
             - endpoint name (str)
             - latest_timestamp (datetime)
             - first_timestamp (datetime)
             - count (int) representing the number of occurrences.
    """
    result = (
        session.query(
            ExceptionInfo.exception_type,
            ExceptionInfo.exception_msg,
            Endpoint.name,
            func.max(Request.time_requested).label('latest_timestamp'),
            func.min(Request.time_requested).label('first_timestamp'),
            func.count(ExceptionInfo.request_id).label('count')
        )
        .join(Request, ExceptionInfo.request_id == Request.id)
        .join(Endpoint, Request.endpoint_id == Endpoint.id)
        .group_by(Endpoint.name, ExceptionInfo.full_stack_trace_id)
        .order_by(desc('latest_timestamp'))
        .offset(offset)
        .limit(per_page)
        .all()
    )
    session.expunge_all()
    return result
