"""
Module: contains the REDCapUpdate class.
"""

import pandas  # type: ignore[import]


class REDCapUpdate:
    """
    Describes whether (and--if so--how) REDCap needs to be updated for a given patient.
    """

    def __init__(self, study_id: int):
        self.__update_needed: bool = False

        if not isinstance(study_id, int):
            raise TypeError('Argument "study_id" is not the expected int.')

        self.__study_id: int = study_id
        self.__first_name: str = ""
        self.__last_name: str = ""

    def needed(self) -> bool:
        """Allows external code to ask if an update is needed at all.

        Returns
        -------
        needed : bool
        """
        return self.__update_needed

    def package(self) -> dict:
        """Provides just the properties that need to be changed.

        Returns
        -------
        package : dict
        """
        update_package: dict = {}

        if self.__update_needed:
            if self.__first_name:
                update_package["first_name"] = self.__first_name

            if self.__last_name:
                update_package["last_name"] = self.__last_name

        return update_package

    def set(self, property: str, value: str) -> None:
        """Allows other classes to set update properties.

        Parameters
        ----------
        property : str
        value : str

        """
        if not isinstance(property, str):
            raise TypeError('Argument "property" is not the expected str.')

        if not isinstance(value, str):
            raise TypeError('Argument "value" is not the expected str.')

        if property == "first_name":
            self.__update_needed = True
            self.__first_name = value
            return

        if property == "last_name":
            self.__update_needed = True
            self.__last_name = value
            return

        raise KeyError(f'Property "{property}" is unexpected.')
