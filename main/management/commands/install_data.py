from django.core.management.base import BaseCommand
from main.models.core import *
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

        # Объекты

        cos = Company.objects.create(name="АО \"Fossa\"", short_name="АО \"Fossa\"", full_name="АО \"Fossa\"")

        a = Area.objects.create(name="Fossa Коворкинг №1", type=area_type_coworking)

        for n in range(1, 21):
            m = Seat.objects.create(name=str(n).zfill(2))
            a.resource_set.add(m)
        a.save()

        r = Room.objects.create(name='Fossa Переговорная №1', capacity=20)
        a.resource_set.add(r)
        a.save()

        cos.area_set.add(a)
        cos.save()

        a = Area.objects.create(name="Fossa Коворкинг №2", type=area_type_coworking)
        for n in range(1, 11):
            m = Seat.objects.create(name=str(n).zfill(2))
            a.resource_set.add(m)
        a.save()

        cos.area_set.add(a)
        cos.save()


        ras = Company.objects.create(name="АО \"Beaver\"", short_name="АО \"Beaver\"", full_name="АО \"Beaver\"")

        a = Area.objects.create(name="Beaver Коворкинг №1", type=area_type_coworking)
        for n in range(1, 21):
            m = Seat.objects.create(name=str(n).zfill(2))
            a.resource_set.add(m)
        a.save()

        ras.area_set.add(a)
        ras.save()

        a = Area.objects.create(name="Beaver Коворкинг №2", type=area_type_coworking)
        for n in range(1, 11):
            m = Seat.objects.create(name=str(n).zfill(2))
            a.resource_set.add(m)
        a.save()

        ras.area_set.add(a)
        ras.save()


        # Пользователи

        u =ExtUser.objects.create(username="ivanov-ii", email="ivanov-ii@a.com", company=cos,
            first_name="Иван", middle_name="Иванович", last_name="Иванов")
        u.set_password("1234")
        u.save()

        r = u.company.area_set.get(pk=1).resource_set.get(name='01')
        r.seat.persisted = True
        r.seat.owner = u
        r.save()

        u = ExtUser.objects.create(username="petrov-pp", email="petrov-pp@a.com", company=cos,
            first_name="Петор", middle_name="Пертрович", last_name="Петров")
        u.set_password("1234")
        u.save()
