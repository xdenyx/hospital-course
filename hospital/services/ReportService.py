from hospital.repositories import FinancialReportRepository, ProtocolRepository

class ReportService:
    """BLL для генерації фінансових звітів та протоколів"""

    def __init__(self):
        self.report_repo = FinancialReportRepository()
        self.protocol_repo = ProtocolRepository()

    def get_procedure_financials(self):
        """Отримати фінансові дані за класами процедур"""
        return self.report_repo.get_procedure_financials()

    def get_work_category_financials(self):
        """Отримати фінансові дані за категоріями робіт"""
        return self.report_repo.get_work_category_financials()

    def get_financials_by_date_range(self, start_date, end_date):
        """Отримати фінансові дані за період"""
        return self.report_repo.get_financials_by_date_range(start_date, end_date)

    def get_patient_protocol(self, patient_id):
        """Отримати детальний протокол пацієнта"""
        appointments = self.protocol_repo.get_patient_appointments(patient_id)
        return {
            'appointments': appointments,
            'total_count': appointments.count()
        }
