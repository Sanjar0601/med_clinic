# your_app_name/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('register/manager/', views.register_manager, name='register_manager'),
    path('accounts/login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),

    # Manager-specific paths
    path('add-doctor/', views.add_doctor, name='add_doctor'),
    path('manager/dashboard/', views.manager_dashboard, name='manager_dashboard'),

    # Doctor-specific paths
    path('doctor/dashboard/', views.doctor_dashboard, name='doctor_dashboard'),

    # Patient-specific paths
    path('patient/dashboard/', views.patient_dashboard, name='patient_dashboard'),

    # Dashboard dispatcher (root after login)
    path('', views.home_dashboard, name='home_dashboard'),
    path("cashier/dashboard/", views.cashier_dashboard, name="cashier_dashboard"),
    path("cashier/invoices/<int:invoice_id>/approve/", views.approve_payment, name="approve_payment"),
]

