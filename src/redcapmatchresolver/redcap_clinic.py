"""
Module: contains class REDCapClinic
used to prioritize appointments according to
clinic location.
"""
import os.path
import pandas
import importlib_resources as pkg_resources


class REDCapClinic:  # pylint: disable=too-few-public-methods
    """
    Builds a dictionary from an Excel file listing all the clinics and their priority.
    """

    def __init__(self) -> None:
        #   Read Excel file. https://stackoverflow.com/a/67122465/20241849
        with pkg_resources.path(
            "redcapmatchresolver.data", "Epic DEP with future appts - 04192022 .xlsx"
        ) as excel_filename:  # pragma: no cover
            if not os.path.exists(excel_filename):
                raise FileNotFoundError(f"Unable to find {excel_filename}.")

            clinic_specs = pandas.read_excel(excel_filename)

            if clinic_specs is None or not isinstance(
                clinic_specs, pandas.DataFrame
            ):  # pragma: no cover
                raise OSError(f"Unable to read {excel_filename}.")

            self.__members = {}
            all_department_names = clinic_specs["department_name"]

            #   Create members.
            for dept_name in all_department_names:
                this_clinic = clinic_specs.loc[
                    clinic_specs["department_name"] == dept_name
                ]
                this_clinic_priority = int(this_clinic["Priority #"])
                self.__members[dept_name.upper()] = this_clinic_priority

    def priority(self, dept_name: str) -> int:
        """Lets external code ask what priority value has been assigned to this clinic/department.

        Parameters
        ----------
        dept_name : str

        Returns
        -------
        priority : int
        """

        if dept_name and dept_name.upper() in self.__members:
            return self.__members[dept_name.upper()]

        return 9999


if __name__ == "__main__":
    pass
