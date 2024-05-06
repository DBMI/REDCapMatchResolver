"""
Module test_match.py, which performs automated
testing of the classes:
    CommonField
    MatchRecord
    MatchTuple
    MatchVariable
"""
from src.redcapmatchresolver.match_quality import MatchQuality
from src.redcapmatchresolver.match_records import (
    CommonField,
    MatchRecord,
    MatchTuple,
    MatchVariable,
)
import pytest


def test_common_field() -> None:
    common_field_obj = CommonField(
        common_name="C_FIRST", epic_field="PAT_FIRST_NAME", redcap_field="first_name"
    )
    assert isinstance(common_field_obj, CommonField)
    assert common_field_obj.common_name() == "C_FIRST"
    assert common_field_obj.epic_field() == "PAT_FIRST_NAME"
    assert common_field_obj.epic_field_present(field_name="PAT_FIRST_NAME")
    assert not common_field_obj.epic_field_present(field_name="Not here")
    assert common_field_obj.redcap_field() == "first_name"
    assert common_field_obj.redcap_field_present(field_name="first_name")
    assert not common_field_obj.redcap_field_present(field_name="Not here")


def test_common_field_error() -> None:
    with pytest.raises(TypeError):
        CommonField(
            common_name=None, epic_field="PAT_FIRST_NAME", redcap_field="first_name"
        )

    with pytest.raises(TypeError):
        CommonField(
            common_name=1979, epic_field="PAT_FIRST_NAME", redcap_field="first_name"
        )

    with pytest.raises(TypeError):
        CommonField(common_name="C_FIRST", epic_field=None, redcap_field="first_name")

    with pytest.raises(TypeError):
        CommonField(common_name="C_FIRST", epic_field=1979, redcap_field="first_name")

    with pytest.raises(TypeError):
        CommonField(
            common_name="C_FIRST", epic_field="PAT_FIRST_NAME", redcap_field=None
        )

    with pytest.raises(TypeError):
        CommonField(
            common_name="C_FIRST", epic_field="PAT_FIRST_NAME", redcap_field=1979
        )

    common_field_obj = CommonField(
        common_name="C_FIRST", epic_field="PAT_FIRST_NAME", redcap_field="first_name"
    )
    assert isinstance(common_field_obj, CommonField)

    with pytest.raises(TypeError):
        common_field_obj.epic_field_present(field_name=1979)

    with pytest.raises(TypeError):
        common_field_obj.redcap_field_present(field_name=1979)


def test_match_record(fake_records_dataframe) -> None:
    match_record = MatchRecord(
        fake_records_dataframe.iloc[0], facility_addresses=[], facility_phone_numbers=[]
    )
    assert isinstance(match_record, MatchRecord)
    result = match_record.is_match()
    assert isinstance(result, MatchTuple)
    assert hasattr(result, "bool")
    assert result.bool
    assert hasattr(result, "summary")
    assert isinstance(result.summary, str)
    score = match_record.score()
    assert isinstance(score, int)
    assert score == 6
    pat_id = match_record.pat_id()
    assert isinstance(pat_id, str)
    assert pat_id == fake_records_dataframe.iloc[0]["PAT_ID"]
    study_id = match_record.study_id()
    assert isinstance(study_id, int)
    assert study_id == int(fake_records_dataframe.iloc[0]["study_id"])


def test_match_record_bonus(fake_records_using_bonus_dataframe) -> None:
    match_record = MatchRecord(
        fake_records_using_bonus_dataframe.iloc[0],
        facility_addresses=[],
        facility_phone_numbers=[],
    )
    assert isinstance(match_record, MatchRecord)
    result = match_record.is_match(criteria=4)
    assert isinstance(result, MatchTuple)
    assert hasattr(result, "bool")
    assert result.bool
    assert hasattr(result, "summary")
    assert isinstance(result.summary, str)
    score = match_record.score()
    assert isinstance(score, int)
    assert score == 4


def test_match_record_use_alias(fake_records_dataframe) -> None:
    row = fake_records_dataframe.iloc[0].copy()

    #   Change the REDCap name so that it doesn't match Epic, but include that REDCap name as an alias.
    #   The name in Epic:
    row["PAT_FIRST_NAME"] = "Alice"
    row["PAT_LAST_NAME"] = "Smith"

    #   The name in REDCap:
    row["first_name"] = "Alan"
    row["last_name"] = "Smyth"
    row["ALIAS"] = "Smyth,Alan B;Smith,Alice C"
    match_record = MatchRecord(row, facility_addresses=[], facility_phone_numbers=[])
    assert isinstance(match_record, MatchRecord)
    score = match_record.score()
    assert isinstance(score, int)
    assert score == 6
    result = match_record.is_match(criteria=5)
    assert isinstance(result, MatchTuple)
    assert hasattr(result, "bool")
    assert result.bool
    assert hasattr(result, "summary")
    assert isinstance(result.summary, str)


def test_match_record_use_mrn_hx(fake_records_dataframe) -> None:
    row = fake_records_dataframe.iloc[0].copy()

    #   Change the REDCap MRN so that it doesn't match Epic, but include that REDCap MRN as a historical MRN.
    #   The MRN in Epic:
    row["MRN"] = "A12345"

    #   The MRN in REDCap:
    row["mrn"] = "B23456"
    row["MRN_HX"] = "B23456"
    match_record = MatchRecord(row, facility_addresses=[], facility_phone_numbers=[])
    assert isinstance(match_record, MatchRecord)
    score = match_record.score()
    assert isinstance(score, int)
    assert score == 6
    result = match_record.is_match(criteria=5)
    assert isinstance(result, MatchTuple)
    assert hasattr(result, "bool")
    assert result.bool


def test_match_record_corner_cases(fake_records_dataframe) -> None:
    #   Delete the Epic HOME_PHONE field to force use of WORK_PHONE.
    row = fake_records_dataframe.iloc[0].copy()
    row["HOME_PHONE"] = ""
    match_record = MatchRecord(row, facility_addresses=[], facility_phone_numbers=[])
    assert isinstance(match_record, MatchRecord)

    result = match_record.is_match()
    assert isinstance(result, MatchTuple)
    assert hasattr(result, "bool")
    assert result.bool
    assert hasattr(result, "summary")
    assert isinstance(result.summary, str)

    #   Using 'exact' parameter, with and without exact match.
    match_record = MatchRecord(
        row=fake_records_dataframe.iloc[0],
        facility_addresses=[],
        facility_phone_numbers=[],
    )
    assert isinstance(match_record, MatchRecord)

    result = match_record.is_match(exact=True, criteria=6)
    assert isinstance(result, MatchTuple)
    assert hasattr(result, "bool")
    assert result.bool

    result = match_record.is_match(exact=True, criteria=5)
    assert isinstance(result, MatchTuple)
    assert hasattr(result, "bool")
    assert not result.bool


def test_match_record_errors(fake_records_dataframe) -> None:
    with pytest.raises(TypeError):
        MatchRecord(row=None, facility_addresses=[], facility_phone_numbers=[])

    with pytest.raises(TypeError):
        MatchRecord(row=1979, facility_addresses=[], facility_phone_numbers=[])


def test_match_record_ignore_list(same_facility_dataframe) -> None:
    row = same_facility_dataframe.iloc[0].copy()

    #   Create two records with same address, phone number and first name, but everything else different.
    match_record = MatchRecord(row, facility_addresses=[], facility_phone_numbers=[])
    assert isinstance(match_record, MatchRecord)
    score = match_record.score()
    assert isinstance(score, int)
    assert score == 2

    #   Now add this address to ignore_list.
    facility_addresses = [row["E_ADDR_CALCULATED"]]
    match_record = MatchRecord(
        row, facility_addresses=facility_addresses, facility_phone_numbers=[]
    )
    assert isinstance(match_record, MatchRecord)
    result = match_record.is_match(criteria=3)
    assert isinstance(result, MatchTuple)
    assert hasattr(result, "bool")
    assert not result.bool
    assert hasattr(result, "summary")
    assert isinstance(result.summary, str)
    score = match_record.score()
    assert isinstance(score, int)
    assert score == 1

    #   Now add this phone number to ignore_list but leave address BLANK.
    facility_phone_numbers = [row["phone_number"]]
    match_record = MatchRecord(
        row, facility_addresses=[], facility_phone_numbers=facility_phone_numbers
    )
    assert isinstance(match_record, MatchRecord)
    score = match_record.score()
    assert isinstance(score, int)
    assert score == 1


def test_match_variable() -> None:
    match_variable_obj = MatchVariable(epic_value="Alice", redcap_value="Alice")
    assert isinstance(match_variable_obj, MatchVariable)
    assert match_variable_obj.epic_value() == "Alice"
    assert match_variable_obj.redcap_value() == "Alice"
    result = match_variable_obj.match_quality()
    assert isinstance(result, MatchQuality)
    assert result == MatchQuality.MATCHED_EXACT

    match_variable_obj = MatchVariable(epic_value="Alice", redcap_value="AliceBob")
    assert isinstance(match_variable_obj, MatchVariable)
    assert match_variable_obj.match_quality() == MatchQuality.MATCHED_SUBSTRING

    #   Exercise NULL match.
    match_variable_obj = MatchVariable(epic_value="", redcap_value="")
    assert isinstance(match_variable_obj, MatchVariable)
    assert match_variable_obj.match_quality() == MatchQuality.MATCHED_NULL

    #   Exercise ignore list; first, values match WITHOUT ignore list.
    match_variable_obj = MatchVariable(
        epic_value="123 Maple St | 00000", redcap_value="123 Maple St | 00000"
    )
    assert isinstance(match_variable_obj, MatchVariable)
    assert match_variable_obj.match_quality() == MatchQuality.MATCHED_EXACT

    #   Now with ignore list provided.
    match_variable_obj = MatchVariable(
        epic_value="123 Maple St | 00000",
        redcap_value="123 Maple St | 00000",
        ignore_list=["234 Maple St | 00000", "123 Maple St | 00000"],
    )
    assert isinstance(match_variable_obj, MatchVariable)
    assert match_variable_obj.match_quality() == MatchQuality.IGNORED


def test_match_variable_error() -> None:
    with pytest.raises(TypeError):
        MatchVariable(epic_value=None, redcap_value="Alice")

    with pytest.raises(TypeError):
        MatchVariable(epic_value=1979, redcap_value="Alice")

    with pytest.raises(TypeError):
        MatchVariable(epic_value="Alice", redcap_value=None)

    with pytest.raises(TypeError):
        MatchVariable(epic_value="Alice", redcap_value=1979)


if __name__ == "__main__":
    pass
