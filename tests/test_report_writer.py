"""
Module test_report_writer.py, which performs automated
testing of the REDCapMatchResolver class.
"""

import os
import pytest
from redcapmatchresolver import REDCapMatchResolver


@pytest.fixture(name="addendum")
def fixture_addendum():
    """Defines the additional text report_writer tacks onto each match."""
    return """CRC Review: Patients are\n    ☐ Same\n    ☐ NOT Same\n"""


def test_writer_init(tmp_path) -> None:
    """Tests initializing the Report Writer class."""
    # Default report name.
    obj = REDCapMatchResolver()
    assert obj is not None
    assert isinstance(obj, REDCapMatchResolver)

    # Reasonable report name.
    tmp_filename = str(tmp_path / "test_filename.txt")
    obj = REDCapMatchResolver(report_filename=tmp_filename)
    assert obj is not None
    assert isinstance(obj, REDCapMatchResolver)

    # Unrealizable report name.
    with pytest.raises(OSError):
        bad_filename = str(tmp_path / "name that can't be </parsed.txt")
        REDCapMatchResolver(report_filename=bad_filename)


def test_writing(addendum, matching_patients, tmp_path) -> None:
    """End-to-end test of writing a report."""
    output_filename = str(tmp_path / "test_filename.txt")
    writer_obj = REDCapMatchResolver(report_filename=output_filename)
    assert writer_obj is not None
    assert isinstance(writer_obj, REDCapMatchResolver)

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
