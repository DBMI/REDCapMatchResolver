"""
Module: contains class REDCapPatient.
"""
from __future__ import annotations
from typing import Union
from redcapmatchresolver.redcap_appointment import REDCapAppointment


class REDCapPatient:
    """
    Represents a patient record, allowing for multiple appointments.
    """

    def __init__(self, headers: list = None, row: list = None):
        #   Build a dictionary, where the keys come from 'headers' and
        #   the values come from 'row'.
        self.__record = {}
        self.__appointments = []

        if headers is None or not isinstance(headers, list) or len(headers) == 0:
            raise TypeError("Input 'headers' can't be empty.")

        #   Which header fields are NOT part of the appointment?
        (
            self._non_appointment_fields,
            appointment_fields,
        ) = REDCapPatient._not_appointment_fields(headers)
        appointment_data = []

        for index, field_name in enumerate(headers):
            if row is None or not isinstance(row, list) or len(row) <= index:
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
                    self.__record[field_name] = row[index]

        if appointment_fields and appointment_data:
            appointment_object = REDCapAppointment(appointment_fields, appointment_data)

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
        """Selects the 'best' contact opportunity according to heuristics.
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
        all_appointment_dates = [
            appointment.date()
            for appointment in self.__appointments
            if appointment.valid()
        ]

        if all_appointment_dates:
            best_appointment = self.__appointments[
                all_appointment_dates.index(max(all_appointment_dates))
            ]

        return best_appointment

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
