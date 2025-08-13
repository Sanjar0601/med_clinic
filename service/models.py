from django.db import models




class Room(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название кабинета")
    room_type = models.CharField(max_length=100, blank=True, verbose_name="Тип кабинета")

    def __str__(self):
        return self.name


class Service(models.Model):
    name = models.CharField(max_length=200, verbose_name="Название услуги")
    description = models.TextField(blank=True, verbose_name="Описание")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Стоимость")
    doctors = models.ManyToManyField("users.DoctorProfile", related_name="services", verbose_name="Врачи")
    rooms = models.ManyToManyField(Room, related_name="services", verbose_name="Кабинеты")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Услуга"
        verbose_name_plural = "Услуги"
        ordering = ['name']
