import os
import firebase_admin
from firebase_admin import auth as firebase_auth, credentials
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import authentication, exceptions

User = get_user_model()


def initialize_firebase():
    """
    Initializes the Firebase Admin SDK if not already initialized.
    Uses credentials file if FIREBASE_CREDENTIALS_PATH exists, else default credentials.
    """
    if not firebase_admin._apps:
        cred_path = getattr(settings, "FIREBASE_CREDENTIALS_PATH", None)
        if cred_path and os.path.exists(cred_path):
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
        else:
            try:
                firebase_admin.initialize_app()
            except Exception:
                pass


initialize_firebase()


class FirebaseAuthentication(authentication.BaseAuthentication):
    """
    DRF Authentication scheme that verifies Firebase ID tokens.
    Token is expected in the Authorization header:
        Authorization: Bearer <firebase_id_token>
    """

    def authenticate(self, request):
        auth_header = request.META.get("HTTP_AUTHORIZATION")
        if not auth_header:
            return None

        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            return None

        id_token = parts[1]

        try:
            decoded_token = firebase_auth.verify_id_token(id_token)
        except Exception as e:
            raise exceptions.AuthenticationFailed(f"Invalid or expired Firebase token: {str(e)}")

        uid = decoded_token.get("uid")
        email = decoded_token.get("email")
        name = decoded_token.get("name") or (email.split("@")[0] if email else f"User-{uid[:6]}")

        if not email:
            raise exceptions.AuthenticationFailed("Firebase user token must contain an email address.")

        # Get or sync the local User record with the verified Firebase identity
        user, created = User.objects.get_or_create(
            email=email,
            defaults={"name": name, "is_active": True},
        )

        return (user, decoded_token)

    def authenticate_header(self, request):
        return 'Bearer realm="api"'
