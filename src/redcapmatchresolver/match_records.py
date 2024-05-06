"""
Module: contains the MatchRecord and MatchVariable classes.
"""

from collections import namedtuple

import pandas  # type: ignore[import]
from .match_quality import MatchQuality
from redcaputilities.string_cleanup import clean_up_phone

from redcapmatchresolver.redcap_update import REDCapUpdate

MatchTuple = namedtuple(
    typename="MatchTuple", field_names=["bool", "summary"]  # type: ignore[misc]
)


class CommonField:
    """
    Hold cases where a field (like patient first name) is present in both Epic and REDCap.
    """

    def __init__(
        self,
        common_name: str,
        epic_field: str,
        redcap_field: str,
    ):
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

    # These fields are used in generating the match summary.
    COMMON_FIELDS: list = [
        CommonField("C_MRN", "MRN", "mrn"),
        CommonField("C_FIRST", "PAT_FIRST_NAME", "first_name"),
        CommonField("C_LAST", "PAT_LAST_NAME", "last_name"),
        CommonField("C_DOB", "BIRTH_DATE", "dob"),
        CommonField("C_EMAIL", "EMAIL_ADDRESS", "email_address"),
        CommonField("C_ADDR_CALCULATED", "E_ADDR_CALCULATED", "R_ADDR_CALCULATED"),
        CommonField("C_HOME_PHONE", "HOME_PHONE", "phone_number"),
        CommonField("C_WORK_PHONE", "WORK_PHONE", "phone_number"),
        CommonField("C_MOBILE_PHONE", "Mobile_Phone", "phone_number"),
    ]

    FORMAT: str = "%-20s %-40s %-40s"

    #   These fields are used for computing the match score.
    SCORE_FIELDS: list = [
        "C_ADDR_CALCULATED",
        "C_DOB",
        "C_EMAIL",
        "C_MRN_CALCULATED",
        "C_NAME_CALCULATED",
        "C_PHONE_CALCULATED",
    ]

    #   If ALL these fields match, we'll assign a bonus score.
    #   (Even though three matches would ordinarily receive a score of three,
    #    these fields are so valuable that we'll assign a bonus so
    #    the records will automatically be matched.
    BONUS_SCORE_FIELDS: list = [
        "C_ADDR_CALCULATED",
        "C_DOB",
        "C_NAME_CALCULATED",
    ]

    def __init__(
        self, row: pandas.Series, facility_addresses: list, facility_phone_numbers: list
    ):
        """Create MatchRecord object.

        Parameters
        ----------
        row : pandas.Series             One database row listing both Epic and REDCap values for (perhaps) the same patient.
        facility_addresses : list       Addresses that don't score as a match even if they do match.
        facility_phone_numbers : list   Phone numbers that don't score as a match even if they do match.
        """
        if not isinstance(row, pandas.Series):
            raise TypeError("Argument 'row' is not the expected pandas.Series.")

        if not isinstance(facility_addresses, list):
            facility_addresses = []

        if not isinstance(facility_phone_numbers, list):
            facility_phone_numbers = []

        self.__alias: str
        self.__mrn_hx: str
        self.__pat_id: str
        self.__record: dict = {}
        self.__redcap_update: REDCapUpdate = REDCapUpdate()
        self.__score: int
        self.__study_id: str

        self.__build_dictionary(row, facility_addresses, facility_phone_numbers)
        self.__score_record()

    # Helper...  strip everything but alphanumerics from a string
    @staticmethod
    def as_alphanum(string: str) -> str:
        _filter = filter(str.isalnum, string)
        _string = "".join(_filter)
        return _string

    def __build_dictionary(
        self, row: pandas.Series, facility_addresses: list, facility_phone_numbers: list
    ) -> None:
        """Builds the self.__record dict of MatchVariables describing the match between the Epic and REDCap values.

        Parameters
        ----------
        row : pandas.Series             Extracted from the database epic and redcap tables.
        facility_addresses : list       Addresses that don't score as a match even if they do match.
        facility_phone_numbers : list   Phone numbers that don't score as a match even if they do match.
        """
        if not isinstance(row, pandas.Series):
            raise TypeError("Argument 'row' is not the expected pandas.Series.")

        #   Only expect these merge fields to appear in ONE system:
        #   First, REDCap study_id ...
        if "study_id" in row:
            self.__study_id = str(row["study_id"])

        #   ...Second, Epic ALIAS, MRN_HX and PAT_ID
        if "ALIAS" in row:
            self.__alias = str(row["ALIAS"])

        if "MRN_HX" in row:
            self.__mrn_hx = str(row["MRN_HX"])

        if "PAT_ID" in row:
            self.__pat_id = str(row["PAT_ID"])

        #   Now all the fields present in both systems.
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

            ignore_list = []

            if common_name == "C_ADDR_CALCULATED":
                ignore_list = facility_addresses

            self.__record[common_name] = MatchVariable(
                epic_value=epic_value,
                redcap_value=redcap_value,
                ignore_list=ignore_list,
            )

        # Match phone numbers (Epic has several), names (including aliases) and MRNs (including old ones).
        self.__select_best_phone(row, facility_phone_numbers=facility_phone_numbers)
        self.__select_best_epic_name(row)
        self.__select_best_epic_mrn(row)

    def __epic_mrn(self) -> str:
        """Simplifies getting Epic Medical Record Number.

        Returns
        -------
        epic_mrn : str
        """
        mrn_match: MatchVariable = self.__record["C_MRN"]
        epic_mrn: str = mrn_match.epic_value().strip()
        return epic_mrn

    def __init_summary(self) -> str:
        """Initializes the 'summary' block describing the match between Epic and REDCap records.

        Returns
        -------
        summary : str
        """
        format_spec: str = MatchRecord.FORMAT + "%s\n"
        summary: str = ""
        summary += "-------------\n"
        summary += "Study ID: " + str(self.study_id()) + "\n"
        summary += "PAT_ID: " + self.pat_id() + "\n"
        summary += "Aliases: " + self.__alias + "\n"
        summary += "Other MRNs: " + self.__mrn_hx + "\n"

        summary += format_spec % (
            "Common Name",
            "Epic Value",
            "RedCap Value",
            "Match Quality",
        )
        return summary

    def is_match(
        self, exact: bool = False, criteria: int = 5, aliases=None, mrn_hx=None
    ) -> MatchTuple:
        """See if a universal record is a match between its Epic fields and REDCap fields.

        Parameters
        ----------
        exact : bool    Do we only call a match if score EQUALS the criterion? Or >=?
        criteria : int  Threshold for deciding it's a match.

        Returns
        -------
        MatchTuple containing a bool (match/no match) & a str summary
        """
        if aliases is None:
            aliases = []

        summary: str = self.__init_summary()

        for key_fieldname in MatchRecord.SCORE_FIELDS:
            this_record: MatchVariable = self.__record[key_fieldname]
            summary += this_record.summarize_match(common_name=key_fieldname) + "\n"

        summary += "-------------\n"
        good_match: bool = self.__score >= criteria

        if exact:
            good_match = self.__score == criteria

        return MatchTuple(bool=good_match, summary=summary)

    def pat_id(self) -> str:
        """Allows external code to ask for the Epic PAT_ID of this object.

        Returns
        -------
        pat_id : str
        """
        return self.__pat_id

    def __redcap_mrn(self) -> str:
        """Simplifies getting REDCap Medical Record Number.

        Returns
        -------
        redcap_mrn : str
        """
        mrn_match: MatchVariable = self.__record["C_MRN"]
        redcap_mrn: str = mrn_match.redcap_value().strip()
        return redcap_mrn

    def __redcap_name(self) -> tuple:
        """Simplifies getting REDCap first, last name.

        Returns
        -------
        names : tuple (first, last)
        """
        first_name_match: MatchVariable = self.__record["C_FIRST"]
        redcap_first_name: str = first_name_match.redcap_value().strip()
        last_name_match: MatchVariable = self.__record["C_LAST"]
        redcap_last_name: str = last_name_match.redcap_value().strip()
        return redcap_first_name, redcap_last_name

    def redcap_update(self) -> REDCapUpdate:
        """Allows external code to get the REDCapUpdate object,
        describing if--and how--REDCap record should be updated.

        Returns
        -------
        update : REDCapUpdate
        """
        return self.__redcap_update

    def score(self) -> int:
        """Returns the match score.

        Returns
        -------
        score : int
        """
        return self.__score

    # Scores a record and assigns a matching result
    def __score_record(self) -> None:
        """Based on the matches in each field, assign a numeric score."""

        self.__score = 0

        # Count up the fields that match.
        # Common fields are defined at the beginning of this class.  This chunk of code
        # also scores things that are handled explicitly elsewhere, such as phone, date of birth, etc.
        for common_name in MatchRecord.SCORE_FIELDS:
            this_record = self.__record[common_name]

            if this_record.good_enough():
                self.__score += 1

        # If score > 3, no need to also test for bonus fields.
        if self.__score > 3:
            return

        all_bonus_fields_match: bool = True

        # Do all the BONUS fields match?
        for common_name in MatchRecord.BONUS_SCORE_FIELDS:
            this_record = self.__record[common_name]

            if not this_record.good_enough():
                all_bonus_fields_match = False
                break

        if all_bonus_fields_match:
            self.__score = 4

    def __select_best_phone(
        self, row: pandas.Series, facility_phone_numbers: list
    ) -> None:
        """Try each Epic phone number against the REDCap phone number
        and use whichever matches (if any).

        Parameters
        ----------
        row : pandas.Series             Extracted from the database epic and redcap tables.
        facility_phone_numbers : list   Phone numbers that don't score as a match even if they do match.
        """
        epic_home_phone: str = ""
        epic_work_phone: str = ""
        epic_mobile_phone: str = ""
        redcap_phone: str = ""

        if "HOME_PHONE" in row:
            epic_home_phone = str(clean_up_phone(row["HOME_PHONE"]))

        if "Mobile_Phone" in row:
            epic_mobile_phone = str(clean_up_phone(row["Mobile_Phone"]))

        if "WORK_PHONE" in row:
            epic_work_phone = str(clean_up_phone(row["WORK_PHONE"]))

        if "phone_number" in row:
            redcap_phone = str(clean_up_phone(row["phone_number"]))

        #   Use the same formatting for the facility phone numbers.
        if facility_phone_numbers:
            facility_phone_numbers = list(map(clean_up_phone, facility_phone_numbers))

        match_variable = MatchVariable(
            epic_value=epic_home_phone,
            redcap_value=redcap_phone,
            ignore_list=facility_phone_numbers,
        )

        #   If phone number is from a group facility, no need to search further.
        if not match_variable.ignored():
            if not match_variable.good_enough():
                match_variable = MatchVariable(
                    epic_value=epic_work_phone,
                    redcap_value=redcap_phone,
                    ignore_list=facility_phone_numbers,
                )

            #   If phone number is from a group facility, no need to search further.
            if not match_variable.ignored():
                if not match_variable.good_enough():
                    match_variable = MatchVariable(
                        epic_value=epic_mobile_phone,
                        redcap_value=redcap_phone,
                        ignore_list=facility_phone_numbers,
                    )

        self.__record["C_PHONE_CALCULATED"] = match_variable

    def __select_best_epic_name(self, row: pandas.Series) -> None:
        """Try both Epic name & alias name against the REDCap name
        and use whichever matches (if any).

        Parameters
        ----------
        row : pandas.Series             Extracted from the database epic and redcap tables.
        """
        epic_name: str = ""
        epic_alias: str = ""
        redcap_name: str = ""

        if "ALIAS" in row:
            epic_alias = row["ALIAS"]

        if "PAT_FIRST_NAME" in row and "PAT_LAST_NAME" in row:
            epic_name = row["PAT_LAST_NAME"] + "," + row["PAT_FIRST_NAME"]

        if "first_name" in row and "last_name" in row:
            redcap_name = row["last_name"] + "," + row["first_name"]

        match_variable = MatchVariable(epic_value=epic_name, redcap_value=redcap_name)

        # Don't bother making this comparison if there IS no alias.
        if isinstance(epic_alias, str) and len(epic_alias) > 0:
            if not match_variable.good_enough():
                match_variable = MatchVariable(
                    epic_value=epic_alias, redcap_value=redcap_name
                )

        self.__record["C_NAME_CALCULATED"] = match_variable

    def __select_best_epic_mrn(self, row: pandas.Series) -> None:
        """Try both Epic MRN & historical MRNs against the REDCap MRN
        and use whichever matches (if any).

        Parameters
        ----------
        row : pandas.Series             Extracted from the database epic and redcap tables.
        """
        epic_mrn: str = ""
        epic_mrn_historical: str = ""
        redcap_mrn: str = ""

        if "MRN" in row:
            epic_mrn = str(row["MRN"])

        if "MRN_HX" in row:
            epic_mrn_historical = str(row["MRN_HX"])

        if "mrn" in row:
            redcap_mrn = str(row["mrn"])

        match_variable = MatchVariable(epic_value=epic_mrn, redcap_value=redcap_mrn)

        #   Don't bother if historical MRN is None.
        if isinstance(epic_mrn_historical, str) and len(epic_mrn_historical) > 0:
            if not match_variable.good_enough():
                match_variable = MatchVariable(
                    epic_value=epic_mrn_historical, redcap_value=redcap_mrn
                )

        self.__record["C_MRN_CALCULATED"] = match_variable

    def study_id(self) -> int:
        """Retrieve the REDCap study id.

        Returns
        -------
        study_id : int
        """
        return int(self.__study_id)


class MatchVariable:
    """
    Holds the comparison between REDCap and Epic for one variable.
    """

    def __init__(
        self,
        epic_value: str,
        redcap_value: str,
        ignore_list=None,
    ):
        """Creates the MatchVariable object.

        Parameters
        ----------
        epic_value : str
        redcap_value : str
        ignore_list : list  What values (like address of a group facility)
                            should be ignored even if they match?
        """
        if not isinstance(epic_value, str):
            raise TypeError("Argument 'epic_value' is not a string.")

        self.__epic_value: str = epic_value.strip()

        if not isinstance(redcap_value, str):
            raise TypeError("Argument 'redcap_value' is not a string.")

        self.__redcap_value: str = redcap_value.strip()

        if not ignore_list:
            ignore_list = []

        self.__match_quality: MatchQuality
        self.__evaluate(ignore_list)

    def epic_value(self) -> str:
        return self.__epic_value

    # see if two strings are similar
    def __evaluate(self, ignore_list: list) -> None:
        self.__match_quality = MatchQuality.MATCHED_NOPE

        if self.__epic_value == "" and self.__redcap_value == "":
            self.__match_quality = MatchQuality.MATCHED_NULL
        elif self.__epic_value in ignore_list or self.__redcap_value in ignore_list:
            self.__match_quality = MatchQuality.IGNORED
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
        """Lets external code drill down to the MatchQuality object inside.

        Returns
        -------
        good_enough : bool
        """
        return self.__match_quality.good_enough()

    def ignored(self) -> bool:
        """Lets external code drill down to the MatchQuality object inside.

        Returns
        -------
        ignored : bool
        """
        return self.__match_quality.ignored()

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
