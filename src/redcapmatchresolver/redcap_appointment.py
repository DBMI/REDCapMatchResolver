"""
Module: contains class REDCapAppointment.
"""
from datetime import datetime
import re
from typing import Union


class REDCapAppointment:
    """
    Represents a single patient appointment.
    """

    __appointment_date_keywords = ["APPOINTMENT_DATE", "APPT_DATE"]
    __appointment_time_keywords = ["APPOINTMENT_TIME", "APPT_TIME"]
    __department_keywords = ["CLINIC", "DEPARTMENT", "DEPT"]

    def __init__(self, appointment_headers: list = None, appointment_info: list = None):
        if (
            appointment_headers is None
            or not isinstance(appointment_headers, list)
            or len(appointment_headers) == 0
        ):
            raise TypeError("Appointment headers was not the expected list.")

        if (
            appointment_info is None
            or not isinstance(appointment_info, list)
            or len(appointment_info) == 0
        ):
            raise TypeError("Appointment info was not the expected list.")

        for index, header in enumerate(appointment_headers):
            if header is None or not isinstance(header, str):
                raise TypeError("Element in 'headers' is not the expected string.")

            if len(appointment_info) <= index:
                raise TypeError(
                    f"List 'appointment_headers' has length {len(appointment_headers)} "
                    f"but 'appointment_info' has length {len(appointment_info)}."
                )

            if any(
                name in header.upper()
                for name in REDCapAppointment.__department_keywords
            ):
                self.__department = appointment_info[index]
                continue

            if any(
                name in header.upper()
                for name in REDCapAppointment.__appointment_date_keywords
            ):
                self.__date = REDCapAppointment._clean_up_date(appointment_info[index])
                self.__time = REDCapAppointment._clean_up_time(appointment_info[index])

    @staticmethod
    def applicable_header_fields(headers: list = None) -> list:
        """Which of the fields listed apply to the appointment?

        Parameters
        ----------
        headers : list of strings

        Returns
        -------
        applicable_headers : list of the input strings that would be used by this class.
        """
        applicable_headers = []

        for header in headers:
            header_upper_case = header.upper()

            is_appointment_date = any(
                name in header_upper_case
                for name in REDCapAppointment.__appointment_date_keywords
            )
            is_appointment_department = any(
                name in header_upper_case
                for name in REDCapAppointment.__department_keywords
            )
            is_appointment_time = any(
                name in header_upper_case
                for name in REDCapAppointment.__appointment_time_keywords
            )

            if is_appointment_date or is_appointment_department or is_appointment_time:
                applicable_headers.append(header)

        return applicable_headers

    # Cleanup specific to dates.  We want a 2022-04-12 format.
    @staticmethod
    def _clean_up_date(date_string: str = None) -> str:
        if not date_string:  # pragma: no cover
            return None

        if len(date_string.split("/")) > 1:
            ret = re.sub(r"(\d{1,2})/(\d{1,2})/(\d{4}).*", "\\3-\\1-\\2", date_string)
            temp = ret.split("-")
            ret = f"{int(temp[0]):04d}-{int(temp[1]):02d}-{int(temp[2]):02d}"
        else:
            ret = re.sub(r"(\d{4})-(\d{1,2})-(\d{1,2}).*", "\\1-\\2-\\3", date_string)
            temp = ret.split("-")
            ret = f"{int(temp[0]):04d}-{int(temp[1]):02d}-{int(temp[2]):02d}"

        return ret

    # clean up specific to time.  We want a 12:30:01 format.
    @staticmethod
    def _clean_up_time(time_string: str = None) -> str:
        if not time_string or len(time_string.split()) < 2:
            return None

        time_string = time_string.split()[1]
        ret = ""

        if len(time_string.split(":")) > 1:
            ret = re.sub(r"(\d{1,2}):(\d{1,2}):(\d{1,2}).*", "\\1:\\2:\\3", time_string)
            temp = ret.split(":")
            ret = f"{int(temp[0]):d}:{int(temp[1]):02d}:{int(temp[2]):02d}"

        return ret

    def csv(self) -> str:
        """Returns department and date in a comma-separated format.

        Returns
        -------
        csv_summary : str
        """
        if self.valid():
            csv_summary = f"{self.__department}, {self.date()}"
        else:
            csv_summary = " , "

        return csv_summary

    def date(self) -> Union[datetime, None]:
        """Convert stored date and time strings into one datetime object.

        Returns
        -------
        datetime_value : datetime
        """
        try:
            date_time_combined = self.__date + " " + self.__time
            datetime_value = datetime.strptime(date_time_combined, "%Y-%m-%d %H:%M:%S")
        except TypeError:
            #   One of the strings (either date or time) are empty or None, so just return None.
            return None
        except ValueError as error:
            raise ValueError(
                f"Unable to parse date {self.__date} and time {self.__time}."
            ) from error

        return datetime_value

    def valid(self) -> bool:
        """Tests to see if department, date both available.

        Returns
        -------
        valid : bool
        """
        date_value = self.date()

        return (
            self.__department is not None
            and isinstance(self.__department, str)
            and date_value is not None
            and isinstance(date_value, datetime)
        )

    def value(self, field: str) -> str:
        """Retrieves either the department or date as requested.

        Parameters
        ----------
        field : str     Like 'dept' or 'date'

        Returns
        -------
        value_string : str

        """
        if field is None or not isinstance(field, str):
            return ""

        if "date" in field.lower():
            return self.__date

        if any(name in field.lower() for name in ["clinic", "dept", "department"]):
            return self.__department

        if "time" in field.lower():
            return self.__time

        return ""


if __name__ == "__main__":
    pass
