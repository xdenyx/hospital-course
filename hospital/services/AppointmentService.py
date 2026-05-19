from hospital.repositories import RequestRepository, AppointmentRepository

class AppointmentService:
    """BLL для управління процесом прийому пацієнта"""

    def __init__(self):
        self.request_repo = RequestRepository()
        self.appointment_repo = AppointmentRepository()

    def register_new_request(self, datetime, patient_id, doctor_id=None):
        """Сформувати заявку на прийом"""
        return self.request_repo.create(datetime, patient_id, doctor_id)

    def get_request(self, request_id):
        """Отримати заявку за ID"""
        return self.request_repo.get_by_id(request_id)

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

    def recalculate_work_finances(self, appointment_work_id):
        """АВТОМАТИЧЕСКИЙ РАСЧЕТ: Пересчитывает витрати та прибуток для конкретної роботи"""
        from hospital.models import AppointmentWork
        
        # Получаем работу со всеми вложенными материалами
        work = AppointmentWork.objects.get(id=appointment_work_id)
    
        # 1. Рахуємо витрати (матеріали + ліки + процедури + власна собівартість роботи)
        total_expenses = work.get_total_expenses()
        
        # 2. Дохід беремо безпосередньо з прайсу категорії роботи
        income = work.work_category.price
        
        # 3. Фіксуємо фінансовий зріз на момент прийому в транзакційну таблицю
        work.price = income
        work.cost = total_expenses
        work.profit = income - total_expenses
        work.save()

    def get_appointment(self, appointment_id):
        """Отримати прийом за ID"""
        return self.appointment_repo.get_by_id(appointment_id)

    def update_appointment(self, appointment_id, notes):
        """Оновити примітки прийому"""
        return self.appointment_repo.update_appointment(appointment_id, notes)