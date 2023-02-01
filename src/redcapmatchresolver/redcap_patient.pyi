from redcapmatchresolver.redcap_appointment import REDCapAppointment as REDCapAppointment
from redcapmatchresolver.redcap_clinic import REDCapClinic as REDCapClinic

class REDCapPatient:
    def __init__(self, headers: list, row: tuple, clinics: REDCapClinic) -> None: ...
    def appointments(self) -> list: ...
    def best_appointment(self) -> Union[REDCapAppointment, None]: ...
    def csv(self, headers: Union[list, None] = ...) -> str: ...
    def merge(self, other_patient: REDCapPatient) -> None: ...
    def same_as(self, other_patient: REDCapPatient) -> bool: ...
    def set_study_id(self, study_id: Union[int, str]) -> None: ...
    def value(self, field: str) -> Union[str, None]: ...