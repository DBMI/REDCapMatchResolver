"""
Defines packaging information.
"""
from setuptools import setup

setup(
    name="REDCapMatchResolver",
    version="0.2.5",
    packages=["redcapmatchresolver"],
    package_dir={"": "src"},
    url="https://github.com/DBMI/REDCapMatchResolver",
    license="",
    author="Kevin J. Delaney",
    author_email="kjdelaney@ucsd.edu",
    description="Assists with human expert review of possible patient matches.",
)
