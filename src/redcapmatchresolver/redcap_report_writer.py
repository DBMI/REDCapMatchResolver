"""
Module: contains class REDCapMatchResolver
used to produce list of patient matches to be reviewed.
"""
import logging
from .utilities import Utilities


class REDCapMatchResolver:  # pylint: disable=logging-fstring-interpolation
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
        self._setup_output()

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
        addendum = """CRC Review: Patients are\n    ☐ Same\n    ☐ NOT Same\n"""

        if match is not None and isinstance(match, str):
            try:
                num_char_written = self.__file_obj.write(match + addendum)
                success = num_char_written == len(match) + len(addendum)
            except Exception as file_write_error:  # pragma: no cover
                self.__log.error(
                    f"Unable to write match to log because {str(file_write_error)}."
                )
                raise

        return success

    def close(self) -> None:
        """Closes the output file."""
        self.__file_obj.close()

    def _setup_output(self) -> None:
        """Initialize the output report file."""
        Utilities.ensure_output_path(self.__report_filename)

        try:  # pylint: disable=consider-using-with
            self.__file_obj = open(self.__report_filename, mode="w", encoding="utf-8")

            if self.__file_obj is None:  # pragma: no cover
                self.__log.error(
                    f"Unable to open file '{self.__report_filename}' for output."
                )

            self.__log.info(
                f"Initialized with report filename '{self.__report_filename}'."
            )
        except FileNotFoundError as file_open_error:  # pragma: no cover
            self.__log.error(
                f"Unable to open file '{self.__report_filename}' for output "
                + f"because {str(file_open_error)}."
            )
            raise


if __name__ == "__main__":
    pass
