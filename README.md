# REDCapMatchResolver ![image info](./pictures/report_logo.png) 

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
![Pylint](./.github/badges/pylint-badge.svg?dummy=8484744)
![Coverage Status](./.github/badges/coverage-badge.svg?dummy=8484744)
![Last Commit Date](./.github/badges/last-commit-badge.svg?dummy=8484744)

---

**Documentation**: [https://github.com/DBMI/REDCapMatchResolver](https://github.com/DBMI/REDCapMatchResolver)

**Source Code**: [https://github.com/DBMI/REDCapMatchResolver](https://github.com/DBMI/REDCapMatchResolver)

---
## Purpose
1. **Resolve patient matches**
Assists with human expert review of possible patient matches.
When software identifies a pair of patient records (one REDCap and one Epic) that *might* refer to the
same patient, the `REDCapReportWriter` class writes human-readable,
machine-parseable reports showing potential patient matches that need review by
a Clinical Research Coordinator (CRC). Once the CRC has reviewed the patient info
and have marked up the reports with their decisions, the `REDCapReportReader` class
reads/parses the marked-up reports, producing a pandas DataFrame output.
Finally, the `REDCapMatchResolver` class reads all the reviewed reports into a temporary database.
Its `lookup_potential_match` method allows external software to submit a block of text showing the patient information from both REDCap and Epic & see if CRCs have already made a decision whether these records are a match.
2. **Select best appointment**
When producing `.csv` files used to update REDCap, we may have patients with multiple upcoming appointments. 
We'd like to select each patient's "best" appointment for inclusion into REDCap, based on clinic location and appointment date.
The calling function (like [refresh_redcap_upcoming_appointments](https://github.com/DBMI/AoU_v2/blob/main/redcap/refresh_redcap_upcoming_appointments.py))
should instantiate a `REDCapClinic` object, which reads the Excel spreadsheet the CRCs have developed to assign a priority value
to each clinic. This `REDCapClinic` object is then provided each time a `REDCapPatient` class object is created, so that
the patient's `REDCapAppointment` objects contain not only clinic location, date and time, but a priority value as well. 
Then, when `refresh_redcap_upcoming_appointments` writes out the REDCap update `.csv` files, it calls
the `REDCapPatient` method `csv`, which in turn calls `best_appointment` to select the `REDCapAppointment` with the highest clinic priority.
In case there are more than one appointment at that clinic, `best_appointment` selects the earliest appointment at that clinic.

## Installation

```sh
pip install git+https://github.com/DBMI/REDCapMatchResolver.git
```

## Development

* Clone this repository
* Requirements:
  * [Poetry](https://python-poetry.org/)
  * Python 3.7+
* Create a virtual environment and install the dependencies

```sh
poetry install
```

* Activate the virtual environment

```sh
poetry shell
```

### Testing

```sh
pytest
```

### Documentation

The documentation is automatically generated from the content of the [docs directory](./docs) and from the docstrings
 of the public signatures of the source code. The documentation is updated and published as a [Github project page
 ](https://pages.github.com/) automatically as part each release.

### Releasing

Trigger the [Draft release workflow](https://github.com/DBMI/REDCapMatchResolver/actions/workflows/draft_release.yml)
(press _Run workflow_). This will update the changelog & version and create a GitHub release which is in _Draft_ state.

Find the draft release from the
[GitHub releases](https://github.com/DBMI/REDCapMatchResolver/releases) and publish it. When
 a release is published, it'll trigger [release](https://github.com/DBMI/REDCapMatchResolver/blob/master/.github/workflows/release.yml) workflow which creates PyPI
 release and deploys updated documentation.

### Pre-commit

Pre-commit hooks run all the auto-formatters (e.g. `black`, `isort`), linters (e.g. `mypy`, `flake8`), and other quality
 checks to make sure the changeset is in good shape before a commit/push happens.

You can install the hooks with (runs for each commit):

```sh
pre-commit install
```

Or if you want them to run only for each push:

```sh
pre-commit install -t pre-push
```

Or if you want e.g. want to run all checks manually for all files:

```sh
pre-commit run --all-files
```

---

This project was generated using the [python-package-cookiecutter](https://github.com/DBMI/python-package-cookiecutter) template, modeled on the [wolt-python-package-cookiecutter](https://github.com/woltapp/wolt-python-package-cookiecutter) template.
