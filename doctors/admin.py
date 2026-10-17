from django.contrib import admin
from doctors.models import Doctor


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ("name", "specialization", "email", "phone", "years_of_experience", "created_at")
    list_filter = ("specialization", "created_at")
    search_fields = ("name", "email", "specialization")
    readonly_fields = ("created_at", "updated_at")
