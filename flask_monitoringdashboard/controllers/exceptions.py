from flask_monitoringdashboard.database.exception_info import get_exceptions_with_timestamps, get_exceptions_with_timestamps_and_stacktrace_id
from flask_monitoringdashboard.database.full_stack_trace import get_code_from_stacktrace_id

def get_exceptions_with_timestamp(session, offset, per_page):
    """
    :param session: session for the database
    :param endpoints: a list of endpoints, encoded by their name
    :return: for every endpoint in endpoints, a list with the performance
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
                for exceptionStackLine in get_code_from_stacktrace_id(session, exception.full_stack_trace_id)],
            'latest_timestamp': exception.latest_timestamp,
            'first_timestamp': exception.first_timestamp,
            'count': exception.count
        }
        for exception in get_exceptions_with_timestamps_and_stacktrace_id(session, offset, per_page, endpoint_id)]
