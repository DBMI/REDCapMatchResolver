"""
Module: contains the MatchRecord and MatchVariable classes.
"""
from collections import namedtuple

import pandas  # type: ignore[import]
from redcapduplicatedetector.match_quality import MatchQuality
from redcaprecordsynthesizer.state_abbr_conversion import StateAbbreviationConverter
from redcaputilities.string_cleanup import clean_up_date, clean_up_phone

MatchTuple = namedtuple(
    typename="MatchTuple", field_names=["bool", "summary"]  # type: ignore[misc]
)


class CommonField:
    """
    Hold cases where a field (like patient first name) is present in both Epic and REDCap.
    """

    def __init__(self, common_name: str, epic_field: str, redcap_field: str):
        if not isinstance(common_name, str):
            raise TypeError("Argument 'common_name' is not a string.")

        self.__common_name: str = common_name

        if not isinstance(epic_field, str):
            raise TypeError("Argument 'epic_field' is not a string.")

        self.__epic_field: str = epic_field

        if not isinstance(redcap_field, str):
            raise TypeError("Argument 'redcap_field' is not a string.")

        self.__redcap_field: str = redcap_field

    def common_name(self) -> str:
        return self.__common_name

    def epic_field(self) -> str:
        return self.__epic_field

    def epic_field_present(self, field_name: str) -> bool:
        if not isinstance(field_name, str):
            raise TypeError("Argument 'field_name' is not a string.")

        return self.__epic_field == field_name

    def redcap_field(self) -> str:
        return self.__redcap_field

    def redcap_field_present(self, field_name: str) -> bool:
        if not isinstance(field_name, str):
            raise TypeError("Argument 'field_name' is not a string.")

        return self.__redcap_field == field_name


class MatchRecord:
    """
    Holds the comparisons between REDCap and Epic for an entire DataFrame.
    internal variable 'record' is a dictionary of MatchVariable objects.
    """

    COMMON_FIELDS: list = [
        CommonField("C_MRN", "MRN", "mrn"),
        CommonField("C_FIRST", "PAT_FIRST_NAME", "first_name"),
        CommonField("C_LAST", "PAT_LAST_NAME", "last_name"),
        CommonField("C_EMAIL", "EMAIL_ADDRESS", "email_address"),
        CommonField("C_ADDR_CALCULATED", "C_ADDR_CALCULATED", "C_ADDR_CALCULATED"),
    ]

    FORMAT: str = "%-20s; %-40s; %-40s;"

    SCORE_FIELDS: list = [
        "C_MRN",
        "C_FIRST",
        "C_LAST",
        "C_DOB",
        "C_EMAIL",
        "C_ADDR_CALCULATED",
        "C_PHONE_CALCULATED",
    ]

    def __init__(self, row: pandas.Series):
        self.__record: dict = {}
        self.__score: int

        self.__build_dictionary(row)
        self.__score_record()

    # Helper...  strip everything but alphanumerics from a string
    @staticmethod
    def as_alphanum(string: str) -> str:
        _filter = filter(str.isalnum, string)
        _string = "".join(_filter)
        return _string

    def __build_dictionary(self, row: pandas.Series) -> None:
        if not isinstance(row, pandas.Series):
            raise TypeError("Argument 'row' is not the expected pandas.Series.")

        if "study_id" in row:
            self.__record["study_id"] = MatchVariable(
                epic_value="", redcap_value=str(row["study_id"])
            )

        for cf_obj in MatchRecord.COMMON_FIELDS:
            common_name: str = cf_obj.common_name()
            epic_value: str = ""
            epic_field: str = cf_obj.epic_field()

            if epic_field in row:
                epic_value = str(row[epic_field])

            redcap_field: str = cf_obj.redcap_field()
            redcap_value: str = ""

            if redcap_field in row:
                redcap_value = str(row[redcap_field])

            self.__record[common_name] = MatchVariable(
                epic_value=epic_value, redcap_value=redcap_value
            )
        #
        # Match phone numbers.
        #
        epic_home_phone: str = ""
        epic_work_phone: str = ""
        redcap_phone: str = ""

        if "WORK_PHONE" in row:
            epic_work_phone = str(clean_up_phone(row["WORK_PHONE"]))

        if "HOME_PHONE" in row:
            epic_home_phone = str(clean_up_phone(row["HOME_PHONE"]))

        if "phone_number" in row:
            redcap_phone = str(clean_up_phone(row["phone_number"]))

        # Try each Epic phone number against the REDCap phone number...
        match_variable = MatchVariable(
            epic_value=epic_home_phone, redcap_value=redcap_phone
        )

        if not match_variable.good_enough():
            match_variable = MatchVariable(
                epic_value=epic_work_phone, redcap_value=redcap_phone
            )

        # ...and use whichever matches (if any).
        self.__record["C_PHONE_CALCULATED"] = match_variable
        #
        #   Date of birth
        #
        epic_dob: str = ""
        redcap_dob: str = ""

        if "BIRTH_DATE" in row:
            # Use clean_up_date() method from REDCapUtilities--it handles date formatting.
            epic_dob = str(clean_up_date(row["BIRTH_DATE"]))

        if "dob" in row:
            redcap_dob = str(clean_up_date(row["dob"]))

        self.__record["C_DOB"] = MatchVariable(
            epic_value=epic_dob, redcap_value=redcap_dob
        )

    # see if a universal record is a match between its epic fields and redcap fields.
    def is_match(self, exact: bool = False, criteria: int = 4) -> MatchTuple:
        redcap_study_id = self.__record["study_id"].redcap_value()
        format: str = MatchRecord.FORMAT + "%s\n"
        summary: str = ""
        summary += "-------------\n"
        summary += "Study ID: " + redcap_study_id + "\n"
        summary += format % (
            "Common Name",
            "Epic Val",
            "RedCap Val",
            "Match Quality",
        )

        for key_fieldname in MatchRecord.SCORE_FIELDS:
            this_record = self.__record[key_fieldname]
            summary += this_record.summarize_match(common_name=key_fieldname) + "\n"

        summary += "-------------\n"
        good_match = self.__score >= criteria

        if exact:
            good_match = self.__score == criteria

        return MatchTuple(bool=good_match, summary=summary)

    def score(self) -> int:
        return self.__score

    # Scores a record and assigns a matching result
    def __score_record(self) -> None:
        self.__score = 0

        # Match all the common fields of a universal record.
        # Common fields are defined at the beginning of this class.  This chunk of code
        # also scores things that are handled explicitly elsewhere, such as phone, date of birth, etc.
        for common_name in MatchRecord.SCORE_FIELDS:
            this_record = self.__record[common_name]

            if this_record.good_enough():
                self.__score += 1


class MatchVariable:
    """
    Holds the comparison between REDCap and Epic for one variable.
    """

    def __init__(
        self,
        epic_value: str,
        redcap_value: str,
    ):
        if not isinstance(epic_value, str):
            raise TypeError("Argument 'epic_value' is not a string.")

        self.__epic_value: str = epic_value.strip()

        if not isinstance(redcap_value, str):
            raise TypeError("Argument 'redcap_value' is not a string.")

        self.__redcap_value: str = redcap_value.strip()

        self.__match_quality: MatchQuality
        self.__evaluate()

    def epic_value(self) -> str:
        return self.__epic_value

    # see if two strings are similar
    def __evaluate(self) -> None:
        self.__match_quality = MatchQuality.MATCHED_NOPE

        if not self.__epic_value and not self.__redcap_value:
            self.__match_quality = MatchQuality.MATCHED_NULL
        if self.__epic_value == "" and self.__redcap_value == "":
            self.__match_quality = MatchQuality.MATCHED_NULL
        elif not self.__epic_value or not self.__redcap_value:
            self.__match_quality = MatchQuality.MATCHED_NOPE
        elif self.__epic_value == self.__redcap_value:
            self.__match_quality = MatchQuality.MATCHED_EXACT
        elif self.__epic_value.lower() == self.__redcap_value.lower():
            self.__match_quality = MatchQuality.MATCHED_CASE_INSENSITIVE
        elif MatchRecord.as_alphanum(self.__epic_value) == MatchRecord.as_alphanum(
            self.__redcap_value
        ):
            self.__match_quality = MatchQuality.MATCHED_ALPHA_NUM
        elif (
            len(self.__epic_value) >= 4
            and len(self.__redcap_value) >= 4
            and (
                self.__epic_value.lower() in self.__redcap_value.lower()
                or self.__redcap_value.lower() in self.__epic_value.lower()
            )
        ):
            self.__match_quality = MatchQuality.MATCHED_SUBSTRING

    def good_enough(self) -> bool:
        return self.__match_quality.good_enough()

    def match_quality(self) -> MatchQuality:
        return self.__match_quality

    def redcap_value(self) -> str:
        return self.__redcap_value

    # simple enum to string conversion.  Useful for output.
    def summarize_match(self, common_name: str) -> str:
        format: str = MatchRecord.FORMAT + "[%s]"
        return format % (
            common_name,
            self.__epic_value,
            self.__redcap_value,
            str(self.__match_quality),
        )
