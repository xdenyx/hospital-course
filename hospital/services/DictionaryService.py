from hospital.repositories import DictionaryRepository

class DictionaryService:
    """BLL для управління довідниками"""

    def __init__(self):
        self.dict_repo = DictionaryRepository()

    # ===== Категорії робіт =====
    def get_all_work_categories(self):
        return self.dict_repo.get_all_work_categories()

    def create_work_category(self, name):
        return self.dict_repo.create_work_category(name)

    # ===== Категорії матеріалів =====
    def get_all_material_categories(self):
        return self.dict_repo.get_all_material_categories()

    def create_material_category(self, name):
        return self.dict_repo.create_material_category(name)

    # ===== Категорії ліків =====
    def get_all_medicine_categories(self):
        return self.dict_repo.get_all_medicine_categories()

    def create_medicine_category(self, name):
        return self.dict_repo.create_medicine_category(name)

    # ===== Категорії процедур =====
    def get_all_procedure_categories(self):
        return self.dict_repo.get_all_procedure_categories()

    def create_procedure_category(self, name):
        return self.dict_repo.create_procedure_category(name)

    # ===== Лікарі =====
    def get_all_doctors(self):
        return self.dict_repo.get_all_doctors()

    def create_doctor(self, full_name, specialization):
        return self.dict_repo.create_doctor(full_name, specialization)
