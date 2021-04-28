from datetime import datetime, timedelta
from dateutil.tz import tzlocal
from django.conf import settings
from django.utils.timezone import localtime, now
from django.db import models
from django.contrib.auth.models import User, Group
from api.utils import datetimestring_to_ts
from main.utils import get_pin


class Common(models.Model):
    name = models.CharField(help_text='Наименование', max_length=250)

    def __str__(self):
        return ("Id: %s; Name: %s;"  % (self.id, self.name))

    class Meta:
        abstract = True


class Company(Common):
    """
    Компания это вершина иерархии объектов (Компания - Площадка(Area) - Ресурсы)
    Пользователь имеет доступ только к тем ресурсам которые привязаны к его компании.
    """
    short_name = models.CharField(help_text='Короткое наименование',max_length=100)
    full_name = models.CharField(help_text='Полное наименование', max_length=250)
    code = models.PositiveBigIntegerField(help_text='Код ЦФО', blank=False, default=0)
    root_dir = models.CharField(help_text='Каталог со статикой', max_length=100)

    def to_json(self, is_short=True, target_date=None):
        result={
            "id": self.id,
            "name": self.name,
            "short_name": self.short_name,
            "full_name": self.full_name,
            "code": self.code,
            "root_dir": self.root_dir,
            "areas": {} if is_short else self.get_areas_json(is_short=is_short, target_date=target_date)
        }
        return result

    def get_areas_json(self, is_short=True, target_date=None):
        result = []
        for a in self.area_set.all():
            result.append(a.to_json(is_short, target_date))
        return result


class Area(Common):
    """
    Площадки (Коворкинги)
    map_url - Карта площадки в формате svg, с расширением *.html для включение в тело страницы
    company - Компания которой пренадлежит площадка
    """
    AREA_TYPE_COWORKING = 'cow'
    AREA_TYPE_FLOOR = 'flr'
    AREA_TYPE = (
        (AREA_TYPE_COWORKING, 'Коворкинг'),
        (AREA_TYPE_FLOOR, 'Этаж'),
    )
    type = models.CharField(help_text='Тип площадки', max_length=3, choices=AREA_TYPE, default=AREA_TYPE_COWORKING)
    map_url = models.CharField(help_text='Карта площадки', max_length=100)
    company = models.ForeignKey(Company, help_text= 'Компания',
                                on_delete=models.deletion.CASCADE, blank=True, null=True, default=None)

    def __str__(self):
        return ("%s::%s (id: %s);"  % (self.type, self.name, self.id))

    def to_json(self, is_short=True, target_date=None):
        result={
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "map_url": self.map_url,
            "company": self.company_id,
            "resources": {} if is_short else self.get_resources_json(is_short=is_short, target_date=target_date)
        }
        return result

    def get_resources_json(self, is_short=False, target_date=None):
        result = {
            "rooms": [],
            "seats": []
        }
        for r in self.resource_set.all():
                result[r.type + "s"].append(r.to_json(is_short, target_date))
        return result


class ExtUser(User):
    """
    Дополнительная информация о пользователе
    """
    middle_name = models.CharField(help_text='Отчество', max_length=500)
    company = models.ForeignKey(Company, help_text='Компания', on_delete=models.deletion.CASCADE, blank=True, null=True, default=None)
    def_area = models.ForeignKey(Area, help_text='Площадка по умолчанию', on_delete=models.deletion.CASCADE, blank=True, null=True, default=None)

    def to_json(self, is_short=False):
        if is_short:
            result = {
                "id": self.id,
                "username": self.username,
            }
        else:
            result = {
                "id": self.id,
                "username": self.username,
                "first_name": self.first_name,
                "middle_name": self.middle_name,
                "last_name": self.last_name,
                "email": self.email,
                "is_superuser": self.is_superuser,
                "is_staff": self.is_staff,
                "is_active": self.is_active,
                "company_id": self.company_id,
                "booking_set": []
            }

            booking_set = self.booking_set.all()
            booking_arr = []
            for b in booking_set:
                booking_arr.append({
                    "id": b.id,
                    "start_ts": b.start_ts,
                    "end_ts": b.end_ts
                })
            result["booking_set"] = booking_arr
        return result


class Notification(Common):
    """
    Массовые сообщения для пользователей
    """
    message = models.CharField(help_text='Сообщение', max_length=500)
    start = models.DateTimeField(help_text='Начало брони', blank=True)
    finish = models.DateTimeField(help_text='Окончание брони', blank=True)
    users_group = models.ForeignKey(Group, help_text= 'Группа', on_delete=models.deletion.CASCADE, blank=True, null=True, default=None)
    is_active = models.BooleanField(blank=True, default=True)


class Resource(Common):
    """
    Ресурсы
    Родительский объект для всех объектов которые могут быть забронированы
    """
    RESOURCE_TYPE_ALL = 'resource'
    RESOURCE_TYPE_SEAT = 'seat'
    RESOURCE_TYPE_ROOM = 'room'
    area = models.ForeignKey(Area, help_text='Родительская площадка', on_delete=models.deletion.CASCADE, blank=True, null=True, default=None)

    @property
    def type(self):
        """ Возвращает тип ресурса """
        if hasattr(self, 'room'):
            return self.RESOURCE_TYPE_ROOM
        if hasattr(self, 'seat'):
            return self.RESOURCE_TYPE_SEAT
        return self.RESOURCE_TYPE_ALL

    def __str__(self):
        return ("Id: %s; Type: %s; Name: %s;" % (self.id, type, self.name))

    def get_raw_calendar(self):
        """
        Календарь ресурса на день
        Возвращает словарь временных отрезков с разбивкой по полчаса с открытия по закрытие
        """
        calendar = []

        # Default OPEN_TIME is 8AM
        open_hour = '8'
        open_minute = '00'
        if hasattr(settings, 'OPEN_TIME') and ':' in settings.OPEN_TIME:
            open_hour = settings.OPEN_TIME.split(':')[0]
            open_minute = settings.OPEN_TIME.split(':')[1]

        # Default CLOSE_TIME is 6PM
        close_hour = '18'
        close_minute = '00'
        if hasattr(settings, 'CLOSE_TIME') and ':' in settings.CLOSE_TIME:
            close_hour = settings.CLOSE_TIME.split(':')[0]
            close_minute = settings.CLOSE_TIME.split(':')[1]

        for num in range(int(open_hour), int(close_hour)):
            minutes = open_minute
            for count in range(0, 2):
                time_block = {}
                calendar.append(time_block)
                if num <= 12:
                    time_block['hour'] = str(num)
                else:
                    time_block['hour'] = str(num - 12)
                time_block['mil_hour'] = str(num)

                time_block['minutes'] = minutes
                if minutes == '00':
                    minutes = '30'
                else:
                    minutes = '00'
                    num += 1
        return calendar

    def get_calendar(self, target_date=None):
        """
        Календарь ресурса бронирования ресурса на текущую дату
        target_date - Дата за которую нужно получить календарь брони
        Возвращает словарь временных отрезков с разбивкой по полчаса с открытия по закрытие
        Помеченных в зависимости от их статуса занятости.
        """
        if not target_date:
            target_date = localtime(now()).date()
        else:
            # todo: переделать
            date_arr = target_date.split('-')
            target_date = datetime(year=int(date_arr[0]), month=int(date_arr[1]), day=int(date_arr[2]))

        calendar = self.get_raw_calendar()

        # Extract the start and end times from our target date and the raw calendar
        first_block = calendar[0]
        last_block = calendar[len(calendar) - 1]
        tz = tzlocal()
        booking_window = timedelta(days=settings.BOOKING_WINDOW)
        start = datetime(year=target_date.year, month=target_date.month, day=target_date.day, hour=int(first_block['mil_hour']), minute=int(first_block['minutes']), tzinfo=tz) - booking_window
        end = datetime(year=target_date.year, month=target_date.month, day=target_date.day, hour=int(last_block['mil_hour']), minute=int(last_block['minutes']), tzinfo=tz) + booking_window
        end = end + timedelta(minutes=30)

        bookings = self.booking_set.filter(resource=self, start_ts__gte=start, end_ts__lte=end)
        for booking in bookings:
            start_ts = localtime(booking.start_ts)
            end_ts = localtime(booking.end_ts)
            for block in calendar:
                block_ts = datetime(year=target_date.year, month=target_date.month, day=target_date.day, hour=int(block['mil_hour']), minute=int(block['minutes']), tzinfo=tz)
                if start_ts <= block_ts and block_ts < end_ts:
                    block['reserved'] = True
                    block['user'] = booking.user.username
        return calendar

    def get_percent_of_booked_time(self, target_date=None):
        """
        Процент забронированного времени от доступного в пределах дня.
        """
        if not target_date:
            target_date = localtime(now()).date()
        else:
            # todo: переделать
            date_arr = target_date.split('-')
            target_date = datetime(year=int(date_arr[0]), month=int(date_arr[1]), day=int(date_arr[2]))

        tz = tzlocal()
        booking_window = timedelta(days=settings.BOOKING_WINDOW)
        day_start = datetime(year=target_date.year, month=target_date.month, day=target_date.day, hour=0, minute=0, tzinfo=tz) - booking_window
        day_end = datetime(year=target_date.year, month=target_date.month, day=target_date.day, hour=23, minute=59, tzinfo=tz) + booking_window

        open_time = datetime(year=target_date.year, month=target_date.month, day=target_date.day, hour=int(settings.OPEN_TIME.split(":")[0]), minute=int(settings.OPEN_TIME.split(":")[1]), tzinfo=tz)
        close_time = datetime(year=target_date.year, month=target_date.month, day=target_date.day, hour=int(settings.CLOSE_TIME.split(":")[0]), minute=int(settings.CLOSE_TIME.split(":")[1]), tzinfo=tz)

        all_time = close_time - open_time
        booked_time = timedelta()

        bookings = self.booking_set.filter(resource=self, start_ts__gte=day_start, end_ts__lte=day_end)
        for booking in bookings:
            booking_start_ts = localtime(booking.start_ts)
            booking_end_ts = localtime(booking.end_ts)
            if booking.start_ts < open_time and booking.start_ts.day != target_date.day:
                booking_start_ts = open_time
            if booking.end_ts > close_time and booking.end_ts.day != target_date.day:
                booking_end_ts = close_time

            if (localtime(booking.start_ts) <= open_time and close_time < localtime(booking.end_ts)) or (booking.start_ts.day == target_date.day or booking.end_ts.day == target_date.day):
                booked_time = booked_time + (booking_end_ts - booking_start_ts)


        return(round(booked_time.total_seconds()/all_time.total_seconds()*100, 2))

    def to_json(self, is_short=False, target_date=None):
        if hasattr(self, 'room'):
            return self.room.to_json(is_short, target_date)
        if hasattr(self, 'seat'):
            return self.seat.to_json(is_short, target_date)


class Room(Resource):
    """
    Переговорные
    location - Адрес, описание как найти;
    description - Общее описание комнаты;
    capacity - количество сидячих мест;
    has_av - Наличие аудио/видео аппаратуры
    has_phone - Наличие телефона
    """
    location = models.TextField(help_text='Описание расположения', blank=True, null=True)
    description = models.TextField(help_text='Общее описание', blank=True, null=True)
    capacity = models.SmallIntegerField(help_text='Количество сидячих мест', default=0)
    has_av = models.BooleanField(help_text='Наличие аудио/видео аппаратуры', default=False)
    has_phone = models.BooleanField(help_text='Наличие телефона', default=False)

    def to_json(self, is_short=False, target_date=None):
        result = {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "area": self.area_id,
            "location": self.location,
            "capacity": self.capacity,
            "description": self.description,
            "has_av": self.has_av,
            "has_phone": self.has_phone,
            "calendar": {} if is_short else self.get_calendar(target_date),
            "percent_of_booked_time": self.get_percent_of_booked_time(target_date)
        }
        return result


class Seat(Resource):
    """
    Рабочие места
    persisted - True если закреплено за конкретным сотрудником
    owner - Сотрудник за которым закреплено место
    """
    persisted = models.BooleanField(help_text= 'Постоянное место', blank=True, default=False)
    owner = models.ForeignKey(User, help_text= 'За кем закреплено', on_delete=models.deletion.CASCADE, blank=True, null=True, default=None)

    def to_json(self, is_short=False, target_date=None):
        result = {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "area": self.area_id,
            "persisted": self.persisted,
            "owner": self.owner_id,
            "calendar": {} if is_short else self.get_calendar(target_date),
            "percent_of_booked_time": self.get_percent_of_booked_time(target_date)
        }
        return result


class Event(Common):
    """
    Событие всязанное с бронированием
    Например: Ежедневная планерка
    Актуально только для переговорок (пока)
    """
    description = models.CharField(help_text='Описание', max_length=500)
    users = models.ManyToManyField(User, blank=True, help_text= 'Участники', default=None)

    def to_json(self):
        result = {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "users": [],
        }
        users = [];
        for u in self.users:
            users.append(u.id)

        result.users = users
        return result


class ServiceRequest(Common):
    """
    Запросы пользователей к администрации коворкинга
     resource - Ресурс к которому привязан запрос. Пока предполагается что в основном это будет забронированное место.
     created_by - ползователь сгенерировавший запрос
     message - тело запроса
     active - активный или отработанный запрос
    """
    created_at = models.DateTimeField(help_text='Время создания', auto_now_add=True)
    created_by = models.CharField(help_text= 'Кем создано', max_length=50, null=False, default='')
    resource = models.ForeignKey(Resource, help_text='Объект запроса', on_delete=models.deletion.CASCADE, blank=True, null=True, default=None)
    message = models.CharField(help_text='Сообщение', max_length=500)
    active = models.BooleanField(blank=True, default=True)

    def to_json(self, is_short=True):
        result = {
            "id": self.id,
            "created_at": self.created_at,
            "created_by": self.created_by,
            "resource": self.resource_id,
            "message": self.message if not is_short else {},
            "active": self.active
        }
        return result


class Booking(Common):
    """
    Записи о бронировании ресурсов
    """
    created_at = models.DateTimeField(help_text='Время создания', auto_now_add=True)
    created_by = models.CharField(help_text= 'Кем создано', max_length=50, null=False, default='')
    changed_at = models.DateTimeField(help_text='Время изменения', auto_now=True)
    changed_by = models.CharField(help_text= 'Кем изменено', max_length=50, null=False, default='')
    resource = models.ForeignKey(Resource, help_text= 'Объект бронирования', on_delete=models.deletion.CASCADE, blank=True, null=True, default=None)
    user = models.ForeignKey(User, help_text= 'Бронирующий', on_delete=models.deletion.CASCADE, blank=False, null=True, default=None)
    start_ts = models.DateTimeField(help_text='Начало брони', blank=False)
    end_ts = models.DateTimeField(help_text='Окончание брони', blank=False)
    confirmed = models.BooleanField(help_text='Подтверждение брони', blank=True, default=False)
    confirmed_at = models.DateTimeField(help_text='Время изменения', blank=True, null=True)
    confirmed_by = models.CharField(help_text= 'Кем подтверждено', max_length=50, blank=True, null=True, default='')
    pin = models.PositiveSmallIntegerField(help_text='PIN-код', default=get_pin)
    event = models.ForeignKey(Event, help_text= 'Событие', on_delete=models.deletion.CASCADE, blank=True, null=True, default=None)
    active = models.BooleanField(blank=True, default=True)

    @staticmethod
    def can_it_booked(resource_id, start_date=None, start_time=None, end_date=None, end_time=None):
        """
        Проверка может ли быть забронирован указанный промежуток времени.
        Booking.can_it_booked(
            resource_id=2,
            start_date="2021-04-27",
            start_time="13:00",
            end_date="2021-04-27",
            end_time="14:30"
        )
        """
        if not start_date: start_date = datetime.today().strftime('%Y-%m-%d')
        if not start_time: start_time = settings.OPEN_TIME
        if not end_date: end_date = start_date
        if not end_time: end_time = settings.CLOSE_TIME

        start_ts = datetimestring_to_ts(start_date + " " + start_time, "%Y-%m-%d %H:%M")
        end_ts = datetimestring_to_ts(end_date + " " + end_time, "%Y-%m-%d %H:%M")

        # Проверяем короткие брони
        # Если есть хотя бы одна котороя уместится между началом и концом нашего отрезка, значит бронировать нельзя
        bq = Booking.objects.filter(resource_id=resource_id, start_ts__gte=start_ts, end_ts__lte=end_ts)
        #print("Short booking count:", bq.count())
        if bq.count() > 0: return False

        # Проверяем длинные брони
        # Проверяем окажется ли начало и/или конец нашего отрезка бронирования между началом и концом длинной брони
        tz = tzlocal()
        bq = Booking.objects.filter(resource_id=resource_id, start_ts__gte=datetime.now(tz=tz)-timedelta(settings.BOOKING_WINDOW), end_ts__lte=datetime.now(tz=tz)+timedelta(settings.BOOKING_WINDOW))
        for b in bq:
            # print("Start point =", start_ts)
            # print("End point =", end_ts)
            # print("b.start_ts =", b.start_ts, "b.end_ts =", b.end_ts)
            # print("Result:", (b.start_ts < start_ts < b.end_ts) or (b.start_ts < end_ts < b.end_ts))
            if (b.start_ts < start_ts < b.end_ts) or (b.start_ts < end_ts < b.end_ts): return False
        return True


    def to_json(self):
        result = {
            "id": self.id,
            "created_at": self.created_at,
            "created_by": self.created_by,
            "changed_at": self.changed_at,
            "changed_by": self.changed_by,
            "resource": self.resource_id,
            "user": self.user_id,
            "start_ts": self.start_ts,
            "end_ts": self.end_ts,
            "confirmed": self.confirmed,
            "confirmed_at": self.confirmed_at,
            "confirmed_by": self.confirmed_by,
            "pin": self.pin,
            "event": self.event_id,
            "active": self.active
        }
        return result