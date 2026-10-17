from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from users.models import User


class AuthenticationTests(APITestCase):
    def setUp(self):
        self.register_url = reverse("user-register")
        self.login_url = reverse("user-login")
        self.user_data = {
            "name": "Jane Doe",
            "email": "jane@example.com",
            "password": "Password123#Strong",
            "password_confirm": "Password123#Strong",
        }

    def test_register_user_success(self):
        response = self.client.post(self.register_url, self.user_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email=self.user_data["email"]).exists())
        self.assertEqual(response.data["data"]["email"], self.user_data["email"])

    def test_register_duplicate_email_fails(self):
        self.client.post(self.register_url, self.user_data, format="json")
        dup_response = self.client.post(self.register_url, self.user_data, format="json")
        self.assertEqual(dup_response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_user_success(self):
        self.client.post(self.register_url, self.user_data, format="json")
        login_data = {
            "email": self.user_data["email"],
            "password": self.user_data["password"],
        }
        response = self.client.post(self.login_url, login_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data["data"])
        self.assertIn("refresh", response.data["data"])
        self.assertEqual(response.data["data"]["user"]["email"], self.user_data["email"])

    def test_firebase_authentication_creates_and_authenticates_user(self):
        from unittest.mock import patch
        fake_decoded_token = {
            "uid": "firebase-uid-12345",
            "email": "firebaseuser@example.com",
            "name": "Firebase User",
        }
        patients_url = reverse("patient-list-create")
        with patch("firebase_admin.auth.verify_id_token", return_value=fake_decoded_token):
            self.client.credentials(HTTP_AUTHORIZATION="Bearer valid_firebase_token")
            response = self.client.get(patients_url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertTrue(User.objects.filter(email="firebaseuser@example.com").exists())
