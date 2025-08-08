from django.contrib import admin
from django.urls import path, include
from .views import (service_list,
                   service_create,
                   service_delete, service_update)

urlpatterns = [
    path('services/', service_list, name='service_list'),
    path('services/create/', service_create, name='service_create'),
    path('services/update/<int:service_id>/', service_update, name='service_update'),
    path('services/delete/<int:service_id>/', service_delete, name='service_delete'),

]