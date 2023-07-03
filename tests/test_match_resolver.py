"""
Module test_match_resolver.py, which performs automated
testing of the REDCapMatchResolver class.
"""
import os
import sqlite3
import pytest

from redcapmatchresolver.redcap_match_resolver import REDCapMatchResolver
from redcapmatchresolver.redcap_report_reader import DecisionReview
from redcaputilities.directories import ensure_output_path_exists

@pytest.fixture(name="bad_reports_directory")
def fixture_bad_reports_directory():
    """Defines temporary bad reports directory."""
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), "bad_reports")


@pytest.fixture(name="empty_reports_directory")
def fixture_empty_reports_directory():
    """Defines temporary empty reports directory."""
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), "empty_folder")


@pytest.fixture(name="reports_directory")
def fixture_reports_directory():
    """Defines temporary reports directory."""
    return os.path.dirname(os.path.realpath(__file__))


@pytest.fixture(name="temp_database_connection")
def fixture_temp_database_connection() -> sqlite3.Connection:
    """Creates connection to temporary sqlite3 database filename."""
    db_name: str = os.path.join(os.path.dirname(os.path.realpath(__file__)), "temp_database.db")
    ensure_output_path_exists(db_name)
    conn: sqlite3.Connection = sqlite3.connect(db_name)
    return conn


def test_match_resolver_creation(temp_database_connection) -> None:
    """Tests instantiation and setup of a REDCapMatchResolver object."""
    mr_obj = REDCapMatchResolver(connection=temp_database_connection)
    assert isinstance(mr_obj, REDCapMatchResolver)

    #   Test instantiation with default filename.
    mr_obj = REDCapMatchResolver()
    assert isinstance(mr_obj, REDCapMatchResolver)


def test_match_resolver_db_operation(
    temp_database_connection, reports_directory, matching_patients, non_matching_patients
) -> None:
    """Tests lookup_potential_match() method of REDCapMatchResolver object."""
    mr_obj = REDCapMatchResolver(connection=temp_database_connection)

    #   Can we read the already-reviewed report files & populate the temp database?
    assert mr_obj.read_reports(import_folder=reports_directory)

    #   Can we query the db with a new potential match?
    past_decision = mr_obj.lookup_potential_match(match_block=matching_patients)
    assert isinstance(past_decision, DecisionReview)
    assert past_decision == DecisionReview.MATCH

    #   Can we query the db with a match NOT present in the database?
    past_decision = mr_obj.lookup_potential_match(match_block=non_matching_patients)
    assert isinstance(past_decision, DecisionReview)
    assert past_decision == DecisionReview.NOT_SURE


def test_match_resolver_corner_cases(
    temp_database_connection, bad_reports_directory, empty_reports_directory, matching_patients
) -> None:
    """Tests lookup_potential_match() method of REDCapMatchResolver object."""
    mr_obj = REDCapMatchResolver(connection=temp_database_connection)

    #   Exercise section in _insert_reports that fills in missing fields.
    assert mr_obj.read_reports(import_folder=bad_reports_directory)

    #   Exercise section in _insert_reports that skips if decision not shown.
    assert mr_obj.read_reports(import_folder=bad_reports_directory)

    #   What if there ARE no previous records? (This is how we'll start, after all.)
    assert mr_obj.read_reports(import_folder=empty_reports_directory)

    #   Can we query an EMPTY db with a new potential match?
    past_decision = mr_obj.lookup_potential_match(match_block=matching_patients)
    assert isinstance(past_decision, DecisionReview)
    assert past_decision == DecisionReview.NOT_SURE


def test_match_resolver_errors(
    temp_database_connection, reports_directory, malformed_match_block, missing_fields_match_block
):
    """Exercises error cases."""
    mr_obj = REDCapMatchResolver(connection=temp_database_connection)

    #   Read the already-reviewed report files & populate the temp database.
    assert mr_obj.read_reports(import_folder=reports_directory)

    #   Send improper inputs.
    with pytest.raises(TypeError):
        mr_obj.lookup_potential_match(match_block=None)

    with pytest.raises(TypeError):
        mr_obj.read_reports(import_folder=1979)

    with pytest.raises(RuntimeError):
        mr_obj.lookup_potential_match(match_block=malformed_match_block)

    with pytest.raises(RuntimeError):
        mr_obj.lookup_potential_match(match_block=missing_fields_match_block)


if __name__ == "__main__":
    pass
