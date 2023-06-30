"""
Module test_report_reader.py, which performs automated
testing of the REDCapReportReader class.
"""

import os

import pandas
import pytest

from redcapmatchresolver.redcap_report_reader import (
    DecisionReason,
    DecisionReview,
    REDCapReportReader,
)


def test_crc_reason_class() -> None:
    """Exercise CrcReason enum class."""
    with pytest.raises(TypeError):
        DecisionReason.convert()

    assert DecisionReason.convert(None) == DecisionReason.OTHER

    assert DecisionReason.convert(1979) == DecisionReason.OTHER

    assert DecisionReason.convert("NOT Same: Relatives") == DecisionReason.RELATIVES
    assert (
        DecisionReason.convert("NOT Same: Living at same address")
        == DecisionReason.SAME_ADDRESS
    )
    assert (
        DecisionReason.convert("NOT Same: Parent & child")
        == DecisionReason.PARENT_CHILD
    )

    assert DecisionReason.convert("") == DecisionReason.OTHER


def test_crc_review_class() -> None:
    """Exercise CrcReview enum class."""
    with pytest.raises(TypeError):
        DecisionReview.convert()

    with pytest.raises(TypeError):
        DecisionReview.convert(None)

    with pytest.raises(TypeError):
        DecisionReview.convert(1979)

    assert DecisionReview.convert("MATCH") == DecisionReview.MATCH
    assert DecisionReview.convert("NO_MATCH") == DecisionReview.NO_MATCH
    assert DecisionReview.convert("NOT_SURE") == DecisionReview.NOT_SURE
    assert DecisionReview.convert("") == DecisionReview.NOT_SURE

    #   Exercise list processing.
    converted_list = DecisionReview.convert(["MATCH", "NO_MATCH"])
    assert converted_list == [DecisionReview.MATCH, DecisionReview.NO_MATCH]
    assert DecisionReview.MATCH == DecisionReview.MATCH
    assert DecisionReview.MATCH > DecisionReview.NO_MATCH
    assert DecisionReview.MATCH > DecisionReview.NOT_SURE
    assert DecisionReview.NO_MATCH > DecisionReview.NOT_SURE
    assert DecisionReview.NOT_SURE < DecisionReview.NO_MATCH

    assert DecisionReview.MATCH != "Something"

    with pytest.raises(TypeError):
        DecisionReview.MATCH > None

    with pytest.raises(TypeError):
        None > DecisionReview.MATCH

    with pytest.raises(TypeError):
        DecisionReview.MATCH > 1979

    with pytest.raises(TypeError):
        1979 > DecisionReview.MATCH

    with pytest.raises(TypeError):
        DecisionReview.MATCH > "Something"


def test_reading_file(
    report_filename_address,
    report_filename_blank,
    report_filename_parent_child,
    report_filename_relatives,
    report_filename_same,
    my_location,
) -> None:
    """Test reading match report FILE."""
    obj = REDCapReportReader()
    assert isinstance(obj, REDCapReportReader)

    test_df = obj.read_file(report_filename=report_filename_blank)
    assert isinstance(test_df, pandas.DataFrame)
    assert "DECISION" in test_df
    assert test_df.iloc[0]["DECISION"] == "DecisionReview.NOT_SURE"

    test_df = obj.read_file(report_filename=report_filename_address)
    assert isinstance(test_df, pandas.DataFrame)
    assert "DECISION" in test_df
    assert test_df.iloc[0]["DECISION"] == "DecisionReview.NO_MATCH"

    test_df = obj.read_file(report_filename=report_filename_parent_child)
    assert isinstance(test_df, pandas.DataFrame)
    assert "DECISION" in test_df
    assert test_df.iloc[0]["DECISION"] == "DecisionReview.NO_MATCH"

    test_df = obj.read_file(report_filename=report_filename_relatives)
    assert isinstance(test_df, pandas.DataFrame)
    assert "DECISION" in test_df
    assert test_df.iloc[0]["DECISION"] == "DecisionReview.NO_MATCH"

    test_df = obj.read_file(report_filename=report_filename_same)
    assert isinstance(test_df, pandas.DataFrame)
    assert "DECISION" in test_df
    assert test_df.iloc[0]["DECISION"] == "DecisionReview.MATCH"

    partial_report_filename = os.path.join(
        my_location, "bogus_patient_report_CRC_partial.txt"
    )
    test_df = obj.read_file(report_filename=partial_report_filename)
    assert isinstance(test_df, pandas.DataFrame)

    partial_report_filename = os.path.join(
        my_location, "bogus_patient_report_CRC_partial_II.txt"
    )
    test_df = obj.read_file(report_filename=partial_report_filename)
    assert isinstance(test_df, pandas.DataFrame)

    missing_values_filename = os.path.join(
        my_location, "bogus_patient_report_missing_values.txt"
    )
    test_df = obj.read_file(report_filename=missing_values_filename)
    assert isinstance(test_df, pandas.DataFrame)


def test_reading_text(matching_patients) -> None:
    """Test reading match report TEXT block."""
    obj = REDCapReportReader()
    assert isinstance(obj, REDCapReportReader)

    test_df = obj.read_text(block_txt=matching_patients)
    assert isinstance(test_df, pandas.DataFrame)


def test_reader_errors(my_location) -> None:
    """Test reading under conditions we expect to cause errors."""

    obj = REDCapReportReader()

    #   Supply bad report name.
    with pytest.raises(TypeError):
        obj.read_file(report_filename=None)

    #   Intentionally use improper type as input.
    with pytest.raises(TypeError):
        obj.read_file(report_filename=1979)

    with pytest.raises(TypeError):
        obj.read_text(None)

    with pytest.raises(FileNotFoundError):
        obj.read_file(report_filename="C:/unobtanium/report.txt")

    with pytest.raises(RuntimeError):
        bad_filename = os.path.join(
            my_location, "bogus_patient_report_partial_header.txt"
        )
        obj.read_file(report_filename=bad_filename)

    bad_filename = os.path.join(
        my_location, "bogus_patient_report_ends_before_data.txt"
    )
    assert obj.read_file(report_filename=bad_filename) is None

    bad_filename = os.path.join(my_location, "bogus_patient_report_ends_too_soon.txt")
    assert obj.read_file(report_filename=bad_filename) is None


def test_static_methods() -> None:
    """Exercise the public static methods of the REDCapReportReader class."""
    assert REDCapReportReader.convert_nulls(None) is None
    assert REDCapReportReader.convert_nulls(1979) is None


if __name__ == "__main__":
    pass
