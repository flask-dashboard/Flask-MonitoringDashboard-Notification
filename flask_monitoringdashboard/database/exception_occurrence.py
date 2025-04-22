"""
Contains all functions that access an ExceptionOccurrence object.
"""

from typing import Union
from sqlalchemy import func, desc
from sqlalchemy.orm import Session
from flask_monitoringdashboard.database import (
    ExceptionOccurrence,
    Request,
    Endpoint,
    ExceptionType,
    ExceptionMessage,
)
from flask_monitoringdashboard.core.database_pruning import (
    delete_entries_unreferenced_by_exception_occurrence,
)


def get_first_exception_occurrence(
    session: Session, request_id: int
) -> Union[ExceptionOccurrence, None]:
    """
    Retrieve an ExceptionOccurrence record by request_id.
    """
    result = session.query(ExceptionOccurrence).filter_by(request_id=request_id).first()
    return result


def add_exception_occurrence(
    session: Session,
    request_id: int,
    trace_id: int,
    exception_type_id: int,
    exception_msg_id: int,
    is_user_captured: bool,
):
    """
    Add a new ExceptionOccurrence record.
    """
    exception_occurrence = ExceptionOccurrence(
        request_id=request_id,
        exception_type_id=exception_type_id,
        exception_msg_id=exception_msg_id,
        stack_trace_snapshot_id=trace_id,
        is_user_captured=is_user_captured,
    )
    session.add(exception_occurrence)
    session.commit()


def count_grouped_exceptions(session: Session):
    """
    Count the number of different kinds of exceptions grouped by endpoint and stack trace snapshot.
    :param session: session for the database
    :return: Integer (total number of groups of exceptions)
    """
    return (
        session.query(ExceptionOccurrence.request_id)
        .join(Request, ExceptionOccurrence.request)
        .join(Endpoint, Request.endpoint)
        .group_by(Endpoint.name, ExceptionOccurrence.stack_trace_snapshot_id)
        .count()
    )


def count_endpoint_grouped_exceptions(session: Session, endpoint_id: int):
    """
    Count the number of different kinds of exceptions on an endpoint grouped by stack trace snapshot.
    :param session: session for the database
    :param endpoint_id: filter exceptions on this endpoint id
    :return: Integer (total number of groups of exceptions)
    """
    return (
        session.query(ExceptionOccurrence.request_id)
        .join(Request, ExceptionOccurrence.request)
        .join(Endpoint, Request.endpoint)
        .filter(Endpoint.id == endpoint_id)
        .group_by(ExceptionOccurrence.stack_trace_snapshot_id)
        .count()
    )


def get_exceptions_with_timestamps(session: Session, offset: int, per_page: int):
    """
    Gets the information about exceptions grouped by endpoint and stack trace snapshot and sorted by latest request time.
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
            ExceptionType.type,
            ExceptionMessage.message,
            Endpoint.name,
            Endpoint.id,
            func.max(Request.time_requested).label("latest_timestamp"),
            func.min(Request.time_requested).label("first_timestamp"),
            func.count(ExceptionOccurrence.request_id).label("count"),
        )
        .join(Request, ExceptionOccurrence.request)
        .join(Endpoint, Request.endpoint)
        .join(ExceptionType, ExceptionOccurrence.exception_type)
        .join(ExceptionMessage, ExceptionOccurrence.exception_msg)
        .group_by(Endpoint.name, ExceptionOccurrence.stack_trace_snapshot_id)
        .order_by(desc("latest_timestamp"))
        .offset(offset)
        .limit(per_page)
        .all()
    )
    return result


def delete_exception_occurrence(session: Session, stack_trace_snapshot_id: int) -> None:
    """
    Deletes an exception based on the stack trace id
    :param session: session for the database
    :param stack_trace_snapshot_id: the stack trace id
    :return: None
    """
    _ = (
        session.query(ExceptionOccurrence)
        .filter(ExceptionOccurrence.stack_trace_snapshot_id == stack_trace_snapshot_id)
        .delete()
    )
    delete_entries_unreferenced_by_exception_occurrence(session)
    session.commit()


def get_exceptions_with_timestamps_and_stack_trace_id(
    session: Session, offset: int, per_page: int, endpoint_id: int
):
    """
    Gets the information about exceptions on an endpoint grouped by stack trace snapshot and sorted by latest request time.
    :param session: session for the database
    :param offset: number of items to skip
    :param per_page: number of items to return
    :param endpoint_id: filter exceptions on this endpoint id
    :return: A list of dicts. Each dict contains:
             - exception_type (str)
             - exception_msg (str)
             - stack_trace_snapshot_id (int) for the exceptions
             - latest_timestamp (datetime)
             - first_timestamp (datetime)
             - count (int) representing the number of occurrences.
    """
    result = (
        session.query(
            ExceptionType.type,
            ExceptionMessage.message,
            ExceptionOccurrence.stack_trace_snapshot_id,
            func.max(Request.time_requested).label("latest_timestamp"),
            func.min(Request.time_requested).label("first_timestamp"),
            func.count(ExceptionOccurrence.request_id).label("count"),
        )
        .join(Request, ExceptionOccurrence.request)
        .join(Endpoint, Request.endpoint)
        .join(ExceptionType, ExceptionOccurrence.exception_type)
        .join(ExceptionMessage, ExceptionOccurrence.exception_msg)
        .filter(Endpoint.id == endpoint_id)
        .group_by(ExceptionOccurrence.stack_trace_snapshot_id)
        .order_by(desc("latest_timestamp"))
        .offset(offset)
        .limit(per_page)
        .all()
    )
    return result
