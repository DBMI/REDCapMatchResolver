"""
Module: contains the MatchRecordGenerator class.
"""
import pandas  # type: ignore[import]

from redcapmatchresolver.match_records import MatchRecord


class MatchRecordGenerator:
    """
    Allows one-time provision of group facility info so that MatchRecords can be more easily generated.
    """

    def __init__(self, facility_addresses: list, facility_phone_numbers: list) -> None:
        if not isinstance(facility_addresses, list):
            raise TypeError("Argument 'facility_addresses' is not the expected list.")

        self.__facility_addresses = facility_addresses

        if not isinstance(facility_phone_numbers, list):
            raise TypeError(
                "Argument 'facility_phone_numbers' is not the expected list."
            )

        self.__facility_phone_numbers = facility_phone_numbers

    def generate_match_record(self, row: pandas.Series) -> MatchRecord:
        if not isinstance(row, pandas.Series):
            raise TypeError("Argument 'row' is not the expected pandas.Series.")

        return MatchRecord(
            row=row,
            facility_addresses=self.__facility_addresses,
            facility_phone_numbers=self.__facility_phone_numbers,
        )
