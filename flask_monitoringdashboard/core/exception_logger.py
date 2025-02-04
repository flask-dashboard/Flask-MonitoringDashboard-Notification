from typing import TYPE_CHECKING
import json
import linecache
from types import TracebackType
from flask_monitoringdashboard.database import CodeLine
from flask_monitoringdashboard.database.exception_info import add_exception_stack_line, add_exception_info

def create_codeline(tb: TracebackType) -> CodeLine:
    c_line = CodeLine()
    c_line.filename = tb.tb_frame.f_code.co_filename
    c_line.line_number = tb.tb_lineno
    c_line.function_name = tb.tb_frame.f_code.co_name
    c_line.code = linecache.getline(c_line.filename, c_line.line_number)
    return c_line


class ExceptionLogger():
    def __init__(self, exc_info):
        self.type : type[BaseException] = exc_info[0]
        self.value : BaseException = exc_info[1]
        self.tb : TracebackType = exc_info[2]


    def rec_tb(self, tb : TracebackType, acc):
        if tb is None:
            return acc
            #f"Endpoint: {tb.tb_frame.f_code.co_name} at line number: {tb.tb_lineno} in file: {tb.tb_frame.f_code.co_filename}"
        print(tb.tb_frame.f_code.co_name)
        acc.append(create_codeline(tb))
        return self.rec_tb(tb.tb_next, acc)

    def log(self, request_id: int, session):
        add_exception_info(session, request_id, str(self.type), str(self.value))
        print("hitttttttttttttttttttttt")

        lines = self.rec_tb(self.tb, [])
        for i in range(len(lines)):
            add_exception_stack_line(session, request_id, i, lines[i])
        

