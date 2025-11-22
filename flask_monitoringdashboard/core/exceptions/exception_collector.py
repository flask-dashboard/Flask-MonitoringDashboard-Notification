import copy
from typing import Union

from sqlalchemy.orm import Session

from flask_monitoringdashboard.core.config import Config
from ..alert import email, issue, chat
from ..alert.GithubRequestInfo import GitHubRequestInfo
from ..alert.alert_content import AlertContent


class ExceptionCollector:
    """
    This class is for logging user captured exceptions, in the scope of the current request.
    It is just a DTO for transmitting the user captured exceptions and uncaught exceptions to the exception logger.
    """

    def __init__(self) -> None:
        self.user_captured_exceptions: list[BaseException] = []
        self.uncaught_exception: Union[BaseException, None] = None

    def add_user_captured_exc(self, e: BaseException):
        e_copy = _get_copy_of_exception(e)
        self.user_captured_exceptions.append(e_copy)

    def set_uncaught_exc(self, e: BaseException):
        e_copy = _get_copy_of_exception(e)
        self.uncaught_exception = e_copy

    def save_to_db(self, request_id: int, session: Session, config: Config):

        # import package config lazily to avoid circular import at module import time
        from flask_monitoringdashboard.database.exception_occurrence import (
            save_exception_occurence_to_db,
        )

        """
        Iterates over all the user captured exceptions and also a possible uncaught one, and saves each exception to the DB
        """
        for e in self.user_captured_exceptions:
            save_exception_occurence_to_db(
                request_id, session, e, type(e), e.__traceback__, True
            )

        e = self.uncaught_exception
        if e is not None:
            if e.__traceback__ is not None:
                # We have to choose the next frame as else it will include the evaluate function from measurement.py in the traceback
                # where it was temporaritly captured for logging by the ExceptionCollector, before getting reraised later
                e = e.with_traceback(e.__traceback__.tb_next)

            e_copy = _get_copy_of_exception(e)

            if config.alert_enabled:
                _notify(e_copy, session, config)
            save_exception_occurence_to_db(
                request_id, session, e, type(e), e.__traceback__, False
            )


def _get_copy_of_exception(e: BaseException):
    """
    Helper function to reraise the uncaught exception with its original traceback,
    The copy is made in order to preserve the original exception's stack trace
    """
    if e is None:
        return None

    try:
        new_exc = e.__class__(*e.args)
    except Exception:
        try:
            new_exc = copy.deepcopy(e)
        except Exception:
            # For exceptions that can't be instantiated without args, just return the original
            return e

    if e.__traceback__:
        return new_exc.with_traceback(e.__traceback__)
    return new_exc


def _notify(
        exception: BaseException,
        session: Session,
        config: Config):
    from flask_monitoringdashboard.database.exception_occurrence import (
        check_if_stack_trace_exists,
    )

    if check_if_stack_trace_exists(session, exception, exception.__traceback__):
        # Create alert content
        alert_content = AlertContent(exception, config)
        types = config.alert_type

        if 'email' in types:
            email.send_email(alert_content)
        if 'issue' in types:
            github_info = GitHubRequestInfo(
                github_token=config.github_token,
                repo_owner=config.repository_owner,
                repo_name=config.repository_name
            )
            # Send Post Request to repository to create issue
            issue.create_issue(github_info, alert_content)
        if 'chat' in types:
            chat.send_message(alert_content)
    else:
        print('Stack trace already exists in DB, no alert sent.')
