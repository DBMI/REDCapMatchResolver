import pandas  # type: ignore[import]

from redcapmatchresolver.match_records import MatchRecord

class MatchRecordGenerator:
    def __init__(self, facility_addresses: list, facility_phone_numbers: list) -> None:
        self.__facility_addresses: list = []
        self.__facility_phone_numbers: list = []

    def generate_match_record(self, row: pandas.Series) -> MatchRecord: ...
