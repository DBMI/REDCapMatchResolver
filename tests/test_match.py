"""
Module test_match.py, which performs automated
testing of the classes:
    CommonField
    MatchRecord
    MatchTuple
    MatchVariable
"""
from redcapduplicatedetector.match_quality import MatchQuality

import redcap_update
from src.redcapmatchresolver.match_records import (
    CommonField,
    MatchRecord,
    MatchTuple,
    MatchVariable,
)
from src.redcapmatchresolver.redcap_update import REDCapUpdate
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
    pat_id = match_record.pat_id()
    assert isinstance(pat_id, str)
    assert pat_id == fake_records_dataframe.iloc[0]["PAT_ID"]


def test_match_record_alias(fake_records_dataframe) -> None:
    match_record = MatchRecord(fake_records_dataframe.iloc[0])
    assert isinstance(match_record, MatchRecord)
    result = match_record.is_match(aliases=["Smith,Alice", "Smyth,Alan"])
    assert isinstance(result, MatchTuple)
    assert hasattr(result, "bool")
    assert result.bool
    assert hasattr(result, "summary")
    assert isinstance(result.summary, str)


def test_match_record_corner_cases(fake_records_dataframe) -> None:
    #   Delete the Epic HOME_PHONE field to force use of WORK_PHONE.
    row = fake_records_dataframe.iloc[0].copy()
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


def test_match_record_errors(fake_records_dataframe) -> None:
    with pytest.raises(TypeError):
        MatchRecord(row=None)

    with pytest.raises(TypeError):
        MatchRecord(row=1979)


def test_match_record_mrn_match(fake_records_dataframe) -> None:
    row = fake_records_dataframe.iloc[0].copy()
    match_record = MatchRecord(row)
    assert isinstance(match_record, MatchRecord)

    mrns_match = match_record.mrns_match()
    assert isinstance(mrns_match, bool)
    assert mrns_match

    # Force MRNs not to match.
    row["MRN"] = row["mrn"] + 1
    match_record = MatchRecord(row)
    assert isinstance(match_record, MatchRecord)
    mrns_match = match_record.mrns_match()
    assert isinstance(mrns_match, bool)
    assert not mrns_match


def test_match_record_revision(fake_records_dataframe) -> None:
    row = fake_records_dataframe.iloc[0].copy()

    # Manipulate so names DON'T match, but alias will.
    #   The name in Epic:
    row["PAT_FIRST_NAME"] = "Alice"
    row["PAT_LAST_NAME"] = "Smith"

    #   The name in REDCap:
    row["first_name"] = "Alan"
    row["last_name"] = "Smyth"
    match_record = MatchRecord(row)
    assert isinstance(match_record, MatchRecord)

    names_match = match_record.names_match()
    assert isinstance(names_match, bool)
    assert not names_match

    score = match_record.score()
    assert isinstance(score, int)
    assert score == 5

    #   Revise with alias.
    match_record.use_aliases(["Smith,Alice", "Smyth,Alan"])

    #   The names still won't match, because even though
    #   we recognize that the REDCap name is one of the Epic aliases,
    #   the names haven't been changed....
    names_match = match_record.names_match()
    assert isinstance(names_match, bool)
    assert not names_match

    #   ...but the score improves.
    score = match_record.score()
    assert isinstance(score, int)
    assert score == 7

    #   Retrieve the update package from MatchRecord object.
    update_obj = match_record.redcap_update()
    assert isinstance(update_obj, redcap_update.REDCapUpdate)
    assert update_obj.needed()


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
