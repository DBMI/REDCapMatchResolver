"""
Module test_match.py, which performs automated
testing of the classes:
    CommonField
    MatchRecord
    MatchVariable
"""
from redcapduplicatedetector.match_quality import MatchQuality
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
    match_record = MatchRecord(fake_records_dataframe.iloc[0])
    assert isinstance(match_record, MatchRecord)
    result = match_record.is_match()
    assert isinstance(result, MatchTuple)
    assert hasattr(result, "bool")
    assert result.bool
    assert hasattr(result, "summary")
    assert isinstance(result.summary, str)
    score = match_record.score()
    assert isinstance(score, int)
    assert score == 7


def test_match_record_errors(fake_records_dataframe) -> None:
    with pytest.raises(TypeError):
        MatchRecord(row=None)

    with pytest.raises(TypeError):
        MatchRecord(row=1979)


def test_match_record_corner_cases(fake_records_dataframe) -> None:
    #   Delete the Epic HOME_PHONE field to force use of WORK_PHONE.
    row = fake_records_dataframe.iloc[0]
    row["HOME_PHONE"] = ""
    match_record = MatchRecord(row)
    assert isinstance(match_record, MatchRecord)

    result = match_record.is_match()
    assert isinstance(result, MatchTuple)
    assert hasattr(result, "bool")
    assert result.bool
    assert hasattr(result, "summary")
    assert isinstance(result.summary, str)

    #   Using 'exact' parameter, with and without exact match.
    match_record = MatchRecord(row=fake_records_dataframe.iloc[0])
    assert isinstance(match_record, MatchRecord)

    result = match_record.is_match(exact=True, criteria=7)
    assert isinstance(result, MatchTuple)
    assert hasattr(result, "bool")
    assert result.bool

    result = match_record.is_match(exact=True, criteria=5)
    assert isinstance(result, MatchTuple)
    assert hasattr(result, "bool")
    assert not result.bool


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
