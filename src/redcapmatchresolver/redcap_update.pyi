from typing import Union

class REDCapUpdate:
    def __init__(self) -> None:
        self.__update_needed: bool
        self.__first_name: str
        self.__last_name: str
        self.__study_id: int
    def needed(self) -> bool:
        pass
    def package(self) -> dict:
        pass
    def set(self, property: str, value: Union[int, str]) -> None:
        pass
    def to_query(self) -> str: ...
