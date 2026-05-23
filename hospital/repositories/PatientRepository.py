from ..models import Patient

class PatientRepository:
    """DAL для роботи з пацієнтами"""

    @staticmethod
    def get_by_id(patient_id: int) -> Patient:
        return Patient.objects.get(id=patient_id)

    @staticmethod
    def get_all():
        return Patient.objects.all()

    @staticmethod
    def create(full_name: str, date_of_birth, phone_number: str = None):
        return Patient.objects.create(
            full_name=full_name,
            date_of_birth=date_of_birth,
            phone_number=phone_number
        )

    @staticmethod
    def update(patient_id: int, **kwargs):
        patient = Patient.objects.get(id=patient_id)
        for key, value in kwargs.items():
            setattr(patient, key, value)
        patient.save()
        return patient

    @staticmethod
    def delete(patient_id: int):
        Patient.objects.get(id=patient_id).delete()

    @staticmethod
    def find_by_period_and_work(start_date, end_date, work_category_id):
        # Вибірка: Список пацієнтів, за якими виконувалися роботи за період
        from . import AppointmentRepository
        appointments = AppointmentRepository.get_by_work_and_period(
            start_date, end_date, work_category_id
        )
        return list({app.request.patient for app in appointments})