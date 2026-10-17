from rest_framework import generics, status
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from doctors.serializers import DoctorSerializer
from patients.models import Patient
from mappings.models import PatientDoctorMapping
from mappings.serializers import (
    PatientDoctorMappingReadSerializer,
    PatientDoctorMappingCreateSerializer,
)


class MappingListCreateView(generics.ListCreateAPIView):
    """
    POST /api/mappings/ : Assign a doctor to a patient
    GET  /api/mappings/ : List all mappings where the patient belongs to the logged-in user
    """
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return PatientDoctorMappingCreateSerializer
        return PatientDoctorMappingReadSerializer

    def get_queryset(self):
        return PatientDoctorMapping.objects.filter(
            patient__created_by=self.request.user
        ).select_related("patient", "doctor")


# Note: The route '/api/mappings/<int:identifier>/' serves two purposes depending on the HTTP method:
# 1. GET  /api/mappings/<patient_id>/ : Returns the list of all doctors assigned to the specified patient
#    (verifying that the patient was created by the requesting user).
# 2. DELETE /api/mappings/<id>/       : Deletes a specific PatientDoctorMapping by its primary key
#    (verifying that the mapping belongs to a patient created by the requesting user).
# Handling both in a single APIView allows strict adherence to the exact spec path without requiring '/delete/'.
class MappingPatientOrDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, identifier):
        """
        GET /api/mappings/<patient_id>/
        List all doctors assigned to that patient (patient must belong to the requesting user).
        """
        try:
            patient = Patient.objects.get(id=identifier, created_by=request.user)
        except Patient.DoesNotExist:
            raise NotFound(detail=f"Patient with ID {identifier} not found or you do not have permission.")

        mappings = PatientDoctorMapping.objects.filter(patient=patient).select_related("doctor")
        doctors = [m.doctor for m in mappings]
        serializer = DoctorSerializer(doctors, many=True)
        return Response(
            {
                "patient_id": patient.id,
                "patient_name": patient.name,
                "assigned_doctors_count": len(doctors),
                "doctors": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def delete(self, request, identifier):
        """
        DELETE /api/mappings/<id>/
        Remove a mapping by its mapping ID (mapping must belong to a patient owned by requesting user).
        """
        try:
            mapping = PatientDoctorMapping.objects.get(id=identifier, patient__created_by=request.user)
        except PatientDoctorMapping.DoesNotExist:
            raise NotFound(detail=f"Mapping with ID {identifier} not found or you do not have permission.")

        mapping.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
