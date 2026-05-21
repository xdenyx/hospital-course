from hospital.repositories import RequestRepository, AppointmentRepository

class AppointmentService:
    """BLL для управління процесом прийому пацієнта"""

    def __init__(self):
        self.request_repo = RequestRepository()
        self.appointment_repo = AppointmentRepository()

    def process_appointment(self, request_id, notes, works_data):
        """Обробити прийом та заповнити дані про роботи, матеріали, ліки, процедури"""
        # 1. Створюємо прийом
        appointment = self.appointment_repo.create_appointment(request_id, notes)

        # 2. Обробляємо кожну роботу в рамках прийому
        for work_item in works_data:
            work = self.appointment_repo.add_work(
                appointment_id=appointment.id,
                work_category_id=work_item['work_category_id'],
                cost=work_item.get('cost', 0),
                profit=work_item.get('profit', 0)
            )

            # 3. Додаємо матеріали
            for material in work_item.get('materials', []):
                self.appointment_repo.add_material(
                    appointment_work_id=work.id,
                    material_category_id=material['category_id'],
                    quantity=material['quantity'],
                    cost=material['cost']
                )

            # 4. Додаємо ліки
            for medicine in work_item.get('medicines', []):
                self.appointment_repo.add_medicine(
                    appointment_work_id=work.id,
                    medicine_category_id=medicine['category_id'],
                    quantity=medicine['quantity'],
                    cost=medicine['cost']
                )

            # 5. Додаємо процедури
            for procedure in work_item.get('procedures', []):
                self.appointment_repo.add_procedure(
                    appointment_work_id=work.id,
                    procedure_category_id=procedure['category_id'],
                    cost=procedure['cost']
                )

        return appointment

    @staticmethod
    def recalculate_work_finances(appointment_work):
        # автоматично витягує базову вартість з cost_price
        # 1. Рахуємо та оновлюємо кожен витрачений матеріал
        materials_cost = 0
        for m in appointment_work.materials.all():
            if m.category:
                base_cost = getattr(m.category, 'cost_price', 0)
                m.cost = base_cost * (m.quantity or 1)
                m.save()
                materials_cost += m.cost

        # 2. Рахуємо та оновлюємо кожні ліки
        medicines_cost = 0
        for med in appointment_work.medicines.all():
            if med.category:
                base_cost = getattr(med.category, 'cost_price', 0)
                med.cost = base_cost * (med.quantity or 1)
                med.save()
                medicines_cost += med.cost

        # 3. Рахуємо супутні процедури
        procedures_cost = 0
        for p in appointment_work.procedures.all():
            if p.category:
                base_cost = getattr(p.category, 'cost_price', 0)
                p.cost = base_cost
                p.save()
                procedures_cost += p.cost

        # 4. Оновлюємо фінанси самої роботи (AppointmentWork)
        appointment_work.cost = materials_cost + medicines_cost + procedures_cost
        appointment_work.profit = (appointment_work.price or 0) - appointment_work.cost
        appointment_work.save()

        return appointment_work

    def get_appointment(self, appointment_id):
        """Отримати прийом за ID"""
        return self.appointment_repo.get_by_id(appointment_id)

    def update_appointment(self, appointment_id, notes):
        """Оновити примітки прийому"""
        return self.appointment_repo.update_appointment(appointment_id, notes)