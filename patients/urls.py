from django.urls import path
from patients.views import PatientListCreateView, PatientDetailView

urlpatterns = [
    path("", PatientListCreateView.as_view(), name="patient-list-create"),
    path("<int:pk>/", PatientDetailView.as_view(), name="patient-detail"),
]
