from datetime import datetime
from typing import Union

import pandas  # type: ignore[import]

from redcapmatchresolver.redcap_clinic import REDCapClinic as REDCapClinic

class REDCapAppointment:
    __appointment_date_keywords = list
    __department_keywords = list
    __appointment_time_keywords = list

    def __init__(
        self,
        df: pandas.DataFrame,
        clinics: Union[REDCapClinic, None] = ...,
    ) -> None:
        self.__date = str
        self.__department = str
        self.__priority = int
        self.__time = str
        ...
    @staticmethod
    def applicable_header_fields(headers: list) -> list: ...
    @staticmethod
    def clean_up_date(date_string: Union[int, str, None] = ...) -> str: ...
    def csv(self) -> str: ...
    def date(self) -> Union[datetime, None]: ...
    def priority(self) -> int: ...
    def to_df(self) -> pandas.DataFrame: ...
    def valid(self) -> bool: ...
    def value(self, field: str) -> str: ...
    def __assign_priority(self, clinics) -> None:
        pass
