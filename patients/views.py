from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from healthcare_backend.permissions import IsOwner
from patients.models import Patient
from patients.serializers import PatientSerializer


class PatientListCreateView(generics.ListCreateAPIView):
    serializer_class = PatientSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Scoped strictly to the logged-in user
        return Patient.objects.filter(created_by=self.request.user)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class PatientDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PatientSerializer
    permission_classes = [IsAuthenticated, IsOwner]

    def get_queryset(self):
        # Isolation: prevents users from discovering/interacting with others' patients
        return Patient.objects.filter(created_by=self.request.user)
