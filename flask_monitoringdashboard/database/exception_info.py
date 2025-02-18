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

def count_grouped_exceptions(session):
    """
    Count the number of different kinds of exceptions grouped by endpoint and full stack trace.
    :param session: session for the database
    :return: Integer (total number of groups of exceptions)
    """
    return (
        session.query(ExceptionInfo.request_id)
        .join(Request, ExceptionInfo.request_id == Request.id)
        .join(Endpoint, Request.endpoint_id == Endpoint.id)
        .group_by(Endpoint.name, ExceptionInfo.full_stack_trace_id)
        .count()
    )
    
def count_endpoint_grouped_exceptions(session, endpoint_id):
    """
    Count the number of different kinds of exceptions on an endpoint grouped by full stack trace.
    :param session: session for the database
    :param endpoint_id: filter exceptions on this endpoint id
    :return: Integer (total number of groups of exceptions)
    """
    return (
        session.query(ExceptionInfo.request_id)
        .join(Request, ExceptionInfo.request_id == Request.id)
        .join(Endpoint, Request.endpoint_id == Endpoint.id)
        .filter(Endpoint.id == endpoint_id)
        .group_by(ExceptionInfo.full_stack_trace_id)
        .count()
    )

def get_exceptions_with_timestamps(session, offset, per_page):
    """
    Gets the information about exceptions grouped by endpoint and full stack trace and sorted by latest request time.
    :param session: session for the database
    :param offset: number of items to skip
    :param per_page: number of items to return
    :return: A list of dicts. Each dict contains:
             - exception_type (str)
             - exception_msg (str)
             - endpoint name (str)
             - endpoint id (int)
             - latest_timestamp (datetime)
             - first_timestamp (datetime)
             - count (int) representing the number of occurrences.
    """
    result = (
        session.query(
            ExceptionInfo.exception_type,
            ExceptionInfo.exception_msg,
            Endpoint.name,
            Endpoint.id,
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
    return result


def get_exceptions_with_timestamps_and_stacktrace_id(session, offset, per_page, endpoint_id):
    """
    Gets the information about exceptions on an endpoint grouped by full stack trace and sorted by latest request time.
    :param session: session for the database
    :param offset: number of items to skip
    :param per_page: number of items to return
    :param endpoint_id: filter exceptions on this endpoint id
    :return: A list of dicts. Each dict contains:
             - exception_type (str)
             - exception_msg (str)
             - full_stack_trace_id (int) for the exceptions
             - latest_timestamp (datetime)
             - first_timestamp (datetime)
             - count (int) representing the number of occurrences.
    """
    result = (
        session.query(
            ExceptionInfo.exception_type,
            ExceptionInfo.exception_msg,
            ExceptionInfo.full_stack_trace_id,
            func.max(Request.time_requested).label('latest_timestamp'),
            func.min(Request.time_requested).label('first_timestamp'),
            func.count(ExceptionInfo.request_id).label('count')
        )
        .join(Request, ExceptionInfo.request_id == Request.id)
        .join(Endpoint, Request.endpoint_id == Endpoint.id)
        .where(Endpoint.id == endpoint_id)
        .group_by(ExceptionInfo.full_stack_trace_id)
        .order_by(desc('latest_timestamp'))
        .offset(offset)
        .limit(per_page)
        .all()
    )
    return result
