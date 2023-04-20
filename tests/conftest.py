"""
Contains test fixtures available across all test_*.py files.
"""
import os
import pandas
import pytest


@pytest.fixture(name="appointment_df")
def fixture_appointment_df() -> pandas.DataFrame:
    d = {
        "appointment_clinic": "LWC CARDIOLOGY",
        "appointment_date": "2022-12-01",
        "appointment_time": "10:40:00",
    }
    return pandas.DataFrame(d, index=[0])


@pytest.fixture(name="appointment_df_malformed")
def fixture_appointment_df_malformed() -> pandas.DataFrame:
    d = {"appointment_clinic": "LWC CARDIOLOGY"}
    return pandas.DataFrame(d, index=[0])


@pytest.fixture(name="appointment_df_slashes")
def fixture_appointment_record_slashes() -> pandas.DataFrame:
    d = {
        "appointment_clinic": "LWC CARDIOLOGY",
        "appointment_date": "12/01/2022",
        "appointment_time": "10:40:00",
    }
    return pandas.DataFrame(d, index=[0])


@pytest.fixture(name="appointment_fields")
def fixture_appointment_fields() -> list:
    return [
        "appointment_date",
        "appt_date",
        "appointment_time",
        "appt_time",
        "clinic",
        "department",
        "dept",
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


#   For use with .csv() method. Can we rearrange and downselect the .csv output?
@pytest.fixture(name="patient_headers_scrambled")
def fixture_patient_headers_scrambled() -> list:
    headers = """
        study_id
        mrn
        last_name
        first_name
        appointment_clinic
        appointment_date
        appointment_time
        """.split()
    return headers


@pytest.fixture(name="patient_record_1")
def fixture_patient_record_1() -> pandas.DataFrame:
    d = {
        "study_id": "1234567",
        "mrn": "2345678",
        "first_name": "George",
        "last_name": "Washington",
        "street_address_1": "1600 Pennsylvania Ave. NW",
        "street_address_2": "Null",
        "city": "Washington",
        "state": "DC",
        "zip_code": "20500",
        "phone_number": "202-456-11111",
        "email_address": "george.washington@whitehouse.gov",
        "dob": "1732-02-22",
        "death_datetime": "1799-12-14",
        "appointment_clinic": "UPC DRAW STATION",
        "appointment_date": "2022-12-26",
        "appointment_time": "10:11:12",
    }
    df = pandas.DataFrame(d, index=[0])
    df.set_index('study_id', inplace=True)
    return df


@pytest.fixture(name="patient_record_2")
def fixture_patient_record_2() -> pandas.DataFrame:
    d = {
        "study_id": "1234567",
        "mrn": "2345678",
        "first_name": "George",
        "last_name": "Washington",
        "street_address_1": "1600 Pennsylvania Ave. NW",
        "street_address_2": "Null",
        "city": "Washington",
        "state": "DC",
        "zip_code": "20500",
        "phone_number": "202-456-11111",
        "email_address": "george.washington@whitehouse.gov",
        "dob": "1732-02-22",
        "death_datetime": "1799-12-14",
        "appointment_clinic": "UPC INTERNAL MEDICINE",
        "appointment_date": "2022-12-25",
        "appointment_time": "11:12:13",
    }
    df = pandas.DataFrame(d, index=[0])
    df.set_index('study_id', inplace=True)
    return df


@pytest.fixture(name="patient_records_1_2_merged")
def fixture_patient_records_1_2_merged() -> str:
    return """study_id,mrn,first_name,last_name,street_address_1,street_address_2,city,state,zip_code,phone_number,email_address,dob,death_datetime,appointment_clinic,appointment_date,appointment_time
1234567,2345678,George,Washington,1600 Pennsylvania Ave. NW,Null,Washington,DC,20500,202-456-11111,george.washington@whitehouse.gov,1732-02-22,1799-12-14,UPC DRAW STATION,2022-12-26,10:11:12
"""


@pytest.fixture(name="patient_records_1_2_merged_no_header")
def fixture_patient_records_1_2_merged_no_header() -> str:
    return """1234567,2345678,George,Washington,1600 Pennsylvania Ave. NW,Null,Washington,DC,20500,202-456-11111,george.washington@whitehouse.gov,1732-02-22,1799-12-14,UPC DRAW STATION,2022-12-26,10:11:12
"""


@pytest.fixture(name="patient_records_1_2_merged_limited_cols")
def fixture_patient_records_1_2_merged_limited_cols() -> str:
    return """study_id,mrn,last_name,first_name,appointment_clinic,appointment_date,appointment_time
1234567,2345678,Washington,George,UPC DRAW STATION,2022-12-26,10:11:12
"""


@pytest.fixture(name="patient_record_3")
def fixture_patient_record_3() -> pandas.DataFrame:
    d = {
        "study_id": "2345678",
        "mrn": "3456789",
        "first_name": "Martha",
        "last_name": "Washington",
        "street_address_1": "1600 Pennsylvania Ave. NW",
        "street_address_2": "Null",
        "city": "Washington",
        "state": "DC",
        "zip_code": "20500",
        "phone_number": "1-202-456-1111",
        "email_address": "marthae.washington@whitehouse.gov",
        "dob": "1731-06-02",
        "death_datetime": "1802-05-22",
        "appointment_clinic": "UPC ORTHOPAEDICS",
        "appointment_date": "2022-12-27",
        "appointment_time": "13:14:15",
    }
    df = pandas.DataFrame(d, index=[0])
    df.set_index('study_id', inplace=True)
    return df


@pytest.fixture(name="patient_record_4")
def fixture_patient_record_4() -> pandas.DataFrame:
    d = {
        "study_id": "2345678",
        "mrn": "3456789",
        "first_name": "Martha",
        "last_name": "Washington",
        "street_address_1": "1600 Pennsylvania Ave. NW",
        "street_address_2": "Null",
        "city": "Washington",
        "state": "DC",
        "zip_code": "20500",
        "phone_number": "1-202-456-1111",
        "email_address": "marthae.washington@whitehouse.gov",
        "dob": "06/02/1731",
        "death_datetime": "1802-05-22",
        "appointment_clinic": "UPC ORTHOPAEDICS",
        "appointment_date": "2022-12-27",
        "appointment_time": "13:14:15",
    }
    df = pandas.DataFrame(d, index=[0])
    df.set_index('study_id', inplace=True)
    return df


@pytest.fixture(name="patient_record_5")
def fixture_patient_record_5() -> pandas.DataFrame:
    d = {
        "study_id": "1234567",
        "mrn": "2345678",
        "first_name": "George",
        "last_name": "Washington",
        "street_address_1": "1600 Pennsylvania Ave. NW",
        "street_address_2": "Null",
        "city": "Washington",
        "state": "DC",
        "zip_code": "20500",
        "phone_number": "202-456-11111",
        "email_address": "george.washington@whitehouse.gov",
        "dob": "1732-02-22",
        "death_datetime": "1799-12-14",
        "appointment_clinic": "UPC INTERNAL MEDICINE",
        "appointment_date": "2022-12-25",
        "appointment_time": "14:15:16",
    }
    df = pandas.DataFrame(d, index=[0])
    df.set_index('study_id', inplace=True)
    return df


@pytest.fixture(name="patient_record_6")
def fixture_patient_record_6() -> pandas.DataFrame:
    d = {
        "study_id": "1234567",
        "mrn": "2345678",
        "first_name": "George",
        "last_name": "Washington",
        "street_address_1": "1600 Pennsylvania Ave. NW",
        "street_address_2": "Null",
        "city": "Washington",
        "state": "DC",
        "zip_code": "20500",
        "phone_number": "202-456-11111",
        "email_address": "george.washington@whitehouse.gov",
        "dob": None,
        "death_datetime": "1799-12-14",
        "appointment_clinic": "UPC INTERNAL MEDICINE",
        "appointment_date": "2022-12-25",
        "appointment_time": "11:12:13",
    }
    df = pandas.DataFrame(d, index=[0])
    df.set_index('study_id', inplace=True)
    return df


@pytest.fixture(name="patient_record_7")
def fixture_patient_record_7() -> pandas.DataFrame:
    d = {
        "study_id": "1234567",
        "mrn": "2345678",
        "first_name": "George",
        "last_name": "Washington",
        "street_address_1": "1600 Pennsylvania Ave. NW",
        "street_address_2": "Null",
        "city": "Washington",
        "state": "DC",
        "zip_code": "20500",
        "phone_number": "202-456-11111",
        "email_address": "george.washington@whitehouse.gov",
        "dob": "1732A-02-22",
        "death_datetime": "1799-12-14",
        "appointment_clinic": "UPC INTERNAL MEDICINE",
        "appointment_date": "2022-12-25",
        "appointment_time": "11:12:13",
    }
    df = pandas.DataFrame(d, index=[0])
    df.set_index('study_id', inplace=True)
    return df


@pytest.fixture(name="patient_record_1_no_appt")
def fixture_patient_record_1_no_appt() -> pandas.DataFrame:
    d = {
        "study_id": "1234567",
        "mrn": "2345678",
        "first_name": "George",
        "last_name": "Washington",
        "street_address_1": "1600 Pennsylvania Ave. NW",
        "street_address_2": "Null",
        "city": "Washington",
        "state": "DC",
        "zip_code": "20500",
        "phone_number": "202-456-11111",
        "email_address": "george.washington@whitehouse.gov",
        "dob": "1732-02-22",
        "death_datetime": "1799-12-14",
    }
    df = pandas.DataFrame(d, index=[0])
    df.set_index('study_id', inplace=True)
    return df


@pytest.fixture(name="patient_record_1_with_hpi")
def fixture_patient_record_1_with_hpi() -> pandas.DataFrame:
    d = {
        "study_id": "1234567",
        "mrn": "2345678",
        "first_name": "George",
        "last_name": "Washington",
        "street_address_1": "1600 Pennsylvania Ave. NW",
        "street_address_2": "Null",
        "city": "Washington",
        "state": "DC",
        "zip_code": "20500",
        "phone_number": "202-456-11111",
        "email_address": "george.washington@whitehouse.gov",
        "dob": "1732-02-22",
        "death_datetime": "1799-12-14",
        "hpi_percentile": "95.0",
        "hpi_score": "1.1",
    }
    df = pandas.DataFrame(d, index=[0])
    df.set_index('study_id', inplace=True)
    return df


if __name__ == "__main__":
    pass
