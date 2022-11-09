"""
REDCap Match Resolver

This application assists with human expert review of possible patient matches.
When software identifies a pair of patient records that >might< refer to the
same patient, the REDCap Report Writer class writes human-readable,
machine-parseable reports showing potential patient matches that need review by
a Clinical Research Coordinator (CRC). Once the CRC has reviewed the patient info
and have marked up the reports with their decisions, the REDCapReportReader class
reads/parses the marked-up reports, producing a pandas DataFrame output.

Classes:
    REDCap Report Reader
    REDCap Report Writer
"""
from .redcap_report_reader import REDCapReportReader
from .redcap_report_writer import REDCapReportWriter
from .utilities import Utilities
