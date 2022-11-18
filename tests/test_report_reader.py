"""
Module test_report_reader.py, which performs automated
testing of the REDCapReportReader class.
"""

import os
import pandas
import pytest
from redcapmatchresolver.redcap_report_reader import REDCapReportReader


@pytest.fixture(name="report_filename")
def report_filename():
    return os.path.join(
        os.path.dirname(os.path.realpath(__file__)), "test_patient_report.txt"
    )


def test_reading_file(report_filename) -> None:
    obj = REDCapReportReader()
    assert obj is not None
    assert isinstance(obj, REDCapReportReader)

    test_df = obj.read_file(report_filename=report_filename)
    assert test_df is not None
    assert isinstance(test_df, pandas.DataFrame)


def test_reading_text(matching_patients) -> None:
    obj = REDCapReportReader()
    assert obj is not None
    assert isinstance(obj, REDCapReportReader)

    test_df = obj.read_text(block_txt=matching_patients)
    assert test_df is not None
    assert isinstance(test_df, pandas.DataFrame)


def test_reader_errors() -> None:
    my_location = os.path.dirname(os.path.realpath(__file__))
    obj = REDCapReportReader()

    #   Supply bad report name.
    with pytest.raises(TypeError):
        obj.read_file(report_filename=None)

    #   Intentionally use improper type as input.
    with pytest.raises(TypeError):
        obj.read_file(report_filename=1979)

    with pytest.raises(FileNotFoundError):
        obj.read_file(report_filename="C:/unobtanium/report.txt")

    with pytest.raises(RuntimeError):
        bad_filename = os.path.join(
            my_location, "bogus_patient_report_partial_header.txt"
        )
        obj.read_file(report_filename=bad_filename)

    with pytest.raises(RuntimeError):
        bad_filename = os.path.join(my_location, "bogus_patient_report_CRC_partial.txt")
        obj.read_file(report_filename=bad_filename)

    bad_filename = os.path.join(my_location, "bogus_patient_report_missing_fields.txt")
    assert obj.read_file(report_filename=bad_filename) is None

    bad_filename = os.path.join(
        my_location, "bogus_patient_report_ends_before_data.txt"
    )
    assert obj.read_file(report_filename=bad_filename) is None

    bad_filename = os.path.join(my_location, "bogus_patient_report_ends_too_soon.txt")
    assert obj.read_file(report_filename=bad_filename) is None

    bad_filename = os.path.join(my_location, "bogus_patient_report_CRC_partial_II.txt")
    assert obj.read_file(report_filename=bad_filename) is None


if __name__ == "__main__":
    pass
