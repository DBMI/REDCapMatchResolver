"""
Module: contains class REDCapReportWriter
used to produce list of patient matches to be reviewed.
"""

import os
from pathlib import Path
from typing import List, Union

from redcaputilities.directories import ensure_output_path_exists
from redcaputilities.logging import patient_data_directory, setup_logging


class REDCapReportWriter:  # pylint: disable=logging-fstring-interpolation
    """
    Produces formatted patient report.
    """

    addendum = (
        "Review: ABOVE (↑) patients are\n"
        "    ☐ Same\n"
        "    ☐ NOT Same: Relatives\n"
        "    ☐ NOT Same: Living at same address\n"
        "    ☐ NOT Same: Parent & child\n"
        "    ☐ NOT Same: Other\n\n"
        "Notes:...................................................\n\n"
    )

    def __init__(self):
        self.__log = setup_logging(log_filename="redcap_report_writer.log")
        self.__reports: List[str] = []

    def add_match(self, match: str) -> None:
        """Allows external code to add a pre-formatted text block comparing two patient records.

        Parameters
        ----------
        match : str     Pre-formatted block of text
        """
        if match is not None and isinstance(match, str) and len(match) > 0:
            self.__reports.append(match)

    @staticmethod
    def __ensure_safe_path(target_path: str) -> str:
        if patient_data_directory() not in target_path:
            path_parts = Path(target_path).parts
            target_path = patient_data_directory()

            for part in path_parts[1:]:
                target_path = os.path.join(target_path, part)

        return target_path

    def num_reports(self) -> int:
        """Allows external code to ask if there's anything to report.

        Returns
        -------
        count : int
        """
        return len(self.__reports)

    def write(self, report_filename: Union[str, None] = None) -> tuple:
        """Writes out the accumulated match reports, assigning a sequential number to each one.

        Parameters
        ----------
        report_filename : str Full path to location of desired report.

        Returns
        -------
        package : tuple of (bool, str) representing success/filename
        """

        success: bool = False
        total_number_of_match_reports = self.num_reports()

        #   Don't generate an empty report.
        if total_number_of_match_reports > 0:
            if not isinstance(report_filename, str) or len(report_filename) == 0:
                report_filename = os.path.join(
                    patient_data_directory(), "patient_reports", "patient_report.txt"
                )

            report_filename = REDCapReportWriter.__ensure_safe_path(report_filename)
            ensure_output_path_exists(report_filename)

            match_index = 1

            with open(report_filename, mode="a", encoding="utf-8") as file_obj:
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
                            return success, report_filename  # pragma: no cover

                    except Exception as file_write_error:  # pragma: no cover
                        self.__log.exception(
                            "Unable to write match to log because {file_write_error}."
                        )
                        raise file_write_error

                    match_index += 1

        success = True
        return success, report_filename


if __name__ == "__main__":
    pass
