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

        # Создаем рабочие места
        for n in range(1, 21):
            m = Seat.objects.create(name=str(n).zfill(2))
            a.resource_set.add(m)
        a.save()

        # Создаем ячейки хранения
        for n in range(1, 11):
            c = Cell.objects.create(name=str(n).zfill(2))
            a.resource_set.add(c)
        a.save()


        r1 = Room.objects.create(name='A1', capacity=4)
        r2 = Room.objects.create(name='A2', capacity=4)
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

        ivan = ExtUser.objects.create(username="ivanov-ii", email="ivanov-ii@a.com", company=cos,
            first_name="Иван", middle_name="Иванович", last_name="Иванов", is_staff=True, is_superuser=True)
        ivan.set_password("1234")
        ivan.save()
        # Бронируем постоянное место
        r = ivan.company.area_set.first().resource_set.filter(name='07').first()
        r.seat.status = Seat.STATUS_PERSISTED
        r.seat.owner = ivan
        r.seat.save()

        petr = ExtUser.objects.create(username="petrov-pp", email="petrov-pp@a.com", company=cos,
            first_name="Пётр", middle_name="Петрович", last_name="Петров")
        petr.set_password("1234")
        petr.save()

        sidor = ExtUser.objects.create(username="sidorov-ss", email="sidorov-ss@a.com", company=cos,
            first_name="Сидор", middle_name="Сидорович", last_name="Сидоров")
        sidor.set_password("1234")
        sidor.save()

        # Брони

        tz = tzlocal()
        target_date = localtime(now()).date()

        event1 = Event.objects.create(description="Тестовое событие 1")
        event1.users.add(ivan, petr, sidor)
        event1.save()

        event2 = Event.objects.create(description="Тестовое событие 2")
        event2.users.add(ivan, petr)
        event2.save()

        event3 = Event.objects.create(description="Тестовое событие 3")
        event3.users.add(petr)
        event3.save()

        event4 = Event.objects.create(description="Планерка")
        event4.users.add(ivan, petr, sidor)
        event4.save()

        event5 = Event.objects.create(description="Совещание")
        event5.users.add(ivan, petr, sidor)
        event5.save()

        Booking.objects.create(
            resource=Seat.objects.filter(name='02').first(),
            user=ivan,
            start_ts=datetime(year=target_date.year, month=target_date.month, day=target_date.day, hour=9, minute=0, tzinfo=tz),
            end_ts=datetime(year=target_date.year, month=target_date.month, day=target_date.day, hour=13, minute=0, tzinfo=tz)
        )
        Booking.objects.create(
            resource=Seat.objects.filter(name='02').first(),
            user=petr,
            start_ts=datetime(year=target_date.year, month=target_date.month, day=target_date.day, hour=14, minute=0, tzinfo=tz),
            end_ts=datetime(year=target_date.year, month=target_date.month, day=target_date.day, hour=16, minute=0, tzinfo=tz)
        )
        Booking.objects.create(
            resource=Seat.objects.filter(name='02').first(),
            user=sidor,
            start_ts=datetime(year=target_date.year, month=target_date.month, day=target_date.day, hour=17, minute=0, tzinfo=tz),
            end_ts=datetime(year=target_date.year, month=target_date.month, day=target_date.day, hour=19, minute=0, tzinfo=tz)
        )
        Booking.objects.create(
            resource=Seat.objects.filter(name='03').first(),
            user=sidor,
            start_ts=datetime(year=target_date.year, month=target_date.month, day=target_date.day, hour=15, minute=0, tzinfo=tz) - timedelta(days=1),
            end_ts=datetime(year=target_date.year, month=target_date.month, day=target_date.day, hour=16, minute=0, tzinfo=tz)  + timedelta(days=2)
        )
        Booking.objects.create(
            resource=Room.objects.filter(name="A1").first(),
            user=ivan,
            start_ts=datetime(year=target_date.year, month=target_date.month, day=target_date.day, hour=10, minute=0, tzinfo=tz),
            end_ts=datetime(year=target_date.year, month=target_date.month, day=target_date.day, hour=11, minute=0, tzinfo=tz),
            event=event1
        )
        Booking.objects.create(
            resource=Room.objects.filter(name="A1").first(),
            user=ivan,
            start_ts=datetime(year=target_date.year, month=target_date.month, day=target_date.day, hour=13, minute=0, tzinfo=tz),
            end_ts=datetime(year=target_date.year, month=target_date.month, day=target_date.day, hour=13, minute=30, tzinfo=tz),
            event=event4
        )
        Booking.objects.create(
            resource=Room.objects.filter(name="A1").first(),
            user=ivan,
            start_ts=datetime(year=target_date.year, month=target_date.month, day=target_date.day, hour=16, minute=0, tzinfo=tz),
            end_ts=datetime(year=target_date.year, month=target_date.month, day=target_date.day, hour=17, minute=0, tzinfo=tz),
            event=event5
        )
        Booking.objects.create(
            resource=Room.objects.filter(name="A2").first(),
            user=ivan,
            start_ts=datetime(year=target_date.year, month=target_date.month, day=target_date.day, hour=8, minute=0, tzinfo=tz),
            end_ts=datetime(year=target_date.year, month=target_date.month, day=target_date.day, hour=9, minute=0, tzinfo=tz),
            event=event2
        )
        Booking.objects.create(
            resource=Room.objects.filter(name="A2").first(),
            user=ivan,
            start_ts=datetime(year=target_date.year, month=target_date.month, day=target_date.day, hour=9, minute=30, tzinfo=tz),
            end_ts=datetime(year=target_date.year, month=target_date.month, day=target_date.day, hour=19, minute=0, tzinfo=tz),
            event=event3
        )
        Booking.objects.create(
            resource=Cell.objects.filter(name='07').first(),
            user=ivan,
            start_ts=datetime(year=target_date.year, month=target_date.month, day=target_date.day, hour=8, minute=0, tzinfo=tz),
            end_ts=datetime(year=target_date.year, month=target_date.month, day=target_date.day, hour=19, minute=0, tzinfo=tz)
        )
        Booking.objects.create(
            resource=Cell.objects.filter(name='09').first(),
            user=ivan,
            start_ts=datetime(year=target_date.year, month=target_date.month, day=target_date.day, hour=13, minute=0, tzinfo=tz),
            end_ts=datetime(year=target_date.year, month=target_date.month, day=target_date.day, hour=14, minute=0, tzinfo=tz)
        )
