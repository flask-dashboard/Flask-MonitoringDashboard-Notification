from flask_monitoringdashboard.database import CodeLine, ExceptionStackLine, FunctionDefinition


def add_function_definition(session, f_def: FunctionDefinition):
    """
    Adds a StackLine to the database (and possibly a CodeLine)
    :param session: Session for the database
    """
    result = (session.query(FunctionDefinition)
            .filter(FunctionDefinition.function_hash == f_def.function_hash)
            .first())
    if result is not None:
        return result.id
    else:
        session.add(f_def)
        session.flush()
        return f_def.id

def get_function_definition_from_id(session, function_id):
    return (session.query(FunctionDefinition)
            .filter(FunctionDefinition.id == function_id)
            .first())

def get_function_startlineno_and_relativelineno_from_function_id(session, function_id):
    result : ExceptionStackLine | None = (session.query(ExceptionStackLine)
                    .join(FunctionDefinition, FunctionDefinition.id == ExceptionStackLine.function_id)
                    .filter(FunctionDefinition.id == function_id)
                    .first())
    if result is not None:
        return result.code.line_number, result.relative_line_number
    else:
        return None, None


