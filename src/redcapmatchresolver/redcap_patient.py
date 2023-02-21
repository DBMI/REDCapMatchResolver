"""
Module: contains class REDCapPatient.
"""
from __future__ import annotations

import pandas
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
    __phone_keywords = ["PHONE", "HOME_PHONE", "WORK_PHONE"]

    def __init__(self, df: pandas.DataFrame, clinics: REDCapClinic) -> None:
        #   Build a dictionary, where the keys come from 'headers' and
        #   the values come from 'row'. Save room for study_id field.
        if not isinstance(df, pandas.DataFrame):
            raise TypeError("Argument 'df' is not the expected DataFrame.")

        #   Make all column names uppercase.
        df.columns = map(str.upper, df.columns)
        self.__df = df
        self.__cleanup()

        self.__appointments = []
        self.__find_appointments(clinics)

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

    def __cleanup(self) -> None:
        """Cleans up the phone and date fields."""
        columns_list = list(self.__df.columns)
        date_column_names = [col for col in columns_list if col in self.__dob_keywords]

        for date_column_name in date_column_names:
            self.__df[date_column_name] = self.__df[date_column_name].apply(
                clean_up_date
            )

        phone_column_names = [
            col for col in columns_list if col in self.__phone_keywords
        ]

        for phone_column_name in phone_column_names:
            self.__df[phone_column_name] = self.__df[phone_column_name].apply(
                clean_up_phone
            )

    def csv(self, headers: list | None = None) -> str:
        """Creates one line summary of patient record, suitable for a .csv file.

        Parameters
        ----------
        headers : list  Optional list of which fields go where

        Returns
        -------
        csv_summary : str
        """
        df_including_best_appt = self.to_df()

        if isinstance(headers, list):
            #   Only request columns that are present in the dataframe.
            headers_present = [
                h for h in headers if h in df_including_best_appt.columns
            ]
            return df_including_best_appt.to_csv(columns=headers_present)

        return df_including_best_appt.to_csv()

    def __find_appointments(self, clinics: REDCapClinic) -> None:
        if not isinstance(clinics, REDCapClinic):
            raise TypeError(
                "Argument 'clinics' is not the expected REDCapClinic object."
            )

        #   Which columns are NOT part of the appointment?
        (
            self.__non_appointment_fields,
            appointment_fields,
        ) = REDCapPatient.__not_appointment_fields(list(self.__df.columns))

        df_subset = self.__df[appointment_fields]
        appointment_object = REDCapAppointment(
            df=df_subset,
            clinics=clinics,
        )

        if appointment_object.valid():
            self.__appointments.append(appointment_object)

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
        return self.__df.to_markdown()

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
                self.__df["STUDY_ID"] = study_id
            elif isinstance(study_id, int):
                self.__df["STUDY_ID"] = str(study_id)

    # https: // stackoverflow.com / a / 60202636 / 20241849
    def __str__(self) -> str:
        return self.__df.to_markdown()

    def to_df(self) -> pandas.DataFrame:
        """Converts Patient object to a pandas DataFrame, including the best appointment.

        Returns
        -------
        df : pandas.DataFrame
        """
        df = self.__df

        #   Substitute the best appointment for the appointment
        #   that just happened to be assigned last.
        best_appt = self.best_appointment()

        if best_appt:
            df["APPT_DATE_TIME"] = best_appt.value("datetime")
            df["DEPARTMENT_NAME"] = best_appt.value("department")

        return df

    def value(self, field: str) -> str | None:
        """Look up a value from the dictionary _record.

        Parameters
        ----------
        field : str Name of the property

        Returns
        -------
        value : str Value of the property, or None if it's missing.
        """
        if field in self.__df:
            this_value = self.__df[field][0]
            return str(this_value)

        return None
