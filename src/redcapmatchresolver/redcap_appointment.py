"""
Module: contains class REDCapAppointment.
"""
from datetime import datetime
from typing import Union

from redcaputilities.string_cleanup import clean_up_date, clean_up_time

from redcapmatchresolver.redcap_clinic import REDCapClinic


class REDCapAppointment:
    """
    Represents a single patient appointment.
    """

    __appointment_date_keywords = ["APPOINTMENT_DATE", "APPT_DATE"]
    __appointment_time_keywords = ["APPOINTMENT_TIME", "APPT_TIME"]
    __department_keywords = ["CLINIC", "DEPARTMENT", "DEPT"]

    def __init__(
        self,
        appointment_headers: list,
        appointment_info: list,
        clinics: Union[REDCapClinic, None] = None,
    ):
        if not isinstance(appointment_headers, list) or len(appointment_headers) == 0:
            raise TypeError("Appointment headers was not the expected list.")

        if not isinstance(appointment_info, list) or len(appointment_info) == 0:
            raise TypeError("Appointment info was not the expected list.")

        #   It's OK for 'clinics' to be None--
        #   this forces the '__assign_priority' method to look them up.

        for index, header in enumerate(appointment_headers):
            if not isinstance(header, str):
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
                self.__department = str(appointment_info[index])
                continue

            if any(
                name in header.upper()
                for name in REDCapAppointment.__appointment_date_keywords
            ):
                self.__date = clean_up_date(appointment_info[index])
                self.__time = clean_up_time(appointment_info[index])

        self.__priority = self.__assign_priority(clinics=clinics)

    @staticmethod
    def applicable_header_fields(headers: list) -> list:
        """Which of the fields listed apply to the appointment?

        Parameters
        ----------
        headers : list of strings

        Returns
        -------
        applicable_headers : list of the input strings that would be used by this class.
        """
        applicable_headers = []

        if not isinstance(headers, list) or len(headers) == 0:
            raise TypeError("Argument 'headers' is not the expected list.")

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

    def __assign_priority(self, clinics: Union[REDCapClinic, None]) -> int:

        if not isinstance(clinics, REDCapClinic):
            clinics = REDCapClinic()

        priority = clinics.priority(self.__department)
        return priority

    #   Cleanup specific to dates.  We want a 2022-04-12 format.
    #   Making this a public method so that it can be used in REDCapPatient class.
    def csv(self) -> str:
        """Returns department and date in a comma-separated format.

        Returns
        -------
        csv_summary : str
        """
        return f"{self.__department}, {self.date()}"

    def date(self) -> Union[datetime, None]:
        """Convert stored date and time strings into one datetime object.

        Returns
        -------
        datetime_value : datetime
        """
        date_time_combined = self.__date + " " + self.__time
        return datetime.strptime(date_time_combined, "%Y-%m-%d %H:%M:%S")

    def priority(self) -> int:
        """Allows querying of self.__priority value.

        Returns
        -------
        priority : int
        """
        return self.__priority

    def valid(self) -> bool:
        """Tests to see if department, date both available.

        Returns
        -------
        valid : bool
        """
        date_value = self.date()

        return isinstance(self.__department, str) and isinstance(date_value, datetime)

    def value(self, field: str) -> str:
        """Retrieves either the department or date as requested.

        Parameters
        ----------
        field : str     Like 'dept' or 'date'

        Returns
        -------
        value_string : str

        """
        if not isinstance(field, str) or len(field) == 0:
            return ""

        if "date" in field.lower():
            return self.__date

        clinic_keywords = [
            keyword.lower() for keyword in REDCapAppointment.__department_keywords
        ]

        if any(name in field.lower() for name in clinic_keywords):
            return self.__department

        if "time" in field.lower():
            return self.__time

        return ""


if __name__ == "__main__":
    pass
