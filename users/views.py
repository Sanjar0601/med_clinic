# your_app_name/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.timezone import now

from .forms import UserLoginForm, ManagerRegistrationForm, DoctorRegistrationForm, PatientRegistrationForm
from .models import User, DoctorProfile, PatientProfile
from finance.models import Invoice

# --- Custom Decorators for Role-Based Access ---
def manager_required(function=None, redirect_field_name=None, login_url='login'):
    """
    Decorator for views that checks that the user is logged in and is a manager,
    redirecting to the login page if necessary.
    """
    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated and u.is_manager,
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator


def doctor_required(function=None, redirect_field_name=None, login_url='login'):
    """
    Decorator for views that checks that the user is logged in and is a doctor.
    """
    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated and u.is_doctor,
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator


def patient_required(function=None, redirect_field_name=None, login_url='login'):
    """
    Decorator for views that checks that the user is logged in and is a patient.
    """
    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated and u.is_patient,
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator


# --- Authentication Views ---

def register_manager(request):
    """
    Handles initial manager registration.
    This view can be used to create the very first manager account.
    Consider removing or restricting access to this view after initial setup.
    """
    if request.user.is_authenticated:
        messages.warning(request, "You are already logged in.")
        return redirect('home_dashboard')  # Redirect to their dashboard if logged in

    if request.method == 'POST':
        form = ManagerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Manager account created successfully! Please log in.')
            return redirect('login')
        else:
            messages.error(request, 'Manager registration failed. Please correct the errors.')
    else:
        form = ManagerRegistrationForm()
    return render(request, 'users/register_manager.html', {'form': form})


def login_user(request):
    """
    Handles user login for all roles and redirects to appropriate dashboard.
    """
    if request.user.is_authenticated:
        messages.info(request, "You are already logged in.")
        return redirect('home_dashboard')  # Redirect to their dashboard if logged in

    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome, {username} ({user.get_role_display()})!')
                return redirect('home_dashboard')  # Redirect to the general dashboard dispatcher
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = UserLoginForm()
    return render(request, 'users/login.html', {'form': form})


@login_required
def logout_user(request):
    """
    Logs out the current user.
    """
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('login')


# --- Manager-Specific Views ---

@manager_required
def add_doctor(request):
    """
    Allows a manager to add a new doctor on a separate page.
    """
    form = DoctorRegistrationForm(request.POST or None)
    if form.is_valid():
        user = form.save()
        messages.success(request, f'Doctor "{user.username}" added successfully!')
        print(f"Doctor '{user.username}' added successfully.")
        return redirect('manager_dashboard')

    context = {
        'message': "Add a new Doctor",
        'form': form
    }
    return render(request, 'users/add_doctor.html', context)


# The add_patient view is now consolidated into manager_dashboard and has been removed from here.

# --- Dashboard Dispatcher ---

@login_required
def home_dashboard(request):
    user = request.user

    if user.is_manager:
        return redirect('manager_dashboard')
    elif user.is_doctor:
        return redirect('doctor_dashboard')
    elif user.is_patient:
        return redirect('patient_dashboard')
    elif user.is_cashier:
        return redirect('cashier_dashboard')
    else:
        messages.error(request, "Ваш аккаунт имеет неизвестную роль. Обратитесь в поддержку.")
        logout(request)
        return redirect('login')

# --- Role-Specific Dashboard Views ---

@manager_required
def manager_dashboard(request):
    """
    Dashboard for Manager role, now with an embedded Patient form and patient list.
    """
    print(f"--- manager_dashboard accessed by: {request.user.username} ---")

    if request.method == 'POST':
        if 'add_patient_submit' in request.POST:
            patient_form = PatientRegistrationForm(request.POST)
            if patient_form.is_valid():
                user, temp_password = patient_form.save()
                messages.success(request,
                                 f'Patient "{user.username}" added successfully! The system-generated password is: **{temp_password}**. The patient can also retrieve their credentials via the Telegram bot using their registered phone number: **{user.phone}**.')
                print(f"Patient '{user.username}' added successfully via dashboard. Temp password: {temp_password}")
                return redirect('manager_dashboard')
            else:
                messages.error(request, 'Failed to add patient. Please correct the errors below.')
                print(f"Patient form errors: {patient_form.errors}")

    # Fetch all patients and their profiles, ordered by the user's creation date
    patients = User.objects.filter(role=User.ROLE_PATIENT).order_by('-date_joined')

    context = {
        'message': "Welcome, Manager! Here's your dashboard.",
        'patient_form': PatientRegistrationForm(),  # We re-instantiate the form for GET requests
        'patients': patients,
    }
    return render(request, 'users/manager_dashboard.html', context)


@doctor_required
def doctor_dashboard(request):
    """
    Dashboard for Doctor role.
    """
    return render(request, 'users/doctor_dashboard.html', {'message': "Welcome, Doctor! Here's your dashboard."})


@patient_required
def patient_dashboard(request):
    """
    Dashboard for Patient role.
    """
    return render(request, 'users/patient_dashboard.html', {'message': "Welcome, Patient! Here's your dashboard."})


def cashier_required(function=None, redirect_field_name=None, login_url='login'):
    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated and getattr(u, "is_cashier", False),
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator


@login_required
@cashier_required
def cashier_dashboard(request):
    """Панель кассира: список счетов, по умолчанию — все, неоплаченные сверху."""
    invoices = (
        Invoice.objects
        .select_related("appointment__patient__user")
        .order_by("status", "-created_at")  # сначала ожидают оплаты, потом оплаченные
    )
    return render(request, "users/cashier_dashboard.html", {"invoices": invoices})


@login_required
@cashier_required
def approve_payment(request, invoice_id):
    """Подтвердить оплату счёта."""
    invoice = get_object_or_404(Invoice, id=invoice_id)
    if invoice.status == "оплачено":
        messages.warning(request, f"Счёт #{invoice.id} уже оплачен.")
    else:
        invoice.status = "оплачено"
        invoice.paid_at = now()
        invoice.confirmed_by = request.user
        invoice.save()
        messages.success(request, f"Счёт #{invoice.id} успешно оплачен.")
    return redirect("cashier_dashboard")