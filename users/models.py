# your_app_name/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser

# We'll use a custom user model to handle different roles.
class User(AbstractUser):
    ROLE_MANAGER = 'manager'
    ROLE_DOCTOR = 'doctor'
    ROLE_PATIENT = 'patient'
    ROLE_CASHIER = 'cashier'

    ROLE_CHOICES = (
        (ROLE_MANAGER, 'Manager'),
        (ROLE_DOCTOR, 'Doctor'),
        (ROLE_PATIENT, 'Patient'),
        (ROLE_CASHIER, 'Cashier'),

    )
    # The 'manager', 'doctor', and 'patient' roles are managed here
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_PATIENT)
    phone = models.CharField(max_length=15, blank=True, null=True)
    birthday = models.DateField(null=True, blank=True)

    @property
    def is_manager(self):
        return self.role == self.ROLE_MANAGER

    @property
    def is_doctor(self):
        return self.role == self.ROLE_DOCTOR

    @property
    def is_patient(self):
        return self.role == self.ROLE_PATIENT

    @property
    def is_cashier(self):
        return self.role == self.ROLE_CASHIER

class DoctorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='doctor_profile')
    # New fields for the doctor profile
    phone = models.CharField(max_length=15, blank=True, null=True)
    specialty = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    room = models.CharField(max_length=50, blank=True, null=True)
    # A simple CharField to store a string of available time slots, e.g., "Mon: 9-5, Wed: 1-4"
    available_time_slots = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"Dr. {self.user.username}"

class PatientProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='patient_profile')
    # New fields for the patient
    first_name = models.CharField(max_length=100, default='')
    last_name = models.CharField(max_length=100, default='')

    def __str__(self):
        return self.user.username

