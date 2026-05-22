from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    PatientViewSet, RequestViewSet, AppointmentViewSet, DoctorViewSet,
    WorkCategoryViewSet, MaterialCategoryViewSet, MedicineCategoryViewSet,
    ProcedureCategoryViewSet, AppointmentWorkViewSet, WorkMaterialViewSet,
    WorkMedicineViewSet, WorkProcedureViewSet, ReportViewSet, api_login,
)

router = DefaultRouter()
router.register(r'patients', PatientViewSet, basename='patient')
router.register(r'requests', RequestViewSet, basename='request')
router.register(r'appointments', AppointmentViewSet, basename='appointment')
router.register(r'doctors', DoctorViewSet, basename='doctor')
router.register(r'work-categories', WorkCategoryViewSet, basename='work-category')
router.register(r'material-categories', MaterialCategoryViewSet, basename='material-category')
router.register(r'medicine-categories', MedicineCategoryViewSet, basename='medicine-category')
router.register(r'procedure-categories', ProcedureCategoryViewSet, basename='procedure-category')
router.register(r'appointment-works', AppointmentWorkViewSet, basename='appointment-work')
router.register(r'reports', ReportViewSet, basename='report')

router.register(r'work-materials', WorkMaterialViewSet, basename='work-material')
router.register(r'work-medicines', WorkMedicineViewSet, basename='work-medicine')
router.register(r'work-procedures', WorkProcedureViewSet, basename='work-procedure')

urlpatterns = [
    path('login/', api_login, name='api-login'),
    path('api-auth/', include('rest_framework.urls')),
    path('', include(router.urls)),
]