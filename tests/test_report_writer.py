"""
Module test_report_writer.py, which performs automated
testing of the REDCapReportWriter class.
"""

import os
from redcapmatchresolver import REDCapReportWriter
from redcaputilities.logging import patient_data_directory


def test_writer_init(tmp_path) -> None:
    """Tests initializing the Report Writer class."""
    # Default report name.
    obj = REDCapReportWriter()
    assert obj is not None
    assert isinstance(obj, REDCapReportWriter)

    # Report name in UNsafe drive.
    tmp_filename = str(tmp_path / "test_filename.txt")
    obj = REDCapReportWriter(report_filename=tmp_filename)
    assert obj is not None
    assert isinstance(obj, REDCapReportWriter)
    # Ensure report is sent to safe drive.
    assert patient_data_directory() in obj.report_filename()

    # Report name in safe drive.
    safe_report_filename = os.path.join(patient_data_directory(), "test_filename.txt")
    obj = REDCapReportWriter(report_filename=safe_report_filename)
    assert obj is not None
    assert isinstance(obj, REDCapReportWriter)
    assert obj.report_filename() == safe_report_filename


def test_writing(matching_patients, tmp_path) -> None:
    """End-to-end test of writing a report."""
    output_filename = str(tmp_path / "test_filename.txt")
    writer_obj = REDCapReportWriter(report_filename=output_filename)
    assert writer_obj is not None
    assert isinstance(writer_obj, REDCapReportWriter)

    writer_obj.add_match(matching_patients)

    assert writer_obj.write()

    # Check that the output file was created.
    assert os.path.exists(writer_obj.report_filename())

    # Check its contents.
    with open(file=writer_obj.report_filename(), encoding="utf-8") as file_obj:
        retrieved_contents = file_obj.read()
        record_read_line = "Record 1 of 1\n"
        assert (
            retrieved_contents
            == matching_patients + record_read_line + REDCapReportWriter.addendum
        )


if __name__ == "__main__":
    pass
