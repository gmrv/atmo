from django.core.management.base import BaseCommand
from main.models import *
from django.db import connection


class Command(BaseCommand):
    help = "Загузка начальных тестовых данных"
    args = ""
    requires_system_checks = True

    def handle(self, *args, **options):

        # Справочники

        # Типы площадок
        area_type_coworking = AreaType.objects.create(name='Коворкинг')
        area_type_floor = AreaType.objects.create(name='Этаж')

        # Типы ресурсов
        resource_type_room = ResourceType.objects.create(name="Переговорная")
        resource_type_seat = ResourceType.objects.create(name="Место")


        # Объекты

        cos = Company.objects.create(name="АО \"Fossa\"", short_name="АО \"Fossa\"", full_name="АО \"Fossa\"")

        m1 = Resource.objects.create(type=resource_type_seat, name="01")
        Property.objects.create(type=Property.BOOL, name="Постоянное", value_bool=True, resource=m1)

        a = Area.objects.create(name="Fossa Коворкинг №1", type=area_type_coworking)
        a.resource_set.add(m1)
        a.save()

        for n in range(2, 21):
            m = Resource.objects.create(type=resource_type_seat, name=str(n).zfill(2))
            a.resource_set.add(m)
        a.save()

        cos.area_set.add(a)
        cos.save()

        a = Area.objects.create(name="Fossa Коворкинг №2", type=area_type_coworking)
        for n in range(1, 11):
            m = Resource.objects.create(type=resource_type_seat, name=str(n).zfill(2))
            a.resource_set.add(m)
        a.save()

        cos.area_set.add(a)
        cos.save()


        ras = Company.objects.create(name="АО \"Beaver\"", short_name="АО \"Beaver\"", full_name="АО \"Beaver\"")

        a = Area.objects.create(name="Beaver Коворкинг №1", type=area_type_coworking)
        for n in range(1, 21):
            m = Resource.objects.create(type=resource_type_seat, name=str(n).zfill(2))
            a.resource_set.add(m)
        a.save()

        ras.area_set.add(a)
        ras.save()

        a = Area.objects.create(name="Beaver Коворкинг №2", type=area_type_coworking)
        for n in range(1, 11):
            m = Resource.objects.create(type=resource_type_seat, name=str(n).zfill(2))
            a.resource_set.add(m)
        a.save()

        ras.area_set.add(a)
        ras.save()


        # Пользователи

        u =ExtUser.objects.create(username="ivanov-ii", email="ivanov-ii@a.com", company=cos,
            first_name="Иван", middle_name="Иванович", last_name="Иванов")
        u.set_password("1234")
        u.save()

        u = ExtUser.objects.create(username="petrov-pp", email="petrov-pp@a.com", company=cos,
            first_name="Петор", middle_name="Пертрович", last_name="Петров")
        u.set_password("1234")
        u.save()
