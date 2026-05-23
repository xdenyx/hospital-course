import os
import random
from datetime import date, timedelta

from locust import HttpUser, between, task


class HospitalApiUser(HttpUser):
    wait_time = between(1, 3)
    host = os.getenv('LOCUST_HOST', 'http://127.0.0.1:8000')

    def on_start(self):
        self.work_ids = []
        self.authenticate()
        self.load_reference_data()

    def authenticate(self):
        token = os.getenv('LOCUST_TOKEN')
        if token:
            self.client.headers.update({'Authorization': f'Token {token}'})
            return

        username = os.getenv('LOCUST_USERNAME')
        password = os.getenv('LOCUST_PASSWORD')
        if not username or not password:
            raise RuntimeError('Set LOCUST_TOKEN or LOCUST_USERNAME and LOCUST_PASSWORD')

        response = self.client.post(
            '/api/login/',
            json={'username': username, 'password': password},
            name='/api/login/',
        )
        if response.status_code != 200:
            raise RuntimeError(f'Login failed with status {response.status_code}')

        payload = response.json()
        token_value = payload.get('token')
        if not token_value:
            raise RuntimeError('Login response did not contain token')

        self.client.headers.update({'Authorization': f'Token {token_value}'})

    def load_reference_data(self):
        response = self.client.get('/api/work-categories/', name='/api/work-categories/')
        if response.status_code == 200:
            try:
                self.work_ids = [row['id'] for row in response.json()]
            except Exception:
                self.work_ids = []

    @task(5)
    def read_patients(self):
        self.client.get('/api/patients/', name='/api/patients/')

    @task(4)
    def read_requests(self):
        self.client.get('/api/requests/', name='/api/requests/')

    @task(4)
    def read_appointments(self):
        self.client.get('/api/appointments/', name='/api/appointments/')

    @task(3)
    def read_doctors(self):
        self.client.get('/api/doctors/', name='/api/doctors/')

    @task(2)
    def read_categories(self):
        self.client.get('/api/work-categories/', name='/api/work-categories/')
        self.client.get('/api/material-categories/', name='/api/material-categories/')
        self.client.get('/api/medicine-categories/', name='/api/medicine-categories/')
        self.client.get('/api/procedure-categories/', name='/api/procedure-categories/')

    @task(2)
    def search_patients_by_work(self):
        if not self.work_ids:
            return

        work_id = random.choice(self.work_ids)
        today = date.today()
        start_date = (today - timedelta(days=30)).isoformat()
        end_date = today.isoformat()

        self.client.get(
            f'/api/patients/by-work/?work_id={work_id}&start_date={start_date}&end_date={end_date}',
            name='/api/patients/by-work/',
        )

    @task(1)
    def read_reports(self):
        if os.getenv('LOCUST_ADMIN', '').lower() not in {'1', 'true', 'yes'}:
            return

        self.client.get('/api/reports/work-financials/', name='/api/reports/work-financials/')