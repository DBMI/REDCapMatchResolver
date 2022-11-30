"""
Module test_patient.py, which performs automated
testing of the REDCapPatient class.
"""
from datetime import datetime
import pytest
from redcapmatchresolver.redcap_appointment import REDCapAppointment
from redcapmatchresolver.redcap_patient import REDCapPatient


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

    appointment_obj = REDCapAppointment(
        appointment_headers=appointment_headers,
        appointment_info=appointment_record_malformed,
    )

    with pytest.raises(ValueError):
        appointment_obj.date()


def test_patient_appointments(patient_headers, patient_record_1, patient_record_2):
    #   Patient with NO appointments.
    patient_record_no_appointments = patient_record_1.copy()
    patient_record_no_appointments = patient_record_no_appointments[
        : len(patient_record_no_appointments) - 2
    ]
    patient_with_no_appointments = REDCapPatient(
        headers=patient_headers, row=patient_record_no_appointments
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

    #   Two appointments--ask for the "best".
    best_appointment = patient_obj_2.best_appointment()
    assert best_appointment is not None and isinstance(
        best_appointment, REDCapAppointment
    )


def test_patient_corner_cases(patient_headers, patient_record_1):
    REDCapPatient(headers=patient_headers, row=None)
    patient_obj = REDCapPatient(headers=patient_headers, row=patient_record_1[:-1])
    assert patient_obj.best_appointment() is None

    patient_obj.same_as(None)

    assert patient_obj.value("field_not_present") is None


def test_patient_errors(patient_headers, patient_record_1):
    with pytest.raises(TypeError):
        REDCapPatient(headers=None, row=patient_record_1)


def test_patient_instantiation(patient_headers, patient_record_1):
    patient_obj = REDCapPatient(headers=patient_headers, row=patient_record_1)
    assert patient_obj is not None and isinstance(patient_obj, REDCapPatient)

    #   Try retrieving a value.
    assert patient_obj.value("PAT_ID") == "1234567"

    patient_description = str(patient_obj)
    assert patient_description is not None and isinstance(patient_description, str)


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
