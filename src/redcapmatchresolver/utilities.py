"""
Module: contains utility functions.
"""
from datetime import datetime
import logging
import os


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
    def setup_logging() -> None:
        """Set up the logging utility correctly."""
        # https: // stackoverflow.com / a / 49202811 / 20241849
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)

        logging.basicConfig(
            datefmt="%Y_%m_%d %I:%M:%S %p",
            filename=datetime.now().strftime("%Y_%m_%d_%H%M%S") + ".log",
            format="%(asctime)s %(message)s",
            level=logging.DEBUG,
        )


if __name__ == "__main__":
    pass
