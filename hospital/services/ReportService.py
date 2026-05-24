from hospital.services.interfaces import (
    FinancialReportRepositoryProtocol,
    PatientRepositoryProtocol,
    ProtocolRepositoryProtocol,
)


class ReportService:
    """BLL для генерації фінансових звітів та протоколів"""

    def __init__(
        self,
        report_repo: FinancialReportRepositoryProtocol,
        patient_repo: PatientRepositoryProtocol,
        protocol_repo: ProtocolRepositoryProtocol,
    ):
        self.report_repo = report_repo
        self.patient_repo = patient_repo
        self.protocol_repo = protocol_repo

    def get_work_category_financials(self):
        """Отримати фінансові дані за категоріями робіт"""
        return self.report_repo.get_work_category_financials()

    # def get_appointment_work_financials(self, appointment_work_id: int):
    #     """Розрахунок фінансових витрат на прийомі"""
    #     return self.report_repo.get_appointment_work_financials(appointment_work_id)

    def generate_patient_protocol(self, patient_id: int):
        """Генерувати детальний протокол пацієнта"""
        patient = self.patient_repo.get_by_id(patient_id)
        appointments = self.protocol_repo.get_patient_appointments(patient_id)

        return {
            'patient': patient,
            'appointments': appointments
        }
