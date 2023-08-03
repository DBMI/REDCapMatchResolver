"""
Module test_redcap_update.py, which performs automated
testing of the REDCapUpdate class.
"""
import pytest
from redcapmatchresolver.redcap_update import REDCapUpdate


def test_redcap_update_creation() -> None:
    """Tests instantiation and setup of a REDCapUpdate object."""
    update_obj = REDCapUpdate()
    assert isinstance(update_obj, REDCapUpdate)

    update_needed = update_obj.needed()
    assert isinstance(update_needed, bool)
    assert not update_needed

    update_obj.set(property="first_name", value="Alice")
    update_needed = update_obj.needed()
    assert isinstance(update_needed, bool)
    assert update_needed

    package = update_obj.package()
    assert isinstance(package, dict)
    assert "first_name" in package
    assert package["first_name"] == "Alice"
    assert not "last_name" in package


def test_redcap_update_errors() -> None:
    update_obj = REDCapUpdate()
    assert isinstance(update_obj, REDCapUpdate)

    with pytest.raises(TypeError):
        update_obj.set(property="not enough arguments")

    with pytest.raises(KeyError):
        update_obj.set(property="unexpected argument", value="won't work")
