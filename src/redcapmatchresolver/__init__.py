"""
REDCap Match Resolver

This application assists with human expert review of possible patient matches.
When software identifies a pair of patient records that >might< refer to the
same patient, the REDCap Report Writer class writes human-readable,
machine-parseable reports showing potential patient matches that need review by human.
Once the reviewer has reviewed the patient info and have marked up the reports
 with their decisions, the REDCapReportReader class
reads/parses the marked-up reports, producing a pandas DataFrame output.

Classes:
    CommonField
    MatchRecord
    MatchTuple
    MatchVariable
    REDCap Appointment
    REDCap Match Resolver
    REDCap Patient
    REDCap Report Reader
    REDCap Report Writer
"""
from .match_records import CommonField, MatchRecord, MatchTuple, MatchVariable
from .redcap_appointment import REDCapAppointment
from .redcap_clinic import REDCapClinic
from .redcap_match_resolver import REDCapMatchResolver
from .redcap_patient import REDCapPatient
from .redcap_report_reader import REDCapReportReader
from .redcap_report_writer import REDCapReportWriter
