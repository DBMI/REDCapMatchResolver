"""
Module test_report_reader.py, which performs automated
testing of the REDCapReportReader class.
"""

import os
import pandas
import pytest
from redcapmatchresolver.redcap_report_reader import CrcReason, CrcReview, REDCapReportReader


@pytest.fixture(name="report_filename")
def fixture_report_filename():
    """Temporary report filename"""
    return os.path.join(
        os.path.dirname(os.path.realpath(__file__)), "test_patient_report.txt"
    )


def test_crc_reason_class() -> None:
    """Exercise CrcReason enum class."""
    with pytest.raises(TypeError):
        CrcReason.convert()

    with pytest.raises(TypeError):
        CrcReason.convert(None)

    with pytest.raises(TypeError):
        CrcReason.convert(1979)

    assert CrcReason.convert("NOT Same: Family members") == CrcReason.FAMILY
    assert CrcReason.convert("NOT Same: Living at same address") == CrcReason.SAME_ADDRESS
    assert CrcReason.convert("NOT Same: Parent & child") == CrcReason.PARENT_CHILD
    assert CrcReason.convert("") == CrcReason.OTHER


def test_crc_review_class() -> None:
    """Exercise CrcReview enum class."""
    with pytest.raises(TypeError):
        CrcReview.convert()

    with pytest.raises(TypeError):
        CrcReview.convert(None)

    with pytest.raises(TypeError):
        CrcReview.convert(1979)

    assert CrcReview.convert("MATCH") == CrcReview.MATCH
    assert CrcReview.convert("NO_MATCH") == CrcReview.NO_MATCH
    assert CrcReview.convert("NOT_SURE") == CrcReview.NOT_SURE
    assert CrcReview.convert("") == CrcReview.NOT_SURE

    assert CrcReview.MATCH == CrcReview.MATCH
    assert CrcReview.MATCH > CrcReview.NO_MATCH
    assert CrcReview.MATCH > CrcReview.NOT_SURE
    assert CrcReview.NO_MATCH > CrcReview.NOT_SURE
    assert CrcReview.NOT_SURE < CrcReview.NO_MATCH

    assert not CrcReview.MATCH == "Something"
    assert not CrcReview.MATCH > None
    assert not None > CrcReview.MATCH
    assert not CrcReview.MATCH > 1979
    assert not 1979 > CrcReview.MATCH
    assert not CrcReview.MATCH > "Something"


def test_reading_file(report_filename, my_location) -> None:
    """Test reading match report FILE."""
    obj = REDCapReportReader()
    assert obj is not None
    assert isinstance(obj, REDCapReportReader)

    test_df = obj.read_file(report_filename=report_filename)
    assert test_df is not None
    assert isinstance(test_df, pandas.DataFrame)

    partial_report_filename = os.path.join(
        my_location, "bogus_patient_report_CRC_partial.txt"
    )
    test_df = obj.read_file(report_filename=partial_report_filename)
    assert test_df is not None
    assert isinstance(test_df, pandas.DataFrame)

    partial_report_filename = os.path.join(
        my_location, "bogus_patient_report_CRC_partial_II.txt"
    )
    test_df = obj.read_file(report_filename=partial_report_filename)
    assert test_df is not None
    assert isinstance(test_df, pandas.DataFrame)

    missing_values_filename = os.path.join(
        my_location, "bogus_patient_report_missing_values.txt"
    )
    test_df = obj.read_file(report_filename=missing_values_filename)
    assert test_df is not None
    assert isinstance(test_df, pandas.DataFrame)


def test_reading_text(matching_patients) -> None:
    """Test reading match report TEXT block."""
    obj = REDCapReportReader()
    assert obj is not None
    assert isinstance(obj, REDCapReportReader)

    test_df = obj.read_text(block_txt=matching_patients)
    assert test_df is not None
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
