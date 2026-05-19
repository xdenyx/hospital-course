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
    age = serializers.SerializerMethodField()
    
    class Meta:
        model = Patient
        fields = ['id', 'full_name', 'date_of_birth', 'age']
    
    def get_age(self, obj):
        from django.utils import timezone
        today = timezone.now().date()
        return today.year - obj.date_of_birth.year - (
            (today.month, today.day) < (obj.date_of_birth.month, obj.date_of_birth.day)
        )


class RequestSerializer(serializers.ModelSerializer):
    patient = PatientSerializer(read_only=True)
    patient_id = serializers.IntegerField(write_only=True)
    doctor = DoctorSerializer(read_only=True)
    doctor_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Request
        fields = ['id', 'patient', 'patient_id', 'datetime', 'doctor', 'doctor_id']
    
    def create(self, validated_data):
        patient_id = validated_data.pop('patient_id')
        doctor_id = validated_data.pop('doctor_id')
        
        patient = Patient.objects.get(id=patient_id)
        doctor = Doctor.objects.get(id=doctor_id)
        
        # створюємо заявку з лікарем та пацієнтом
        request = Request.objects.create(patient=patient, doctor=doctor, **validated_data)
        return request

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
        fields = ['id', 'appointment_work', 'category', 'category_name', 'quantity', 'cost']

    def create(self, validated_data):
        category = validated_data['category']
        quantity = validated_data.get('quantity', 1)
        
        # Находим базовую цену материала в справочнике и умножаем на количество
        category_cost = _find_price_value(category)
        validated_data['cost'] = category_cost * int(quantity)
        
        instance = super().create(validated_data)
        
        # Обновляем финансовые метрики в родительской работе
        appt_work = instance.appointment_work
        appt_work.cost = float(appt_work.cost or 0) + float(instance.cost)
        appt_work.profit = float(appt_work.price or 0) - float(appt_work.cost)
        appt_work.save()
        
        return instance


class WorkMedicineSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    cost = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    
    class Meta:
        model = WorkMedicine
        fields = ['id', 'appointment_work', 'category', 'category_name', 'quantity', 'cost']

    def create(self, validated_data):
        category = validated_data['category']
        quantity = validated_data.get('quantity', 1)
        
        category_cost = _find_price_value(category)
        validated_data['cost'] = category_cost * int(quantity)
        
        instance = super().create(validated_data)
        
        appt_work = instance.appointment_work
        appt_work.cost = float(appt_work.cost or 0) + float(instance.cost)
        appt_work.profit = float(appt_work.price or 0) - float(appt_work.cost)
        appt_work.save()
        
        return instance


class WorkProcedureSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    cost = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    
    class Meta:
        model = WorkProcedure
        fields = ['id', 'appointment_work', 'category', 'category_name', 'cost']

    def create(self, validated_data):
        category = validated_data['category']
        
        category_cost = _find_price_value(category)
        validated_data['cost'] = category_cost
        
        instance = super().create(validated_data)
        
        appt_work = instance.appointment_work
        appt_work.cost = float(appt_work.cost or 0) + float(instance.cost)
        appt_work.profit = float(appt_work.price or 0) - float(appt_work.cost)
        appt_work.save()
        
        return instance


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

    def create(self, validated_data):
        work_category = validated_data['work_category']
        
        # Автоматически вытягиваем стоимость
        if 'price' not in validated_data or validated_data['price'] is None:
            validated_data['price'] = _find_price_value(work_category)
        
        validated_data['cost'] = 0
        validated_data['profit'] = validated_data['price']
        
        return super().create(validated_data)


class AppointmentDetailSerializer(serializers.ModelSerializer):
    request = RequestSerializer(read_only=True)
    works = AppointmentWorkSerializer(many=True, read_only=True)
    
    class Meta:
        model = Appointment
        fields = ['id', 'request', 'works', 'notes']


class AppointmentSerializer(serializers.ModelSerializer):
    request = RequestSerializer(read_only=True)
    request_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = Appointment
        fields = ['id', 'request', 'request_id', 'notes']
    
    def create(self, validated_data):
        request_id = validated_data.pop('request_id')
        try:
            request = Request.objects.get(id=request_id)
            validated_data['request'] = request
        except Request.DoesNotExist:
            raise serializers.ValidationError({'request_id': 'Request не знайден'})
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        request_id = validated_data.pop('request_id', None)
        if request_id:
            try:
                request = Request.objects.get(id=request_id)
                validated_data['request'] = request
            except Request.DoesNotExist:
                raise serializers.ValidationError({'request_id': 'Request не знайден'})
        return super().update(instance, validated_data)

def _find_price_value(obj):
    if not obj:
        return 0.0
    from django.db.models import DecimalField, FloatField, IntegerField
    for field in obj._meta.fields:
        if field.name == 'id':
            continue
        if isinstance(field, (DecimalField, FloatField, IntegerField)):
            val = getattr(obj, field.name)
            if val is not None:
                return float(val)
    return 0.0