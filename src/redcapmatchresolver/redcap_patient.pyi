from typing import Union

import pandas

from redcapmatchresolver.redcap_appointment import (
    REDCapAppointment as REDCapAppointment,
)
from redcapmatchresolver.redcap_clinic import REDCapClinic as REDCapClinic

class REDCapPatient:
    def __init__(self, df: pandas.DataFrame, clinics: REDCapClinic) -> None:
        self.__appointments = list
        self.__dob_keywords = list
        self.__non_appointment_fields = list
        self.__phone_keywords = list
        self.__df = pandas.DataFrame
        ...
    def appointments(self) -> list: ...
    def best_appointment(self) -> Union[REDCapAppointment, None]: ...
    def __cleanup(self) -> None:
        pass
    def csv(self, headers: Union[list, None] = ...) -> str: ...
    def __find_appointments(self, clinics) -> None:
        pass
    def merge(self, other_patient: REDCapPatient) -> None: ...
    @staticmethod
    def __not_appointment_fields(headers: list) -> tuple:
        pass
    def same_as(self, other_patient: REDCapPatient) -> bool: ...
    def set_study_id(self, study_id: Union[int, str]) -> None: ...
    def value(self, field: str) -> Union[str, None]: ...
