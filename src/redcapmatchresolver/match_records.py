"""
Module: contains the MatchRecord and MatchVariable classes.
"""
from collections import namedtuple

import pandas  # type: ignore[import]
from redcapduplicatedetector.match_quality import MatchQuality
from redcaputilities.string_cleanup import clean_up_phone
from redcap_update import REDCapUpdate

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

    # A note on phone matching. Epic has THREE phone numbers (home, work and mobile) but REDCap has only one.
    # We'll try to match all but expect only one to match. By keeping the score threshold the same,
    # we'll still get the same score as when we pre-filtered the phone numbers to match.
    COMMON_FIELDS: list = [
        CommonField("C_MRN", "MRN", "mrn"),
        CommonField("C_FIRST", "PAT_FIRST_NAME", "first_name"),
        CommonField("C_LAST", "PAT_LAST_NAME", "last_name"),
        CommonField("C_DOB", "BIRTH_DATE", "dob"),
        CommonField("C_EMAIL", "EMAIL_ADDRESS", "email_address"),
        CommonField("C_ADDR_CALCULATED", "E_ADDR_CALCULATED", "R_ADDR_CALCULATED"),
        CommonField("C_HOME_PHONE", "HOME_PHONE", "phone_number"),
        CommonField("C_WORK_PHONE", "WORK_PHONE", "phone_number"),
        CommonField("C_MOBILE_PHONE", "Mobil_Phone", "phone_number"),
    ]

    FORMAT: str = "%-20s %-40s %-40s"

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
        self.__redcap_update: REDCapUpdate = REDCapUpdate()

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
        """Builds the self.__record dict of MatchVariables describing the match between the Epic and REDCap values.

        Parameters
        ----------
        row : pandas.Series extracted from the database epic and redcap tables.
        """
        if not isinstance(row, pandas.Series):
            raise TypeError("Argument 'row' is not the expected pandas.Series.")

        #   Only expect these merge fields to appear in ONE system:
        #   First, REDCap study_id ...
        if "study_id" in row:
            self.__record["study_id"] = MatchVariable(
                epic_value="", redcap_value=str(row["study_id"])
            )

        #   ...Second, Epic PAT_ID.
        if "PAT_ID" in row:
            self.__record["PAT_ID"] = MatchVariable(
                epic_value=str(row["PAT_ID"]), redcap_value=""
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

        # Match phone numbers.
        self.__select_best_phone(row)

    def __epic_name(self) -> tuple:
        """Simplifies getting Epic first, last name.

        Returns
        -------
        names : tuple (first, last)
        """
        first_name_match: MatchVariable = self.__record["C_FIRST"]
        epic_first_name: str = first_name_match.epic_value().strip()
        last_name_match: MatchVariable = self.__record["C_LAST"]
        epic_last_name: str = last_name_match.epic_value().strip()
        return epic_first_name, epic_last_name

    def __init_summary(self, aliases: list = []) -> str:
        """Initializes the 'summary' block describing the match between Epic and REDCap records.

        Parameters
        ----------
        aliases : list Other names for this patient.

        Returns
        -------
        summary : str
        """
        format_spec: str = MatchRecord.FORMAT + "%s\n"
        summary: str = ""
        summary += "-------------\n"
        summary += "Study ID: " + str(self.study_id()) + "\n"
        summary += "PAT_ID: " + self.pat_id() + "\n"

        if aliases:
            summary += "Aliases: " + "; ".join(aliases) + "\n"

        summary += format_spec % (
            "Common Name",
            "Epic Value",
            "RedCap Value",
            "Match Quality",
        )
        return summary

    def is_match(
        self, exact: bool = False, criteria: int = 4, aliases: list = []
    ) -> MatchTuple:
        """See if a universal record is a match between its Epic fields and REDCap fields.

        Parameters
        ----------
        exact : bool  Do we only call a match if score EQUALS the criterion? Or >=?
        criteria : int Threshold for deciding it's a match.
        aliases : list Other names for this patient.

        Returns
        -------
        MatchTuple containing a bool (match/no match) & a str summary
        """
        summary: str = self.__init_summary(aliases=aliases)

        for key_fieldname in MatchRecord.SCORE_FIELDS:
            this_record = self.__record[key_fieldname]
            summary += this_record.summarize_match(common_name=key_fieldname) + "\n"

        summary += "-------------\n"
        good_match: bool = self.__score >= criteria

        if exact:
            good_match = self.__score == criteria

        return MatchTuple(bool=good_match, summary=summary)

    def mrns_match(self) -> bool:
        """Allows external code to ask if the Epic & REDCap Medical Record Numbers match.

        Returns
        -------
        match : bool
        """
        mrn_match: MatchVariable = self.__record["C_MRN"]
        return mrn_match.good_enough()

    def names_match(self) -> bool:
        """Allows external code to ask if the Epic & REDCap names match.

        Returns
        -------
        match : bool
        """
        first_name_match: MatchVariable = self.__record["C_FIRST"]
        last_name_match: MatchVariable = self.__record["C_LAST"]
        return first_name_match.good_enough() & last_name_match.good_enough()

    def pat_id(self) -> str:
        """Allows external code to ask for the Epic PAT_ID of this object.

        Returns
        -------
        pat_id : str
        """
        if "PAT_ID" in self.__record:
            pat_id_mv: MatchVariable = self.__record["PAT_ID"]
            return pat_id_mv.epic_value()

        return ""

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

        # Match all the common fields of a universal record.
        # Common fields are defined at the beginning of this class.  This chunk of code
        # also scores things that are handled explicitly elsewhere, such as phone, date of birth, etc.
        for common_name in MatchRecord.SCORE_FIELDS:
            this_record = self.__record[common_name]

            if this_record.good_enough():
                self.__score += 1

    def __select_best_phone(self, row: pandas.Series) -> None:
        """Try each Epic phone number against the REDCap phone number
        and use whichever matches (if any).

        Parameters
        ----------
        row : pandas.Series extracted from the database epic and redcap tables.
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

        match_variable = MatchVariable(
            epic_value=epic_home_phone, redcap_value=redcap_phone
        )

        if not match_variable.good_enough():
            match_variable = MatchVariable(
                epic_value=epic_work_phone, redcap_value=redcap_phone
            )

        if not match_variable.good_enough():
            match_variable = MatchVariable(
                epic_value=epic_mobile_phone, redcap_value=redcap_phone
            )

        self.__record["C_PHONE_CALCULATED"] = match_variable

    def study_id(self) -> int:
        """Retrieve the REDCap study id.

        Returns
        -------
        study_id : int
        """
        return int(self.__record["study_id"].redcap_value())

    def use_aliases(self, aliases: list) -> None:
        """Allows us to reconsider the match given patient aliases from Epic.

        Parameters
        ----------
        aliases : list  example: ['Smyth,Alan', 'Smith,Alice']
        """
        if not isinstance(aliases, list):
            raise TypeError('Argument "aliases" is not the expected list.')

        redcap_first_name, redcap_last_name = self.__redcap_name()
        assembled_name: str = redcap_last_name + "," + redcap_first_name

        #   Try to match each alias in list.
        for alias in aliases:
            #   If Epic alias matches the REDCap name,
            #   alert external code to update REDCap to use the Epic name
            #   (since we assume the Epic name is most current)
            #   and increment score-we're FORCING the names to match.
            if assembled_name == alias:
                epic_first_name, epic_last_name = self.__epic_name()
                self.__redcap_update.set('first_name', epic_first_name)
                self.__redcap_update.set('last_name', epic_last_name)

                #   By how much should we increment the score?
                if redcap_first_name != epic_first_name:
                    self.__score += 1   # First names now match.

                if redcap_last_name != epic_last_name:
                    self.__score += 1   # Last names now match.

                #   No need to consider further aliases in list.
                return


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
