"""
Module test_patient.py, which performs automated
testing of the REDCapPatient class.
"""
from datetime import datetime
import pytest
from redcapmatchresolver.redcap_appointment import REDCapAppointment
from redcapmatchresolver.redcap_patient import REDCapPatient


def test_appointment_corner_cases(
    appointment_headers, appointment_record_slashes, appointment_datetime
):
    appointment_obj = REDCapAppointment(
        appointment_headers=appointment_headers,
        appointment_info=appointment_record_slashes,
    )
    assert appointment_obj is not None and isinstance(
        appointment_obj, REDCapAppointment
    )
    assert appointment_obj.date() == appointment_datetime


def test_appointment_errors(
    appointment_headers,
    appointment_record,
    appointment_record_partial,
    appointment_record_malformed,
):
    with pytest.raises(TypeError):
        REDCapAppointment(appointment_headers=None, appointment_info=appointment_record)

    with pytest.raises(TypeError):
        REDCapAppointment(appointment_headers=1979, appointment_info=appointment_record)

    with pytest.raises(TypeError):
        REDCapAppointment(
            appointment_headers=appointment_headers, appointment_info=None
        )

    with pytest.raises(TypeError):
        REDCapAppointment(
            appointment_headers=appointment_headers, appointment_info=1979
        )

    appointment_headers_modified = appointment_headers.copy()
    appointment_headers_modified[0] = 1979

    with pytest.raises(TypeError):
        REDCapAppointment(
            appointment_headers=appointment_headers_modified,
            appointment_info=appointment_record,
        )

    with pytest.raises(TypeError):
        #   Remove last item from appointment_record, to cause length mismatch error.
        REDCapAppointment(
            appointment_headers=appointment_headers,
            appointment_info=appointment_record[:-1],
        )

    appointment_obj = REDCapAppointment(
        appointment_headers=appointment_headers,
        appointment_info=appointment_record_partial,
    )
    assert appointment_obj.date() is None
    partial_csv = appointment_obj.csv()
    assert (
        partial_csv is not None
        and isinstance(partial_csv, str)
        and partial_csv == " , "
    )

    appointment_obj = REDCapAppointment(
        appointment_headers=appointment_headers,
        appointment_info=appointment_record_malformed,
    )

    with pytest.raises(ValueError):
        appointment_obj.date()


def test_appointment_instantiation(
    appointment_headers, appointment_record, appointment_datetime
):
    appointment_obj = REDCapAppointment(
        appointment_headers=appointment_headers, appointment_info=appointment_record
    )
    assert appointment_obj is not None and isinstance(
        appointment_obj, REDCapAppointment
    )

    #   Can we parse the date/time from the REDCapAppointment object?
    extracted_datetime = appointment_obj.date()
    assert extracted_datetime is not None and isinstance(extracted_datetime, datetime)
    assert extracted_datetime == appointment_datetime

    #   Test .csv output.
    csv_summary = appointment_obj.csv()
    assert csv_summary is not None and isinstance(csv_summary, str)

    #   Ask for clinic, date, time.
    value = appointment_obj.value("appointment_clinic")
    assert value is not None and isinstance(value, str) and value == "LWC CARDIOLOGY"

    value = appointment_obj.value("appointment_date")
    assert value is not None and isinstance(value, str) and value == "2022-12-01"

    value = appointment_obj.value("appointment_time")
    assert value is not None and isinstance(value, str) and value == "10:40:00"

    value = appointment_obj.value("not_valid_name")
    assert value is not None and isinstance(value, str) and len(value) == 0

    value = appointment_obj.value(1979)
    assert value is not None and isinstance(value, str) and len(value) == 0

    #   Ask for appointment priority.
    priority = appointment_obj.priority()
    assert priority is not None and isinstance(priority, int) and priority == 14


def test_patient_appointments(
    patient_headers, patient_record_1, patient_record_2, patient_record_5
):
    #   Patient with NO appointments.
    patient_record_no_appointments_list = list(patient_record_1)
    patient_record_no_appointments_list = patient_record_no_appointments_list[
        : len(patient_record_no_appointments_list) - 2
    ]
    patient_with_no_appointments = REDCapPatient(
        headers=patient_headers, row=tuple(patient_record_no_appointments_list)
    )
    assert patient_with_no_appointments is not None and isinstance(
        patient_with_no_appointments, REDCapPatient
    )
    appointments = patient_with_no_appointments.appointments()
    assert appointments is not None
    assert isinstance(appointments, list)
    assert len(appointments) == 0
    best_appointment = patient_with_no_appointments.best_appointment()
    assert best_appointment is None

    patient_obj_1 = REDCapPatient(headers=patient_headers, row=patient_record_1)
    assert patient_obj_1 is not None and isinstance(patient_obj_1, REDCapPatient)

    #   Only one appointment, but can still ask for the "best".
    best_appointment = patient_obj_1.best_appointment()
    assert best_appointment is not None and isinstance(
        best_appointment, REDCapAppointment
    )

    #   Same patient, different appointments.
    patient_obj_2 = REDCapPatient(headers=patient_headers, row=patient_record_2)
    assert patient_obj_2 is not None and isinstance(patient_obj_2, REDCapPatient)

    patient_obj_1.merge(patient_obj_2)
    assert patient_obj_1 is not None and isinstance(patient_obj_1, REDCapPatient)
    assert len(patient_obj_1.appointments()) == 2

    #   Two appointments at different clinics--ask for the "best".
    #   In this case, best will be determined by clinic location.
    best_appointment = patient_obj_1.best_appointment()
    assert (
        best_appointment is not None
        and isinstance(best_appointment, REDCapAppointment)
        and best_appointment.value("department") == "UPC DRAW STATION"
    )

    #   Two appointments at the same clinic. Best is earliest.
    patient_obj_5 = REDCapPatient(headers=patient_headers, row=patient_record_5)
    assert patient_obj_5 is not None and isinstance(patient_obj_5, REDCapPatient)
    patient_obj_2.merge(patient_obj_5)
    assert patient_obj_2 is not None and isinstance(patient_obj_2, REDCapPatient)
    assert len(patient_obj_2.appointments()) == 2
    best_appointment = patient_obj_2.best_appointment()
    assert (
        best_appointment is not None
        and isinstance(best_appointment, REDCapAppointment)
        and best_appointment.value("date") == "2022-12-25"
    )


def test_patient_corner_cases(patient_headers, patient_record_1, patient_record_4):
    REDCapPatient(headers=patient_headers, row=None)
    patient_obj = REDCapPatient(headers=patient_headers, row=patient_record_1[:-1])
    assert patient_obj.best_appointment() is None

    patient_obj.same_as(None)

    assert patient_obj.value("field_not_present") is None

    #   Exercise more of _clean_up_phone method.
    REDCapPatient(headers=patient_headers, row=patient_record_4)


def test_patient_errors(patient_headers, patient_record_1):
    with pytest.raises(TypeError):
        REDCapPatient(headers=None, row=patient_record_1)


def test_patient_instantiation(patient_headers, patient_record_1, export_fields):
    patient_obj = REDCapPatient(headers=patient_headers, row=patient_record_1)
    assert patient_obj is not None and isinstance(patient_obj, REDCapPatient)

    patient_obj.set_study_id(study_id="654321")

    #   Try retrieving values.
    assert patient_obj.value("STUDY_ID") == "654321"
    assert patient_obj.value("PAT_ID") == "1234567"

    patient_description = str(patient_obj)
    assert patient_description is not None and isinstance(patient_description, str)

    patient_csv_description = patient_obj.csv()
    assert patient_csv_description is not None and isinstance(
        patient_csv_description, str
    )

    patient_csv_description = patient_obj.csv(headers=export_fields)
    assert patient_csv_description is not None and isinstance(
        patient_csv_description, str
    )


def test_patient_merger(
    patient_headers, patient_record_1, patient_record_2, patient_record_3
):
    patient_obj_1 = REDCapPatient(headers=patient_headers, row=patient_record_1)
    assert patient_obj_1 is not None and isinstance(patient_obj_1, REDCapPatient)

    #   Same patient, different appointments.
    patient_obj_2 = REDCapPatient(headers=patient_headers, row=patient_record_2)
    assert patient_obj_2 is not None and isinstance(patient_obj_2, REDCapPatient)
    assert patient_obj_1.same_as(patient_obj_2)

    assert len(patient_obj_1.appointments()) == 1
    patient_obj_1.merge(patient_obj_2)
    assert patient_obj_1 is not None and isinstance(patient_obj_1, REDCapPatient)
    assert len(patient_obj_1.appointments()) == 2

    #   Different patients.
    patient_obj_3 = REDCapPatient(headers=patient_headers, row=patient_record_3)
    assert patient_obj_3 is not None and isinstance(patient_obj_3, REDCapPatient)
    assert not patient_obj_1.same_as(patient_obj_3)

    patient_obj_2.merge(patient_obj_3)
    assert patient_obj_2 is not None and isinstance(patient_obj_2, REDCapPatient)
    assert len(patient_obj_2.appointments()) == 1


if __name__ == "__main__":
    pass
