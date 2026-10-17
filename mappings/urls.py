from django.urls import path
from mappings.views import MappingListCreateView, MappingPatientOrDetailView

urlpatterns = [
    path("", MappingListCreateView.as_view(), name="mapping-list-create"),
    # Handles both GET /api/mappings/<patient_id>/ and DELETE /api/mappings/<id>/
    path("<int:identifier>/", MappingPatientOrDetailView.as_view(), name="mapping-patient-or-detail"),
]
