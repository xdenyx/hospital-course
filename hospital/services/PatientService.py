from hospital.repositories import PatientRepository

class PatientService:
    """BLL для управління пацієнтами"""

    def __init__(self):
        self.patient_repo = PatientRepository()

    def create_patient(self, full_name, date_of_birth):
        """Створити нового пацієнта"""
        return self.patient_repo.create(full_name, date_of_birth)

    def get_patient(self, patient_id):
        """Отримати пацієнта за ID"""
        return self.patient_repo.get_by_id(patient_id)

    def get_all_patients(self):
        """Отримати всіх пацієнтів"""
        return self.patient_repo.get_all()

    def update_patient(self, patient_id, **kwargs):
        """Оновити дані пацієнта"""
        return self.patient_repo.update(patient_id, **kwargs)

    def delete_patient(self, patient_id):
        """Видалити пацієнта"""
        return self.patient_repo.delete(patient_id)
