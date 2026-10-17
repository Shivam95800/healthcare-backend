from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from users.models import User
from patients.models import Patient


class PatientOwnershipTests(APITestCase):
    def setUp(self):
        self.user_a = User.objects.create_user(
            email="usera@example.com", name="User A", password="Password123#A"
        )
        self.user_b = User.objects.create_user(
            email="userb@example.com", name="User B", password="Password123#B"
        )
        self.patient_a = Patient.objects.create(
            name="Alice",
            age=30,
            gender="F",
            phone="111-222-3333",
            address="123 Alpha St",
            created_by=self.user_a,
        )
        self.patient_b = Patient.objects.create(
            name="Bob",
            age=40,
            gender="M",
            phone="444-555-6666",
            address="456 Beta Ave",
            created_by=self.user_b,
        )
        self.patients_url = reverse("patient-list-create")

    def test_user_can_only_see_own_patients(self):
        self.client.force_authenticate(user=self.user_a)
        response = self.client.get(self.patients_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ids = [item["id"] for item in response.data]
        self.assertIn(self.patient_a.id, ids)
        self.assertNotIn(self.patient_b.id, ids)

    def test_user_cannot_access_or_modify_other_user_patient(self):
        self.client.force_authenticate(user=self.user_a)
        target_url = reverse("patient-detail", kwargs={"pk": self.patient_b.id})

        # GET request isolation
        get_response = self.client.get(target_url)
        self.assertEqual(get_response.status_code, status.HTTP_404_NOT_FOUND)

        # PUT request isolation
        put_response = self.client.put(
            target_url,
            {"name": "Hacked", "age": 25, "gender": "M", "phone": "000", "address": "Any"},
            format="json",
        )
        self.assertEqual(put_response.status_code, status.HTTP_404_NOT_FOUND)

    def test_invalid_age_validation(self):
        self.client.force_authenticate(user=self.user_a)
        payload = {
            "name": "Invalid Person",
            "age": 160,  # invalid (> 149)
            "gender": "O",
            "phone": "999-000-1111",
            "address": "Nowhere",
        }
        response = self.client.post(self.patients_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
