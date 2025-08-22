from django.shortcuts import render
from users.views import manager_required
from .models import Service
from .forms import ServiceForm
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

# Create your views here.


@manager_required
def service_list(request):
    """
    Отображает список всех услуг.
    """
    services = Service.objects.all().order_by('name')
    context = {
        'services': services,
    }
    return render(request, 'service/service_list.html', context)


@manager_required
def service_create(request):
    """
    Позволяет менеджеру добавить новую услугу.
    """
    if request.method == 'POST':
        form = ServiceForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Услуга успешно добавлена.")
            return redirect('service_list')
    else:
        form = ServiceForm()

    context = {
        'form': form,
        'page_title': 'Добавить услугу'
    }
    return render(request, 'service/service_form.html', context)


@manager_required
def service_update(request, service_id):
    """
    Handles the updating of an existing service.
    """
    service = get_object_or_404(Service, id=service_id)
    if request.method == 'POST':
        form = ServiceForm(request.POST, instance=service)
        if form.is_valid():
            form.save()
            messages.success(request, 'Услуга успешно обновлена.')
            return redirect('service_list') # Correct redirect to the service list page
        else:
            messages.error(request, 'Ошибка при обновлении услуги.')
    else:
        form = ServiceForm(instance=service)
    return render(request, 'service/service_form.html', {'form': form, 'page_title': 'Редактировать услугу'})


@manager_required
def service_delete(request, service_id):
    """
    Позволяет менеджеру удалить услугу.
    """
    service = get_object_or_404(Service, id=service_id)
    if request.method == 'POST':
        service.delete()
        messages.success(request, "Услуга успешно удалена.")
        return redirect('service_list')
    return render(request, 'service/service_delete.html', {'service': service})
