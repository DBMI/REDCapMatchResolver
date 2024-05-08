"""
Module test_clinics.py, which performs automated
testing of the REDCapClinic class.
"""

from redcapmatchresolver.redcap_clinic import REDCapClinic


def test_clinics():
    clinics = REDCapClinic()

    assert isinstance(clinics, REDCapClinic)
    assert clinics.priority("UPC DRAW STATION") == 1
    assert clinics.priority("NOT PRESENT") == 9999


if __name__ == "__main__":
    pass
