from rest_framework import serializers
from doctors.models import Doctor
from doctors.serializers import DoctorSerializer
from patients.models import Patient
from patients.serializers import PatientSerializer
from mappings.models import PatientDoctorMapping


class PatientDoctorMappingReadSerializer(serializers.ModelSerializer):
    patient = PatientSerializer(read_only=True)
    doctor = DoctorSerializer(read_only=True)

    class Meta:
        model = PatientDoctorMapping
        fields = ("id", "patient", "doctor", "created_at")


class PatientDoctorMappingCreateSerializer(serializers.ModelSerializer):
    patient_id = serializers.IntegerField(write_only=True)
    doctor_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = PatientDoctorMapping
        fields = ("id", "patient_id", "doctor_id", "created_at")
        read_only_fields = ("id", "created_at")

    def validate(self, attrs):
        request = self.context.get("request")
        user = request.user
        patient_id = attrs.get("patient_id")
        doctor_id = attrs.get("doctor_id")

        # Verify Patient exists and belongs to the authenticated user
        try:
            patient = Patient.objects.get(id=patient_id)
        except Patient.DoesNotExist:
            raise serializers.ValidationError({"patient_id": f"Patient with ID {patient_id} does not exist."})

        if patient.created_by != user:
            raise serializers.ValidationError(
                {"patient_id": "You can only assign doctors to patients you have created."}
            )

        # Verify Doctor exists
        try:
            doctor = Doctor.objects.get(id=doctor_id)
        except Doctor.DoesNotExist:
            raise serializers.ValidationError({"doctor_id": f"Doctor with ID {doctor_id} does not exist."})

        # Check for duplicate mapping
        if PatientDoctorMapping.objects.filter(patient=patient, doctor=doctor).exists():
            raise serializers.ValidationError(
                {"detail": f"Mapping already exists: Dr. {doctor.name} is already assigned to {patient.name}."}
            )

        attrs["patient"] = patient
        attrs["doctor"] = doctor
        return attrs

    def create(self, validated_data):
        return PatientDoctorMapping.objects.create(
            patient=validated_data["patient"],
            doctor=validated_data["doctor"],
        )

    def to_representation(self, instance):
        return PatientDoctorMappingReadSerializer(instance).data
