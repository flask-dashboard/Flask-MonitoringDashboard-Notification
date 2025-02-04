"""
Contains all functions that access an ExceptionInfo object.
"""

from flask_monitoringdashboard.database import ExceptionInfo, ExceptionStackLine
from flask_monitoringdashboard.database.code_line import get_code_line

def get_exception_info(session, request_id: int):
    """
    Retrieve an ExceptionInfo record by request_id.
    """
    return session.query(ExceptionInfo).filter_by(request_id=request_id).first()


def add_exception_info(session, request_id: int, exception_type: int, exception_msg: str):
    """
    Add a new ExceptionInfo record.
    """
    exception_info = ExceptionInfo(
        request_id=request_id,
        exception_type=exception_type,
        exception_msg=exception_msg
    )
    session.add(exception_info)
    session.commit()
    return exception_info

def add_exception_stack_line(session, request_id, position, code_line):
    """
    Adds a StackLine to the database (and possibly a CodeLine)
    :param session: Session for the database
    :param request_id: id of the request
    :param position: position of the StackLine
    :param indent: indent-value
    :param duration: duration of this line (in ms)
    :param code_line: quadruple that consists of: (filename, line_number, function_name, code)
    """
    fn, ln, name, code = code_line
    db_code_line = get_code_line(session, fn, ln, name, code)
    session.add(
        ExceptionStackLine(
            request_id=request_id,
            position=position,
            code_id=db_code_line.id,
        )
    )