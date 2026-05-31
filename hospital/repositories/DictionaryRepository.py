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

    @staticmethod
    def update_work_category(category_id: int, **kwargs):
        cat = WorkCategory.objects.get(id=category_id)
        for k, v in kwargs.items():
            if hasattr(cat, k):
                setattr(cat, k, v)
        cat.save()
        return cat

    @staticmethod
    def update_material_category(category_id: int, **kwargs):
        cat = MaterialCategory.objects.get(id=category_id)
        for k, v in kwargs.items():
            if hasattr(cat, k):
                setattr(cat, k, v)
        cat.save()
        return cat

    @staticmethod
    def update_medicine_category(category_id: int, **kwargs):
        cat = MedicineCategory.objects.get(id=category_id)
        for k, v in kwargs.items():
            if hasattr(cat, k):
                setattr(cat, k, v)
        cat.save()
        return cat

    @staticmethod
    def update_procedure_category(category_id: int, **kwargs):
        cat = ProcedureCategory.objects.get(id=category_id)
        for k, v in kwargs.items():
            if hasattr(cat, k):
                setattr(cat, k, v)
        cat.save()
        return cat

    @staticmethod
    def update_doctor(doctor_id: int, **kwargs):
        doc = Doctor.objects.get(id=doctor_id)
        for k, v in kwargs.items():
            if hasattr(doc, k):
                setattr(doc, k, v)
        doc.save()
        return doc