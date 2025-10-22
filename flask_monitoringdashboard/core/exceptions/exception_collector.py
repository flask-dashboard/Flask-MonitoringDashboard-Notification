from typing import Union
import copy

from sqlalchemy.orm import Session
from ..notification import issue
from ..notification import GithubRequestInfo

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
        self.notify(e_copy)
        self.uncaught_exception = e_copy
   
    def notify(self, e: BaseException):
        print("Now notifying about exception")
        request_info = GithubRequestInfo.GitHubRequestInfo(
            github_token="your_github_token",
            repo_owner="xXPinkmagicXx",
            repo_name="fmd_test")    
        
        data = {
            "title": "this is a new title",
            "body": "This is the body"
            }

        response = issue.make_post_request(request_info, "issues", data)
        print("Notification response:", response.status_code, response.text)
    
    def save_to_db(self, request_id: int, session: Session):

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
            new_exc = e.__class__()

    if e.__traceback__:
        return new_exc.with_traceback(e.__traceback__)
    return new_exc
