from datetime import timedelta
from decimal import Decimal

from django.test import TestCase
from django.utils import timezone

from ..models import (
    Appointment,
    AppointmentWork,
    Doctor,
    MaterialCategory,
    MedicineCategory,
    Patient,
    ProcedureCategory,
    Request,
    WorkCategory,
)
from ..services import AppointmentService, ClinicService, ReportService


class AppointmentServiceUnitTests(TestCase):
    def setUp(self):
        self.service = AppointmentService()
        self.patient = Patient.objects.create(
            full_name='Тестовий Пацієнт',
            date_of_birth=timezone.now().date() - timedelta(days=30 * 365),
        )
        self.doctor = Doctor.objects.create(full_name='Доктор Тест', specialization='Терапевт')
        self.request = Request.objects.create(
            datetime=timezone.now(),
            patient=self.patient,
            doctor=self.doctor,
        )
        self.appointment = Appointment.objects.create(request=self.request, notes='unit')
        self.work_category = WorkCategory.objects.create(name='Консультація', price=Decimal('100.00'))
        self.material_category = MaterialCategory.objects.create(name='Матеріал', cost_price=Decimal('10.0'))
        self.medicine_category = MedicineCategory.objects.create(name='Ліки', cost_price=Decimal('20.0'))
        self.procedure_category = ProcedureCategory.objects.create(name='Процедура', cost_price=Decimal('5.0'))

    def test_recalculate_finances_from_consumables(self):
        work = self.service.create_appointment_work(
            {
                'appointment': self.appointment,
                'work_category': self.work_category,
            }
        )

        self.service.create_work_material(
            {
                'appointment_work': work,
                'category': self.material_category,
                'quantity': Decimal('2.0'),
            }
        )
        self.service.create_work_medicine(
            {
                'appointment_work': work,
                'category': self.medicine_category,
                'quantity': Decimal('3.0'),
            }
        )
        self.service.create_work_procedure(
            {
                'appointment_work': work,
                'category': self.procedure_category,
            }
        )

        work.refresh_from_db()
        self.assertEqual(work.price, Decimal('100.00'))
        self.assertEqual(work.cost, Decimal('85.00'))
        self.assertEqual(work.profit, Decimal('15.00'))


class ClinicServiceUnitTests(TestCase):
    def test_invalid_period_raises_error(self):
        service = ClinicService()
        with self.assertRaises(ValueError):
            service.get_patients_by_work_and_date('2026-12-31', '2026-01-01', 1)

class ReportServiceUnitTests(TestCase):
    def setUp(self):
        self.service = ReportService()
        self.patient = Patient.objects.create(full_name='Тест', date_of_birth='1990-01-01')
        self.doctor = Doctor.objects.create(full_name='Лікар', specialization='Хірург')
        self.request = Request.objects.create(datetime=timezone.now(), patient=self.patient, doctor=self.doctor)
        self.appointment = Appointment.objects.create(request=self.request)
        
        self.work_category = WorkCategory.objects.create(name='Хірургія', price=Decimal('1000.00'))
        
        # Створюємо роботу з фіксованими показниками
        AppointmentWork.objects.create(
            appointment=self.appointment,
            work_category=self.work_category,
            price=Decimal('1000.00'),
            cost=Decimal('200.00'),
            profit=Decimal('800.00')
        )

    def test_get_work_category_financials(self):
        # Правильність агрегації фінансів у звіті
        report_data = self.service.get_work_category_financials()
        
        # Шукаємо нашу категорію у звіті
        work_report = next((row for row in report_data if row.id == self.work_category.id), None)
        
        self.assertIsNotNone(work_report)
        self.assertEqual(work_report.total_income, Decimal('1000.00'))
        self.assertEqual(work_report.work_cost, Decimal('200.00'))
        self.assertEqual(work_report.net_profit, Decimal('800.00'))