class REDCapReportWriter:
    addendum: str
    def __init__(self, report_filename: str = ...) -> None:
        self.__log = None
        self.__reports = None
        self.__report_filename = None
        ...
    def add_match(self, match: str) -> None: ...
    def report_filename(self) -> str: ...
    def write(self) -> bool: ...
    @classmethod
    def __ensure_safe_path(cls, report_filename):
        pass
