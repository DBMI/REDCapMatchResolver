"""
Contains test fixtures available across all test_*.py files.
"""
from datetime import datetime
import os
import pytest


@pytest.fixture(name="appointment_datetime")
def fixture_appointment_datetime() -> datetime:
    return datetime.strptime("2022-12-01 10:40:00", "%Y-%m-%d %H:%M:%S")


@pytest.fixture(name="appointment_headers")
def fixture_appointment_headers() -> list:
    return ["DEPARTMENT_NAME", "APPT_DATE_TIME"]


@pytest.fixture(name="appointment_record")
def fixture_appointment_record() -> list:
    return ["LWC CARDIOLOGY", "2022-12-01 10:40:00"]


@pytest.fixture(name="appointment_record_malformed")
def fixture_appointment_record_malformed() -> list:
    return ["LWC CARDIOLOGY", "20220-12-01 100:40:00"]


@pytest.fixture(name="appointment_record_partial")
def fixture_appointment_record_partial() -> list:
    return ["LWC CARDIOLOGY", ""]


@pytest.fixture(name="appointment_record_slashes")
def fixture_appointment_record_slashes() -> list:
    return ["LWC CARDIOLOGY", "12/01/2022 10:40:00"]


@pytest.fixture(name="export_fields")
def fixture_export_fields() -> list:
    return """
        study_id
        mrn
        first_name
        last_name
        dob
        street_address_line_1
        street_address_line_2
        city
        state
        zip_code
        email_address
        phone_number
        appointment_clinic
        appointment_date
        appointment_time
        primary_consent_date
        paired_status
    """.split()


@pytest.fixture(name="matching_patients")
def fixture_matching_patients():
    """Defines patient match text that IS present in our database."""
    return """
    ---------------
    Study ID: 1234
    Common Name         Epic Val               RedCap Val           Score
    C_MRN               123                    123                   1.0
    C_FIRST             John                   Jon                   0.8
    C_LAST              Smith                  Smith                 1.0
    C_DOB               2022-11-01             Nov 1, 2022           1.0
    C_EMAIL             jsmith@yahoo.com       j.smith@gmail.com     1.0
    C_ADDR_CALCULATED   1313 Mockingbird Lane  1313 Mockingbird Ln   1.0
    C_PHONE_CALCULATED  800-555-1212           800-555-1212          1.0
    ---------------
    """


@pytest.fixture(name="my_location")
def fixture_my_location():
    """Defines reusable fixture for location of this test file."""
    return os.path.dirname(os.path.realpath(__file__))


@pytest.fixture(name="malformed_match_block")
def fixture_malformed_match_block():
    """Defines a patient match text that's malformed & will cause errors."""
    return """
    ---------------
    Study ID: 1234
    Record: 1 of 1000
    Common Name         Epic Val                         Score
    C_MRN               1234                   1235                  0.7
    C_FIRST             Johnnie                Jonfen                0.8
    C_LAST              Schmidt                Schmidt               1.0
    C_EMAIL             jsmith@yahoo.com       j.smith@gmail.com     1.0
    C_ADDR_CALCULATED   4 Privet Drive         4 Privet Drive        1.0
    C_PHONE_CALCULATED  800-555-1212           800-555-1212          1.0
    ---------------
    """


@pytest.fixture(name="missing_fields_match_block")
def fixture_missing_fields_match_block():
    """Defines patient match text that's missing the DOB field."""
    return """
    ---------------
    Study ID: 1234
    Record: 1 of 1000
    Common Name         Epic Val               RedCap Val           Score
    C_MRN               1234                   1235                  0.7
    C_FIRST             Johnnie                Jonfen                0.8
    C_LAST              Schmidt                Schmidt               1.0
    C_EMAIL             jsmith@yahoo.com       j.smith@gmail.com     1.0
    C_ADDR_CALCULATED   4 Privet Drive         4 Privet Drive        1.0
    C_PHONE_CALCULATED  800-555-1212           800-555-1212          1.0
    ---------------
    """


@pytest.fixture(name="non_matching_patients")
def fixture_non_matching_patients():
    """Defines patient match text NOT found in database."""
    return """
    ---------------
    Study ID: 1234
    Record: 1 of 1000
    Common Name         Epic Val               RedCap Val           Score
    C_MRN               1234                   1235                  0.7
    C_FIRST             Johnnie                Jonfen                0.8
    C_LAST              Schmidt                Schmidt               1.0
    C_DOB               2022-11-18             Nov 18, 2022          1.0
    C_EMAIL             jsmith@yahoo.com       j.smith@gmail.com     1.0
    C_ADDR_CALCULATED   4 Privet Drive         4 Privet Drive        1.0
    C_PHONE_CALCULATED  800-555-1212           800-555-1212          1.0
    ---------------
    """


@pytest.fixture(name="patient_headers")
def fixture_patient_headers() -> list:
    headers = """
        PAT_ID
        MRN
        EPIC_INTERNAL_ID
        PAT_FIRST_NAME
        PAT_LAST_NAME
        ADD_LINE_1
        ADD_LINE_2
        CITY
        STATE_ABBR
        ZIP
        HOME_PHONE
        WORK_PHONE
        EMAIL_ADDRESS
        BIRTH_DATE
        DEATH_DATE
        DEPARTMENT_NAME
        APPT_DATE_TIME
        """.split()
    return headers


@pytest.fixture(name="patient_record_1")
def fixture_patient_record_1():
    return (
        "1234567",
        "2345678",
        "E987654321",
        "George",
        "Washington",
        "1600 Pennsylvania Ave. NW",
        "Null",
        "Washington",
        "DC",
        "20500",
        "NULL",
        "202-456-11111",
        "george.washington@whitehouse.gov",
        "1732-02-22",
        "1799-12-14",
        "UPC DRAW STATION",
        "2022-12-26 10:11:12",
    )


@pytest.fixture(name="patient_record_2")
def fixture_patient_record_2():
    return (
        "1234567",
        "2345678",
        "E987654321",
        "George",
        "Washington",
        "1600 Pennsylvania Ave. NW",
        "Null",
        "Washington",
        "DC",
        "20500",
        "NULL",
        "202-456-11111",
        "george.washington@whitehouse.gov",
        "1732-02-22",
        "1799-12-14",
        "UPC INTERNAL MEDICINE",
        "2022-12-25 11:12:13",
    )


@pytest.fixture(name="patient_record_3")
def fixture_patient_record_3():
    return (
        "2345678",
        "3456789",
        "E876543210",
        "Martha",
        "Washington",
        "1600 Pennsylvania Ave. NW",
        "Null",
        "Washington",
        "DC",
        "20500",
        "000-000-0000",
        "1-202-456-1111",
        "marthae.washington@whitehouse.gov",
        "1731-06-02",
        "1802-05-22",
        "UNC ORTHOPAEDICS",
        "2022-12-27 13:14:15",
    )


@pytest.fixture(name="patient_record_4")
def fixture_patient_record_4():
    return (
        "2345678",
        "3456789",
        "E876543210",
        "Martha",
        "Washington",
        "1600 Pennsylvania Ave. NW",
        "Null",
        "Washington",
        "DC",
        "20500",
        "NONE",
        "202-456-1111",
        "marthae.washington@whitehouse.gov",
        "1731-06-02",
        "1802-05-22",
        "UNC ORTHOPAEDICS",
        "2022-12-27 13:14:15",
    )


@pytest.fixture(name="patient_record_5")
def fixture_patient_record_5():
    return (
        "1234567",
        "2345678",
        "E987654321",
        "George",
        "Washington",
        "1600 Pennsylvania Ave. NW",
        "Null",
        "Washington",
        "DC",
        "20500",
        "NULL",
        "202-456-11111",
        "george.washington@whitehouse.gov",
        "1732-02-22",
        "1799-12-14",
        "UPC INTERNAL MEDICINE",
        "2022-12-26 11:12:13",
    )


if __name__ == "__main__":
    pass
