from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

from ..models import (
    Request, Appointment, Doctor, AppointmentWork, WorkMaterial,
    WorkMedicine, WorkProcedure
)
from .serializers import (
    PatientSerializer, RequestSerializer, AppointmentSerializer,
    DoctorSerializer, WorkCategorySerializer, MaterialCategorySerializer,
    MedicineCategorySerializer, ProcedureCategorySerializer,
    AppointmentWorkSerializer, WorkMaterialSerializer, WorkMedicineSerializer,
    WorkProcedureSerializer, AppointmentDetailSerializer
)
from hospital.services import ( 
    PatientService, AppointmentService, DictionaryService, 
    ReportService, ClinicService, RequestService,
    )
from hospital.repositories import (
    PatientRepository,
    AppointmentRepository,
    RequestRepository,
    DictionaryRepository,
    FinancialReportRepository,
    ProtocolRepository,
)

class PatientViewSet(viewsets.ModelViewSet):
    # API для управління пацієнтами.
    serializer_class = PatientSerializer
    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 1. Створюємо конкретну інфраструктуру (репозиторій)
        repo = PatientRepository()
        # 2. Передаємо її в сервіси (впровадження залежності)
        self.patient_service = PatientService(patient_repo=repo)
        self.clinic_service = ClinicService(patient_repo=repo)

    def get_queryset(self):
        return self.patient_service.get_all_patients()

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        patient = self.get_object()
        serializer = self.get_serializer(patient, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        try:
            updated_patient = self.patient_service.update_patient(patient.id, serializer.validated_data)
        except ValueError as exc:
            return Response({'error': str(exc)}, status=status.HTTP_409_CONFLICT)

        output_serializer = self.get_serializer(updated_patient)
        return Response(output_serializer.data)

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)
    
    @action(detail=False, methods=['get'], url_path='by-work')
    def by_work(self, request):
        work_id = request.query_params.get('work_id')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        if not work_id:
            return Response({'error': 'work_id параметр обов\'язковий'}, status=status.HTTP_400_BAD_REQUEST)

        if not (start_date and end_date):
            return Response({'error': 'start_date та end_date параметри обов\'язкові'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            patients = self.clinic_service.get_patients_by_work_and_date(
                start_date, end_date, work_id
            )
        except ValueError as exc:
            return Response({'error': str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = self.get_serializer(patients, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'], url_path='protocol')
    def get_protocol(self, request, pk=None):
        report_repo = FinancialReportRepository()
        patient_repo = PatientRepository()
        protocol_repo = ProtocolRepository()
        report_service = ReportService(report_repo=report_repo, patient_repo=patient_repo, protocol_repo=protocol_repo)
        
        try:
            protocol_data = report_service.generate_patient_protocol(patient_id=int(pk))
            
            if not protocol_data or not protocol_data.get('appointments'):
                return Response([], status=status.HTTP_200_OK)

            appointments = protocol_data['appointments']
            
            serializer = AppointmentDetailSerializer(appointments, many=True)
            
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {"error": f"Помилка при генерації протоколу: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class RequestViewSet(viewsets.ModelViewSet):
    # API для управління заявками на прийом.
    serializer_class = RequestSerializer
    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.request_service = RequestService(request_repo=RequestRepository())

    def get_queryset(self):
        return self.request_service.get_all_requests()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        created_request = self.request_service.create_request(serializer.validated_data)
        output_serializer = self.get_serializer(created_request)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        request_obj = self.get_object()
        serializer = self.get_serializer(request_obj, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        try:
            updated_request = self.request_service.update_request(request_obj.id, serializer.validated_data)
        except ValueError as exc:
            return Response({'error': str(exc)}, status=status.HTTP_409_CONFLICT)

        output_serializer = self.get_serializer(updated_request)
        return Response(output_serializer.data)

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)


class AppointmentViewSet(viewsets.ModelViewSet):

    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.appointment_service = AppointmentService(appointment_repo=AppointmentRepository())

    def get_queryset(self):
        return Appointment.objects.all()

    def get_serializer_class(self):
        if self.action in ['retrieve', 'create']:
            return AppointmentDetailSerializer
        return AppointmentSerializer

    def create(self, request, *args, **kwargs):
        try:
            # Викликаємо метод сервісу, створить прийом,
            # розкидає роботи, ліки, матеріали та прорахує фінанси
            appointment = self.appointment_service.process_appointment(
                request_id=request.data.get('request_id'),
                notes=request.data.get('notes', ''),
                works_data=request.data.get('works', [])
            )
            serializer = AppointmentDetailSerializer(appointment)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response(
                {"error": f"Не вдалося обробити прийом: {str(e)}"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

    def retrieve(self, request, pk=None, *args, **kwargs):
        try:
            appointment = self.appointment_service.get_appointment(appointment_id=int(pk))
            if not appointment:
                return Response({"detail": "Прийом не знайдено"}, status=status.HTTP_404_NOT_FOUND)
                
            serializer = AppointmentDetailSerializer(appointment)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None, *args, **kwargs):
        try:
            notes = request.data.get('notes', '')
            version = request.data.get('version')
            appointment = self.appointment_service.update_appointment(
                appointment_id=int(pk), 
                notes=notes,
                version=version,
            )
            
            if not appointment:
                return Response({"detail": "Прийом не знайдено для оновлення"}, status=status.HTTP_404_NOT_FOUND)
                
            serializer = AppointmentSerializer(appointment)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class DoctorViewSet(viewsets.ReadOnlyModelViewSet):
    # API для отримання інформації про лікарів.
    serializer_class = DoctorSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Doctor.objects.all()


class WorkCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    # API для управління категоріями робіт.
    serializer_class = WorkCategorySerializer
    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        repo = DictionaryRepository()
        self.dict_service = DictionaryService(dict_repo=repo)

    def get_queryset(self):
        return self.dict_service.get_all_work_categories()


class MaterialCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    # API для управління категоріями матеріалів.
    serializer_class = MaterialCategorySerializer
    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        repo = DictionaryRepository()
        self.dict_service = DictionaryService(dict_repo=repo)

    def get_queryset(self):
        return self.dict_service.get_all_material_categories()


class MedicineCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    # API для управління категоріями ліків.
    serializer_class = MedicineCategorySerializer
    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        repo = DictionaryRepository()
        self.dict_service = DictionaryService(dict_repo=repo)

    def get_queryset(self):
        return self.dict_service.get_all_medicine_categories()


class ProcedureCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    # API для управління категоріями процедур.
    serializer_class = ProcedureCategorySerializer
    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        repo = DictionaryRepository()
        self.dict_service = DictionaryService(dict_repo=repo)

    def get_queryset(self):
        return self.dict_service.get_all_procedure_categories()


class AppointmentWorkViewSet(viewsets.ModelViewSet):
    # управління роботами
    queryset = AppointmentWork.objects.all()
    serializer_class = AppointmentWorkSerializer
    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.appointment_service = AppointmentService(appointment_repo=AppointmentRepository())

    def get_permissions(self):
        if self.request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            return [IsAuthenticated(), IsAdminUser()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        work = self.appointment_service.create_appointment_work(serializer.validated_data)
        serializer.instance = work

    def perform_update(self, serializer):
        work = self.appointment_service.update_appointment_work(serializer.instance, serializer.validated_data)
        serializer.instance = work

class WorkMaterialViewSet(viewsets.ModelViewSet):
    queryset = WorkMaterial.objects.all()
    serializer_class = WorkMaterialSerializer
    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.appointment_service = AppointmentService(appointment_repo=AppointmentRepository())

    def get_permissions(self):
        if self.request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            return [IsAuthenticated(), IsAdminUser()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        material = self.appointment_service.create_work_material(serializer.validated_data)
        serializer.instance = material

    def perform_update(self, serializer):
        material = self.appointment_service.update_work_material(serializer.instance, serializer.validated_data)
        serializer.instance = material

    def perform_destroy(self, instance):
        self.appointment_service.delete_work_material(instance)

class WorkMedicineViewSet(viewsets.ModelViewSet):
    queryset = WorkMedicine.objects.all()
    serializer_class = WorkMedicineSerializer
    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.appointment_service = AppointmentService(appointment_repo=AppointmentRepository())

    def get_permissions(self):
        if self.request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            return [IsAuthenticated(), IsAdminUser()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        medicine = self.appointment_service.create_work_medicine(serializer.validated_data)
        serializer.instance = medicine

    def perform_update(self, serializer):
        medicine = self.appointment_service.update_work_medicine(serializer.instance, serializer.validated_data)
        serializer.instance = medicine

    def perform_destroy(self, instance):
        self.appointment_service.delete_work_medicine(instance)

class WorkProcedureViewSet(viewsets.ModelViewSet):
    queryset = WorkProcedure.objects.all()
    serializer_class = WorkProcedureSerializer
    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.appointment_service = AppointmentService(appointment_repo=AppointmentRepository())

    def get_permissions(self):
        if self.request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            return [IsAuthenticated(), IsAdminUser()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        procedure = self.appointment_service.create_work_procedure(serializer.validated_data)
        serializer.instance = procedure

    def perform_update(self, serializer):
        procedure = self.appointment_service.update_work_procedure(serializer.instance, serializer.validated_data)
        serializer.instance = procedure

    def perform_destroy(self, instance):
        self.appointment_service.delete_work_procedure(instance)


class ReportViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        report_repo = FinancialReportRepository()
        patient_repo = PatientRepository()
        protocol_repo = ProtocolRepository()
        self.report_service = ReportService(report_repo=report_repo, patient_repo=patient_repo, protocol_repo=protocol_repo)

    @action(detail=False, methods=['get'], url_path='work-financials')
    def work_financials(self, request):
        queryset = self.report_service.get_work_category_financials()
        data = list(queryset.values(
            'id',
            'name',
            'total_income',
            'work_cost',
            'materials_cost',
            'medicines_cost',
            'procedures_cost',
            'total_expenses',
            'net_profit',
        ))
        return Response(data, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([AllowAny])
def api_login(request):
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(username=username, password=password)
    
    if user:
        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'is_admin': user.is_staff or user.is_superuser
        })
    return Response({'error': 'Невірний логін або пароль'}, status=status.HTTP_400_BAD_REQUEST)