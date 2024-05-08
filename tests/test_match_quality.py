"""
Module test_match_quality.py, which performs automated
testing of the MatchQuality class.
"""

import pytest

from src.redcapmatchresolver.match_quality import MatchQuality


def test_match_quality():
    match_quality_obj = MatchQuality.convert("IGNORED")
    assert match_quality_obj is not None
    assert isinstance(match_quality_obj, MatchQuality)
    assert match_quality_obj == MatchQuality.IGNORED
    assert not match_quality_obj.good_enough()
    assert match_quality_obj.ignored()
    string_representation = str(match_quality_obj)
    assert string_representation is not None
    assert isinstance(string_representation, str)
    assert string_representation == "ignored"

    match_quality_obj = MatchQuality.convert("NOPE")
    assert match_quality_obj is not None
    assert isinstance(match_quality_obj, MatchQuality)
    assert match_quality_obj == MatchQuality.MATCHED_NOPE
    assert not match_quality_obj.good_enough()
    assert not match_quality_obj.ignored()
    string_representation = str(match_quality_obj)
    assert string_representation is not None
    assert isinstance(string_representation, str)
    assert string_representation == "-"

    match_quality_obj = MatchQuality.convert("null")
    assert match_quality_obj is not None
    assert isinstance(match_quality_obj, MatchQuality)
    assert match_quality_obj == MatchQuality.MATCHED_NULL
    assert not match_quality_obj.good_enough()
    assert not match_quality_obj.ignored()
    string_representation = str(match_quality_obj)
    assert string_representation is not None
    assert isinstance(string_representation, str)
    assert string_representation == "null"

    match_quality_obj = MatchQuality.convert("EXACT")
    assert match_quality_obj is not None
    assert isinstance(match_quality_obj, MatchQuality)
    assert match_quality_obj == MatchQuality.MATCHED_EXACT
    assert match_quality_obj.good_enough()
    assert not match_quality_obj.ignored()
    string_representation = str(match_quality_obj)
    assert string_representation is not None
    assert isinstance(string_representation, str)
    assert string_representation == "exact"

    match_quality_obj = MatchQuality.convert("CASE_INSENSITIVE")
    assert match_quality_obj is not None
    assert isinstance(match_quality_obj, MatchQuality)
    assert match_quality_obj == MatchQuality.MATCHED_CASE_INSENSITIVE
    assert match_quality_obj.good_enough()
    assert not match_quality_obj.ignored()
    string_representation = str(match_quality_obj)
    assert string_representation is not None
    assert isinstance(string_representation, str)
    assert string_representation == "lower"

    match_quality_obj = MatchQuality.convert("ALPHA_NUM")
    assert match_quality_obj is not None
    assert isinstance(match_quality_obj, MatchQuality)
    assert match_quality_obj == MatchQuality.MATCHED_ALPHA_NUM
    assert match_quality_obj.good_enough()
    assert not match_quality_obj.ignored()
    string_representation = str(match_quality_obj)
    assert string_representation is not None
    assert isinstance(string_representation, str)
    assert string_representation == "alphanum"

    match_quality_obj = MatchQuality.convert("substring")
    assert match_quality_obj is not None
    assert isinstance(match_quality_obj, MatchQuality)
    assert match_quality_obj == MatchQuality.MATCHED_SUBSTRING
    assert match_quality_obj.good_enough()
    assert not match_quality_obj.ignored()
    string_representation = str(match_quality_obj)
    assert string_representation is not None
    assert isinstance(string_representation, str)
    assert string_representation == "substring"

    match_quality_obj = MatchQuality.convert("FUZZY")
    assert match_quality_obj is not None
    assert isinstance(match_quality_obj, MatchQuality)
    assert match_quality_obj == MatchQuality.MATCHED_FUZZY
    assert match_quality_obj.good_enough()
    assert not match_quality_obj.ignored()
    string_representation = str(match_quality_obj)
    assert string_representation is not None
    assert isinstance(string_representation, str)
    assert string_representation == "fuzzy"

    match_quality_obj = MatchQuality.convert("CALCULATED")
    assert match_quality_obj is not None
    assert isinstance(match_quality_obj, MatchQuality)
    assert match_quality_obj == MatchQuality.MATCHED_CALCULATED
    assert match_quality_obj.good_enough()
    assert not match_quality_obj.ignored()
    string_representation = str(match_quality_obj)
    assert string_representation is not None
    assert isinstance(string_representation, str)
    assert string_representation == "calculated"


def test_match_quality_errors():
    with pytest.raises(TypeError):
        MatchQuality.convert(None)

    with pytest.raises(TypeError):
        MatchQuality.convert(1979)


if __name__ == "__main__":
    pass
