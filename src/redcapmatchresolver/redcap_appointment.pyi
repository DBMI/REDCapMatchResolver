from datetime import datetime
from typing import Union

from redcapmatchresolver.redcap_clinic import REDCapClinic as REDCapClinic

class REDCapAppointment:
    __appointment_date_keywords = None
    __department_keywords = None
    __appointment_time_keywords = None

    def __init__(
        self,
        appointment_headers: list,
        appointment_info: list,
        clinics: Union[REDCapClinic, None] = ...,
    ) -> None:
        self.__priority = None
        self.__time = None
        self.__date = None
        self.__department = None
        ...
    @staticmethod
    def applicable_header_fields(headers: list) -> list: ...
    @staticmethod
    def clean_up_date(date_string: Union[int, str, None] = ...) -> str: ...
    def csv(self) -> str: ...
    def date(self) -> Union[datetime, None]: ...
    def priority(self) -> int: ...
    def valid(self) -> bool: ...
    def value(self, field: str) -> str: ...
    def __assign_priority(self, clinics):
        pass
