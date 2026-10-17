from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from users.models import User
from doctors.models import Doctor


class DoctorTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="docuser@example.com", name="Doc User", password="Password123#Doc"
        )
        self.doctor_list_url = reverse("doctor-list-create")
        self.doctor_data = {
            "name": "House MD",
            "specialization": "Diagnostics",
            "email": "house@example.com",
            "phone": "555-0100",
            "years_of_experience": 15,
        }

    def test_create_doctor_authenticated(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.doctor_list_url, self.doctor_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Doctor.objects.count(), 1)
        self.assertEqual(response.data["email"], self.doctor_data["email"])

    def test_create_doctor_unauthenticated(self):
        response = self.client.post(self.doctor_list_url, self.doctor_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
