from django import forms
from .models import Service
from users.models import DoctorProfile


class ServiceForm(forms.ModelForm):
    """
    Форма для создания и редактирования услуг.
    """

    class Meta:
        model = Service
        fields = ['name', 'description', 'price', 'doctors']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-input mt-1 block w-full rounded-md border-gray-300 shadow-sm '
                         'focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-input mt-1 block w-full rounded-md border-gray-300 shadow-sm '
                         'focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-input mt-1 block w-full rounded-md border-gray-300 shadow-sm '
                         'focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50'
            }),
            'doctors': forms.SelectMultiple(attrs={
                'class': 'form-multiselect mt-1 block w-full rounded-md border-gray-300 shadow-sm '
                         'focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50'
            }),
                    }
