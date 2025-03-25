from sqlalchemy.orm import Session
from flask_monitoringdashboard.database import ExceptionFrame, FunctionLocation

def add_exception_frame(
    session: Session,
    function_location_id: int,
    line_number: int,
):
    """
    Adds a ExceptionFrame to the database if it does not already exist.
    :param session: Session for the database
    :param function_location_id: The ID of the FunctionLocation of the frame.
    :param line_number: The line number of the frame.
    :return: The ID of the existing or newly added ExceptionFrame.
    """

    existing_exception_frame = (
        session.query(ExceptionFrame)
        .filter(ExceptionFrame.function_location_id == function_location_id)
        .filter(ExceptionFrame.line_number == line_number)
        .first()
    )
    if existing_exception_frame is not None:
        return existing_exception_frame.id
    else:
        frame = ExceptionFrame(function_location_id=function_location_id, line_number=line_number)
        session.add(frame)
        session.flush()
        return frame.id
    
def get_function_info_from_exception_frame_id(session: Session, exception_frame_id: int) -> tuple:
    """
    Retrieves the function definition id, the starting line number of a function and the relative line number of an exception
    from the ExceptionFrame table.

    :param session: session for the database
    :param exception_frame_id: id of the ExceptionFrame
    :return: A triple containing:
            - (int) The absolute starting line number of the function in the source file.
            - (int) The relative line number of the exception within the function.
            - (int) The function definition id.
    """
    frame = session.query(ExceptionFrame).filter(ExceptionFrame.id == exception_frame_id).first()
    function_location_id = frame.function_location_id
    function_location = session.query(FunctionLocation).filter(FunctionLocation.id == function_location_id).first()
    function_definition_id = function_location.function_definition_id
    function_start_line_number = function_location.function_start_line_number
    exception_relative_line_number = frame.line_number - function_start_line_number
    return function_start_line_number, exception_relative_line_number, function_definition_id
