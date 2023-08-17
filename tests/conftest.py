"""
Contains test fixtures available across all test_*.py files.
"""
import os
import datetime
import re
import pandas
import pytest
from faker import Faker
from redcaprecordsynthesizer.state_abbr_conversion import StateAbbreviationConverter
from redcaputilities.string_cleanup import clean_up_phone


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


@pytest.fixture(name="appointment_df_time_missing")
def fixture_appointment_record_time_missing() -> pandas.DataFrame:
    d = {
        "appointment_clinic": "LWC CARDIOLOGY",
        "appointment_date": "2022-12-01",
        "appointment_time": "",
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


# https://stackoverflow.com/a/33879151/20241849
@pytest.fixture(name="fake_records_dataframe")
def fixture_fake_records_dataframe() -> pandas.DataFrame:
    """
    Synthesize multiple records for testing.

    Return
    ------
    pandas.DataFrame
    """
    num_records_to_synthesize: int = 1
    fake: Faker = Faker()
    dataframes = []
    state_abbr_converter: StateAbbreviationConverter = StateAbbreviationConverter()

    for index in range(num_records_to_synthesize):
        birthdate: datetime.datetime = fake.date_of_birth(
            minimum_age=18, maximum_age=115
        )

        # Strip off the extension.
        phone_number: str = fake.phone_number()
        phone_number: str = re.sub(r"x\d+", "", phone_number)
        state_abbr: str = fake.state_abbr(include_territories=False)
        # full_state_name: str = state_abbr_converter.full_name(state_abbr)

        record = {
            "study_id": fake.random_int(min=1000, max=50000),
            "PAT_ID": fake.bothify(text="?#######", letters="ABCDEFGHJKLMNPQRSTUVWXYZ"),
            "MRN": "",
            "MRN_HX": "",
            "mrn": fake.random_int(min=1000, max=100000),
            "PAT_FIRST_NAME": "",
            "first_name": fake.first_name(),
            "PAT_LAST_NAME": "",
            "last_name": fake.last_name(),
            "ALIAS": "",
            "BIRTH_DATE": "",
            "dob": birthdate.strftime("%Y-%m-%d"),
            "ADD_LINE_1": "",
            "street_address_line_1": fake.street_address(),
            "ADD_LINE_2": "",
            "street_address_line_2": "",
            "ZIP": "",
            "zip_code": fake.zipcode_in_state(state_abbr),
            "email_address": fake.email(),  # The order here is REVERSED (first REDCap, then Epic)
            "EMAIL_ADDRESS": "",  # to exercise a different part of the code.
            "HOME_PHONE": "",
            "WORK_PHONE": "",
            "Mobile_Phone": "",
            "phone_number": phone_number,
            "E_ADDR_CALCULATED": "",
            "R_ADDR_CALCULATED": "",
        }

        # We'll start out with mostly identical REDCap and Epic fields.
        record["MRN"] = record["mrn"]
        record["MRN_HX"] = record["mrn"]
        record["ADD_LINE_1"] = record["street_address_line_1"]
        record["ADD_LINE_2"] = record["street_address_line_2"]
        record["ZIP"] = record["zip_code"]
        record["EMAIL_ADDRESS"] = record["email_address"]
        record["HOME_PHONE"] = record["phone_number"]
        record["WORK_PHONE"] = record["phone_number"]
        record["Mobile_Phone"] = record["phone_number"]
        record["E_ADDR_CALCULATED"] = record["ADD_LINE_1"] + " | " + record["ZIP"]
        record["R_ADDR_CALCULATED"] = (
            record["street_address_line_1"] + " | " + record["zip_code"]
        )

        # Add a non-alphanumeric character to the patient's first name
        # to exercise MATCH_QUALITY.MATCHED_ALPHA_NUM.
        record["PAT_FIRST_NAME"] = record["first_name"] + ";"

        # Set PAT_LAST_NAME to all lowercase to exercise MATCH_QUALITY..MATCHED_CASE_INSENSITIVE.
        record["PAT_LAST_NAME"] = record["last_name"].lower()

        # Assume no other names used.
        record["ALIAS"] = record["last_name"] + "," + record["first_name"]

        # Use a different date format to exercise clean_up_date() method.
        record["BIRTH_DATE"] = birthdate.strftime("%Y-%m-%d %H:%M:%S")

        dataframes.append(pandas.DataFrame([record], index=[index]))

    return pandas.concat(dataframes)


@pytest.fixture(name="matching_patients")
def fixture_matching_patients() -> str:
    """Defines patient match text that IS present in our database."""
    return """
    ---------------
    Study ID: 1234
    PAT_ID: A56789
    Common Name         Epic Value             RedCap Value          Match Quality
    C_MRN               123                    123                   [exact]
    C_FIRST             John                   Jon                   [-]
    C_LAST              Smith                  Smith                 [exact]
    C_DOB               2022-11-01             Nov 1, 2022           [exact]
    C_EMAIL             jsmith@yahoo.com       j.smith@gmail.com     [alphanum]
    C_ADDR_CALCULATED   1313 Mockingbird Lane  1313 Mockingbird Ln   [exact]
    C_PHONE_CALCULATED  800-555-1212           800-555-1212          [exact]
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
    Common Name         Epic Value             RedCap Value         Match Quality
    C_MRN               1234                   1235                 [-]
    C_FIRST             Johnnie                Jonfen               [-]
    C_LAST              Schmidt                Schmidt              [exact]
    C_EMAIL             jsmith@yahoo.com       j.smith@gmail.com    [alphanum]
    C_ADDR_CALCULATED   4 Privet Drive         4 Privet Drive       [exact]
    C_PHONE_CALCULATED  800-555-1212           800-555-1212         [exact]
    ---------------
    """


@pytest.fixture(name="non_matching_patients")
def fixture_non_matching_patients() -> str:
    """Defines patient match text NOT found in database."""
    return """
    ---------------
    Study ID: 1234
    PAT_ID: A00000
    Record: 1 of 1000
    Common Name         Epic Value             RedCap Value          Match Quality
    C_MRN               1234                   1235                  [-]
    C_FIRST             Johnnie                Jonfen                [-]
    C_LAST              Schmidt                Schmidt               [exact]
    C_DOB               2022-11-18             Nov 18, 2022          [exact]
    C_EMAIL             jsmith@yahoo.com       j.smith@gmail.com     [alphanum]
    C_ADDR_CALCULATED   4 Privet Drive         4 Privet Drive        [exact]
    C_PHONE_CALCULATED  800-555-1212           800-555-1212          [exact]
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
    df.set_index("study_id", inplace=True)
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
    df.set_index("study_id", inplace=True)
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
    df.set_index("study_id", inplace=True)
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
    df.set_index("study_id", inplace=True)
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
    df.set_index("study_id", inplace=True)
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
    df.set_index("study_id", inplace=True)
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
    df.set_index("study_id", inplace=True)
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
    df.set_index("study_id", inplace=True)
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
    df.set_index("study_id", inplace=True)
    return df


@pytest.fixture(name="report_filename_address")
def fixture_report_filename_address():
    return os.path.join(
        os.path.dirname(os.path.realpath(__file__)), "test_patient_report_address.txt"
    )


@pytest.fixture(name="report_filename_blank")
def fixture_report_filename_blank():
    return os.path.join(
        os.path.dirname(os.path.realpath(__file__)), "test_patient_report_blank.txt"
    )


@pytest.fixture(name="report_filename_parent_child")
def fixture_report_filename_parent_child():
    return os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        "test_patient_report_parent_child.txt",
    )


@pytest.fixture(name="report_filename_relatives")
def fixture_report_filename_relatives():
    return os.path.join(
        os.path.dirname(os.path.realpath(__file__)), "test_patient_report_relatives.txt"
    )


@pytest.fixture(name="report_filename_same")
def fixture_report_filename_same():
    return os.path.join(
        os.path.dirname(os.path.realpath(__file__)), "test_patient_report_same.txt"
    )


@pytest.fixture(name="same_facility_dataframe")
def fixture_same_facility_dataframe() -> pandas.DataFrame:
    """
    Two separate patients that live at same facility with same phone number
    and same first names but everything else different.

    Return
    ------
    pandas.DataFrame
    """
    fake: Faker = Faker()
    dataframes = []

    birthdate_1: datetime.datetime = fake.date_of_birth(minimum_age=18, maximum_age=115)
    birthdate_2: datetime.datetime = fake.date_of_birth(minimum_age=18, maximum_age=115)

    # Strip off the extension.
    common_phone_number: str = clean_up_phone(fake.phone_number())
    common_phone_number: str = re.sub(r"x\d+", "", common_phone_number)
    common_first_name = fake.first_name()
    common_address: str = fake.street_address()
    common_state_abbr: str = fake.state_abbr(include_territories=False)
    common_zip: str = fake.zipcode_in_state(common_state_abbr)

    record = {
        "MRN": fake.random_int(min=1000, max=100000),
        "mrn": fake.random_int(min=1000, max=100000),
        "MRN_HX": "",
        "study_id": fake.random_int(min=1000, max=50000),
        "PAT_ID": fake.bothify(text="?#######", letters="ABCDEFGHJKLMNPQRSTUVWXYZ"),
        "PAT_FIRST_NAME": common_first_name,
        "first_name": common_first_name,
        "PAT_LAST_NAME": fake.last_name(),
        "last_name": fake.last_name(),
        "ALIAS": "",
        "BIRTH_DATE": birthdate_1.strftime("%Y-%m-%d"),
        "dob": birthdate_2.strftime("%Y-%m-%d"),
        "ADD_LINE_1": common_address,
        "street_address_line_1": common_address,
        "ADD_LINE_2": "",
        "street_address_line_2": "",
        "ZIP": common_zip,
        "zip_code": common_zip,
        "EMAIL_ADDRESS": fake.email(),
        "email_address": fake.email(),
        "HOME_PHONE": common_phone_number,
        "WORK_PHONE": "",
        "Mobile_Phone": "",
        "phone_number": common_phone_number,
        "E_ADDR_CALCULATED": "",
        "R_ADDR_CALCULATED": "",
    }

    record["E_ADDR_CALCULATED"] = record["ADD_LINE_1"] + " | " + record["ZIP"]
    record["R_ADDR_CALCULATED"] = (
        record["street_address_line_1"] + " | " + record["zip_code"]
    )

    # Assume no other names, MRNs used.
    record["ALIAS"] = record["PAT_LAST_NAME"] + "," + record["PAT_FIRST_NAME"]
    record["MRN_HX"] = record["MRN"]

    dataframes.append(pandas.DataFrame([record], index=[1]))
    return pandas.concat(dataframes)


if __name__ == "__main__":
    pass
