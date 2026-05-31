from hospital.services.interfaces import PatientRepositoryProtocol


class PatientService:
    """BLL для управління пацієнтами"""

    def __init__(self, patient_repo: PatientRepositoryProtocol):
        self.patient_repo = patient_repo

    def create_patient(self, full_name, date_of_birth, phone_number=None):
        """Створити нового пацієнта"""
        return self.patient_repo.create(full_name, date_of_birth, phone_number)

    def get_patient(self, patient_id):
        """Отримати пацієнта за ID"""
        return self.patient_repo.get_by_id(patient_id)

    def get_all_patients(self):
        """Отримати всіх пацієнтів"""
        return self.patient_repo.get_all()

    def update_patient(self, patient_id, validated_data: dict):
        """Оновити пацієнта з перевіркою версії."""
        patient = self.patient_repo.get_by_id(patient_id)
        expected_version = validated_data.get('version')
        if expected_version is not None and expected_version != patient.version:
            raise ValueError('Версія запису застаріла. Оновіть дані та повторіть спробу.')

        updated_fields = {}
        for field in ['full_name', 'date_of_birth', 'phone_number']:
            if field in validated_data:
                updated_fields[field] = validated_data[field]

        updated_fields['version'] = patient.version + 1
        return self.patient_repo.update(patient_id, **updated_fields)
