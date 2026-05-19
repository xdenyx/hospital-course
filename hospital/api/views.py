from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from ..models import (
    Patient, Request, Appointment, Doctor, WorkCategory, MaterialCategory,
    MedicineCategory, ProcedureCategory, AppointmentWork, WorkMaterial,
    WorkMedicine, WorkProcedure
)
from .serializers import (
    PatientSerializer, RequestSerializer, AppointmentSerializer,
    DoctorSerializer, WorkCategorySerializer, MaterialCategorySerializer,
    MedicineCategorySerializer, ProcedureCategorySerializer,
    AppointmentWorkSerializer, WorkMaterialSerializer, WorkMedicineSerializer,
    WorkProcedureSerializer, AppointmentDetailSerializer
)


class PatientViewSet(viewsets.ModelViewSet):
    """
    API для управління пацієнтами.
    
    Доступні операції:
    - GET /api/patients/ - список всіх пацієнтів
    - GET /api/patients/{id}/ - деталі пацієнта
    - POST /api/patients/ - створити пацієнта
    - PUT /api/patients/{id}/ - оновити пацієнта
    - DELETE /api/patients/{id}/ - видалити пацієнта
    - GET /api/patients/by-work/?work_id={id}&start_date=YYYY-MM-DD&end_date=YYYY-MM-DD - вибірка пацієнтів по роботам за період
    """
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'], url_path='by-work')
    def by_work(self, request):
        work_id = request.query_params.get('work_id')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if not work_id:
            return Response({'error': 'work_id параметр обов\'язковий'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Знайти всі роботи цієї категорії
        appointment_works = AppointmentWork.objects.filter(work_category_id=work_id)
        
        # Фільтрувати за датою
        if start_date and end_date:
            # Використовуємо __date для безпечного порівняння без конфліктів часових поясів
            appointment_works = appointment_works.filter(
                appointment__request__datetime__date__gte=start_date,
                appointment__request__datetime__date__lte=end_date
            )
        
        # Отримуємо ID пацієнтів через прямий ланцюжок зв'язків (набагато надійніше)
        patient_ids = appointment_works.values_list('appointment__request__patient_id', flat=True)
        
        # Отримуємо унікальних пацієнтів за знайденими ID
        patients = Patient.objects.filter(id__in=patient_ids).distinct()
        
        serializer = self.get_serializer(patients, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'], url_path='protocol')
    def protocol(self, request, pk=None):
        """
        Возвращает детальный медицинский протокол по выбранному пациенту:
        все приемы, даты, ответственные врачи, списки работ, расходов и прибыли.
        """
        patient = self.get_object()
        # Находим все приемы, связанные с заявками этого пациента
        appointments = Appointment.objects.filter(request__patient=patient).order_by('-request__datetime')
        
        # Используем AppointmentDetailSerializer, так как в нем уже настроена 
        # глубокая вложенность (works -> materials, medicines, procedures)
        from .serializers import AppointmentDetailSerializer
        serializer = AppointmentDetailSerializer(appointments, many=True)
        return Response(serializer.data)

class RequestViewSet(viewsets.ModelViewSet):
    """
    API для управління заявками на прийом.
    
    Доступні операції:
    - GET /api/requests/ - список всіх заявок
    - GET /api/requests/{id}/ - деталі заявки
    - POST /api/requests/ - створити заявку
    - PUT /api/requests/{id}/ - оновити заявку
    - DELETE /api/requests/{id}/ - видалити заявку
    """
    queryset = Request.objects.all()
    serializer_class = RequestSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        serializer.save()


class AppointmentViewSet(viewsets.ModelViewSet):
    """
    API для управління прийомами.
    
    Доступні операції:
    - GET /api/appointments/ - список всіх прийомів
    - GET /api/appointments/{id}/ - деталі прийому
    - POST /api/appointments/ - створити прийом
    - PUT /api/appointments/{id}/ - оновити прийом
    - DELETE /api/appointments/{id}/ - видалити прийом
    """
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return AppointmentDetailSerializer
        return AppointmentSerializer

    def create(self, request, *args, **kwargs):
        # Normalize incoming payload: prefer `request_id` and remove `request` to avoid
        # PrimaryKeyRelatedField validation errors when a numeric 0 or invalid PK is present.
        import logging
        logger = logging.getLogger(__name__)
        try:
            data = request.data.copy()
        except Exception:
            data = dict(request.data)

        # Also print to stdout for dev debugging
        try:
            print("AppointmentViewSet.create raw payload:", request.data)
        except Exception:
            pass
        logger.error(f"AppointmentViewSet.create raw payload: {request.data}")

        # If client sent 'request', move it to 'request_id'
        if 'request' in data and 'request_id' not in data:
            data['request_id'] = data.get('request')
            data.pop('request', None)

        # Manually create Appointment to avoid ModelSerializer requiring 'request' before we map 'request_id'.
        request_id_val = data.get('request_id')
        if not request_id_val:
            return Response({'request_id': 'This field is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            req_obj = Request.objects.get(id=request_id_val)
        except Request.DoesNotExist:
            return Response({'request_id': 'Request not found.'}, status=status.HTTP_400_BAD_REQUEST)

        # Check OneToOne constraint: a Request can have only one Appointment
        if Appointment.objects.filter(request=req_obj).exists():
            return Response({'request': 'This request already has an appointment.'}, status=status.HTTP_400_BAD_REQUEST)

        notes_val = data.get('notes', '')
        appointment = Appointment.objects.create(request=req_obj, notes=notes_val)

        # Serialize created object with detail serializer
        out_serializer = AppointmentDetailSerializer(appointment, context={'request': request})
        headers = self.get_success_headers(out_serializer.data)
        return Response(out_serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class DoctorViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API для отримання інформації про лікарів.
    
    Доступні операції:
    - GET /api/doctors/ - список всіх лікарів
    - GET /api/doctors/{id}/ - деталі лікаря
    """
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer
    permission_classes = [IsAuthenticated]


class WorkCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API для управління категоріями робіт.
    
    Доступні операції:
    - GET /api/work-categories/ - список категорій робіт
    - POST /api/work-categories/ - створити категорію роботи
    """
    queryset = WorkCategory.objects.all()
    serializer_class = WorkCategorySerializer
    permission_classes = [IsAuthenticated]


class MaterialCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API для управління категоріями матеріалів.
    
    Доступні операції:
    - GET /api/material-categories/ - список категорій матеріалів
    - POST /api/material-categories/ - створити категорію матеріалу
    """
    queryset = MaterialCategory.objects.all()
    serializer_class = MaterialCategorySerializer
    permission_classes = [IsAuthenticated]


class MedicineCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API для управління категоріями ліків.
    
    Доступні операції:
    - GET /api/medicine-categories/ - список категорій ліків
    - POST /api/medicine-categories/ - створити категорію ліку
    """
    queryset = MedicineCategory.objects.all()
    serializer_class = MedicineCategorySerializer
    permission_classes = [IsAuthenticated]


class ProcedureCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API для управління категоріями процедур.
    
    Доступні операції:
    - GET /api/procedure-categories/ - список категорій процедур
    - POST /api/procedure-categories/ - створити категорію процедури
    """
    queryset = ProcedureCategory.objects.all()
    serializer_class = ProcedureCategorySerializer
    permission_classes = [IsAuthenticated]


class AppointmentWorkViewSet(viewsets.ModelViewSet):
    """
    управління роботами
    - GET /api/appointment-works/ - список робіт
    - POST /api/appointment-works/ - додати роботу
    """
    queryset = AppointmentWork.objects.all()
    serializer_class = AppointmentWorkSerializer
    permission_classes = [IsAuthenticated]

class WorkMaterialViewSet(viewsets.ModelViewSet):
    queryset = WorkMaterial.objects.all()
    serializer_class = WorkMaterialSerializer
    permission_classes = [IsAuthenticated]

class WorkMedicineViewSet(viewsets.ModelViewSet):
    queryset = WorkMedicine.objects.all()
    serializer_class = WorkMedicineSerializer
    permission_classes = [IsAuthenticated]

class WorkProcedureViewSet(viewsets.ModelViewSet):
    queryset = WorkProcedure.objects.all()
    serializer_class = WorkProcedureSerializer
    permission_classes = [IsAuthenticated]