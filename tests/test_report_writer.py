"""
Module test_report_writer.py, which performs automated
testing of the REDCapReportWriter class.
"""
import os
from redcapmatchresolver.redcap_report_writer import REDCapReportWriter
from redcaputilities.logging import patient_data_directory


def test_writing(matching_patients) -> None:
    """End-to-end test of writing a report."""
    output_filename = os.path.join(patient_data_directory(), "test_filename.txt")

    #   Get rid of old copies.
    try:
        os.remove(output_filename)
    except OSError:
        pass

    writer_obj = REDCapReportWriter()
    assert isinstance(writer_obj, REDCapReportWriter)

    writer_obj.add_match(matching_patients)
    assert writer_obj.num_reports() == 1
    package = writer_obj.write(report_filename=output_filename)
    assert isinstance(package, tuple)
    assert len(package) == 2
    assert package[0]  # Success
    assert isinstance(package[1], str)
    assert package[1] == output_filename  # Check that file created where we expected.

    # Check that the output file was created.
    assert os.path.exists(output_filename)

    # Check its contents.
    with open(file=output_filename, encoding="utf-8") as file_obj:
        retrieved_contents = file_obj.read()
        record_read_line = "Record 1 of 1\n"
        assert (
            retrieved_contents
            == matching_patients + record_read_line + REDCapReportWriter.addendum
        )


def test_writing_safe_directory(matching_patients, tmp_path) -> None:
    writer_obj = REDCapReportWriter()
    assert isinstance(writer_obj, REDCapReportWriter)

    writer_obj.add_match(matching_patients)
    assert writer_obj.num_reports() == 1

    # Try to direct report to an UNSAFE drive.
    unsafe_report_filename = str(tmp_path / "test_filename.txt")
    package = writer_obj.write(report_filename=unsafe_report_filename)
    assert isinstance(package, tuple)
    assert package[0]  # Success
    assert isinstance(package[1], str)

    # Check that the output file was NOT created.
    assert not os.path.exists(unsafe_report_filename)

    #   This is where report SHOULD have been created.
    assert os.path.exists(package[1])

    #   And ensure file created in proper safe directory.
    assert patient_data_directory() in package[1]

    # Check its contents.
    with open(file=package[1], encoding="utf-8") as file_obj:
        retrieved_contents = file_obj.read()
        record_read_line = "Record 1 of 1\n"
        assert (
            retrieved_contents
            == matching_patients + record_read_line + REDCapReportWriter.addendum
        )


if __name__ == "__main__":
    pass
