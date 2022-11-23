"""
Module: contains class REDCapReportWriter
used to produce list of patient matches to be reviewed.
"""
import logging
import os
from .utilities import Utilities


class REDCapReportWriter:  # pylint: disable=logging-fstring-interpolation
    """
    Produces formatted patient report.
    """

    def __init__(self, report_filename: str = "patient_report.txt"):
        """
        Parameters
        ----------
        report_filename : str Full path to location of desired report.
        """
        Utilities.setup_logging()
        self.__log = logging.getLogger(__name__)
        self.__report_filename = report_filename
        Utilities.ensure_output_path(self.__report_filename)

    def add_match(self, match: str = None) -> bool:
        """Allows external code to add a pre-formatted text block comparing two patient records.

        Parameters
        ----------
        match str Pre-formatted block of text

        Returns
        -------
        success bool Did it work or not?
        """
        success = False
        addendum = (
            """CRC Review: ABOVE (↑) patients are\n    ☐ Same\n    ☐ NOT Same\n"""
        )

        if match is not None and isinstance(match, str):
            try:
                with (
                    open(self.__report_filename, mode="a", encoding="utf-8")
                ) as file_obj:
                    num_char_written = file_obj.write(match + addendum)
                    success = num_char_written == len(match) + len(addendum)
            except Exception as file_write_error:  # pragma: no cover
                self.__log.error(
                    f"Unable to write match to log because {str(file_write_error)}."
                )
                raise

        return success


if __name__ == "__main__":
    pass
