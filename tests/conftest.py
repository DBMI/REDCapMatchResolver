"""
Contains test fixtures available across all test_*.py files.
"""
import os
import pandas
import pytest


@pytest.fixture(name="appointment_df")
def fixture_appointment_df() -> pandas.DataFrame:
    d = {"DEPARTMENT_NAME": "LWC CARDIOLOGY",
         "APPT_DATE_TIME": "2022-12-01 10:40:00"}
    return pandas.DataFrame(d, index=[0])


@pytest.fixture(name="appointment_df_malformed")
def fixture_appointment_df_malformed() -> pandas.DataFrame:
    d = {"DEPARTMENT_NAME": "LWC CARDIOLOGY"}
    return pandas.DataFrame(d, index=[0])


@pytest.fixture(name="appointment_df_slashes")
def fixture_appointment_record_slashes() -> pandas.DataFrame:
    d = {"DEPARTMENT_NAME": "LWC CARDIOLOGY",
         "APPT_DATE_TIME": "12/01/2022 10:40:00"}
    return pandas.DataFrame(d, index=[0])


@pytest.fixture(name="appointment_fields")
def fixture_appointment_fields() -> list:
    return [
        "APPOINTMENT_DATE",
        "APPT_DATE",
        "APPOINTMENT_TIME",
        "APPT_TIME",
        "CLINIC",
        "DEPARTMENT",
        "DEPT",
    ]


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
def fixture_matching_patients() -> str:
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
def fixture_malformed_match_block() -> str:
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
def fixture_missing_fields_match_block() -> str:
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
def fixture_non_matching_patients() -> str:
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
def fixture_patient_record_1() -> pandas.DataFrame:
    d = {'PAT_ID':"1234567",
        'MRN':"2345678",
        'EPIC_INTERNAL_ID':"E987654321",
        'PAT_FIRST_NAME':"George",
        'PAT_LAST_NAME':"Washington",
        'ADD_LINE_1':"1600 Pennsylvania Ave. NW",
        'ADD_LINE_2':"Null",
        'CITY':"Washington",
        'STATE_ABBR':"DC",
        'ZIP':"20500",
        'HOME_PHONE':"NULL",
        'WORK_PHONE':"202-456-11111",
        'EMAIL_ADDRESS':"george.washington@whitehouse.gov",
        'BIRTH_DATE':"1732-02-22",
        'DEATH_DATE':"1799-12-14",
        'DEPARTMENT_NAME':"UPC DRAW STATION",
        'APPT_DATE_TIME':"2022-12-26 10:11:12"}
    return pandas.DataFrame(d, index=[0])


@pytest.fixture(name="patient_record_2")
def fixture_patient_record_2() -> pandas.DataFrame:
    d = {'PAT_ID':"1234567",
        'MRN':"2345678",
        'EPIC_INTERNAL_ID':"E987654321",
        'PAT_FIRST_NAME':"George",
        'PAT_LAST_NAME':"Washington",
        'ADD_LINE_1':"1600 Pennsylvania Ave. NW",
        'ADD_LINE_2':"Null",
        'CITY':"Washington",
        'STATE_ABBR':"DC",
        'ZIP':"20500",
        'HOME_PHONE':"NULL",
        'WORK_PHONE':"202-456-11111",
        'EMAIL_ADDRESS':"george.washington@whitehouse.gov",
        'BIRTH_DATE':"1732-02-22",
        'DEATH_DATE':"1799-12-14",
        'DEPARTMENT_NAME':"UPC INTERNAL MEDICINE",
        'APPT_DATE_TIME':"2022-12-25 11:12:13"}
    return pandas.DataFrame(d, index=[0])


@pytest.fixture(name="patient_record_3")
def fixture_patient_record_3() -> pandas.DataFrame:
    d = {'PAT_ID':"2345678",
        'MRN':"3456789",
        'EPIC_INTERNAL_ID':"E876543210",
        'PAT_FIRST_NAME':"Martha",
        'PAT_LAST_NAME':"Washington",
        'ADD_LINE_1':"1600 Pennsylvania Ave. NW",
        'ADD_LINE_2':"Null",
        'CITY':"Washington",
        'STATE_ABBR':"DC",
        'ZIP':"20500",
        'HOME_PHONE':"000-000-0000",
        'WORK_PHONE':"1-202-456-1111",
        'EMAIL_ADDRESS':"marthae.washington@whitehouse.gov",
        'BIRTH_DATE':"1731-06-02",
        'DEATH_DATE':"1802-05-22",
        'DEPARTMENT_NAME':"UPC ORTHOPAEDICS",
        'APPT_DATE_TIME':"2022-12-27 13:14:15"}
    return pandas.DataFrame(d, index=[0])


@pytest.fixture(name="patient_record_4")
def fixture_patient_record_4() -> pandas.DataFrame:
    d = {'PAT_ID': "2345678",
         'MRN': "3456789",
         'EPIC_INTERNAL_ID': "E876543210",
         'PAT_FIRST_NAME': "Martha",
         'PAT_LAST_NAME': "Washington",
         'ADD_LINE_1': "1600 Pennsylvania Ave. NW",
         'ADD_LINE_2': "Null",
         'CITY': "Washington",
         'STATE_ABBR': "DC",
         'ZIP': "20500",
         'HOME_PHONE': "NONE",
         'WORK_PHONE': "1-202-456-1111",
         'EMAIL_ADDRESS': "marthae.washington@whitehouse.gov",
         'BIRTH_DATE': "06/02/1731",
         'DEATH_DATE': "1802-05-22",
         'DEPARTMENT_NAME': "UPC ORTHOPAEDICS",
         'APPT_DATE_TIME': "2022-12-27 13:14:15"}
    return pandas.DataFrame(d, index=[0])


@pytest.fixture(name="patient_record_5")
def fixture_patient_record_5() -> pandas.DataFrame:
    d = {'PAT_ID':"1234567",
        'MRN':"2345678",
        'EPIC_INTERNAL_ID':"E987654321",
        'PAT_FIRST_NAME':"George",
        'PAT_LAST_NAME':"Washington",
        'ADD_LINE_1':"1600 Pennsylvania Ave. NW",
        'ADD_LINE_2':"Null",
        'CITY':"Washington",
        'STATE_ABBR':"DC",
        'ZIP':"20500",
        'HOME_PHONE':"NULL",
        'WORK_PHONE':"202-456-11111",
        'EMAIL_ADDRESS':"george.washington@whitehouse.gov",
        'BIRTH_DATE':"1732-02-22",
        'DEATH_DATE':"1799-12-14",
        'DEPARTMENT_NAME':"UPC INTERNAL MEDICINE",
        'APPT_DATE_TIME':"2022-12-25 11:12:13"}
    return pandas.DataFrame(d, index=[0])


@pytest.fixture(name="patient_record_6")
def fixture_patient_record_6() -> pandas.DataFrame:
    d = {'PAT_ID':"1234567",
        'MRN':"2345678",
        'EPIC_INTERNAL_ID':"E987654321",
        'PAT_FIRST_NAME':"George",
        'PAT_LAST_NAME':"Washington",
        'ADD_LINE_1':"1600 Pennsylvania Ave. NW",
        'ADD_LINE_2':"Null",
        'CITY':"Washington",
        'STATE_ABBR':"DC",
        'ZIP':"20500",
        'HOME_PHONE':"NULL",
        'WORK_PHONE':"202-456-11111",
        'EMAIL_ADDRESS':"george.washington@whitehouse.gov",
        'BIRTH_DATE':None,
        'DEATH_DATE':"1799-12-14",
        'DEPARTMENT_NAME':"UPC INTERNAL MEDICINE",
        'APPT_DATE_TIME':"2022-12-25 11:12:13"}
    return pandas.DataFrame(d, index=[0])


@pytest.fixture(name="patient_record_7")
def fixture_patient_record_7() -> pandas.DataFrame:
    d = {'PAT_ID':"1234567",
        'MRN':"2345678",
        'EPIC_INTERNAL_ID':"E987654321",
        'PAT_FIRST_NAME':"George",
        'PAT_LAST_NAME':"Washington",
        'ADD_LINE_1':"1600 Pennsylvania Ave. NW",
        'ADD_LINE_2':"Null",
        'CITY':"Washington",
        'STATE_ABBR':"DC",
        'ZIP':"20500",
        'HOME_PHONE':"NULL",
        'WORK_PHONE':"202-456-11111",
        'EMAIL_ADDRESS':"george.washington@whitehouse.gov",
        'BIRTH_DATE':"1732A-02-22",
        'DEATH_DATE':"1799-12-14",
        'DEPARTMENT_NAME':"UPC INTERNAL MEDICINE",
        'APPT_DATE_TIME':"2022-12-25 11:12:13"}
    return pandas.DataFrame(d, index=[0])

@pytest.fixture(name="patient_record_no_appt")
def fixture_patient_record_no_appt() -> pandas.DataFrame:
    d = {'PAT_ID':"1234567",
        'MRN':"2345678",
        'EPIC_INTERNAL_ID':"E987654321",
        'PAT_FIRST_NAME':"George",
        'PAT_LAST_NAME':"Washington",
        'ADD_LINE_1':"1600 Pennsylvania Ave. NW",
        'ADD_LINE_2':"Null",
        'CITY':"Washington",
        'STATE_ABBR':"DC",
        'ZIP':"20500",
        'HOME_PHONE':"NULL",
        'WORK_PHONE':"202-456-11111",
        'EMAIL_ADDRESS':"george.washington@whitehouse.gov",
        'BIRTH_DATE':"1732-02-22",
        'DEATH_DATE':"1799-12-14"}
    return pandas.DataFrame(d, index=[0])


if __name__ == "__main__":
    pass
