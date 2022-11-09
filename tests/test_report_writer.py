"""
Module test_report_writer.py, which performs automated
testing of the REDCapReportWriter class.
"""

import os
import pytest
from redcapmatchresolver import REDCapReportWriter


@pytest.fixture(name="addendum")
def figure_addendum():
    """Defines the additional text report_writer tacks onto each match."""
    return """CRC Review: Patients are\n    ☐ Same\n    ☐ NOT Same\n"""


@pytest.fixture(name="matching_patients")
def fixture_matching_patients():
    """Defines an example of patient match text."""
    return """
    ---------------
    Common Name         Epic Val               RedCap Val           Score
    C_FIRST             John                   Jon                   0.8
    C_LAST              Smith                  Smythe                0.9
    C_DOB               2022-11-01             Nov 1, 2022           1.0
    C_EMAIL             jsmith@yahoo.com       j.smith@gmail.com     1.0
    C_ADDR_CALCULATED   1313 Mockingbird Lane  1313 Mockingbird Ln   1.0
    C_PHONE_CALCULATED  800-555-1212           800-555-1212          1.0
    ---------------
    """


def test_writer_init(tmp_path) -> None:
    """Tests initializing the Report Writer class."""
    # Default report name.
    obj = REDCapReportWriter()
    assert obj is not None
    assert isinstance(obj, REDCapReportWriter)

    # Reasonable report name.
    tmp_filename = tmp_path / "test_filename.txt"
    obj = REDCapReportWriter(report_filename=tmp_filename)
    assert obj is not None
    assert isinstance(obj, REDCapReportWriter)

    # Unrealizable report name.
    with pytest.raises(OSError) as e_info:
        bad_filename = tmp_path / "name that can't be </parsed.txt"
        REDCapReportWriter(report_filename=bad_filename)


def test_writing(addendum, matching_patients, tmp_path) -> None:
    """End-to-end test of writing a report."""
    output_filename = tmp_path / "test_filename.txt"
    writer_obj = REDCapReportWriter(report_filename=output_filename)
    assert writer_obj is not None
    assert isinstance(writer_obj, REDCapReportWriter)

    assert writer_obj.add_match(matching_patients)
    writer_obj.close()

    # Check that the output file was created.
    assert os.path.exists(output_filename)

    # Check its contents.
    with open(file=output_filename, encoding="utf-8") as file_obj:
        retrieved_contents = file_obj.read()
        assert retrieved_contents == matching_patients + addendum


if __name__ == "__main__":
    pass
