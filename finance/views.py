# appointments/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from users.models import PatientProfile, User, DoctorProfile
from service.models import Service
from service.models import Room
from .models import Appointment
from .models import Invoice
from users.views import manager_required

def appointment_create(request, user_id):
    # Get the user and their patient profile
    user = get_object_or_404(User, id=user_id)
    patient = get_object_or_404(PatientProfile, user=user)

    services = Service.objects.all()
    doctors = DoctorProfile.objects.all()
    rooms = Room.objects.all()

    if request.method == "POST":
        selected_services = request.POST.getlist("services")
        selected_doctors = request.POST.getlist("doctors")
        selected_rooms = request.POST.getlist("rooms")

        # Create appointments for each selected service
        for service_id in selected_services:
            service = get_object_or_404(Service, id=service_id)

            # You might decide here which doctor and room to assign
            # For now, let's assign the first doctor & room from POST
            doctor_id = selected_doctors[0] if selected_doctors else None
            room_id = selected_rooms[0] if selected_rooms else None

            doctor = get_object_or_404(Doctor, id=doctor_id) if doctor_id else None
            room = get_object_or_404(Room, id=room_id) if room_id else None

            Appointment.objects.create(
                patient=patient,
                service=service,
                doctor=doctor,
                room=room
            )

        return redirect("some_success_page")  # Replace with your page

    return render(request, "finance/appointment.html", {
        "patient": patient,
        "services": services,
        "doctors": doctors,
        "rooms": rooms
    })



def mark_invoice_paid(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk, status="ожидает оплаты")
    invoice.status = "оплачено"
    invoice.paid_at = now()
    invoice.save()
    messages.success(request, "Счет оплачен.")
    return redirect("unpaid_invoices")