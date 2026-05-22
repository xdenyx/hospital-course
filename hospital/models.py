# Create your models here.
from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.utils import timezone


def validate_birth_date(value):
    if value > timezone.now().date():
        raise ValidationError("Дата народження не може бути пізніше поточної дати.")

class ProcedureCategory(models.Model):
    name = models.CharField(max_length=100, verbose_name="Клас процедури")
    cost_price = models.DecimalField(max_digits=10, decimal_places=1, default=1, verbose_name="Базова вартість (витрати)")
    
    def __str__(self):
        return f"{self.name} ({self.cost_price} грн)"
    
    class Meta:
        verbose_name = "Клас процедури"
        verbose_name_plural = "Класи процедур"


class MaterialCategory(models.Model):
    name = models.CharField(max_length=100, verbose_name="Клас матеріалу")
    cost_price = models.DecimalField(max_digits=10, decimal_places=1, default=1, verbose_name="Базова вартість (закупівля)")
    
    def __str__(self):
        return f"{self.name} ({self.cost_price} грн)"
    
    class Meta:
        verbose_name = "Клас матеріалу"
        verbose_name_plural = "Класи матеріалів"


class MedicineCategory(models.Model):
    name = models.CharField(max_length=100, verbose_name="Клас ліків")
    cost_price = models.DecimalField(max_digits=10, decimal_places=1, default=1, verbose_name="Базова вартість (закупівля)")
    
    def __str__(self):
        return f"{self.name} ({self.cost_price} грн)"
    
    class Meta:
        verbose_name = "Клас ліків"
        verbose_name_plural = "Класи ліків"


class WorkCategory(models.Model):
    name = models.CharField(max_length=100, verbose_name="Клас роботи")
    # Об'єднуємо витрати роботи та ціну для пацієнта в одній моделі
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Власна собівартість роботи (витрати клініки)")
    
    def __str__(self):
        return f"{self.name} (Ціна: {self.price} грн)"
    
    class Meta:
        verbose_name = "Клас роботи"
        verbose_name_plural = "Класи робіт"


class Doctor(models.Model):
    full_name = models.CharField(max_length=150, verbose_name="ПІБ Лікаря")
    specialization = models.CharField(max_length=100, verbose_name="Спеціалізація")
    
    def __str__(self):
        return self.full_name
    
    class Meta:
        verbose_name = "Лікар"
        verbose_name_plural = "Лікарі"


class Patient(models.Model):
    full_name = models.CharField(
        max_length=150,
        verbose_name="ПІБ Пацієнта",
        validators=[RegexValidator(r'^[^0-9]+$', message="У полі ПІБ не можна вводити цифри.")],
    )
    date_of_birth = models.DateField(
        verbose_name="Дата народження",
        validators=[validate_birth_date],
    )
    
    def __str__(self):
        return self.full_name
    
    @property
    def age(self):
        if not self.date_of_birth:
            return None
        today = timezone.now().date()
        return today.year - self.date_of_birth.year - (
            (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
        )

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)
    
    class Meta:
        verbose_name = "Пацієнт"
        verbose_name_plural = "Пацієнти"


class Request(models.Model):
    datetime = models.DateTimeField(verbose_name="Дата та час заявки")
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, verbose_name="Пацієнт")
    doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True, verbose_name="Лікар")
    
    def __str__(self):
        return f"Заявка №{self.id}"
    
    class Meta:
        verbose_name = "Заявка"
        verbose_name_plural = "Заявки"


class Appointment(models.Model):
    request = models.OneToOneField(Request, on_delete=models.CASCADE, verbose_name="Заявка")
    notes = models.TextField(blank=True, verbose_name="Примітки")
    
    def __str__(self):
        return f"Прийом №{self.id} (Пацієнт: {self.request.patient.full_name})"
        
    class Meta:
        verbose_name = "Прийом"
        verbose_name_plural = "Прийоми"


class AppointmentWork(models.Model):
    appointment = models.ForeignKey('Appointment', related_name='works', on_delete=models.CASCADE, verbose_name="Прийом")
    work_category = models.ForeignKey(WorkCategory, on_delete=models.PROTECT, verbose_name="Категорія роботи")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Ціна роботи (фіксація доходу)", default=0)
    cost = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Загальні витрати", default=0)
    profit = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Прибуток", default=0)
    
    def __str__(self):
        return f"{self.work_category.name} (Прийом №{self.appointment.id})"
    
    def get_total_expenses(self):
        from decimal import Decimal
        # Витрати - сума матеріалів, ліків та процедур!
        materials_cost = self.materials.aggregate(total=models.Sum('cost'))['total'] or Decimal('0.00')
        medicines_cost = self.medicines.aggregate(total=models.Sum('cost'))['total'] or Decimal('0.00')
        procedures_cost = self.procedures.aggregate(total=models.Sum('cost'))['total'] or Decimal('0.00')
        
        return materials_cost + medicines_cost + procedures_cost
    
    def get_price(self):
        # ціна роботи
        return self.price
    
    def get_profit(self):
        # прибуток (ціна роботи - витрати)
        return self.price - self.get_total_expenses()
    
    class Meta:
        verbose_name = "Робота в прийомі"
        verbose_name_plural = "Роботи в прийомі"

class WorkMaterial(models.Model):
    appointment_work = models.ForeignKey(AppointmentWork, related_name='materials', on_delete=models.CASCADE, verbose_name="Робота в прийомі")
    category = models.ForeignKey(MaterialCategory, on_delete=models.PROTECT, verbose_name="Категорія матеріалу")
    quantity = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="Кількість")
    cost = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Витрати на матеріал")
    
    def __str__(self):
        return f"{self.category.name}"
    
    class Meta:
        verbose_name = "Матеріал у роботі"
        verbose_name_plural = "Матеріали у роботі"

class WorkMedicine(models.Model):
    appointment_work = models.ForeignKey(AppointmentWork, related_name='medicines', on_delete=models.CASCADE, verbose_name="Робота в прийомі")
    category = models.ForeignKey(MedicineCategory, on_delete=models.PROTECT, verbose_name="Категорія ліків")
    quantity = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="Кількість")
    cost = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Витрати на ліки")
    
    def __str__(self):
        return f"{self.category.name}"

    class Meta:
        verbose_name = "Ліки у роботі"
        verbose_name_plural = "Ліки у роботі"

class WorkProcedure(models.Model):
    appointment_work = models.ForeignKey(AppointmentWork, related_name='procedures', on_delete=models.CASCADE, verbose_name="Робота в прийомі")
    category = models.ForeignKey(ProcedureCategory, on_delete=models.PROTECT, verbose_name="Категорія процедури")
    cost = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Витрати на процедуру")
    
    def __str__(self):
        return f"{self.category.name}"
    
    class Meta:
        verbose_name = "Процедура у роботі"
        verbose_name_plural = "Процедури у роботі"