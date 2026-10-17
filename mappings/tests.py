from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from users.models import User
from patients.models import Patient
from doctors.models import Doctor
from mappings.models import PatientDoctorMapping


class MappingTests(APITestCase):
    def setUp(self):
        self.user_owner = User.objects.create_user(
            email="owner@example.com", name="Owner", password="Password123#Owner"
        )
        self.user_other = User.objects.create_user(
            email="other@example.com", name="Other", password="Password123#Other"
        )
        self.patient = Patient.objects.create(
            name="Charlie",
            age=25,
            gender="M",
            phone="555-1234",
            address="789 Elm St",
            created_by=self.user_owner,
        )
        self.doctor = Doctor.objects.create(
            name="Dr. Smith",
            specialization="Cardiology",
            email="drsmith@example.com",
            phone="555-8888",
            years_of_experience=12,
        )
        self.mapping_list_url = reverse("mapping-list-create")

    def test_assign_doctor_success(self):
        self.client.force_authenticate(user=self.user_owner)
        payload = {
            "patient_id": self.patient.id,
            "doctor_id": self.doctor.id,
        }
        response = self.client.post(self.mapping_list_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(PatientDoctorMapping.objects.count(), 1)

    def test_duplicate_mapping_rejected(self):
        self.client.force_authenticate(user=self.user_owner)
        payload = {
            "patient_id": self.patient.id,
            "doctor_id": self.doctor.id,
        }
        # First assignment succeeds
        self.client.post(self.mapping_list_url, payload, format="json")
        # Duplicate assignment fails
        dup_response = self.client.post(self.mapping_list_url, payload, format="json")
        self.assertEqual(dup_response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cannot_assign_doctor_to_unowned_patient(self):
        self.client.force_authenticate(user=self.user_other)
        payload = {
            "patient_id": self.patient.id,
            "doctor_id": self.doctor.id,
        }
        response = self.client.post(self.mapping_list_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_patient_doctors_and_delete_mapping_routes(self):
        self.client.force_authenticate(user=self.user_owner)
        mapping = PatientDoctorMapping.objects.create(
            patient=self.patient,
            doctor=self.doctor,
        )

        # GET /api/mappings/<patient_id>/
        get_url = reverse("mapping-patient-or-detail", kwargs={"identifier": self.patient.id})
        get_resp = self.client.get(get_url)
        self.assertEqual(get_resp.status_code, status.HTTP_200_OK)
        self.assertEqual(get_resp.data["patient_id"], self.patient.id)
        self.assertEqual(get_resp.data["assigned_doctors_count"], 1)

        # DELETE /api/mappings/<id>/
        del_url = reverse("mapping-patient-or-detail", kwargs={"identifier": mapping.id})
        del_resp = self.client.delete(del_url)
        self.assertEqual(del_resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(PatientDoctorMapping.objects.count(), 0)
