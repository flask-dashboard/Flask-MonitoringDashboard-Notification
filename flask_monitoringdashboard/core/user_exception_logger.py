class ScopedExceptionLogger():
    def __init__(self) -> None:
        self.exc_list = []
        self.raised = None

    def add_exc(self, e):
        self.exc_list.append(e)

