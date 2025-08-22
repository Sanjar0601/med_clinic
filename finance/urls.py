from django.urls import path
from . import views

urlpatterns = [
    path('appointments/create/<int:user_id>/', views.appointment_create, name='appointment_create'),
    path("invoices/", views.invoice_list, name="invoice_list"),
]
