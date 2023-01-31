"""
Module: contains utility functions.
"""
import logging
import os
import sys
from typing import Union


class Utilities:  # pylint: disable=too-few-public-methods
    """Contains useful static methods."""

    @staticmethod
    def ensure_output_path(report_filename: str = "") -> None:
        """Make sure the directory to hold the report file is prepared.

        Parameters
        ----------
        report_filename : str Full path to location of desired report.
        """
        if (
            not isinstance(report_filename, str) or len(report_filename) == 0
        ):  # pragma: no cover
            raise RuntimeError("Report filename not supplied.")

        report_path = ""

        try:
            report_path = os.path.dirname(report_filename)

            if not report_path:
                report_path = os.getcwd()

            if not os.path.exists(report_path):
                os.makedirs(report_path)
        except OSError as create_path_error:
            raise OSError(
                f"Unable to create path: '{report_path}' "
                + f"because{str(create_path_error)}."
            ) from create_path_error

    @staticmethod
    def setup_logging(log_filename: Union[str, None]) -> logging.Logger:

        if not isinstance(log_filename, str):
            log_filename = "redcap_match_resolver.log"

        """Set up the logging utility correctly."""
        # https: // stackoverflow.com / a / 49202811 / 20241849
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)

        logger = logging.getLogger(__name__)
        console_handler = logging.StreamHandler(sys.stdout)
        console_format = logging.Formatter("%(name)s - %(levelname)s - %(message)s")
        console_handler.setFormatter(console_format)

        logfile_handler = logging.FileHandler(filename=log_filename)
        logfile_format = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        logfile_handler.setFormatter(logfile_format)

        logger.addHandler(console_handler)
        logger.addHandler(logfile_handler)
        logger.setLevel(logging.INFO)
        return logger


if __name__ == "__main__":
    pass
