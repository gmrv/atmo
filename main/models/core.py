from django.db import models
from django.contrib.auth.models import User, Group
from main.utils import get_pin


class Common(models.Model):
    name = models.CharField(help_text='Наименование', max_length=250)

    def __str__(self):
        return ("Id: %s; Name: %s;"  % (self.id, self.name))

    class Meta:
        abstract = True


class Company(Common):
    """
    Компания которой пренадлежит площадка
    """
    short_name = models.CharField(help_text='Короткое наименование',max_length=100)
    full_name = models.CharField(help_text='Полное наименование', max_length=250)
    code = models.PositiveBigIntegerField(help_text='Код ЦФО', blank=False, default=0)
    root_dir = models.CharField(help_text='Каталог со статикой', max_length=100)


class Area(Common):
    """
    Площадки (Коворкинги)
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


class ExtUser(User):
    """
    Дополнительная информация о пользователе
    """
    middle_name = models.CharField(help_text='Отчество', max_length=500)
    company = models.ForeignKey(Company, help_text='Компания', on_delete=models.deletion.CASCADE, blank=True, null=True, default=None)
    active = models.BooleanField(blank=True, default=True)
    def_area = models.ForeignKey(Area, help_text='Площадка по умолчанию', on_delete=models.deletion.CASCADE, blank=True, null=True, default=None)


class Notification(Common):
    """
    Массовые сообщения для пользователей
    """
    message = models.CharField(help_text='Сообщение', max_length=500)
    start = models.DateTimeField(help_text='Начало брони', blank=True)
    finish = models.DateTimeField(help_text='Окончание брони', blank=True)
    users_group = models.ForeignKey(Group, help_text= 'Группа', on_delete=models.deletion.CASCADE, blank=True, null=True, default=None)
    active = models.BooleanField(blank=True, default=True)


class Resource(Common):
    """
    Ресурсы
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


class Room(Resource):
    """
    Переговорные
    """
    capacity = models.SmallIntegerField(help_text= 'Количество сидячих мест', default=0)


class Seat(Resource):
    """
    Рабочие места
    """
    persisted = models.BooleanField(help_text= 'Постоянное место', blank=True, default=False)
    owner = models.ForeignKey(User, help_text= 'За кем закреплено', on_delete=models.deletion.CASCADE, blank=True, null=True, default=None)


class Event(Common):
    """
    Событие всязанное с бронированием
    Например: Ежедневная планерка
    Актуально только для переговорок (пока)
    """
    description = models.CharField(help_text='Описание', max_length=500)
    users = models.ManyToManyField(User, blank=True, help_text= 'Участники', default=None)


class Request(Common):
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
    start = models.DateTimeField(help_text='Начало брони', blank=False)
    finish = models.DateTimeField(help_text='Окончание брони', blank=False)
    confirmed = models.BooleanField(help_text='Подтверждение брони', blank=True, default=False)
    confirmed_at = models.DateTimeField(help_text='Время изменения')
    confirmed_by = models.CharField(help_text= 'Кем подтверждено', max_length=50, null=False, default='')
    confirmation_pin = models.PositiveSmallIntegerField(help_text= 'PIN-код', default=get_pin)
    event = models.ForeignKey(Event, help_text= 'Событие', on_delete=models.deletion.CASCADE, blank=True, null=True, default=None)
    active = models.BooleanField(blank=True, default=True)