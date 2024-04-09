from typing import Union

import pandas  # type: ignore[import]

from redcapmatchresolver.redcap_appointment import (
    REDCapAppointment as REDCapAppointment,
)
from redcapmatchresolver.redcap_clinic import REDCapClinic as REDCapClinic

class REDCapPatient:
    def __init__(self, df: pandas.DataFrame, clinics: REDCapClinic) -> None:
        self.__appointments = list
        self.__dob_keywords = list
        self.__info_fields = list
        self.__non_appointment_fields = list
        self.__phone_keywords = list
        self.__df = pandas.DataFrame
        ...

    def appointments(self) -> list: ...
    def best_appointment(self) -> Union[REDCapAppointment, None]: ...
    def __cleanup(self) -> None:
        pass

    def csv(
        self, columns: Union[list, None] = None, include_headers: bool = True
    ) -> str: ...
    def __distinguish_fields(self, headers: list) -> tuple:
        pass

    def __find_appointments(self, clinics) -> None:
        pass

    def merge(self, other_patient: REDCapPatient) -> None: ...
    def same_as(self, other_patient: REDCapPatient) -> bool: ...
    def set_study_id(self, study_id: Union[int, str]) -> None: ...
    def to_df(self) -> pandas.DataFrame:
        pass

    def value(self, field: str) -> Union[str, None]: ...
