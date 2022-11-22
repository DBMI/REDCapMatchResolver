"""
Contains test fixtures available across all test_*.py files.
"""
import os
import pytest


@pytest.fixture(name="matching_patients")
def fixture_matching_patients():
    """Defines patient match text that IS present in our database."""
    return """
    ---------------
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


@pytest.fixture(name="non_matching_patients")
def fixture_non_matching_patients():
    """Defines patient match text NOT found in database."""
    return """
    ---------------
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


@pytest.fixture(name="malformed_match_block")
def fixture_malformed_match_block():
    """Defines a patient match text that's malformed & will cause errors."""
    return """
    ---------------
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
    Common Name         Epic Val               RedCap Val           Score
    C_MRN               1234                   1235                  0.7
    C_FIRST             Johnnie                Jonfen                0.8
    C_LAST              Schmidt                Schmidt               1.0
    C_EMAIL             jsmith@yahoo.com       j.smith@gmail.com     1.0
    C_ADDR_CALCULATED   4 Privet Drive         4 Privet Drive        1.0
    C_PHONE_CALCULATED  800-555-1212           800-555-1212          1.0
    ---------------
    """


if __name__ == "__main__":
    pass
