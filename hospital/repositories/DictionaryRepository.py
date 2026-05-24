from ..models import (
    WorkCategory, MaterialCategory, MedicineCategory, 
    ProcedureCategory, Doctor
)
from ..services.interfaces import DictionaryRepositoryProtocol


class DictionaryRepository(DictionaryRepositoryProtocol):
    """DAL для роботи з довідниками (класифікаціями)"""

    @staticmethod
    def get_all_work_categories():
        return WorkCategory.objects.all()

    @staticmethod
    def get_all_material_categories():
        return MaterialCategory.objects.all()

    @staticmethod
    def get_all_medicine_categories():
        return MedicineCategory.objects.all()

    @staticmethod
    def get_all_procedure_categories():
        return ProcedureCategory.objects.all()

    @staticmethod
    def get_all_doctors():
        return Doctor.objects.all()

    @staticmethod
    def create_work_category(name):
        return WorkCategory.objects.create(name=name)

    @staticmethod
    def create_material_category(name):
        return MaterialCategory.objects.create(name=name)

    @staticmethod
    def create_medicine_category(name):
        return MedicineCategory.objects.create(name=name)

    @staticmethod
    def create_procedure_category(name):
        return ProcedureCategory.objects.create(name=name)

    @staticmethod
    def create_doctor(full_name, specialization):
        return Doctor.objects.create(full_name=full_name, specialization=specialization)