from .models import Appointment
from users.models import DoctorProfile
from service.models import Room
from django import forms


class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['services', 'doctor', 'room', 'appointment_date', 'status']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['doctor'].queryset = DoctorProfile.objects.all()

        if 'services' in self.data:
            try:
                service_ids = self.data.getlist('services')
                doctors = DoctorProfile.objects.filter(services__id__in=service_ids).distinct()
                self.fields['doctor'].queryset = doctors
            except (ValueError, TypeError):
                pass
