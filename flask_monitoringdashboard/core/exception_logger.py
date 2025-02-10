import traceback
import linecache
from types import TracebackType
from flask_monitoringdashboard.core.types import ExcInfo
from flask_monitoringdashboard.database import CodeLine
from flask_monitoringdashboard.database.exception_info import add_exception_stack_line, add_exception_info

def create_codeline(fs: traceback.FrameSummary):
    c_line = CodeLine()
    c_line.filename = fs.filename
    c_line.line_number = fs.lineno
    c_line.function_name = fs.name
    c_line.code = linecache.getline(c_line.filename, c_line.line_number).strip()
    return c_line

class ExceptionLogger():
    def __init__(self, exc_info: ExcInfo):
        self.type : type[BaseException] = exc_info[0]
        self.value : BaseException = exc_info[1]
        self.tb : TracebackType = exc_info[2]

    def log(self, request_id: int, session):
        add_exception_info(session, request_id, str(self.type.__name__), str(self.value))
        for idx, fs in enumerate(traceback.extract_tb(self.tb)[1:]):
            c_line = create_codeline(fs)
            add_exception_stack_line(session, request_id, idx, c_line)
        

