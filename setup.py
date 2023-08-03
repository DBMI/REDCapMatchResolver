"""
Defines packaging information.
"""
from setuptools import find_packages, setup

setup(
    name="REDCapMatchResolver",
    version="1.1.7",
    packages=find_packages(),
    package_dir={"src": "src"},
    include_package_data=True,
    package_data={'': ['data/*.xlsx']},
    url="https://github.com/DBMI/REDCapMatchResolver",
    license="",
    author="Kevin J. Delaney",
    author_email="kjdelaney@ucsd.edu",
    description="Assists with human expert review of possible patient matches.",
)
