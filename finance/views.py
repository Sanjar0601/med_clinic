from django.db.models import Prefetch
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from users.models import PatientProfile, User, DoctorProfile
from service.models import Service
from .models import Appointment, Invoice, AppointmentService
from users.views import manager_required, cashier_required
from django.http import JsonResponse
from django.db import transaction
from django.utils.timezone import now, make_aware
from datetime import datetime


@manager_required
def appointment_create(request, user_id):
    user = get_object_or_404(User, id=user_id)
    patient = get_object_or_404(PatientProfile, user=user)

    if request.method == "POST":
        selected_services_str = request.POST.get("services", "")
        selected_services_ids = selected_services_str.split(',') if selected_services_str else []

        appointment_date_str = request.POST.get("date")

        if not selected_services_ids:
            messages.error(request, "Выберите хотя бы одну услугу.")
            return redirect("appointment_create", user_id=user_id)

        if not appointment_date_str:
            messages.error(request, "Выберите дату и время приёма.")
            return redirect("appointment_create", user_id=user_id)

        try:
            # преобразуем строку в datetime
            naive_appointment_date = datetime.fromisoformat(appointment_date_str)
            aware_appointment_date = make_aware(naive_appointment_date)
        except ValueError:
            messages.error(request, "Неверный формат даты.")
            return redirect("appointment_create", user_id=user_id)

        try:
            with transaction.atomic():
                # создаём приём
                appt = Appointment.objects.create(
                    patient=patient,
                    appointment_date=aware_appointment_date,
                )

                total = 0
                services_qs = Service.objects.prefetch_related('doctors__user')

                for sid in selected_services_ids:
                    service = get_object_or_404(services_qs, id=sid)

                    doctor_id = request.POST.get(f"doctor_for_{sid}")
                    doctor = None
                    if doctor_id and service.doctors.filter(id=doctor_id).exists():
                        doctor = DoctorProfile.objects.get(id=doctor_id)

                    AppointmentService.objects.create(
                        appointment=appt,
                        service=service,
                        doctor=doctor,
                        price=service.price,
                    )
                    total += service.price

                # создаём единый счёт на весь приём
                invoice = Invoice.objects.create(
                    appointment=appt,
                    total_amount=total,
                    status="ожидает оплаты"
                )

                # привязка к приёму
                appt.invoice = invoice
                appt.save()

                messages.success(request, "Приём создан, счёт выставлен.")
                return redirect("manager_dashboard")

        except Exception as e:
            messages.error(request, f"Произошла ошибка: {e}")
            return redirect("appointment_create", user_id=user_id)

    else:
        services_qs = Service.objects.prefetch_related('doctors__user')
        return render(request, "finance/appointment.html", {
            "patient": patient,
            "services": services_qs,
        })


@cashier_required
def mark_invoice_paid(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk, status="ожидает оплаты")
    invoice.status = "оплачено"
    invoice.paid_at = now()
    invoice.confirmed_by = request.user  # <-- вот это добавляем
    invoice.save()
    messages.success(request, f"Счёт за приём №{invoice.appointment.id} оплачен кассиром {request.user.get_full_name()}.")
    return redirect("unpaid_invoices")


def invoice_list(request):
    invoices = (
        Invoice.objects
        .select_related("appointment__patient__user")
        .prefetch_related(
            Prefetch(
                "appointment__services",   # правильный related_name
                queryset=AppointmentService.objects.select_related("service", "doctor__user")
            )
        )
    )

    # Пересчёт суммы (если ещё не пересчитана)
    for invoice in invoices:
        if not invoice.total_amount:
            total = sum(s.price for s in invoice.appointment.services.all())
            invoice.total_amount = total
            invoice.save(update_fields=["total_amount"])

    return render(request, "finance/invoice_list.html", {"invoices": invoices})