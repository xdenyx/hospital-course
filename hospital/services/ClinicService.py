from ..repositories import (
    PatientRepository, FinancialReportRepository, ProtocolRepository, DictionaryRepository
)

class ClinicService:
    """
    Фасад для доступу до основних бізнес-функцій системи.
    """

    def __init__(self):
        self.patient_repo = PatientRepository()
        self.report_repo = FinancialReportRepository()
        self.protocol_repo = ProtocolRepository()
        self.dict_repo = DictionaryRepository()

    def get_patients_by_work_and_date(self, start_date: str, end_date: str, work_category_id: int):
        """Вибірка: Список пацієнтів, за якими виконувалися роботи за період"""
        if not (start_date and end_date and work_category_id):
            return None
        return self.patient_repo.find_by_period_and_work(start_date, end_date, work_category_id)

    def generate_financial_report(self):
        """Генерувати фінансовий звіт за класами процедур"""
        return self.report_repo.get_procedure_financials()

    def generate_work_financial_report(self):
        """Генерувати фінансовий звіт за категоріями робіт"""
        return self.report_repo.get_work_category_financials()

    def generate_patient_protocol(self, patient_id: int):
        """Генерувати детальний протокол пацієнта"""
        patient = self.patient_repo.get_by_id(patient_id)
        appointments = self.protocol_repo.get_patient_appointments(patient_id)

        return {
            'patient': patient,
            'appointments': appointments
        }

    def get_work_categories_for_filter(self):
        """Отримати категорії робіт для фільтрації"""
        return self.dict_repo.get_all_work_categories()