from flask_monitoringdashboard.database import CodeLine, ExceptionStackLine
from flask_monitoringdashboard.database.code_line import get_code_line

def add_exception_stack_line(session, request_id, position, code_line: CodeLine):
    """
    Adds a StackLine to the database (and possibly a CodeLine)
    :param session: Session for the database
    :param request_id: id of the request
    :param position: position of the StackLine
    :param indent: indent-value
    :param duration: duration of this line (in ms)
    :param code_line: quadruple that consists of: (filename, line_number, function_name, code)
    """
    #fn, ln, name, code = code_line
    fn = code_line.filename
    ln = code_line.line_number
    name = code_line.function_name
    code = code_line.code
    db_code_line = get_code_line(session, fn, ln, name, code)
    session.add(
        ExceptionStackLine(
            stack_trace_id=request_id,
            position=position,
            code_id=db_code_line.id,
        )
    )