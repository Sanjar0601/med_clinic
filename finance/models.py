from django.db import models
from django.utils.timezone import now
from users.models import PatientProfile, DoctorProfile
from service.models import Service
from django.db.models import Sum


class Appointment(models.Model):
    patient = models.ForeignKey(
        PatientProfile,
        on_delete=models.CASCADE,
        related_name="appointments"
    )
    appointment_date = models.DateTimeField(default=now)


    def __str__(self):
        return f"Приём {self.id} — {self.patient}"

    @property
    def total_cost(self):
        """Сумма всех услуг приёма"""
        return self.services.aggregate(total=Sum("price"))["total"] or 0


class AppointmentService(models.Model):
    appointment = models.ForeignKey(
        Appointment,
        on_delete=models.CASCADE,
        related_name="services"
    )
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name="appointment_services"
    )
    doctor = models.ForeignKey(
        DoctorProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="appointment_services"
    )
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.service.name} ({self.doctor or 'без врача'})"


class Invoice(models.Model):
    appointment = models.OneToOneField(
        Appointment,
        on_delete=models.CASCADE,
        related_name="invoice_link",
        blank=True,
        null=True
    )
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(
        max_length=20,
        choices=[
            ("ожидает оплаты", "Ожидает оплаты"),
            ("оплачено", "Оплачено"),
        ],
        default="ожидает оплаты"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    confirmed_by = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="confirmed_invoices",
        verbose_name="Кассир"
    )

    def __str__(self):
        return f"Счёт #{self.pk} (Приём {self.appointment.id}) на {self.total_amount} сум"

    class Meta:
        verbose_name = "Счёт"
        verbose_name_plural = "Счета"
        ordering = ['-created_at']

    def recalc_total(self):
        """Пересчитать сумму по услугам приёма"""
        self.total_amount = self.appointment.total_cost
        self.save()
