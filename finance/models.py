from django.db import models
from users.models import User, DoctorProfile, PatientProfile
from service.models import Service


class Appointment(models.Model):
    STATUS_CHOICES = (
        ('запланирован', 'Запланирован'),
        ('готов к приему', 'Готов к приему'),
        ('завершен', 'Завершен'),
        ('отменен', 'Отменен'),
    )

    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, verbose_name="Пациент", related_name="appointments")
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE, verbose_name="Врач", related_name="appointments")
    service = models.ForeignKey(Service, on_delete=models.CASCADE, verbose_name="Услуга")
    appointment_date = models.DateTimeField(verbose_name="Дата и время приема")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='запланирован', verbose_name="Статус")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    def __str__(self):
        return f"Прием {self.patient} у {self.doctor} на {self.service}"

    class Meta:
        verbose_name = "Прием"
        verbose_name_plural = "Приемы"
        ordering = ['appointment_date']


class Invoice(models.Model):
    STATUS_CHOICES = (
        ('ожидает оплаты', 'Ожидает оплаты'),
        ('оплачено', 'Оплачено'),
        ('отменено', 'Отменено'),
    )

    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE, verbose_name="Прием", related_name="invoice")
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Сумма")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ожидает оплаты', verbose_name="Статус")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    def __str__(self):
        return f"Счет #{self.pk} на сумму {self.amount}"

    class Meta:
        verbose_name = "Счет"
        verbose_name_plural = "Счета"
        ordering = ['-created_at']
