"""
Module test_match_generator.py, which performs automated
testing of the MatchRecordGenerator class.
"""

import redcapmatchresolver.match_records
from redcapmatchresolver.match_record_generator import MatchRecordGenerator


def test_match_record_generator(
    fake_records_dataframe, same_facility_dataframe
) -> None:
    #   We should REJECT this row's addresses & phone numbers.
    row = same_facility_dataframe.iloc[0].copy()
    facility_addresses = [row["E_ADDR_CALCULATED"]]
    facility_phone_numbers = [row["phone_number"]]

    mrg = MatchRecordGenerator(
        facility_addresses=facility_addresses,
        facility_phone_numbers=facility_phone_numbers,
    )
    assert isinstance(mrg, MatchRecordGenerator)
    match_record = mrg.generate_match_record(row)
    assert isinstance(match_record, redcapmatchresolver.match_records.MatchRecord)
    result = match_record.is_match(criteria=3)
    assert not result.bool
    score = match_record.score()
    assert isinstance(score, int)
    assert score == 0

    #   We should USE this row's addresses & phone numbers.
    row = fake_records_dataframe.iloc[0].copy()
    mrg = MatchRecordGenerator(
        facility_addresses=facility_addresses,
        facility_phone_numbers=facility_phone_numbers,
    )
    assert isinstance(mrg, MatchRecordGenerator)
    match_record = mrg.generate_match_record(row)
    assert isinstance(match_record, redcapmatchresolver.match_records.MatchRecord)
    result = match_record.is_match()
    assert result.bool
    score = match_record.score()
    assert isinstance(score, int)
    assert score == 8
