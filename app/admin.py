from django.contrib import admin
from .models import Doctor, Patient, Consultation

@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('nome', 'crm', 'specialty', 'email', 'is_deleted')
    list_filter = ('specialty', 'is_deleted')
    search_fields = ('nome', 'crm', 'email')

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('nome', 'email', 'telefone', 'is_deleted')
    search_fields = ('nome', 'email')

@admin.register(Consultation)
class ConsultationAdmin(admin.ModelAdmin):
    list_display = ('patient', 'doctor', 'date', 'is_deleted')
    list_filter = ('date', 'doctor')
    search_fields = ('patient__nome', 'doctor__nome')