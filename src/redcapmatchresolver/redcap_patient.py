"""
Module: contains class REDCapPatient.
"""
from __future__ import annotations
import re
from typing import Union
from redcapmatchresolver.redcap_appointment import REDCapAppointment
from redcapmatchresolver.redcap_clinic import REDCapClinic


class REDCapPatient:
    """
    Represents a patient record, allowing for multiple appointments.
    """

    #   Mark these for special handling.
    __dob_keywords = ["BIRTH_DATE", "DOB"]

    #   We create the patient object with one set of field names,
    #   but may wish to retrieve the values with slightly different names.
    __fields_dict = {
        "FIRST_NAME": "PAT_FIRST_NAME",
        "LAST_NAME": "PAT_LAST_NAME",
        "STREET_ADDRESS_LINE_1": "ADD_LINE_1",
        "STREET_ADDRESS_LINE_2": "ADD_LINE_2",
        "STATE": "STATE_ABBR",
        "ZIP_CODE": "ZIP",
        "PHONE_NUMBER": "HOME_PHONE",
        "DOB": "BIRTH_DATE",
    }
    __phone_keywords = ["PHONE"]

    def __init__(self, headers: list, row: tuple, clinics: REDCapClinic):
        #   Build a dictionary, where the keys come from 'headers' and
        #   the values come from 'row'.
        self.__record = {}
        self.__appointments = []

        if headers is None or not isinstance(headers, list) or len(headers) == 0:
            raise TypeError("Input 'headers' can't be empty.")

        #   Don't want confusion about upper/lower case. Let's set all to uppercase now.
        headers = [name.upper() for name in headers]

        #   Which header fields are NOT part of the appointment?
        (
            self._non_appointment_fields,
            appointment_fields,
        ) = REDCapPatient._not_appointment_fields(headers)
        appointment_data = []

        for index, field_name in enumerate(headers):
            if row is None or not isinstance(row, tuple) or len(row) <= index:
                #   Then this field is not present in the 'row' structure.
                #   Leave a blank.
                if field_name in appointment_fields:
                    appointment_data.append(None)
                else:
                    self.__record[field_name] = None
            else:
                if field_name in appointment_fields:
                    appointment_data.append(row[index])
                else:
                    if any(word in field_name for word in self.__phone_keywords):
                        self.__record[field_name] = self._clean_up_phone(row[index])
                    else:
                        self.__record[field_name] = row[index]

        #   Save room for study_id field.
        self.__record["STUDY_ID"] = None

        if appointment_fields and appointment_data:
            appointment_object = REDCapAppointment(
                appointment_headers=appointment_fields,
                appointment_info=appointment_data,
                clinics=clinics,
            )

            if appointment_object.valid():
                self.__appointments.append(appointment_object)

    def appointments(self) -> list:
        """Returns the list stored in self.__appointments.

        Returns
        -------
        appointments : list of REDCapAppointment objects.
        """
        return [
            appointment for appointment in self.__appointments if appointment.valid()
        ]

    def best_appointment(self) -> Union[REDCapAppointment, None]:
        """Selects the 'best' contact opportunity according to clinic priority & schedule.
        Returns
        -------
        best_appointment : REDCapAppointment
        """
        if (
            self.__appointments is None
            or not isinstance(self.__appointments, list)
            or len(self.__appointments) < 1
        ):
            return None

        best_appointment = None
        all_appointment_priorities = [
            appointment.priority() for appointment in self.__appointments
        ]

        if all_appointment_priorities:
            best_appointments_by_location = [
                appointment
                for appointment in self.__appointments
                if appointment.priority() == min(all_appointment_priorities)
            ]

        if len(best_appointments_by_location) == 1:
            return best_appointments_by_location[0]

        all_appointment_dates = [
            appointment.date() for appointment in best_appointments_by_location
        ]

        if all_appointment_dates:
            best_appointment = [
                appointment
                for appointment in best_appointments_by_location
                if appointment.date() == min(all_appointment_dates)
            ]

        return best_appointment[0]

    @staticmethod
    # Cleanup specific to dates.  We want a 2022-04-12 format.
    def _clean_up_date(date_string: str) -> Union[str, None]:
        if not date_string:
            return None

        if len(date_string.split("/")) > 1:
            ret = re.sub(r"(\d{1,2})/(\d{1,2})/(\d{4}).*", "\\3-\\1-\\2", date_string)
            temp = ret.split("-")
            try:
                ret = "%04d-%02d-%02d" % (int(temp[0]), int(temp[1]), int(temp[2]))
            except ValueError:
                pass
        else:
            ret = re.sub(r"(\d{4})-(\d{1,2})-(\d{1,2}).*", "\\1-\\2-\\3", date_string)
            temp = ret.split("-")

            try:
                ret = "%04d-%02d-%02d" % (int(temp[0]), int(temp[1]), int(temp[2]))
            except ValueError:
                pass

        return ret

    @staticmethod
    def _clean_up_phone(phone_number_string: str) -> str:
        if not phone_number_string or phone_number_string.upper().strip() == "NULL":
            return ""

        if not phone_number_string or phone_number_string.upper().strip() == "NONE":
            return ""

        numeric_filter = filter(str.isdigit, phone_number_string)
        numeric_string = "".join(numeric_filter)

        if numeric_string in (
            "0000000000",
            "10000000000",
            "9999999999",
            "19999999999",
            "1111111111",
        ):
            return ""

        if numeric_string.startswith("1") and len(numeric_string) == 11:  # 1YYYXXXZZZZ
            numeric_string = numeric_string[1:]

        if len(numeric_string) != 10:
            return phone_number_string

        prefix = numeric_string[0:3]
        exchange = numeric_string[3:6]
        rest = numeric_string[6:10]
        return f"{prefix}-{exchange}-{rest}"

    def csv(self, headers: list = None) -> str:
        """Creates one line summary of patient record, suitable for a .csv file.

        Parameters
        ----------
        headers : list  Optional list of which fields go where

        Returns
        -------
        csv_summary : str
        """
        single_appointment = None

        if self.__appointments and len(self.__appointments) > 0:
            single_appointment = self.best_appointment()

        if headers is None or not isinstance(headers, list):
            headers = self.__record.keys()

        headers = [name.upper() for name in headers]

        #   Which of these fields need special appointment handling?
        #   (Need to do this again here because the output fields are different
        #   from the ones with which the object was instantiated.)
        appointment_fields = REDCapAppointment.applicable_header_fields(headers)
        values_list = []

        for field in headers:
            value = " "

            if field in self.__record:
                value = self.__record[field]
            elif field in appointment_fields and single_appointment:
                value = single_appointment.value(field)
            elif field in self.__dob_keywords:
                #   Special date of birth formatting.
                value = REDCapPatient._clean_up_date(self.__record[field])
            elif field in self.__fields_dict:
                translated_field = self.__fields_dict[field]

                if translated_field in self.__record:
                    value = self.__record[translated_field]

            values_list.append(value)

        #   Eliminate Nones, NULLS from the list.
        values_list = ["" if v is None else v for v in values_list]
        values_list = ["" if v is "NULL" else v for v in values_list]

        #   Join with comma and space.
        csv_summary = ", ".join(values_list)

        return csv_summary

    def merge(self, other_patient: REDCapPatient) -> None:
        """Combines the appointments from two copies of the same patient.
        If the other patient is actually a different patient, does not modify itself.
        Note that there's no sophistication here, no fuzzy matching: the two objects
        must match EXACTLY everywhere except appointment department

        Parameters
        ----------
        other_patient : REDCapPatient object

        Returns
        -------
        None It merges the new appointment into the existing REDCapPatient object.
        """
        if self.same_as(other_patient):
            self.__appointments += other_patient.appointments()

    @staticmethod
    def _not_appointment_fields(headers: list) -> tuple:
        appointment_fields = REDCapAppointment.applicable_header_fields(headers)
        appointment_fields = [field.upper() for field in appointment_fields]
        non_appointment_fields = [
            term for term in headers if term not in appointment_fields
        ]
        return non_appointment_fields, appointment_fields

    def __repr__(self):  # pragma: no cover
        nice_summary = ""

        for key, value in self.__record.items():
            nice_summary += f"{key}: {value}" + "\n"

        return nice_summary

    def same_as(self, other_patient: REDCapPatient) -> bool:
        """Tests to see if two REDCapPatient objects match in every field EXCEPT appointments.

        Parameters
        ----------
        other_patient : REDCapPatient object

        Returns
        -------
        same : bool
        """
        if other_patient is None or not isinstance(other_patient, REDCapPatient):
            return False

        for field in self._non_appointment_fields:
            if self.value(field) != other_patient.value(field):
                return False

        return True

    def set_study_id(self, study_id: Union[int, str]) -> None:
        """Allows external code to set the patient's study_id after the object is instantiated.

        Parameters
        ----------
        study_id : str or int
        """
        if study_id is not None:
            if isinstance(study_id, str):
                self.__record["STUDY_ID"] = study_id
            elif isinstance(study_id, int):
                self.__record["STUDY_ID"] = str(study_id)

    def __str__(self):
        nice_summary = ""

        for key, value in self.__record.items():
            nice_summary += f"{key}: {value}" + "\n"

        return nice_summary

    def value(self, field: str) -> Union[str, None]:
        """Look up a value from the dictionary _record.

        Parameters
        ----------
        field : str Name of the property

        Returns
        -------
        value : str Value of the property, or None if it's missing.
        """
        if field in self.__record:
            return self.__record[field]

        return None


if __name__ == "__main__":
    pass
