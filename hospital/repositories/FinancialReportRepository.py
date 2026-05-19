from django.db.models import Sum, F, DecimalField, Q
from django.db.models.functions import Coalesce
from ..models import ProcedureCategory, WorkCategory

class FinancialReportRepository:
    """DAL для отримання фінансових звітів"""

    @staticmethod
    def get_procedure_financials():
        # Звіти: За класами процедур дохід, витрати (матеріали, роботи), чистий дохід
        return ProcedureCategory.objects.annotate(
            # Дохід = сумма цін robіт які мають цю процедуру
            total_income=Coalesce(Sum('workprocedure__appointment_work__price'), 0.0, output_field=DecimalField()),
            # Вартість самих процедур
            proc_cost=Coalesce(Sum('workprocedure__cost'), 0.0, output_field=DecimalField()),
            # Вартість матеріалів в роботах які мають цю процедуру
            materials_cost=Coalesce(Sum('workprocedure__appointment_work__materials__cost'), 0.0, output_field=DecimalField()),
            # Вартість ліків в роботах які мають цю процедуру
            medicines_cost=Coalesce(Sum('workprocedure__appointment_work__medicines__cost'), 0.0, output_field=DecimalField()),
            # Вартість самих робіт
            works_cost=Coalesce(Sum('workprocedure__appointment_work__price'), 0.0, output_field=DecimalField()),
        ).annotate(
            # Всього витрат
            total_expenses=F('proc_cost') + F('materials_cost') + F('medicines_cost'),
            # Чистий дохід (дохід від робіт мінус витрати)
            net_profit=F('total_income') - F('total_expenses')
        ).filter(total_income__gt=0)

    @staticmethod
    def get_work_category_financials():
        # Фінансові дані за категоріями робіт
        return WorkCategory.objects.annotate(
            # Дохід від робіт (ціна)
            total_income=Coalesce(Sum('appointmentwork__price'), 0.0, output_field=DecimalField()),
            # Витрати на роботу (вважаємо що це дохід, тобто ціна)
            work_cost=Coalesce(Sum('appointmentwork__price'), 0.0, output_field=DecimalField()),
            # Витрати на матеріали
            materials_cost=Coalesce(Sum('appointmentwork__materials__cost'), 0.0, output_field=DecimalField()),
            # Витрати на ліки
            medicines_cost=Coalesce(Sum('appointmentwork__medicines__cost'), 0.0, output_field=DecimalField()),
            # Витрати на процедури
            procedures_cost=Coalesce(Sum('appointmentwork__procedures__cost'), 0.0, output_field=DecimalField()),
        ).annotate(
            # Всього витрат (матеріали + ліки + процедури)
            total_expenses=F('materials_cost') + F('medicines_cost') + F('procedures_cost'),
            # Чистий дохід (дохід від робіт - витрати)
            net_profit=F('total_income') - F('total_expenses')
        ).filter(total_income__gt=0)

    @staticmethod
    def get_financials_by_date_range(start_date, end_date):
        # Фінансові дані за період
        return WorkCategory.objects.filter(
            appointmentwork__appointment__request__datetime__date__range=[start_date, end_date]
        ).annotate(
            # Ціна роботи за період
            total_income=Coalesce(Sum('appointmentwork__price'), 0.0, output_field=DecimalField()),
            # Витрати за період
            materials_cost=Coalesce(Sum('appointmentwork__materials__cost'), 0.0, output_field=DecimalField()),
            medicines_cost=Coalesce(Sum('appointmentwork__medicines__cost'), 0.0, output_field=DecimalField()),
            procedures_cost=Coalesce(Sum('appointmentwork__procedures__cost'), 0.0, output_field=DecimalField()),
        ).annotate(
            total_expenses=F('materials_cost') + F('medicines_cost') + F('procedures_cost'),
            net_profit=F('total_income') - F('total_expenses')
        ).distinct()