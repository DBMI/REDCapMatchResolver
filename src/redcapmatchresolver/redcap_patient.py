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
    __dob_keywords = ["birth_date", "dob"]
    __phone_keywords = ["home_phone", "phone", "phone_number", "work_phone"]

    #   These fields --describe-- the patient but don't --indentify-- them.
    __info_fields = ["hpi_percentile", "hpi_score"]

    def __init__(self, df: pandas.DataFrame, clinics: REDCapClinic) -> None:
        if not isinstance(df, pandas.DataFrame):
            raise TypeError("Argument 'df' is not the expected DataFrame.")

        #   Make all column names lowercase, to be REDCap compatible.
        self.__df = df.copy()
        self.__df.columns = map(str.lower, self.__df.columns)
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
            #   https://www.statology.org/pandas-apply-inplace/
            self.__df.loc[:, date_column_name] = self.__df.loc[
                :, date_column_name
            ].apply(clean_up_date)

        phone_column_names = [
            col for col in columns_list if col in self.__phone_keywords
        ]

        for phone_column_name in phone_column_names:
            self.__df.loc[:, phone_column_name] = self.__df.loc[
                :, phone_column_name
            ].apply(clean_up_phone)

    def csv(self, columns: list | None = None, include_headers: bool = True) -> str:
        """Creates one line summary of patient record, suitable for a .csv file.

        Parameters
        ----------
        columns : list  Optional list of which fields go where
        include_headers : bool Optional: do we show the headers? (Default: True)

        Returns
        -------
        csv_summary : str
        """
        df_including_best_appt = self.to_df()

        if isinstance(columns, list):
            #   Only request columns that are present in the dataframe.
            columns_present = [
                c for c in columns if c in df_including_best_appt.columns
            ]
            return df_including_best_appt.to_csv(
                columns=columns_present, header=include_headers, line_terminator=""
            )

        return df_including_best_appt.to_csv(header=include_headers, line_terminator="")

    def __find_appointments(self, clinics: REDCapClinic) -> None:
        if not isinstance(clinics, REDCapClinic):
            raise TypeError(
                "Argument 'clinics' is not the expected REDCapClinic object."
            )

        #   Which columns are NOT part of the appointment?
        (
            self.__patient_identifying_fields,
            appointment_fields,
        ) = self.__distinguish_fields(list(self.__df.columns))

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

    def __distinguish_fields(self, headers: list) -> tuple:
        appointment_fields = REDCapAppointment.applicable_header_fields(headers)
        appointment_fields = [field.lower() for field in appointment_fields]
        patient_identifying_fields = [
            term
            for term in headers
            if term not in appointment_fields and term not in self.__info_fields
        ]
        return patient_identifying_fields, appointment_fields

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

        for field in self.__patient_identifying_fields:
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
                self.__df["study_id"] = study_id
            elif isinstance(study_id, int):
                self.__df["study_id"] = str(study_id)

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
            df["appointment_date"] = best_appt.value("date")
            df["appointment_time"] = best_appt.value("time")
            df["appointment_clinic"] = best_appt.value("department")

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
            this_value = self.__df[field].values[0]
            return str(this_value)

        return None
