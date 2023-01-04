"""
Module: contains class REDCapReportWriter
used to produce list of patient matches to be reviewed.
"""
import logging
from typing import List

from .utilities import Utilities


class REDCapReportWriter:  # pylint: disable=logging-fstring-interpolation
    """
    Produces formatted patient report.
    """

    addendum = (
        "CRC Review: ABOVE (↑) patients are\n"
        "    ☐ Same\n"
        "    ☐ NOT Same: Family members\n"
        "    ☐ NOT Same: Living at same address\n"
        "    ☐ NOT Same: Parent & child\n"
        "    ☐ NOT Same: Other\n\n"
        "Notes:...................................................\n\n"
    )

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
        self.__reports: List[str] = []

    def add_match(self, match: str) -> None:
        """Allows external code to add a pre-formatted text block comparing two patient records.

        Parameters
        ----------
        match : str     Pre-formatted block of text
        """
        if match is not None and isinstance(match, str) and len(match) > 0:
            self.__reports.append(match)

    def report_filename(self) -> str:
        """Allows external code to ask where the file went.

        Returns
        -------
        filename : str
        """
        return self.__report_filename

    def write(self) -> bool:
        """Writes out the accumulated match reports, assigning a sequential number to each one.

        Returns
        -------
        success : bool
        """
        match_index = 1
        total_number_of_match_reports = len(self.__reports)

        with (open(self.__report_filename, mode="a", encoding="utf-8")) as file_obj:
            for match in self.__reports:
                record_numbering_line = (
                    f"Record {match_index} of {total_number_of_match_reports}\n"
                )
                this_record = (
                    match + record_numbering_line + REDCapReportWriter.addendum
                )

                try:
                    num_char_written = file_obj.write(this_record)

                    if num_char_written != len(this_record):
                        return False  # pragma: no cover

                except Exception as file_write_error:  # pragma: no cover
                    self.__log.exception(
                        "Unable to write match to log because {file_write_error}."
                    )
                    raise file_write_error

                match_index += 1

        return True


if __name__ == "__main__":
    pass
