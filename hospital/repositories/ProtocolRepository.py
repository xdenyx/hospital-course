from ..models import Appointment

class ProtocolRepository:
    """DAL для роботи з протоколами прийому"""

    @staticmethod
    def get_patient_appointments(patient_id: int):
        # Завантажуємо всі прийоми пацієнта з оптимізацією запитів до БД
        return Appointment.objects.filter(
            request__patient_id=patient_id
        ).select_related(
            'request', 'request__doctor'
        ).prefetch_related(
            'works',
            'works__materials__category',
            'works__medicines__category',
            'works__procedures__category',
            'works__work_category'
        ).order_by('-request__datetime')