from rest_framework import serializers
from ..models import (
    Patient, Request, Appointment, Doctor, WorkCategory, MaterialCategory,
    MedicineCategory, ProcedureCategory, AppointmentWork, WorkMaterial,
    WorkMedicine, WorkProcedure
)

class DoctorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = ['id', 'full_name', 'specialization']


class PatientSerializer(serializers.ModelSerializer):
    age = serializers.ReadOnlyField()
    
    class Meta:
        model = Patient
        fields = ['id', 'full_name', 'date_of_birth', 'age', 'phone_number']


class RequestSerializer(serializers.ModelSerializer):
    patient = PatientSerializer(read_only=True)
    patient_id = serializers.PrimaryKeyRelatedField(source='patient', queryset=Patient.objects.all(), write_only=True)
    doctor = DoctorSerializer(read_only=True)
    doctor_id = serializers.PrimaryKeyRelatedField(source='doctor', queryset=Doctor.objects.all(), write_only=True)

    class Meta:
        model = Request
        fields = ['id', 'patient', 'patient_id', 'datetime', 'doctor', 'doctor_id']

class WorkCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkCategory
        fields = ['id', 'name']


class MaterialCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = MaterialCategory
        fields = ['id', 'name']


class MedicineCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicineCategory
        fields = ['id', 'name']


class ProcedureCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProcedureCategory
        fields = ['id', 'name']


class WorkMaterialSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    cost = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    
    class Meta:
        model = WorkMaterial
        fields = '__all__'

class WorkMedicineSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    cost = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    
    class Meta:
        model = WorkMedicine
        fields = '__all__'


class WorkProcedureSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    cost = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    
    class Meta:
        model = WorkProcedure
        fields = '__all__'


class AppointmentWorkSerializer(serializers.ModelSerializer):
    materials = WorkMaterialSerializer(many=True, read_only=True)
    medicines = WorkMedicineSerializer(many=True, read_only=True)
    procedures = WorkProcedureSerializer(many=True, read_only=True)
    category_name = serializers.CharField(source='work_category.name', read_only=True)
    
    price = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    cost = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    profit = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    
    class Meta:
        model = AppointmentWork
        fields = [
            'id', 'appointment', 'work_category', 'category_name', 'price', 'cost', 'profit', 'materials', 'medicines', 'procedures'
        ]


class AppointmentDetailSerializer(serializers.ModelSerializer):
    request = RequestSerializer(read_only=True)
    works = AppointmentWorkSerializer(many=True, read_only=True)
    
    class Meta:
        model = Appointment
        fields = ['id', 'request', 'works', 'notes']


class AppointmentSerializer(serializers.ModelSerializer):
    request = RequestSerializer(read_only=True)
    request_id = serializers.PrimaryKeyRelatedField(source='request', queryset=Request.objects.all(), write_only=True)
    
    class Meta:
        model = Appointment
        fields = ['id', 'request', 'request_id', 'notes']
