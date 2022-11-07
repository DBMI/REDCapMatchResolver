# REDCapReportWriter ![image info](./pictures/report_logo.png) 

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
![Pylint](./.github/badges/pylint-badge.svg?dummy=8484744)
![Coverage Status](./.github/badges/coverage-badge.svg?dummy=8484744)
![Last Commit Date](./.github/badges/last-commit-badge.svg?dummy=8484744)

---

**Documentation**: [https://github.com/DBMI/REDCapReportWriter](https://github.com/DBMI/REDCapReportWriter)

**Source Code**: [https://github.com/DBMI/REDCapReportWriter](https://github.com/DBMI/REDCapReportWriter)

---

Produces a nicely-formatted text-only report suitable for email listing which patient matches need to be checked by the Clinical Research Coordinators (CRCs).

## Installation

```sh
pip install git+https://github.com/DBMI/REDCapReportWriter.git
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

Trigger the [Draft release workflow](https://github.com/DBMI/REDCapReportWriter/actions/workflows/draft_release.yml)
(press _Run workflow_). This will update the changelog & version and create a GitHub release which is in _Draft_ state.

Find the draft release from the
[GitHub releases](https://github.com/DBMI/REDCapReportWriter/releases) and publish it. When
 a release is published, it'll trigger [release](https://github.com/DBMI/REDCapReportWriter/blob/master/.github/workflows/release.yml) workflow which creates PyPI
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
