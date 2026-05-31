from hospital.services.interfaces import DictionaryRepositoryProtocol


class DictionaryService:
    """BLL для управління довідниками"""

    def __init__(self, dict_repo: DictionaryRepositoryProtocol):
        self.dict_repo = dict_repo

    # ===== Категорії робіт =====
    def get_all_work_categories(self):
        return self.dict_repo.get_all_work_categories()

    def create_work_category(self, name):
        return self.dict_repo.create_work_category(name)

    def update_work_category(self, category_id: int, **kwargs):
        return self.dict_repo.update_work_category(category_id, **kwargs)

    # ===== Категорії матеріалів =====
    def get_all_material_categories(self):
        return self.dict_repo.get_all_material_categories()

    def create_material_category(self, name):
        return self.dict_repo.create_material_category(name)

    def update_material_category(self, category_id: int, **kwargs):
        return self.dict_repo.update_material_category(category_id, **kwargs)

    # ===== Категорії ліків =====
    def get_all_medicine_categories(self):
        return self.dict_repo.get_all_medicine_categories()

    def create_medicine_category(self, name):
        return self.dict_repo.create_medicine_category(name)

    def update_medicine_category(self, category_id: int, **kwargs):
        return self.dict_repo.update_medicine_category(category_id, **kwargs)

    # ===== Категорії процедур =====
    def get_all_procedure_categories(self):
        return self.dict_repo.get_all_procedure_categories()

    def create_procedure_category(self, name):
        return self.dict_repo.create_procedure_category(name)

    def update_procedure_category(self, category_id: int, **kwargs):
        return self.dict_repo.update_procedure_category(category_id, **kwargs)

    # ===== Лікарі =====
    def get_all_doctors(self):
        return self.dict_repo.get_all_doctors()

    def create_doctor(self, full_name, specialization):
        return self.dict_repo.create_doctor(full_name, specialization)

    def update_doctor(self, doctor_id: int, **kwargs):
        return self.dict_repo.update_doctor(doctor_id, **kwargs)
