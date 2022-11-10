"""
Module test_report_reader.py, which performs automated
testing of the REDCapReportReader class.
"""

import os
import pandas
import pytest
from redcapmatchresolver.redcap_report_reader import REDCapReportReader


@pytest.fixture(name="report_filename")
def figure_report_filename():
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), "test_patient_report.txt")


def test_reader(report_filename) -> None:
    # Default report name.
    obj = REDCapReportReader()
    assert obj is not None
    assert isinstance(obj, REDCapReportReader)

    test_df = obj.read(report_filename=report_filename)
    assert test_df is not None
    assert isinstance(test_df, pandas.DataFrame)


def test_reader_errors() -> None:
    my_location = os.path.dirname(os.path.realpath(__file__))
    obj = REDCapReportReader()

    # Supply bad report name.
    with pytest.raises(TypeError):
        obj.read(report_filename=None)

    with pytest.raises(TypeError):
        obj.read(report_filename=1979)

    with pytest.raises(FileNotFoundError):
        obj.read(report_filename="C:/unobtanium/report.txt")

    with pytest.raises(RuntimeError):
        bad_filename = os.path.join(my_location, "bogus_patient_report_partial_header.txt")
        obj = obj.read(report_filename=bad_filename)
        obj.read()

    bad_filename = os.path.join(my_location, "bogus_patient_report_ends_before_data.txt")
    obj.read(report_filename=bad_filename)

    bad_filename = os.path.join(my_location, "bogus_patient_report_ends_too_soon.txt")
    obj.read(report_filename=bad_filename)

    bad_filename = os.path.join(my_location, "bogus_patient_report_CRC_partial.txt")
    obj.read(report_filename=bad_filename)

    bad_filename = os.path.join(my_location, "bogus_patient_report_CRC_partial_II.txt")
    obj.read(report_filename=bad_filename)


if __name__ == "__main__":
    pass
