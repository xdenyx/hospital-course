from ..repositories import PatientRepository

class ClinicService:

    def __init__(self):
        self.patient_repo = PatientRepository()

    def get_patients_by_work_and_date(self, start_date: str, end_date: str, work_category_id: int):
        """Вибірка: Список пацієнтів, за якими виконувалися роботи за період"""
        if not (start_date and end_date and work_category_id):
            return None
        if start_date > end_date:
            raise ValueError('Дата початку не може бути пізніше дати кінця.')
        return self.patient_repo.find_by_period_and_work(start_date, end_date, work_category_id)
