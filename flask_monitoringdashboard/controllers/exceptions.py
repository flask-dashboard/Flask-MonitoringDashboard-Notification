from flask_monitoringdashboard.database.exception_info import get_exceptions_with_timestamps, get_exceptions_with_timestamps_and_stacktrace_id
from flask_monitoringdashboard.database.full_stack_trace import get_stacklines_from_stacktrace_id

def get_exceptions_with_timestamp(session, offset, per_page):
    """
    Gets information about exceptions including timestamps of latest and first occurence. 
    :param session: session for the database
    :param offset: number of items to skip
    :param per_page: number of items to return
    :return: A list of dicts. Each dict contains:
             - exception_type (str)
             - exception_msg (str)
             - endpoint name (str)
             - endpoint_id (int)
             - latest_timestamp (datetime)
             - first_timestamp (datetime)
             - count (int) representing the number of occurrences.
    """
    
    return [
        {
            'type': exception.exception_type, 
            'message': exception.exception_msg, 
            'endpoint': exception.name,
            'endpoint_id': exception.id,
            'latest_timestamp': exception.latest_timestamp,
            'first_timestamp': exception.first_timestamp,
            'count': exception.count
        }
        for exception in get_exceptions_with_timestamps(session, offset, per_page)
    ]

def get_detailed_exception_info(session, offset, per_page, endpoint_id):
    """
    Gets detailed information about exceptions on an endpoint (including stack trace).
    :param session: session for the database
    :param offset: number of items to skip
    :param per_page: number of items to return
    :param endpoint_id: the id of the endpoint
    :return: A list of dicts. Each dict contains:
             - type (str) of the exception
             - message (str) of the exception
             - full_stacktrace (lst of dicts) Each dict contains:
                - code (str)
                - filename (str)
                - line_number (int)
                - function_name (str)
             - latest_timestamp (datetime)
             - first_timestamp (datetime)
             - count (int) representing the number of occurrences.
    """
    return [
        {
            'type': exception.exception_type, 
            'message': exception.exception_msg, 
            'full_stacktrace': [ 
                {
                    'code': exceptionStackLine.code.code,
                    'filename': exceptionStackLine.code.filename,
                    'line_number': exceptionStackLine.code.line_number,
                    'function_name': exceptionStackLine.code.function_name
                }
                for exceptionStackLine in get_stacklines_from_stacktrace_id(session, exception.full_stack_trace_id)],
            'latest_timestamp': exception.latest_timestamp,
            'first_timestamp': exception.first_timestamp,
            'count': exception.count
        }
        for exception in get_exceptions_with_timestamps_and_stacktrace_id(session, offset, per_page, endpoint_id)]
