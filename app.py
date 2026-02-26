import streamlit as st

# =======================
# Paths (عدل لو محتاج)
# =======================
BASE_DIR = r"D:\Python Sessions DEPI\Session5"
PATIENTS_PATH = BASE_DIR + r"\patients.txt"
DOCTORS_PATH = BASE_DIR + r"\doctors.txt"
APPOINTMENTS_PATH = BASE_DIR + r"\appointments.txt"


# =======================
# Your classes (مع تعديل بسيط لمرضى: update_data_ui)
# =======================

class Patient:
    def find_ids(self):
        ids = []
        try:
            with open(PATIENTS_PATH, "r", encoding="utf-8") as patient_file:
                for line in patient_file:
                    result = line.strip().split('|')
                    if result and result[0]:
                        ids.append(result[0])
        except FileNotFoundError as e:
            # نسيبها (Streamlit هيتعامل)
            pass
        return ids

    def validate_data(self):
        ids = self.find_ids()

        if str(self.patient_id) in ids:
            raise ValueError("this ID is existed")

        if self.age < 0:
            raise ValueError("Invalid age")

        if self.gender.lower() not in ["male", "female"]:
            raise ValueError("Invalid gender")

    def store_data(self, patient_id, name, age, gender, disease):
        self.patient_id = patient_id
        self.name = name
        self.age = age
        self.gender = gender
        self.disease = disease

        self.validate_data()

        with open(PATIENTS_PATH, mode="a", encoding="utf-8") as patient_file:
            patient_file.write(f"{patient_id}|{name}|{age}|{gender}|{disease}\n")

    # ✅ نسخة UI-friendly من update (بدون input)
    def update_data_ui(self, patient_id, age, disease):
        ids = self.find_ids()
        if str(patient_id) not in ids:
            raise ValueError("Patient ID not found")

        if age < 0:
            raise ValueError("Invalid age")

        updated_lines = []
        with open(PATIENTS_PATH, "r", encoding="utf-8") as patient_file:
            for line in patient_file:
                data = line.strip().split('|')
                if len(data) != 5:
                    updated_lines.append(line)
                    continue

                if data[0] == str(patient_id):
                    data[2] = str(age)
                    data[4] = disease
                    updated_lines.append('|'.join(data) + '\n')
                else:
                    updated_lines.append(line)

        with open(PATIENTS_PATH, "w", encoding="utf-8") as file:
            file.writelines(updated_lines)


class Doctor:
    def find_ids(self):
        ids = []
        try:
            with open(DOCTORS_PATH, "r", encoding="utf-8") as doctor_file:
                for line in doctor_file:
                    result = line.strip().split('|')
                    if result and result[0]:
                        ids.append(result[0])
        except FileNotFoundError:
            pass
        return ids

    def validate_data(self):
        ids = self.find_ids()

        # ✅ مهم: doctor_id مش patient_id
        if str(self.doctor_id) in ids:
            raise ValueError("this ID is existed")

        if self.age < 0:
            raise ValueError("Invalid age")

        if self.gender.lower() not in ["male", "female"]:
            raise ValueError("Invalid gender")

    def store_data(self, doctor_id, name, age, gender, speciality):
        self.doctor_id = doctor_id
        self.name = name
        self.age = age
        self.gender = gender
        self.speciality = speciality

        self.validate_data()

        # ✅ مهم: write doctor_id مش patient_id
        with open(DOCTORS_PATH, mode="a", encoding="utf-8") as doctor_file:
            doctor_file.write(f"{doctor_id}|{name}|{age}|{gender}|{speciality}\n")


class Appointment:
    FILE_PATH = APPOINTMENTS_PATH

    def is_doctor_existed(self, doctor_id):
        try:
            with open(DOCTORS_PATH, "r") as doctor_file:
                for line in doctor_file:
                    parts = line.strip().split('|')
                    if parts and parts[0] == doctor_id:
                        return True
        except FileNotFoundError:
            return False
        return False

    def is_patient_existed(self, patient_id):
        try:
            with open(PATIENTS_PATH, "r") as patient_file:
                for line in patient_file:
                    parts = line.strip().split('|')
                    if parts and parts[0] == patient_id:
                        return True
        except FileNotFoundError:
            return False
        return False

    def find_appointments_ids(self):
        ids = []
        try:
            with open(self.FILE_PATH, "r") as appointment_file:
                for line in appointment_file:
                    parts = line.strip().split('|')
                    if parts and parts[0]:
                        ids.append(parts[0])
        except FileNotFoundError:
            pass
        return ids

    # appointments.txt format: appointment_id|patient_id|doctor_id|date_time
    def is_doctor_available(self, doctor_id, date_time):
        try:
            with open(self.FILE_PATH, "r") as f:
                for line in f:
                    parts = line.strip().split('|')
                    if len(parts) != 4:
                        continue
                    a_id, p_id, d_id, dt = parts
                    if d_id == doctor_id and dt == date_time:
                        return False
        except FileNotFoundError:
            return True
        return True

    def schedule_appointment(self, appointment_id, doctor_id, patient_id, date_time):
        if not self.is_doctor_existed(doctor_id):
            raise ValueError("Doctor ID is not existed")

        if not self.is_patient_existed(patient_id):
            raise ValueError("Patient ID is not existed")

        if not self.is_doctor_available(doctor_id, date_time):
            raise ValueError("Scheduling conflict: doctor is not available")

        if appointment_id in self.find_appointments_ids():
            raise ValueError("appointment ID is existed")

        with open(self.FILE_PATH, "a", encoding="utf-8") as f:
            f.write(f"{appointment_id}|{patient_id}|{doctor_id}|{date_time}\n")
        return True


# =======================
# Streamlit UI
# =======================

# Create objects once (Streamlit reruns script)
if "patient" not in st.session_state:
    st.session_state.patient = Patient()
if "doctor" not in st.session_state:
    st.session_state.doctor = Doctor()
if "appointment" not in st.session_state:
    st.session_state.appointment = Appointment()

patient = st.session_state.patient
doctor = st.session_state.doctor
appointment = st.session_state.appointment

st.title("🏥 Hospital System")

option = st.sidebar.selectbox(
    "Choose Operation",
    [
        "Add Patient",
        "Update Patient (Age & Disease)",
        "Add Doctor",
        "Schedule Appointment",
        "Check Doctor Availability",
    ],
)

def handle(fn):
    try:
        fn()
    except ValueError as e:
        st.error(str(e))
    except Exception as e:
        st.error(f"Unexpected error: {e}")

if option == "Add Patient":
    st.subheader("Add Patient")
    pid = st.text_input("Patient ID")
    name = st.text_input("Name")
    age = st.number_input("Age", min_value=0, step=1)
    gender = st.selectbox("Gender", ["male", "female"])
    disease = st.text_input("Disease")

    if st.button("Save Patient"):
        def action():
            patient.store_data(pid.strip(), name.strip(), int(age), gender.strip(), disease.strip())
            st.success("Patient added ✅")
        handle(action)

elif option == "Update Patient (Age & Disease)":
    st.subheader("Update Patient")
    pid = st.text_input("Patient ID to update")
    new_age = st.number_input("New Age", min_value=0, step=1)
    new_disease = st.text_input("New Disease")

    if st.button("Update Patient"):
        def action():
            patient.update_data_ui(pid.strip(), int(new_age), new_disease.strip())
            st.success("Patient updated ✅")
        handle(action)

elif option == "Add Doctor":
    st.subheader("Add Doctor")
    did = st.text_input("Doctor ID")
    name = st.text_input("Name")
    age = st.number_input("Age", min_value=0, step=1)
    gender = st.selectbox("Gender", ["male", "female"])
    speciality = st.text_input("Speciality")

    if st.button("Save Doctor"):
        def action():
            doctor.store_data(did.strip(), name.strip(), int(age), gender.strip(), speciality.strip())
            st.success("Doctor added ✅")
        handle(action)

elif option == "Schedule Appointment":
    st.subheader("Schedule Appointment")
    aid = st.text_input("Appointment ID")
    pid = st.text_input("Patient ID")
    did = st.text_input("Doctor ID")
    dt = st.text_input("DateTime (example: 2026-02-10)")

    if st.button("Schedule"):
        def action():
            appointment.schedule_appointment(aid.strip(), did.strip(), pid.strip(), dt.strip())
            st.success("Appointment scheduled ✅")
        handle(action)

elif option == "Check Doctor Availability":
    st.subheader("Check Doctor Availability")
    did = st.text_input("Doctor ID")
    dt = st.text_input("DateTime (example: 2026-02-10)")

    if st.button("Check"):
        def action():
            available = appointment.is_doctor_available(did.strip(), dt.strip())
            st.success("Available ✅") if available else st.warning("Not available ❌")
        handle(action)
