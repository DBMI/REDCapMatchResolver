"""
Module: contains the REDCapUpdate class.
"""

from typing import Union

import pandas  # type: ignore[import]


class REDCapUpdate:
    """
    Describes if--and how--REDCap needs to be updated for a given patient.
    """

    def __init__(self):
        self.__first_name: str = ""
        self.__last_name: str = ""
        self.__study_id: int = 0
        self.__update_needed: bool = False

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

            if self.__study_id > 0:
                update_package["study_id"] = self.__study_id

        return update_package

    def set(self, property: str, value: Union[int, str]) -> None:
        """Allows other classes to set update properties.

        Parameters
        ----------
        property : str
        value : str

        """
        if not isinstance(property, str):
            raise TypeError('Argument "property" is not the expected str.')

        if property == "first_name":
            self.__update_needed = True

            if not isinstance(value, str):
                raise TypeError('Argument "value" is not the expected str.')

            self.__first_name = value
            return

        if property == "last_name":
            self.__update_needed = True

            if not isinstance(value, str):
                raise TypeError('Argument "value" is not the expected str.')

            self.__last_name = value
            return

        if property == "study_id":
            self.__update_needed = True

            if not isinstance(value, int):
                raise TypeError('Argument "value" is not the expected int.')

            self.__study_id = value
            return

        raise KeyError(f'Property "{property}" is unexpected.')

    def to_query(self) -> str:
        """Builds 'column = value' strings from update package.

        Returns
        -------
        update_text : str
        """
        package: dict = self.package()
        update_text = []

        for property_name in list(package.keys()):
            property_value = package[property_name]
            update_text.append(property_name + " = " + str(property_value))

        return "\n".join(update_text)
