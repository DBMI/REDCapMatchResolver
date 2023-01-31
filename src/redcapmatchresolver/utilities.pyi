import logging
from typing import Union

class Utilities:
    @staticmethod
    def ensure_output_path(report_filename: str = ...) -> None: ...
    @staticmethod
    def setup_logging(log_filename: Union[str, None]) -> logging.Logger: ...
