import traceback
import linecache
import hashlib

from types import TracebackType
from flask_monitoringdashboard import config
from flask_monitoringdashboard.database import CodeLine
from flask_monitoringdashboard.database.exception_info import add_exception_info
from flask_monitoringdashboard.database.full_stack_trace import add_full_stack_trace, get_stack_trace_by_hash
from flask_monitoringdashboard.database.exception_stack_line import add_exception_stack_line

def create_codeline(fs: traceback.FrameSummary):
    c_line = CodeLine()
    c_line.filename = fs.filename.replace(config.app.root_path, '.')
    c_line.line_number = fs.lineno
    c_line.function_name = fs.name
    c_line.code = linecache.getline(fs.filename, fs.lineno).strip()
    return c_line

def hash_stack_trace(self):
    stack_trace_string = ''.join(traceback.format_exception(self.type, self.value, self.tb))
    stack_trace_hash = hashlib.sha256(stack_trace_string.encode('utf-8')).hexdigest()
    
    return stack_trace_hash

class ExceptionLogger():
    def __init__(self, exc_info):
        self.type : type[BaseException] = exc_info[0]
        self.value : BaseException = exc_info[1]
        self.tb : TracebackType = exc_info[2]

    def log(self, request_id: int, session):
        hashed_trace = hash_stack_trace(self)
        existing_trace = get_stack_trace_by_hash(session, hashed_trace)
        
        if existing_trace:
            trace_id = existing_trace.id
        else:
            trace_id = add_full_stack_trace(session, hashed_trace)
            print(f"hit request_id: {request_id}")
            for idx, fs in enumerate(traceback.extract_tb(self.tb)[1:]):
                c_line = create_codeline(fs)
                add_exception_stack_line(session, trace_id, idx, c_line)
        
        add_exception_info(session, request_id, trace_id, str(self.type.__name__), str(self.value))

        

