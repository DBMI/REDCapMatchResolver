"""
Module: contains class REDCapPatient.
"""
from __future__ import annotations

from dateutil.parser import ParserError
from redcaputilities.string_cleanup import clean_up_date, clean_up_phone
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

    def __init__(self, headers: list, row: tuple, clinics: REDCapClinic) -> None:
        #   Build a dictionary, where the keys come from 'headers' and
        #   the values come from 'row'. Save room for study_id field.
        self.__record = {"STUDY_ID": None}

        self.__appointments = []

        if not isinstance(headers, list) or len(headers) == 0:
            raise TypeError("Input 'headers' can't be empty.")

        self.__build_record(headers, row, clinics)

    def appointments(self) -> list:
        """Returns the list stored in self.__appointments.

        Returns
        -------
        appointments : list of REDCapAppointment objects.
        """
        return [
            appointment for appointment in self.__appointments if appointment.valid()
        ]

    def best_appointment(self) -> REDCapAppointment | None:
        """Selects the 'best' contact opportunity according to clinic priority & schedule.
        Returns
        -------
        best_appointment : REDCapAppointment
        """
        if not isinstance(self.__appointments, list) or len(self.__appointments) < 1:
            return None

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
                    if appointment.date()
                    == min(d for d in all_appointment_dates if d is not None)
                ]
                return best_appointment[0]

    def __build_record(self, headers: list, row: tuple, clinics: REDCapClinic) -> None:
        #   Don't want confusion about upper/lower case. Let's set all to uppercase now.
        headers = [name.upper() for name in headers]

        #   Which header fields are NOT part of the appointment?
        (
            self.__non_appointment_fields,
            appointment_fields,
        ) = REDCapPatient.__not_appointment_fields(headers)
        appointment_data = []  # type: ignore[var-annotated]

        for index, field_name in enumerate(headers):
            if not isinstance(row, tuple) or len(row) <= index:
                #   Then this field is not present in the 'row' structure.
                #   Leave a blank.
                if field_name in appointment_fields:
                    appointment_data.append(None)
                else:
                    self.__record[field_name] = ""
            else:
                if field_name in appointment_fields:
                    appointment_data.append(row[index])
                else:
                    if any(word in field_name for word in self.__phone_keywords):
                        self.__record[field_name] = str(clean_up_phone(row[index]))
                    else:
                        self.__record[field_name] = row[index]

        if appointment_fields and appointment_data:
            try:
                appointment_object = REDCapAppointment(
                    appointment_headers=appointment_fields,
                    appointment_info=appointment_data,
                    clinics=clinics,
                )

                if appointment_object.valid():
                    self.__appointments.append(appointment_object)
            except (ParserError, TypeError):
                # Then there is no valid Appointment object.
                pass

    def csv(self, headers: list | None = None) -> str:
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

        if not isinstance(headers, list) or len(headers) == 0:
            headers = list(self.__record.keys())

        headers = [name.upper() for name in headers]

        #   Which of these fields need special appointment handling?
        #   (Need to do this again here because the output fields are different
        #   from the ones with which the object was instantiated.)
        appointment_fields = REDCapAppointment.applicable_header_fields(headers)
        values_list = []

        for field in headers:
            value: int | str | None = None

            if field in self.__record:
                value = self.__record[field]
            elif field in appointment_fields and single_appointment:
                value = single_appointment.value(field)
            elif field in self.__fields_dict:
                translated_field = self.__fields_dict[field]

                if translated_field in self.__record:
                    value = self.__record[translated_field]

            if field in self.__dob_keywords:
                #   Special date of birth formatting.
                #   Doing this clean up after the above means we don't have to separately
                #    handle whether field is already part of the self.__record ('BIRTH_DATE')
                #    or needs to be translated first ('DOB').
                value = clean_up_date(value)

            #   Stuff an empty into value if it's None.
            if not value:
                value = ""

            #   Get rid of stray commas that will look like new fields.
            value_as_str = str(value)
            values_list.append(value_as_str.replace(",", ""))

        #   Eliminate Nones, NULLS from the list.
        values_list = ["" if v is None else v for v in values_list]
        values_list = ["" if v == "NULL" else v for v in values_list]
        values_list = ["" if v == " " else v for v in values_list]

        #   Join with comma and space.
        csv_summary = ",".join(values_list)

        #   Get rid of double-space empties.
        csv_summary = csv_summary.replace("  ", " ").replace(", ,", ",,")
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
    def __not_appointment_fields(headers: list) -> tuple:
        appointment_fields = REDCapAppointment.applicable_header_fields(headers)
        appointment_fields = [field.upper() for field in appointment_fields]
        non_appointment_fields = [
            term for term in headers if term not in appointment_fields
        ]
        return non_appointment_fields, appointment_fields

    def __repr__(self) -> str:  # pragma: no cover
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
        if not isinstance(other_patient, REDCapPatient):
            return False

        for field in self.__non_appointment_fields:
            if self.value(field) != other_patient.value(field):
                return False

        return True

    def set_study_id(self, study_id: int | str) -> None:
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

    def __str__(self) -> str:
        nice_summary = ""

        for key, value in self.__record.items():
            nice_summary += f"{key}: {value}" + "\n"

        return nice_summary

    def value(self, field: str) -> str | None:
        """Look up a value from the dictionary _record.

        Parameters
        ----------
        field : str Name of the property

        Returns
        -------
        value : str Value of the property, or None if it's missing.
        """
        if field in self.__record:
            return str(self.__record[field])

        return None
