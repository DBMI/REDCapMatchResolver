"""
Module test_patient.py, which performs automated
testing of the REDCapPatient class.
"""
from datetime import datetime

import pandas
import pytest

from redcapmatchresolver.redcap_appointment import REDCapAppointment
from redcapmatchresolver.redcap_clinic import REDCapClinic
from redcapmatchresolver.redcap_patient import REDCapPatient


@pytest.fixture(name="clinics")
def fixture_clinics() -> REDCapClinic:
    return REDCapClinic()


def test_appointment_corner_cases(
    appointment_df,
    appointment_df_malformed,
    appointment_df_slashes,
    appointment_df_time_missing,
):
    #   Make it look up clinics by itself.
    appointment_obj = REDCapAppointment(df=appointment_df)
    assert isinstance(appointment_obj, REDCapAppointment)
    full_datetime_string = (
        appointment_df.appointment_date[0] + " " + appointment_df.appointment_time[0]
    )
    assert appointment_obj.date() == datetime.strptime(
        full_datetime_string,
        "%Y-%m-%d %H:%M:%S",
    )

    appointment_obj = REDCapAppointment(df=appointment_df_malformed)
    assert isinstance(appointment_obj, REDCapAppointment)
    assert not appointment_obj.valid()

    #   Handle dd/mm/yyyy format.
    appointment_obj = REDCapAppointment(df=appointment_df_slashes)
    assert isinstance(appointment_obj, REDCapAppointment)
    assert appointment_obj.date() == datetime.strptime(
        full_datetime_string,
        "%Y-%m-%d %H:%M:%S",
    )

    #   Handle time missing.
    appointment_obj = REDCapAppointment(df=appointment_df_time_missing)
    assert isinstance(appointment_obj, REDCapAppointment)
    assert appointment_obj.date() == datetime.strptime(
        appointment_df.appointment_date[0],
        "%Y-%m-%d",
    )


def test_appointment_errors(clinics):
    with pytest.raises(TypeError):
        REDCapAppointment(
            df=None,
            clinics=clinics,
        )

    with pytest.raises(TypeError):
        REDCapAppointment(
            df=1979,
            clinics=clinics,
        )


def test_appointment_fields(appointment_fields):
    # Test the ability of the REDCapAppointment class to determine
    # which record fields pertain to an appointment.
    possible_fields = appointment_fields.copy()
    possible_fields.extend(["name", "city", "zip", "phone"])
    appt_fields = REDCapAppointment.applicable_header_fields(headers=possible_fields)
    assert isinstance(appt_fields, list)
    assert appt_fields == appointment_fields

    with pytest.raises(TypeError):
        REDCapAppointment.applicable_header_fields(headers=[])


def test_appointment_instantiation(appointment_df, clinics):
    appointment_obj = REDCapAppointment(
        df=appointment_df,
        clinics=clinics,
    )
    assert isinstance(appointment_obj, REDCapAppointment)

    #   Can we parse the date/time from the REDCapAppointment object?
    extracted_datetime = appointment_obj.date()
    assert isinstance(extracted_datetime, datetime)
    full_datetime_string = (
        appointment_df.appointment_date[0] + " " + appointment_df.appointment_time[0]
    )
    assert extracted_datetime == datetime.strptime(
        full_datetime_string, "%Y-%m-%d %H:%M:%S"
    )

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

    value = appointment_obj.value("datetime")
    assert isinstance(value, str) and value == "2022-12-01 10:40:00"

    value = appointment_obj.value("not_valid_name")
    assert isinstance(value, str) and len(value) == 0

    value = appointment_obj.value(1979)
    assert isinstance(value, str) and len(value) == 0

    #   Ask for appointment priority.
    priority = appointment_obj.priority()
    assert isinstance(priority, int) and priority == 14


def test_patient_appointments(
    patient_record_1_no_appt,
    patient_record_1,
    patient_record_2,
    patient_record_5,
    clinics,
):
    #   Patient with NO appointments.
    patient_with_no_appointments = REDCapPatient(
        df=patient_record_1_no_appt,
        clinics=clinics,
    )
    assert isinstance(patient_with_no_appointments, REDCapPatient)
    appointments = patient_with_no_appointments.appointments()
    assert isinstance(appointments, list)
    assert len(appointments) == 0
    best_appointment = patient_with_no_appointments.best_appointment()
    assert best_appointment is None

    patient_obj_1 = REDCapPatient(df=patient_record_1, clinics=clinics)
    assert isinstance(patient_obj_1, REDCapPatient)

    #   Only one appointment, but can still ask for the "best".
    best_appointment = patient_obj_1.best_appointment()
    assert isinstance(best_appointment, REDCapAppointment)

    #   Same patient, different appointments.
    patient_obj_2 = REDCapPatient(df=patient_record_2, clinics=clinics)
    assert isinstance(patient_obj_2, REDCapPatient)

    patient_obj_1.merge(patient_obj_2)
    assert isinstance(patient_obj_1, REDCapPatient)
    assert len(patient_obj_1.appointments()) == 2

    #   Two appointments at different clinics--ask for the "best".
    #   In this case, best will be determined by clinic location.
    best_appointment = patient_obj_1.best_appointment()
    assert (
        isinstance(best_appointment, REDCapAppointment)
        and best_appointment.value("appointment_clinic") == "UPC DRAW STATION"
    )

    #   Two appointments at the same clinic. Best is earlier.
    patient_obj_5 = REDCapPatient(df=patient_record_5, clinics=clinics)
    assert isinstance(patient_obj_5, REDCapPatient)
    patient_obj_2.merge(patient_obj_5)
    assert isinstance(patient_obj_2, REDCapPatient)
    assert len(patient_obj_2.appointments()) == 2
    best_appointment = patient_obj_2.best_appointment()
    assert isinstance(best_appointment, REDCapAppointment)
    assert best_appointment.value("appointment_date") == "2022-12-25"
    assert best_appointment.value("appointment_time") == "11:12:13"
    assert best_appointment.value("appointment_clinic") == "UPC INTERNAL MEDICINE"

    #   Convert APPOINTMENT to dataframe.
    df = best_appointment.to_df()
    assert isinstance(df, pandas.DataFrame)
    assert "appointment_clinic" in df
    assert df["appointment_clinic"].values[0] == "UPC INTERNAL MEDICINE"
    assert "appointment_date" in df
    assert df["appointment_date"].values[0] == "2022-12-25"
    assert "appointment_time" in df
    assert df["appointment_time"].values[0] == "11:12:13"

    #   Convert PATIENT to dataframe.
    #   Need to do this with merged appts to ensure
    #   to_df() method is using the BEST appt.
    df = patient_obj_2.to_df()
    assert isinstance(df, pandas.DataFrame)
    assert df.index.name == "study_id"
    assert df.index.values[0] == "1234567"
    assert "appointment_clinic" in df
    assert df["appointment_clinic"].values[0] == "UPC INTERNAL MEDICINE"
    assert "appointment_date" in df
    assert df["appointment_date"].values[0] == "2022-12-25"
    assert "appointment_time" in df
    assert df["appointment_time"].values[0] == "11:12:13"


def test_patient_corner_cases(
    patient_record_4,
    patient_record_6,
    patient_record_7,
    patient_record_1_no_appt,
    clinics,
):
    patient_obj = REDCapPatient(df=patient_record_4, clinics=clinics)

    patient_csv_description = patient_obj.csv()
    assert isinstance(patient_csv_description, str)
    assert patient_obj.value("dob") == "1731-06-02"

    patient_obj = REDCapPatient(df=patient_record_6, clinics=clinics)

    patient_csv_description = patient_obj.csv()
    assert isinstance(patient_csv_description, str)
    assert patient_obj.value("dob") == ""

    patient_obj = REDCapPatient(df=patient_record_7, clinics=clinics)

    #   Exercise more of __clean_up_date method.
    patient_csv_description = patient_obj.csv()
    assert isinstance(patient_csv_description, str)
    assert patient_obj.value("dob") == ""

    #   Exercise no-appointments case.
    patient_obj = REDCapPatient(df=patient_record_1_no_appt, clinics=clinics)
    assert isinstance(patient_obj, REDCapPatient)
    assert len(patient_obj.appointments()) == 0


def test_patient_csv(
    patient_headers_scrambled,
    patient_record_1,
    patient_record_2,
    clinics,
    patient_records_1_2_merged,
    patient_records_1_2_merged_no_header,
    patient_records_1_2_merged_limited_cols,
):
    #   Same patient, two appointments at different clinics.
    #   In this case, best will be determined by clinic location.
    patient_obj_1 = REDCapPatient(df=patient_record_1, clinics=clinics)
    patient_obj_2 = REDCapPatient(df=patient_record_2, clinics=clinics)
    patient_obj_1.merge(patient_obj_2)

    patient_csv_description = patient_obj_1.csv()
    assert isinstance(patient_csv_description, str)
    assert patient_csv_description.replace("\r", "") == patient_records_1_2_merged

    #   Now rearrange the columns.
    patient_csv_description = patient_obj_1.csv(columns=patient_headers_scrambled)
    assert isinstance(patient_csv_description, str)
    assert (
        patient_csv_description.replace("\r", "")
        == patient_records_1_2_merged_limited_cols
    )

    #   Exercise the no-headers option.
    patient_csv_description = patient_obj_1.csv(include_headers=False)
    assert isinstance(patient_csv_description, str)
    assert (
        patient_csv_description.replace("\r", "")
        == patient_records_1_2_merged_no_header
    )


def test_patient_errors(patient_record_1, clinics):
    with pytest.raises(TypeError):
        REDCapPatient(df=None, clinics=clinics)

    with pytest.raises(TypeError):
        REDCapPatient(
            df=patient_record_1,
            clinics=1979,
        )


def test_patient_instantiation(patient_record_1, export_fields, clinics):
    patient_obj = REDCapPatient(df=patient_record_1, clinics=clinics)
    assert isinstance(patient_obj, REDCapPatient)
    assert patient_obj is not None and isinstance(patient_obj, REDCapPatient)

    #   Handle string input.
    patient_obj.set_study_id(study_id="654321")

    #   Handle integer input.
    patient_obj.set_study_id(study_id=654321)

    #   Try retrieving values.
    assert patient_obj.value("study_id") == "654321"

    #   Not there.
    assert patient_obj.value("not present") is None

    patient_description = str(patient_obj)
    assert isinstance(patient_description, str)

    patient_csv_description = patient_obj.csv()
    assert isinstance(patient_csv_description, str)

    patient_csv_description = patient_obj.csv(columns=export_fields)
    assert isinstance(patient_csv_description, str)


def test_patient_merger(patient_record_1, patient_record_2, patient_record_3, clinics):
    patient_obj_1 = REDCapPatient(df=patient_record_1, clinics=clinics)
    assert isinstance(patient_obj_1, REDCapPatient)

    #   Same patient, different appointments.
    patient_obj_2 = REDCapPatient(df=patient_record_2, clinics=clinics)
    assert isinstance(patient_obj_2, REDCapPatient)

    assert len(patient_obj_1.appointments()) == 1
    patient_obj_1.merge(patient_obj_2)
    assert isinstance(patient_obj_1, REDCapPatient)
    assert len(patient_obj_1.appointments()) == 2

    #   Different patients.
    patient_obj_3 = REDCapPatient(df=patient_record_3, clinics=clinics)
    assert isinstance(patient_obj_3, REDCapPatient)

    patient_obj_2.merge(patient_obj_3)
    assert isinstance(patient_obj_2, REDCapPatient)
    assert len(patient_obj_2.appointments()) == 1


def test_patient_same_as(
    patient_record_1,
    patient_record_1_with_hpi,
    patient_record_2,
    patient_record_3,
    clinics,
):
    patient_obj_1 = REDCapPatient(df=patient_record_1, clinics=clinics)
    assert isinstance(patient_obj_1, REDCapPatient)

    #   Same patient, different appointments.
    patient_obj_2 = REDCapPatient(df=patient_record_2, clinics=clinics)
    assert isinstance(patient_obj_2, REDCapPatient)
    assert patient_obj_1.same_as(patient_obj_2)

    #   Same patient, with HPI info.
    patient_obj_1_with_hpi = REDCapPatient(
        df=patient_record_1_with_hpi, clinics=clinics
    )
    assert isinstance(patient_obj_1_with_hpi, REDCapPatient)
    assert patient_obj_1.same_as(patient_obj_1_with_hpi)

    #   Different patients.
    patient_obj_3 = REDCapPatient(df=patient_record_3, clinics=clinics)
    assert isinstance(patient_obj_3, REDCapPatient)
    assert not patient_obj_1.same_as(patient_obj_3)

    #   Comparison with something that's NOT a REDCapPatient object.
    assert not patient_obj_1.same_as("not a patient")
