from django.db.models import Sum, F, DecimalField, OuterRef, Subquery
from django.db.models.functions import Coalesce
from ..models import WorkCategory

class FinancialReportRepository:
    """DAL для отримання фінансових звітів"""

    @staticmethod
    def _work_category_base_queryset():
        return WorkCategory.objects.all()

    @staticmethod
    def get_work_category_financials():
        # Окремі підзапити потрібні, щоб не множити суми через joins
        work_base = WorkCategory.objects.filter(id=OuterRef('id'))

        work_income_subquery = (
            work_base.annotate(total=Coalesce(Sum('appointmentwork__price'), 0.0, output_field=DecimalField()))
            .values('total')[:1]
        )

        work_cost_subquery = (
            work_base.annotate(total=Coalesce(Sum('appointmentwork__price'), 0.0, output_field=DecimalField()))
            .values('total')[:1]
        )

        materials_cost_subquery = (
            work_base.annotate(total=Coalesce(Sum('appointmentwork__materials__cost'), 0.0, output_field=DecimalField()))
            .values('total')[:1]
        )

        medicines_cost_subquery = (
            work_base.annotate(total=Coalesce(Sum('appointmentwork__medicines__cost'), 0.0, output_field=DecimalField()))
            .values('total')[:1]
        )

        procedures_cost_subquery = (
            work_base.annotate(total=Coalesce(Sum('appointmentwork__procedures__cost'), 0.0, output_field=DecimalField()))
            .values('total')[:1]
        )

        return FinancialReportRepository._work_category_base_queryset().annotate(
            total_income=Coalesce(Subquery(work_income_subquery, output_field=DecimalField()), 0.0, output_field=DecimalField()),
            work_cost=Coalesce(Subquery(work_cost_subquery, output_field=DecimalField()), 0.0, output_field=DecimalField()),
            materials_cost=Coalesce(Subquery(materials_cost_subquery, output_field=DecimalField()), 0.0, output_field=DecimalField()),
            medicines_cost=Coalesce(Subquery(medicines_cost_subquery, output_field=DecimalField()), 0.0, output_field=DecimalField()),
            procedures_cost=Coalesce(Subquery(procedures_cost_subquery, output_field=DecimalField()), 0.0, output_field=DecimalField()),
        ).annotate(
            total_expenses=F('materials_cost') + F('medicines_cost') + F('procedures_cost'),
            net_profit=F('total_income') - F('total_expenses')
        ).filter(total_income__gt=0)

    @staticmethod
    def get_appointment_work_financials_by_id(appointment_work_id: int):
        """Расчет финансов в приеме"""
        from ..models import AppointmentWork

        qs = (
            AppointmentWork.objects.filter(id=appointment_work_id)
            .annotate(
                materials_cost=Coalesce(Sum('materials__cost'), 0.0, output_field=DecimalField()),
                medicines_cost=Coalesce(Sum('medicines__cost'), 0.0, output_field=DecimalField()),
                procedures_cost=Coalesce(Sum('procedures__cost'), 0.0, output_field=DecimalField()),
            )
        )

        aw = qs.first()
        if not aw:
            return None

        total_expenses = (aw.materials_cost or 0) + (aw.medicines_cost or 0) + (aw.procedures_cost or 0)
        profit = (aw.price or 0) - total_expenses

        return {
            'appointment_work_id': appointment_work_id,
            'price': aw.price,
            'materials_cost': aw.materials_cost or 0,
            'medicines_cost': aw.medicines_cost or 0,
            'procedures_cost': aw.procedures_cost or 0,
            'total_expenses': total_expenses,
            'profit': profit,
        }