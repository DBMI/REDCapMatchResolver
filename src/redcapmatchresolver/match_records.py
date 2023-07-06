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

    COMMON_FIELDS = [
        CommonField("C_MRN", "MRN", "mrn"),
        CommonField("C_FIRST", "PAT_FIRST_NAME", "first_name"),
        CommonField("C_LAST", "PAT_LAST_NAME", "last_name"),
        CommonField("C_DOB", "BIRTH_DATE", "dob"),
        CommonField("C_ADDR1", "ADD_LINE_1", "street_address_line_1"),
        CommonField("C_ADDR2", "ADD_LINE_2", "street_address_line_2"),
        CommonField("C_CITY", "CITY", "city"),
        CommonField("C_STATE", "STATE_ABBR", "state"),
        CommonField("C_ZIP", "ZIP", "zip_code"),
        CommonField("C_EMAIL", "EMAIL_ADDRESS", "email_address"),
    ]

    EPIC_FIELDS = """
        EPIC_MERGE_ID
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
        COUNTY_NAME
        HOME_PHONE
        WORK_PHONE
        EMAIL_ADDRESS
        BIRTH_DATE
        SEX_NAME
        LANGUAGE
        STATE_C
        COUNTY_C
        COUNTRY_C
        PAT_STATUS_C
        LANGUAGE_C
        REG_DATE
        PAT_UPDATE_DATE
        DEATH_DATE
        LANG_CARE_C
        DEPARTMENT_ID
        CUR_PCP_PROV_ID
        PAT_ENC_CSN_ID
        SERV_AREA_ID
        DEPARTMENT_NAME
        APPT_STATUS_C
        APPT_UPDATE_DATE
        APPT_MADE_DTTM
        APPT_CANC_DTTM
        APPT_DTTM
        APPT_LENGTH
        CHECKIN_DTTM
        CHECKOUT_DTTM
        PROV_NAME
        HPI_SCORE
        HPI_PERCENTILE
    """.split()

    # RedCap fields of interest.  Should match to csv header.
    REDCAP_FIELDS = """
        REDCAP_MERGE_ID
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
        hpi_score
        hpi_percentile
    """.split()

    def __init__(self, row: pandas.Series):
        self.__record: dict = {}
        self.__score: int

        if not isinstance(row, pandas.Series):
            raise TypeError("Argument 'row' is not the expected pandas.Series.")

        column_names = row.axes[0]

        for column_name in column_names:
            common_field_obj = [
                cf
                for cf in MatchRecord.COMMON_FIELDS
                if cf.epic_field_present(column_name)
            ]

            if common_field_obj:
                this_common_field_obj = common_field_obj[0]
                epic_field = this_common_field_obj.epic_field()
                epic_value = str(row[epic_field])
                common_name = this_common_field_obj.common_name()
                redcap_value = ""

                if common_name in self.__record:
                    old_record = self.__record[common_name]
                    redcap_value = old_record.redcap_value()

                self.__record[common_name] = MatchVariable(
                    epic_value=epic_value, redcap_value=redcap_value
                )

            common_field_obj = [
                cf
                for cf in MatchRecord.COMMON_FIELDS
                if cf.redcap_field_present(column_name)
            ]

            if common_field_obj:
                this_common_field_obj = common_field_obj[0]
                redcap_field = this_common_field_obj.redcap_field()
                redcap_value = str(row[redcap_field])
                common_name = this_common_field_obj.common_name()
                epic_value = ""

                if common_name in self.__record:
                    old_record = self.__record[common_name]
                    epic_value = old_record.epic_value()

                self.__record[common_name] = MatchVariable(
                    epic_value=epic_value, redcap_value=redcap_value
                )

            value = str(row[column_name])

            # NOT A COMMON FIELD
            if column_name in MatchRecord.EPIC_FIELDS:
                self.__record[column_name] = MatchVariable(
                    epic_value=value, redcap_value=""
                )

            if column_name in MatchRecord.REDCAP_FIELDS:
                self.__record[column_name] = MatchVariable(
                    epic_value="", redcap_value=value
                )

        self.__score_record()

    # Helper...  strip everything but alphanumerics from a string
    @staticmethod
    def as_alphanum(string: str) -> str:
        _filter = filter(str.isalnum, string)
        _string = "".join(_filter)
        return _string

    # see if a universal record is a match between its epic fields and redcap fields.
    def is_match(self, exact: bool = False, criteria: int = 4) -> MatchTuple:
        redcap_study_id = self.__record["study_id"].redcap_value()
        self.__score = 0
        summary: str = ""
        summary += "-------------\n"
        summary += "Study ID: " + redcap_study_id + "\n"
        summary += "%-30s %-30s %-30s %s\n" % (
            "Common Name",
            "Epic Val",
            "RedCap Val",
            "Match Quality",
        )

        for key_fieldname in [
            "C_MRN",
            "C_FIRST",
            "C_LAST",
            "C_DOB",
            "C_EMAIL",
            "C_ADDR_CALCULATED",
            "C_PHONE_CALCULATED",
        ]:
            this_record = self.__record[key_fieldname]

            if this_record.good_enough():
                self.__score += 1

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
        # 1. Easy matches
        # Match all the common fields of a universal record.
        # Common fields are defined at the beginning of this class.  This chunk of code
        # also scores things that are handled explicitly elsewhere, such as phone, date of birth, etc.
        for common_field_obj in self.COMMON_FIELDS:
            common_name = common_field_obj.common_name()
            epic_field = common_field_obj.epic_field()
            epic_value = self.__record[epic_field].epic_value()
            redcap_field = common_field_obj.redcap_field()
            redcap_value = self.__record[redcap_field].redcap_value()
            self.__record[common_name] = MatchVariable(
                epic_value=epic_value, redcap_value=redcap_value
            )

        # 2. Match street address
        # This is a more difficult match.  We're going to do what credit cards do with AVS.
        # Namely, we're going to partially match.  We actually have a higher criteria v AVS.
        # We match street line 1 and zip, call it a day.
        epic_addr_value: str = ""
        redcap_addr_value: str = ""

        for common_name in ["C_ADDR1", "C_ZIP"]:
            match_variable = self.__record[common_name]
            epic_value = match_variable.epic_value()
            redcap_value = match_variable.redcap_value()
            epic_addr_value += epic_value + " | "
            redcap_addr_value += redcap_value + " | "

        self.__record["C_ADDR_CALCULATED"] = MatchVariable(
            epic_value=epic_addr_value,
            redcap_value=redcap_addr_value,
        )

        # 3. Match phone numbers.
        # First, clean up formatting...
        epic_work_phone = str(clean_up_phone(self.__record["WORK_PHONE"].epic_value()))
        epic_home_phone = str(clean_up_phone(self.__record["HOME_PHONE"].epic_value()))
        redcap_phone = str(clean_up_phone(self.__record["phone_number"].redcap_value()))

        # ...then try each Epic phone number against the REDCap phone number...
        match_variable = MatchVariable(
            epic_value=epic_home_phone, redcap_value=redcap_phone
        )

        if not match_variable.good_enough():
            match_variable = MatchVariable(
                epic_value=epic_work_phone, redcap_value=redcap_phone
            )

        # ...and use whichever matches (if any).
        self.__record["C_PHONE_CALCULATED"] = match_variable

        # 4. Match date of birth.
        # Use clean_up_date() method from REDCapUtilities--it handles date formatting.
        epic_dob: str = str(clean_up_date(self.__record["BIRTH_DATE"].epic_value()))
        redcap_dob: str = str(clean_up_date(self.__record["dob"].redcap_value()))
        self.__record["C_DOB"] = MatchVariable(
            epic_value=epic_dob, redcap_value=redcap_dob
        )

        # 5. Match state names, allowing for both abbreviations ("CA") and full names ("California").
        state_abbreviation_converter: StateAbbreviationConverter = (
            StateAbbreviationConverter()
        )
        epic_state: str = state_abbreviation_converter.full_name(
            self.__record["STATE_ABBR"].epic_value()
        )
        redcap_state: str = state_abbreviation_converter.full_name(
            self.__record["state"].redcap_value()
        )
        self.__record["C_STATE"] = MatchVariable(
            epic_value=epic_state, redcap_value=redcap_state
        )


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
        return "%-30s %-30s %-30s [%s]" % (
            common_name,
            self.__epic_value,
            self.__redcap_value,
            str(self.__match_quality),
        )
