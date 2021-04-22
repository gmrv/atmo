from django.core.management.base import BaseCommand
from main.models.core import *
from django.db import connection


class Command(BaseCommand):
    help = "Загузка начальных тестовых данных"
    args = ""
    requires_system_checks = True

    def handle(self, *args, **options):

        # Компания 1
        cos = Company.objects.create(name="АО \"Fossa\"", short_name="АО \"Fossa\"", full_name="АО \"Fossa\"")
        # Площадка 1
        a = Area.objects.create(name="Fossa Коворкинг №1", type=Area.AREA_TYPE_COWORKING, map_url="/static/img/cons/map-01.html")
        for n in range(1, 21):
            m = Seat.objects.create(name=str(n).zfill(2))
            a.resource_set.add(m)
        a.save()
        r1 = Room.objects.create(name='Переговорная A1', capacity=4)
        r2 = Room.objects.create(name='Переговорная A2', capacity=4)
        a.resource_set.add(r1, r2)
        a.save()
        cos.area_set.add(a)
        cos.save()
        # Площадка 2
        a = Area.objects.create(name="Fossa Коворкинг №2", type=Area.AREA_TYPE_COWORKING, map_url="/static/img/cons/map-02.html")
        for n in range(1, 20):
            m = Seat.objects.create(name=str(n).zfill(2))
            a.resource_set.add(m)
        a.save()
        cos.area_set.add(a)
        cos.save()

        # Компания 2
        ras = Company.objects.create(name="АО \"Beaver\"", short_name="АО \"Beaver\"", full_name="АО \"Beaver\"")
        # Площадка 3
        a = Area.objects.create(name="Beaver Коворкинг №1", type=Area.AREA_TYPE_COWORKING)
        for n in range(1, 21):
            m = Seat.objects.create(name=str(n).zfill(2))
            a.resource_set.add(m)
        a.save()
        ras.area_set.add(a)
        ras.save()
        # Компания 4
        a = Area.objects.create(name="Beaver Коворкинг №2", type=Area.AREA_TYPE_COWORKING)
        for n in range(1, 11):
            m = Seat.objects.create(name=str(n).zfill(2))
            a.resource_set.add(m)
        a.save()
        ras.area_set.add(a)
        ras.save()


        # Пользователи

        u = ExtUser.objects.create(username="root", is_staff=True, is_superuser=True)
        u.set_password("1234")
        u.save()

        u = ExtUser.objects.create(username="ivanov-ii", email="ivanov-ii@a.com", company=cos,
            first_name="Иван", middle_name="Иванович", last_name="Иванов")
        u.set_password("1234")
        u.save()
        # Бронируем постоянное место
        r = u.company.area_set.get(pk=1).resource_set.get(name='01')
        r.seat.persisted = True
        r.seat.owner = u
        r.save()

        u = ExtUser.objects.create(username="petrov-pp", email="petrov-pp@a.com", company=cos,
            first_name="Пётр", middle_name="Петрович", last_name="Петров")
        u.set_password("1234")
        u.save()

        u = ExtUser.objects.create(username="sidorov-ss", email="sidorov-ss@a.com", company=cos,
            first_name="Сидор", middle_name="Сидорович", last_name="Сидоров")
        u.set_password("1234")
        u.save()


