from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from users.models import PatientProfile, DoctorProfile
from service.models import Service


class Appointment(models.Model):
    STATUS_CHOICES = (
        ('запланирован', 'Запланирован'),
        ('готов к приему', 'Готов к приему'),
        ('завершен', 'Завершен'),
        ('отменен', 'Отменен'),
    )

    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, verbose_name="Пациент", related_name="appointments")
    room = models.ForeignKey("service.Room", on_delete=models.CASCADE, verbose_name="Кабинет", related_name="appointments", null=True, blank=True)
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE, verbose_name="Врач", related_name="appointments")
    services = models.ManyToManyField(Service, verbose_name="Услуги")
    appointment_date = models.DateTimeField(verbose_name="Дата и время приема")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='запланирован', verbose_name="Статус")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    def __str__(self):
        return f"Прием {self.patient} у {self.doctor} на {self.appointment_date}"

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

    # Привязка 1:1 к приему
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE, verbose_name="Прием", related_name="invoice")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Итоговая сумма", default=0.00)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ожидает оплаты', verbose_name="Статус")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    def __str__(self):
        return f"Счет #{self.pk} на сумму {self.total_amount}"

    class Meta:
        verbose_name = "Счет"
        verbose_name_plural = "Счета"
        ordering = ['-created_at']

# Сигнал для автоматического создания счета при создании приема
@receiver(post_save, sender=Appointment)
def create_invoice_for_appointment(sender, instance, created, **kwargs):
    if created:
        invoice = Invoice.objects.create(appointment=instance)
        # Рассчитываем сумму счета на основе услуг, привязанных к приему
        total = sum(service.price for service in instance.services.all())
        invoice.total_amount = total
        invoice.save()
