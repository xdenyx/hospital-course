from django.db import transaction
from hospital.services.interfaces import AppointmentRepositoryProtocol


class AppointmentService:
    """BLL для управління процесом прийому пацієнта"""

    def __init__(self, appointment_repo: AppointmentRepositoryProtocol):
        self.appointment_repo = appointment_repo

    def process_appointment(self, request_id, notes, works_data):
        """Обробити прийом та заповнити дані про роботи, матеріали, ліки, процедури"""
        with transaction.atomic():
            appointment = self.appointment_repo.create_appointment(request_id, notes)

            for work_item in works_data:
                work = self.create_appointment_work({
                    'appointment_id': appointment.id,
                    'work_category_id': work_item['work_category_id'],
                    'price': work_item.get('price'),
                })

                for material in work_item.get('materials', []):
                    self.create_work_material({
                        'appointment_work_id': work.id,
                        'category_id': material['category_id'],
                        'quantity': material['quantity'],
                    })

                for medicine in work_item.get('medicines', []):
                    self.create_work_medicine({
                        'appointment_work_id': work.id,
                        'category_id': medicine['category_id'],
                        'quantity': medicine['quantity'],
                    })

                for procedure in work_item.get('procedures', []):
                    self.create_work_procedure({
                        'appointment_work_id': work.id,
                        'category_id': procedure['category_id'],
                    })

            return appointment

    def create_appointment_work(self, validated_data):
        appointment = validated_data.get('appointment')
        appointment_id = appointment.id if appointment is not None else validated_data['appointment_id']

        work_category = validated_data.get('work_category')
        work_category_id = work_category.id if work_category is not None else validated_data['work_category_id']

        price = validated_data.get('price')
        if price is None and work_category is not None:
            price = work_category.price

        work = self.appointment_repo.add_work(
            appointment_id=appointment_id,
            work_category_id=work_category_id,
            price=price,
            cost=0,
            profit=price or 0,
        )
        return self.recalculate_work_finances(work)

    def update_appointment_work(self, work, validated_data):
        work_category = validated_data.get('work_category')
        if work_category is not None:
            work.work_category = work_category

        if 'price' in validated_data:
            work.price = validated_data['price']
        elif work_category is not None:
            work.price = work_category.price

        if 'cost' in validated_data:
            work.cost = validated_data['cost']
        if 'profit' in validated_data:
            work.profit = validated_data['profit']

        work.save()
        return self.recalculate_work_finances(work)

    def create_work_material(self, validated_data):
        appointment_work = validated_data.get('appointment_work')
        appointment_work_id = appointment_work.id if appointment_work is not None else validated_data['appointment_work_id']
        category = validated_data.get('category')
        category_id = category.id if category is not None else validated_data['category_id']

        material = self.appointment_repo.add_material(
            appointment_work_id=appointment_work_id,
            material_category_id=category_id,
            quantity=validated_data['quantity'],
            cost=0,
        )
        self.recalculate_work_finances(material.appointment_work)
        return material

    def update_work_material(self, material, validated_data):
        if 'category' in validated_data:
            material.category = validated_data['category']
        if 'quantity' in validated_data:
            material.quantity = validated_data['quantity']
        material.save()
        self.recalculate_work_finances(material.appointment_work)
        return material

    def delete_work_material(self, material):
        appointment_work = material.appointment_work
        material.delete()
        return self.recalculate_work_finances(appointment_work)

    def create_work_medicine(self, validated_data):
        appointment_work = validated_data.get('appointment_work')
        appointment_work_id = appointment_work.id if appointment_work is not None else validated_data['appointment_work_id']
        category = validated_data.get('category')
        category_id = category.id if category is not None else validated_data['category_id']

        medicine = self.appointment_repo.add_medicine(
            appointment_work_id=appointment_work_id,
            medicine_category_id=category_id,
            quantity=validated_data['quantity'],
            cost=0,
        )
        self.recalculate_work_finances(medicine.appointment_work)
        return medicine

    def update_work_medicine(self, medicine, validated_data):
        if 'category' in validated_data:
            medicine.category = validated_data['category']
        if 'quantity' in validated_data:
            medicine.quantity = validated_data['quantity']
        medicine.save()
        self.recalculate_work_finances(medicine.appointment_work)
        return medicine

    def delete_work_medicine(self, medicine):
        appointment_work = medicine.appointment_work
        medicine.delete()
        return self.recalculate_work_finances(appointment_work)

    def create_work_procedure(self, validated_data):
        appointment_work = validated_data.get('appointment_work')
        appointment_work_id = appointment_work.id if appointment_work is not None else validated_data['appointment_work_id']
        category = validated_data.get('category')
        category_id = category.id if category is not None else validated_data['category_id']

        procedure = self.appointment_repo.add_procedure(
            appointment_work_id=appointment_work_id,
            procedure_category_id=category_id,
            cost=0,
        )
        self.recalculate_work_finances(procedure.appointment_work)
        return procedure

    def update_work_procedure(self, procedure, validated_data):
        if 'category' in validated_data:
            procedure.category = validated_data['category']
        procedure.save()
        self.recalculate_work_finances(procedure.appointment_work)
        return procedure

    def delete_work_procedure(self, procedure):
        appointment_work = procedure.appointment_work
        procedure.delete()
        return self.recalculate_work_finances(appointment_work)

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