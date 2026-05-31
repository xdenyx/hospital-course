from hospital.services.interfaces import RequestRepositoryProtocol


class RequestService:
    """BLL для управління заявками на прийом."""

    def __init__(self, request_repo: RequestRepositoryProtocol):
        self.request_repo = request_repo

    def get_all_requests(self):
        return self.request_repo.get_all()

    def get_request(self, request_id):
        return self.request_repo.get_by_id(request_id)

    def create_request(self, validated_data: dict):
        return self.request_repo.create(
            datetime=validated_data['datetime'],
            patient_id=validated_data['patient'].id,
            doctor_id=validated_data.get('doctor').id if validated_data.get('doctor') else None,
        )

    def update_request(self, request_id, validated_data: dict):
        request = self.request_repo.get_by_id(request_id)
        expected_version = validated_data.get('version')
        if expected_version is not None and expected_version != request.version:
            raise ValueError('Версія запису застаріла. Оновіть дані та повторіть спробу.')

        update_payload = {}
        for field in ['datetime', 'patient', 'doctor']:
            if field in validated_data:
                update_payload[field] = validated_data[field]

        if 'patient' in update_payload:
            update_payload['patient_id'] = update_payload.pop('patient').id
        if 'doctor' in update_payload:
            doctor = update_payload.pop('doctor')
            update_payload['doctor_id'] = doctor.id if doctor is not None else None

        update_payload['version'] = request.version + 1
        return self.request_repo.update(request_id, **update_payload)

    def delete_request(self, request_id):
        return self.request_repo.delete(request_id)
