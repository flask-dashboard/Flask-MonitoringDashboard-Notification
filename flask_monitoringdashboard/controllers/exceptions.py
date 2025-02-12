from flask_monitoringdashboard.database.exception_info import get_exceptions_with_timestamps

def get_exceptions_with_timestamp(session, offset, per_page):
    """
    :param session: session for the database
    :param endpoints: a list of endpoints, encoded by their name
    :return: for every endpoint in endpoints, a list with the performance
    """
    exceptions = get_exceptions_with_timestamps(session, offset, per_page)
    print(exceptions)
    
    return [
        {
            'type': exception.exception_type, 
            'message': exception.exception_msg, 
            'endpoint': exception.name,
            'latest_timestamp': exception.latest_timestamp,
            'first_timestamp': exception.first_timestamp,
            'count': exception.count
        }
        for exception in get_exceptions_with_timestamps(session, offset, per_page)
    ]
