from django import forms
from .models import User, DoctorProfile, PatientProfile
from django.contrib.auth.forms import AuthenticationForm
import secrets
import string


# --- Custom Form Widgets ---
class DateInput(forms.DateInput):
    """A custom widget for date fields using type='date'."""
    input_type = 'date'


# --- Authentication Forms ---
class UserLoginForm(AuthenticationForm):
    """
    Login form for all users.
    Uses Django's built-in AuthenticationForm.
    """
    username = forms.CharField(label='Username', widget=forms.TextInput(attrs={
        'class': 'form-input mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50'
    }))
    password = forms.CharField(label='Password', widget=forms.PasswordInput(attrs={
        'class': 'form-input mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50'
    }))


# --- Registration Forms ---
class ManagerRegistrationForm(forms.ModelForm):
    """
    A form for registering a new manager account.
    """

    class Meta:
        model = User
        fields = ['username', 'password']
        widgets = {
            'password': forms.PasswordInput()
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        user.role = User.ROLE_MANAGER
        user.is_active = True
        if commit:
            user.save()
        return user


class DoctorRegistrationForm(forms.ModelForm):
    """
    A form for registering a new doctor account by a manager.
    It automatically generates a temporary password.
    """

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone']

    first_name = forms.CharField(label='First Name', max_length=100, required=True, widget=forms.TextInput(
        attrs={'class': 'form-input mt-1 block w-full rounded-md border-gray-300 shadow-sm'}))
    last_name = forms.CharField(label='Last Name', max_length=100, required=True, widget=forms.TextInput(
        attrs={'class': 'form-input mt-1 block w-full rounded-md border-gray-300 shadow-sm'}))

    def save(self, commit=True):
        # Generate a temporary password
        alphabet = string.ascii_letters + string.digits
        temp_password = ''.join(secrets.choice(alphabet) for i in range(12))

        # Create the user and set their role and password
        user = User.objects.create_user(
            username=f"{self.cleaned_data['first_name'].lower()}{self.cleaned_data['last_name'].lower()}",
            password=temp_password,
            role=User.ROLE_DOCTOR,  # Corrected: Set the role field
            is_active=True
        )
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.phone = self.cleaned_data['phone']
        user.save()

        # Create a doctor profile for the user
        DoctorProfile.objects.create(user=user, first_name=user.first_name, last_name=user.last_name)

        return user, temp_password


class PatientRegistrationForm(forms.ModelForm):
    """
    A form for registering a new patient account by a manager.
    It automatically generates a temporary password and username.
    """

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone', 'birthday']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-input mt-1 block w-full rounded-md border-gray-300 shadow-sm'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-input mt-1 block w-full rounded-md border-gray-300 shadow-sm'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-input mt-1 block w-full rounded-md border-gray-300 shadow-sm'
            }),
            'birthday': DateInput(attrs={
                'class': 'form-input mt-1 block w-full rounded-md border-gray-300 shadow-sm'
            }),
        }

    def save(self, commit=True):
        # Generate a temporary password
        alphabet = string.ascii_letters + string.digits
        temp_password = ''.join(secrets.choice(alphabet) for _ in range(12))

        # Create the user
        user = User.objects.create_user(
            username=f"{self.cleaned_data['first_name'].lower()}{self.cleaned_data['last_name'].lower()}",
            password=temp_password,
            role=User.ROLE_PATIENT,
            is_active=True
        )
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.phone = self.cleaned_data['phone']
        user.birthday = self.cleaned_data['birthday']
        user.save()

        # Create an empty PatientProfile (without first_name/last_name, they now live in User)
        PatientProfile.objects.create(user=user)

        return user, temp_password
