from flask_monitoringdashboard.database import FunctionDefinition


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




