"""
Module test_match_resolver.py, which performs automated
testing of the REDCapMatchResolver class.
"""
from sqlite3 import Connection, Error
import os
import pytest
from redcapmatchresolver.redcap_match_resolver import REDCapMatchResolver


@pytest.fixture(name="temp_database")
def figure_temp_database():
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), "temp_database.db")


@pytest.fixture(name="reports_directory")
def figure_reports_directory():
    return os.path.dirname(os.path.realpath(__file__))


def test_match_resolver_creation(temp_database) -> None:
    """Tests instantiation and setup of a REDCapMatchResolver object."""
    mr_obj = REDCapMatchResolver()

    assert mr_obj is not None
    assert isinstance(mr_obj, REDCapMatchResolver)
    assert mr_obj.setup(db_filename=temp_database)


def test_match_resolver_reading(temp_database, reports_directory) -> None:
    """Tests read_reports() method of REDCapMatchResolver object."""
    mr_obj = REDCapMatchResolver()
    assert mr_obj.setup(db_filename=temp_database)

    assert mr_obj.read_reports(import_folder=reports_directory)

