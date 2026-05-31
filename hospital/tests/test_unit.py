from unittest import TestCase
from unittest.mock import Mock, MagicMock
from decimal import Decimal
from ..services.AppointmentService import AppointmentService


class AppointmentServiceUnitTests(TestCase):
    def setUp(self):
        self.mock_repo = Mock()
        self.service = AppointmentService(self.mock_repo)

    def test_recalculate_finances(self):
        work = MagicMock()
        work.price = Decimal('100.00')

        material = MagicMock()
        material.category.cost_price = Decimal('10.0')
        material.quantity = Decimal('2.0')

        medicine = MagicMock()
        medicine.category.cost_price = Decimal('20.0')
        medicine.quantity = Decimal('3.0')

        procedure = MagicMock()
        procedure.category.cost_price = Decimal('5.0')

        work.materials.all.return_value = [material]
        work.medicines.all.return_value = [medicine]
        work.procedures.all.return_value = [procedure]

        result = self.service.recalculate_work_finances(work)

        self.assertEqual(result.cost, Decimal('85.0'))
        self.assertEqual(result.profit, Decimal('15.0'))
        self.mock_repo.save_work.assert_called_once_with(work)

    def test_invalid_period_raises_error(self):
        from ..services.ClinicService import ClinicService
        mock_patient_repo = Mock()
        service = ClinicService(mock_patient_repo)

        with self.assertRaises(ValueError):
            service.get_patients_by_work_and_date('2026-12-31', '2026-01-01', 1)

        mock_patient_repo.find_by_period_and_work.assert_not_called()