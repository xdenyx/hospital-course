from django.contrib import admin
from django.db import models
from django.forms import NumberInput
from .models import (
    ProcedureCategory, MaterialCategory, MedicineCategory, WorkCategory,
    Doctor, Patient, Request, Appointment, AppointmentWork,
    WorkMaterial, WorkMedicine, WorkProcedure
)

DECIMAL_OVERRIDES = {
    models.DecimalField: {'widget': NumberInput(attrs={'step': '0.50'})},
}

# ============ Класифікації ============
@admin.register(ProcedureCategory)
class ProcedureCategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'cost_price'] 
    list_display_links = ['id', 'name']
    search_fields = ['name']

@admin.register(MaterialCategory)
class MaterialCategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'cost_price']
    list_display_links = ['id', 'name']
    search_fields = ['name']

@admin.register(MedicineCategory)
class MedicineCategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'cost_price']
    list_display_links = ['id', 'name']
    search_fields = ['name']

@admin.register(WorkCategory)
class WorkCategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'price']
    list_display_links = ['id', 'name']
    search_fields = ['name']

# ============ Люди ============
@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ['id', 'full_name', 'specialization']
    search_fields = ['full_name', 'specialization']
    list_filter = ['specialization']
    list_display_links = ['id', 'full_name']


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ['id', 'full_name', 'date_of_birth']
    search_fields = ['full_name']
    list_filter = ['date_of_birth']
    list_display_links = ['id', 'full_name']


# ============ Заявки та прийоми ============
@admin.register(Request)
class RequestAdmin(admin.ModelAdmin):
    list_display = ['id', 'datetime', 'patient', 'doctor']
    search_fields = ['patient__full_name', 'doctor__full_name']
    list_filter = ['datetime', 'doctor']
    date_hierarchy = 'datetime'


class WorkMaterialInline(admin.TabularInline):
    model = WorkMaterial
    extra = 1


class WorkMedicineInline(admin.TabularInline):
    model = WorkMedicine
    extra = 1


class WorkProcedureInline(admin.TabularInline):
    model = WorkProcedure
    extra = 1


class AppointmentWorkInline(admin.TabularInline):
    model = AppointmentWork
    extra = 1
    inlines = [WorkMaterialInline, WorkMedicineInline, WorkProcedureInline]


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['id', 'request', 'get_patient', 'get_datetime']
    search_fields = ['request__patient__full_name']
    inlines = [AppointmentWorkInline]

    def get_patient(self, obj):
        return obj.request.patient.full_name
    get_patient.short_description = 'Пацієнт'

    def get_datetime(self, obj):
        return obj.request.datetime
    get_datetime.short_description = 'Дата та час'
    