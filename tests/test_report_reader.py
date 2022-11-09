"""
Module test_report_reader.py, which performs automated
testing of the REDCapReportReader class.
"""

import pandas
import pytest
from redcapmatchresolver import REDCapReportReader


@pytest.fixture(name="report_filename")
def figure_report_filename():
    return "test_patient_report.txt"


def test_reader(report_filename) -> None:
    # Default report name.
    obj = REDCapReportReader(report_filename=report_filename)
    assert obj is not None
    assert isinstance(obj, REDCapReportReader)

    test_df = obj.read()
    assert test_df is not None
    assert isinstance(test_df, pandas.DataFrame)


if __name__ == "__main__":
    pass
