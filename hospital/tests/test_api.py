from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from ..models import (
    Doctor,
    MaterialCategory,
    MedicineCategory,
    Patient,
    ProcedureCategory,
    Request,
    WorkCategory,
)


class ApiSystemTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.user = user_model.objects.create_user(username='tester', password='secret123')
        self.token = Token.objects.create(user=self.user)

        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')

        self.patient = Patient.objects.create(
            full_name='Системний Пацієнт',
            date_of_birth=timezone.now().date() - timedelta(days=25 * 365),
        )
        self.doctor = Doctor.objects.create(full_name='Системний Лікар', specialization='Ортопед')
        self.request = Request.objects.create(datetime=timezone.now(), patient=self.patient, doctor=self.doctor)
        self.work_category = WorkCategory.objects.create(name='Огляд', price=Decimal('120.00'))
        self.material_category = MaterialCategory.objects.create(name='Вата', cost_price=Decimal('10.0'))
        self.medicine_category = MedicineCategory.objects.create(name='Спрей', cost_price=Decimal('30.0'))
        self.procedure_category = ProcedureCategory.objects.create(name='Полірування', cost_price=Decimal('5.0'))

    def test_patient_by_work_invalid_date_range_returns_400(self):
        url = (
            '/api/patients/by-work/'
            f'?work_id={self.work_category.id}&start_date=2026-12-31&end_date=2026-01-01'
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.data)

    def test_system_flow_appointment_work_and_report(self):
        create_appointment = self.client.post(
            '/api/appointments/',
            {'request_id': self.request.id, 'notes': 'Системний тест'},
            format='json',
        )
        self.assertEqual(create_appointment.status_code, 201)
        appointment_id = create_appointment.data['id']

        create_work = self.client.post(
            '/api/appointment-works/',
            {'appointment': appointment_id, 'work_category': self.work_category.id},
            format='json',
        )
        self.assertEqual(create_work.status_code, 201)
        work_id = create_work.data['id']

        self.assertEqual(
            self.client.post(
                '/api/work-materials/',
                {
                    'appointment_work': work_id,
                    'category': self.material_category.id,
                    'quantity': 2,
                },
                format='json',
            ).status_code,
            201,
        )
        self.assertEqual(
            self.client.post(
                '/api/work-medicines/',
                {
                    'appointment_work': work_id,
                    'category': self.medicine_category.id,
                    'quantity': 1,
                },
                format='json',
            ).status_code,
            201,
        )
        self.assertEqual(
            self.client.post(
                '/api/work-procedures/',
                {'appointment_work': work_id, 'category': self.procedure_category.id},
                format='json',
            ).status_code,
            201,
        )

        detail = self.client.get(f'/api/appointments/{appointment_id}/')
        self.assertEqual(detail.status_code, 200)
        self.assertTrue(len(detail.data['works']) > 0)

        work = detail.data['works'][0]
        self.assertEqual(Decimal(str(work['price'])), Decimal('120.00'))
        self.assertEqual(Decimal(str(work['cost'])), Decimal('55.00'))
        self.assertEqual(Decimal(str(work['profit'])), Decimal('65.00'))

        report = self.client.get('/api/reports/work-financials/')
        self.assertEqual(report.status_code, 200)
        self.assertTrue(any(row['id'] == self.work_category.id for row in report.data))

    def test_update_patient_data_system(self):
        # Редагування даних пацієнта
        url = f'/api/patients/{self.patient.id}/'
        updated_data = {
            'full_name': 'Оновлений Пацієнт',
            'date_of_birth': self.patient.date_of_birth.strftime('%Y-%m-%d')
        }
        
        response = self.client.put(url, updated_data, format='json')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['full_name'], 'Оновлений Пацієнт')
        
        # Перевіряємо, що в базі теж змінилось
        self.patient.refresh_from_db()
        self.assertEqual(self.patient.full_name, 'Оновлений Пацієнт')
    
    def test_patient_by_work_valid_search(self):
        # пошук пацієнта за датою та роботою
        # Спочатку створюємо прийом і роботу, щоб було кого шукати
        appointment = self.client.post('/api/appointments/', 
            {'request_id': self.request.id, 'notes': 'Тест'}, format='json'
        ).data
        
        self.client.post('/api/appointment-works/', 
            {'appointment': appointment['id'], 'work_category': self.work_category.id}, format='json'
        )

        # Робимо пошук
        today = timezone.now().date()
        start_date = (today - timedelta(days=1)).strftime('%Y-%m-%d')
        end_date = (today + timedelta(days=1)).strftime('%Y-%m-%d')
        
        url = f'/api/patients/by-work/?work_id={self.work_category.id}&start_date={start_date}&end_date={end_date}'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        # Перевіряємо, що наш пацієнт є у видачі
        self.assertTrue(any(p['id'] == self.patient.id for p in response.data))