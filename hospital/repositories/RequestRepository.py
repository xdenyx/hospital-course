from ..models import Request

class RequestRepository:
    """DAL для роботи із заявками на прийом"""

    @staticmethod
    def create(datetime, patient_id, doctor_id=None):
        return Request.objects.create(
            datetime=datetime,
            patient_id=patient_id,
            doctor_id=doctor_id
        )

    @staticmethod
    def get_by_id(request_id):
        return Request.objects.select_related(
            'patient', 'doctor'
        ).get(id=request_id)

    @staticmethod
    def get_all():
        return Request.objects.select_related(
            'patient', 'doctor'
        ).order_by('-datetime')

    @staticmethod
    def update(request_id, **kwargs):
        request = Request.objects.get(id=request_id)
        for key, value in kwargs.items():
            if hasattr(request, key):
                setattr(request, key, value)
        request.save()
        return request

    @staticmethod
    def delete(request_id):
        Request.objects.get(id=request_id).delete()