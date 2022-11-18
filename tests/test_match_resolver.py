"""
Module test_match_resolver.py, which performs automated
testing of the REDCapMatchResolver class.
"""
import os
import pytest
from redcapmatchresolver.redcap_match_resolver import REDCapMatchResolver
from redcapmatchresolver.redcap_report_reader import CrcReview


@pytest.fixture(name="temp_database")
def temp_database():
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), "temp_database.db")


@pytest.fixture(name="reports_directory")
def reports_directory():
    return os.path.dirname(os.path.realpath(__file__))


def test_match_resolver_creation(temp_database) -> None:
    """Tests instantiation and setup of a REDCapMatchResolver object."""
    mr_obj = REDCapMatchResolver(db_filename=temp_database)

    assert mr_obj is not None
    assert isinstance(mr_obj, REDCapMatchResolver)


def test_match_resolver_db_operation(
    temp_database, reports_directory, matching_patients, non_matching_patients
) -> None:
    """Tests read_reports() method of REDCapMatchResolver object."""
    mr_obj = REDCapMatchResolver(db_filename=temp_database)

    #   Can we read the already-reviewed report files & populate the temp database?
    assert mr_obj.read_reports(import_folder=reports_directory)

    #   Can we query the db with a new potential match?
    past_decision = mr_obj.lookup_potential_match(match_block=matching_patients)
    assert past_decision is not None
    assert isinstance(past_decision, CrcReview)
    assert past_decision == CrcReview.MATCH

    #   Can we query the db with a match not present in the database?
    past_decision = mr_obj.lookup_potential_match(match_block=non_matching_patients)
    assert past_decision is not None
    assert isinstance(past_decision, CrcReview)
    assert past_decision == CrcReview.NOT_SURE
