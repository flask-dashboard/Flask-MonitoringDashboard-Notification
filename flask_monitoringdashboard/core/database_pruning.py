from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from flask_monitoringdashboard.core.custom_graph import scheduler
from flask_monitoringdashboard.database import ( 
    CodeLine,
    ExceptionMessage,
    ExceptionType,
    session_scope, 
    Request, Outlier, StackLine, CustomGraphData, ExceptionInfo, StacktraceSnapshot, ExceptionStackLine, FunctionDefinition
)

def prune_database_older_than_weeks(weeks_to_keep, delete_custom_graph_data):
    """Prune the database of Request and optionally CustomGraph data older than the specified number of weeks"""
    with session_scope() as session:
        date_to_delete_from = datetime.utcnow() - timedelta(weeks=weeks_to_keep)

        # Prune Request table and related Outlier entries
        requests_to_delete = session.query(Request).filter(Request.time_requested < date_to_delete_from).all()

        for request in requests_to_delete:
            session.query(Outlier).filter(Outlier.request_id == request.id).delete()
            session.query(StackLine).filter(StackLine.request_id == request.id).delete()
            session.query(ExceptionInfo).filter(ExceptionInfo.request_id == request.id).delete()
            session.delete(request)

        if delete_custom_graph_data:
            session.query(CustomGraphData).filter(CustomGraphData.time < date_to_delete_from).delete()
            
        delete_entries_unreferenced_by_exception_info(session)

        session.commit()

def delete_entries_unreferenced_by_exception_info(session: Session):
    """
    Delete ExceptionTypes, ExceptionMessages, StacktraceSnapshots (along with their ExceptionStackLines) that are not referenced by any ExceptionInfos, 
    FunctionDefinitions that are not referenced by any ExceptionStackLines, and
    CodeLines that are not referenced by any ExceptionStackLines and not referenced by any StackLines
    """
    # Delete ExceptionTypes that are not referenced by any ExceptionInfos
    session.query(ExceptionType).filter(
        ~session.query(ExceptionInfo)
        .filter(ExceptionInfo.exception_type_id == ExceptionType.id)
        .exists()
    ).delete(synchronize_session=False)

    # Delete ExceptionMessages that are not referenced by any ExceptionInfos
    session.query(ExceptionMessage).filter(
        ~session.query(ExceptionInfo)
        .filter(ExceptionInfo.exception_msg_id == ExceptionMessage.id)
        .exists()
    ).delete(synchronize_session=False)

    # Find and delete StacktraceSnapshots (along with their ExceptionStackLines) that are not referenced by any ExceptionInfos
    stack_trace_snapshots_to_delete = session.query(StacktraceSnapshot).filter(
        ~session.query(ExceptionInfo)
        .filter(ExceptionInfo.stack_trace_snapshot_id == StacktraceSnapshot.id)
        .exists()
    ).all()
    for stack_trace_snapshot in stack_trace_snapshots_to_delete:
        session.query(ExceptionStackLine).filter(ExceptionStackLine.stack_trace_snapshot_id == stack_trace_snapshot.id).delete()
        session.delete(stack_trace_snapshot)
        
    # Find and delete FunctionDefenitions that are not referenced by any ExceptionStackLines
    session.query(FunctionDefinition).filter(
        ~session.query(ExceptionStackLine)
        .filter(ExceptionStackLine.function_definition_id == FunctionDefinition.id)
        .exists()
    ).delete(synchronize_session=False)
    
    # Find and delete CodeLines that are not referenced by any ExceptionStackLines and not referenced by any StackLines
    session.query(CodeLine).filter(
        ~session.query(ExceptionStackLine)
        .filter(ExceptionStackLine.code_id == CodeLine.id)
        .exists() 
        &
        ~session.query(StackLine)
        .filter(StackLine.code_id == CodeLine.id)
        .exists()
    ).delete(synchronize_session=False)


def add_background_pruning_job(weeks_to_keep, delete_custom_graph_data, **schedule):
    """Add a scheduled job to prune the database of Request and optionally CustomGraph data older than the specified
    number of weeks"""

    scheduler.add_job(
        id='database_pruning_schedule',
        func=prune_database_older_than_weeks,
        args=[weeks_to_keep, delete_custom_graph_data],  # These are arguments passed to the prune function
        trigger='cron',
        replace_existing=True,  # This will replace an existing job
        **schedule
    )
