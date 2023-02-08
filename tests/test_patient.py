"""
Module test_patient.py, which performs automated
testing of the REDCapPatient class.
"""
from datetime import datetime
from dateutil.parser import ParserError

import pytest

from redcapmatchresolver.redcap_appointment import REDCapAppointment
from redcapmatchresolver.redcap_clinic import REDCapClinic
from redcapmatchresolver.redcap_patient import REDCapPatient


@pytest.fixture(name="clinics")
def fixture_clinics() -> REDCapClinic:
    return REDCapClinic()


def test_appointment_corner_cases(
    appointment_headers, appointment_record_slashes, appointment_datetime
):
    #   Make it look up clinics by itself.
    appointment_obj = REDCapAppointment(
        appointment_headers=appointment_headers,
        appointment_info=appointment_record_slashes,
    )
    assert isinstance(appointment_obj, REDCapAppointment)
    assert appointment_obj.date() == appointment_datetime


def test_appointment_errors(
    appointment_headers,
    appointment_record,
    appointment_record_partial,
    appointment_record_malformed,
    clinics,
):
    with pytest.raises(TypeError):
        REDCapAppointment(
            appointment_headers=None,
            appointment_info=appointment_record,
            clinics=clinics,
        )

    with pytest.raises(TypeError):
        REDCapAppointment(
            appointment_headers=1979,
            appointment_info=appointment_record,
            clinics=clinics,
        )

    with pytest.raises(TypeError):
        REDCapAppointment(
            appointment_headers=appointment_headers,
            appointment_info=None,
            clinics=clinics,
        )

    with pytest.raises(TypeError):
        REDCapAppointment(
            appointment_headers=appointment_headers,
            appointment_info=1979,
            clinics=clinics,
        )

    appointment_headers_modified = appointment_headers.copy()
    appointment_headers_modified[0] = 1979

    with pytest.raises(TypeError):
        REDCapAppointment(
            appointment_headers=appointment_headers_modified,
            appointment_info=appointment_record,
            clinics=clinics,
        )

    with pytest.raises(TypeError):
        #   Remove last item from appointment_record, to cause length mismatch error.
        REDCapAppointment(
            appointment_headers=appointment_headers,
            appointment_info=appointment_record[:-1],
            clinics=clinics,
        )

    with pytest.raises(ParserError):
        REDCapAppointment(
            appointment_headers=appointment_headers,
            appointment_info=appointment_record_partial,
            clinics=clinics,
        )

    with pytest.raises(ParserError):
        REDCapAppointment(
            appointment_headers=appointment_headers,
            appointment_info=appointment_record_malformed,
            clinics=clinics,
        )


def test_appointment_instantiation(
    appointment_headers, appointment_record, appointment_datetime, clinics
):
    appointment_obj = REDCapAppointment(
        appointment_headers=appointment_headers,
        appointment_info=appointment_record,
        clinics=clinics,
    )
    assert isinstance(appointment_obj, REDCapAppointment)

    #   Can we parse the date/time from the REDCapAppointment object?
    extracted_datetime = appointment_obj.date()
    assert isinstance(extracted_datetime, datetime)
    assert extracted_datetime == appointment_datetime

    #   Test .csv output.
    csv_summary = appointment_obj.csv()
    assert isinstance(csv_summary, str)

    #   Ask for clinic, date, time.
    value = appointment_obj.value("appointment_clinic")
    assert isinstance(value, str) and value == "LWC CARDIOLOGY"

    value = appointment_obj.value("appointment_date")
    assert isinstance(value, str) and value == "2022-12-01"

    value = appointment_obj.value("appointment_time")
    assert isinstance(value, str) and value == "10:40:00"

    value = appointment_obj.value("not_valid_name")
    assert isinstance(value, str) and len(value) == 0

    value = appointment_obj.value(1979)
    assert isinstance(value, str) and len(value) == 0

    #   Ask for appointment priority.
    priority = appointment_obj.priority()
    assert isinstance(priority, int) and priority == 14


def test_patient_appointments(
    patient_headers, patient_record_1, patient_record_2, patient_record_5, clinics
):
    #   Patient with NO appointments.
    patient_record_no_appointments_list = list(patient_record_1)
    patient_record_no_appointments_list = patient_record_no_appointments_list[
        : len(patient_record_no_appointments_list) - 2
    ]
    patient_with_no_appointments = REDCapPatient(
        headers=patient_headers,
        row=tuple(patient_record_no_appointments_list),
        clinics=clinics,
    )
    assert isinstance(patient_with_no_appointments, REDCapPatient)
    appointments = patient_with_no_appointments.appointments()
    assert isinstance(appointments, list)
    assert len(appointments) == 0
    best_appointment = patient_with_no_appointments.best_appointment()
    assert best_appointment is None

    patient_obj_1 = REDCapPatient(
        headers=patient_headers, row=patient_record_1, clinics=clinics
    )
    assert isinstance(patient_obj_1, REDCapPatient)

    #   Only one appointment, but can still ask for the "best".
    best_appointment = patient_obj_1.best_appointment()
    assert isinstance(best_appointment, REDCapAppointment)

    #   Same patient, different appointments.
    patient_obj_2 = REDCapPatient(
        headers=patient_headers, row=patient_record_2, clinics=clinics
    )
    assert isinstance(patient_obj_2, REDCapPatient)

    patient_obj_1.merge(patient_obj_2)
    assert isinstance(patient_obj_1, REDCapPatient)
    assert len(patient_obj_1.appointments()) == 2

    #   Two appointments at different clinics--ask for the "best".
    #   In this case, best will be determined by clinic location.
    best_appointment = patient_obj_1.best_appointment()
    assert (
        isinstance(best_appointment, REDCapAppointment)
        and best_appointment.value("department") == "UPC DRAW STATION"
    )

    #   Two appointments at the same clinic. Best is earliest.
    patient_obj_5 = REDCapPatient(
        headers=patient_headers, row=patient_record_5, clinics=clinics
    )
    assert isinstance(patient_obj_5, REDCapPatient)
    patient_obj_2.merge(patient_obj_5)
    assert isinstance(patient_obj_2, REDCapPatient)
    assert len(patient_obj_2.appointments()) == 2
    best_appointment = patient_obj_2.best_appointment()
    assert (
        isinstance(best_appointment, REDCapAppointment)
        and best_appointment.value("date") == "2022-12-25"
    )


def test_appointment_fields(appointment_fields):
    # Test the ability of the REDCapAppointment class to determine
    # which record fields pertain to an appointment.
    possible_fields = appointment_fields.copy()
    possible_fields.extend(["NAME", "CITY", "ZIP", "PHONE"])
    appt_fields = REDCapAppointment.applicable_header_fields(headers=possible_fields)
    assert isinstance(appt_fields, list)
    assert appt_fields == appointment_fields

    with pytest.raises(TypeError):
        REDCapAppointment.applicable_header_fields(headers=[])


def test_patient_corner_cases(
    patient_headers,
    patient_record_1,
    patient_record_4,
    patient_record_6,
    patient_record_7,
    clinics,
):
    patient_obj = REDCapPatient(headers=patient_headers, row=None, clinics=clinics)
    assert isinstance(patient_obj, REDCapPatient)
    assert patient_obj.best_appointment() is None

    #   Exercise more of __clean_up_phone method.
    patient_obj = REDCapPatient(
        headers=patient_headers, row=patient_record_4, clinics=clinics
    )

    #   Exercise more of __clean_up_date method.
    patient_csv_description = patient_obj.csv()
    assert isinstance(patient_csv_description, str)

    patient_obj = REDCapPatient(
        headers=patient_headers, row=patient_record_6, clinics=clinics
    )

    #   Exercise more of __clean_up_date method.
    with pytest.raises(TypeError):
        patient_obj.csv()

    patient_obj = REDCapPatient(
        headers=patient_headers, row=patient_record_7, clinics=clinics
    )

    #   Exercise more of __clean_up_date method.
    with pytest.raises(ParserError):
        patient_obj.csv()


def test_patient_errors(patient_headers, patient_record_1, clinics):
    with pytest.raises(TypeError):
        REDCapPatient(headers=None, row=patient_record_1, clinics=clinics)


def test_patient_instantiation(
    patient_headers, patient_record_1, export_fields, clinics
):
    patient_obj = REDCapPatient(
        headers=patient_headers, row=patient_record_1, clinics=clinics
    )
    assert isinstance(patient_obj, REDCapPatient)

    #   Handle string input.
    patient_obj.set_study_id(study_id="654321")

    #   Handle integer input.
    patient_obj.set_study_id(study_id=654321)

    #   Try retrieving values.
    assert patient_obj.value("STUDY_ID") == "654321"
    assert patient_obj.value("PAT_ID") == "1234567"

    #   Not there.
    assert patient_obj.value("not present") is None

    patient_description = str(patient_obj)
    assert isinstance(patient_description, str)

    patient_csv_description = patient_obj.csv()
    assert isinstance(patient_csv_description, str)

    patient_csv_description = patient_obj.csv(headers=export_fields)
    assert isinstance(patient_csv_description, str)


def test_patient_merger(
    patient_headers, patient_record_1, patient_record_2, patient_record_3, clinics
):
    patient_obj_1 = REDCapPatient(
        headers=patient_headers, row=patient_record_1, clinics=clinics
    )
    assert isinstance(patient_obj_1, REDCapPatient)

    #   Same patient, different appointments.
    patient_obj_2 = REDCapPatient(
        headers=patient_headers, row=patient_record_2, clinics=clinics
    )
    assert isinstance(patient_obj_2, REDCapPatient)
    assert patient_obj_1.same_as(patient_obj_2)

    assert len(patient_obj_1.appointments()) == 1
    patient_obj_1.merge(patient_obj_2)
    assert isinstance(patient_obj_1, REDCapPatient)
    assert len(patient_obj_1.appointments()) == 2

    #   Different patients.
    patient_obj_3 = REDCapPatient(
        headers=patient_headers, row=patient_record_3, clinics=clinics
    )
    assert isinstance(patient_obj_3, REDCapPatient)
    assert not patient_obj_1.same_as(patient_obj_3)

    patient_obj_2.merge(patient_obj_3)
    assert isinstance(patient_obj_2, REDCapPatient)
    assert len(patient_obj_2.appointments()) == 1

    #   Comparison with something that's NOT a REDCapPatient object.
    assert not patient_obj_1.same_as("not a patient")
