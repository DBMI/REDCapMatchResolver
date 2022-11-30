"""
Module test_report_writer.py, which performs automated
testing of the REDCapReportWriter class.
"""

import os
import pytest
from redcapmatchresolver import REDCapReportWriter


def test_writer_init(tmp_path) -> None:
    """Tests initializing the Report Writer class."""
    # Default report name.
    obj = REDCapReportWriter()
    assert obj is not None
    assert isinstance(obj, REDCapReportWriter)

    # Reasonable report name.
    tmp_filename = str(tmp_path / "test_filename.txt")
    obj = REDCapReportWriter(report_filename=tmp_filename)
    assert obj is not None
    assert isinstance(obj, REDCapReportWriter)
    assert obj.report_filename() == tmp_filename

    # Unrealizable report name.
    with pytest.raises(OSError):
        bad_filename = str(tmp_path / "name that can't be </parsed.txt")
        REDCapReportWriter(report_filename=bad_filename)


def test_writing(matching_patients, tmp_path) -> None:
    """End-to-end test of writing a report."""
    output_filename = str(tmp_path / "test_filename.txt")
    writer_obj = REDCapReportWriter(report_filename=output_filename)
    assert writer_obj is not None
    assert isinstance(writer_obj, REDCapReportWriter)

    writer_obj.add_match(matching_patients)

    assert writer_obj.write()

    # Check that the output file was created.
    assert os.path.exists(output_filename)

    # Check its contents.
    with open(file=output_filename, encoding="utf-8") as file_obj:
        retrieved_contents = file_obj.read()
        record_read_line = "Record 0 of 1\n"
        assert retrieved_contents == matching_patients + record_read_line + REDCapReportWriter.addendum


if __name__ == "__main__":
    pass
