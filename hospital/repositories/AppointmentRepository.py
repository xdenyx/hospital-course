from ..models import Appointment, AppointmentWork, WorkMaterial, WorkMedicine, WorkProcedure
from ..services.interfaces import AppointmentRepositoryProtocol


class AppointmentRepository(AppointmentRepositoryProtocol):
    """DAL для роботи з прийомами пацієнтів"""

    @staticmethod
    def get_by_id(appointment_id: int):
        return Appointment.objects.select_related(
            'request', 'request__doctor', 'request__patient'
        ).prefetch_related(
            'works__materials__category',
            'works__medicines__category',
            'works__procedures__category',
            'works__work_category'
        ).get(id=appointment_id)

    @staticmethod
    def get_by_work_and_period(start_date, end_date, work_category_id):
        return Appointment.objects.filter(
            request__datetime__date__range=[start_date, end_date],
            works__work_category_id=work_category_id
        ).select_related('request__patient').distinct()

    @staticmethod
    def create_appointment(request_id, notes=""):
        return Appointment.objects.create(
            request_id=request_id,
            notes=notes
        )

    @staticmethod
    def update_appointment(appointment_id, notes=None):
        appointment = Appointment.objects.get(id=appointment_id)
        if notes is not None:
            appointment.notes = notes
        appointment.save()
        return appointment

    @staticmethod
    def add_work(appointment_id, work_category_id, price=None, cost=0, profit=0):
        payload = {
            'appointment_id': appointment_id,
            'work_category_id': work_category_id,
            'cost': cost,
            'profit': profit,
        }
        if price is not None:
            payload['price'] = price
        return AppointmentWork.objects.create(**payload)

    @staticmethod
    def add_material(appointment_work_id, material_category_id, quantity, cost):
        return WorkMaterial.objects.create(
            appointment_work_id=appointment_work_id,
            category_id=material_category_id,
            quantity=quantity,
            cost=cost
        )

    @staticmethod
    def add_medicine(appointment_work_id, medicine_category_id, quantity, cost):
        return WorkMedicine.objects.create(
            appointment_work_id=appointment_work_id,
            category_id=medicine_category_id,
            quantity=quantity,
            cost=cost
        )

    @staticmethod
    def add_procedure(appointment_work_id, procedure_category_id, cost):
        return WorkProcedure.objects.create(
            appointment_work_id=appointment_work_id,
            category_id=procedure_category_id,
            cost=cost
        )