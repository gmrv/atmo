from django.db import models
from django.contrib.auth.models import User, Group
from main.utils import get_pin

# todo: Try
# class Resource(Common)
# class Room(Resource)
# class Seat(Resource)


class Common(models.Model):
    name = models.CharField(help_text='Наименование', max_length=250)

    def __str__(self):
        return ("Id: %s; Name: %s;"  % (self.id, self.name))

    class Meta:
        abstract = True


# Компания которой пренадлежат площадки
class Company(Common):
    short_name = models.CharField(help_text='Короткое наименование',max_length=100)
    full_name = models.CharField(help_text='Полное наименование', max_length=250)
    code = models.PositiveBigIntegerField(help_text='Код ЦФО', blank=False, default=0)
    root_dir = models.CharField(help_text='Каталог со статикой', max_length=100)


# Типы площадок
# Пока нет понимания что за типы.
# Добавлено на развитие
class AreaType(Common):
    pass

    def __str__(self):
        return (self.name)


# Площадки (Коворкинги)
class Area(Common):
    type = models.ForeignKey(AreaType, help_text= 'Тип площадки',
                                on_delete=models.deletion.CASCADE, blank=True, null=True, default=None)
    map_url = models.CharField(help_text='Карта площадки', max_length=100)
    company = models.ForeignKey(Company, help_text= 'Компания',
                                on_delete=models.deletion.CASCADE, blank=True, null=True, default=None)

    def __str__(self):
        return ("%s::%s (id: %s);"  % (self.type, self.name, self.id))


# Типы ресурсов
# Переговорка, рабочее место, парковочное место, локкер и т.д.
# Еще могут быть приватные ресурсы, личное рабочее место
class ResourceType(Common):
    pass

    def __str__(self):
        return (self.name)


# Ресурсы
# см. Типы ресурсов
class Resource(Common):
    type = models.ForeignKey(ResourceType, help_text='Тип ресурса',
                             on_delete=models.deletion.CASCADE, blank=True, null=True, default=None)
    area = models.ForeignKey(Area, help_text='Родительская площадка',
                                  on_delete=models.deletion.CASCADE, blank=True, null=True, default=None)

    def __str__(self):
        return ("Id: %s; Type: %s; Name: %s;" % (self.id, self.type, self.name))


# Свойства ресурса
# Например для переговорки это может быть наличие проектора
# name: Наличие проектора; type: bool; value_bool: True
class Property(Common):
    BOOL = 'bool'
    REAL = 'real'
    TEXT = 'text'
    PROPERTY_TYPE_CHOICES = (
        (BOOL, 'Булево'),
        (REAL, 'Число'),
        (TEXT, 'Строка'),
    )
    resource = models.ForeignKey(Resource, help_text='Родительский ресурс', on_delete=models.deletion.CASCADE,
                                 blank=True, null=True, default=None)
    type = models.CharField(help_text='Тип поля', choices=PROPERTY_TYPE_CHOICES, max_length=4)
    value_bool = models.BooleanField(blank=True, default=False)
    value_real = models.DecimalField(blank=True, null=True, max_digits=11, decimal_places=2)
    value_text = models.CharField(blank=True, null=True, max_length=250)

    def __str__(self):
        return ("%s %s::%s;" % (self.resource.type, self.resource.name, self.name))


# Событие всязанное с бронированием
# Например: Ежедневная планерка
# Актуально только для переговорок (пока)
class Event(Common):
    description = models.CharField(help_text='Описание', max_length=500)
    users = models.ManyToManyField(User, blank=True, help_text= 'Участники', default=None)


# Запросы пользователей к администрации коворкинга
#  resource - Ресурс к которому привязан запрос. Пока предполагается что в основном это будет забронированное место.
#  created_by - ползователь сгенерировавший запрос
#  message - тело запроса
#  active - активный или отработанный запрос
class Request(Common):
    created_at = models.DateTimeField(help_text='Время создания', auto_now_add=True)
    created_by = models.CharField(help_text= 'Кем создано', max_length=50, null=False, default='')
    resource = models.ForeignKey(Resource, help_text='Объект запроса', on_delete=models.deletion.CASCADE, blank=True, null=True, default=None)
    message = models.CharField(help_text='Сообщение', max_length=500)
    active = models.BooleanField(blank=True, default=True)


# Дополнительная информация о пользователе
# todo: Разобраться
class ExtUser(User):
    middle_name = models.CharField(help_text='Отчество', max_length=500)
    company = models.ForeignKey(Company, help_text='Компания', on_delete=models.deletion.CASCADE, blank=True, null=True, default=None)
    active = models.BooleanField(blank=True, default=True)
    def_area = models.ForeignKey(Area, help_text='Площадка по умолчанию', on_delete=models.deletion.CASCADE, blank=True, null=True, default=None)


# Массовые сообщения для пользователей
class Notification(Common):
    message = models.CharField(help_text='Сообщение', max_length=500)
    start = models.DateTimeField(help_text='Начало брони', blank=True)
    finish = models.DateTimeField(help_text='Окончание брони', blank=True)
    users_group = models.ForeignKey(Group, help_text= 'Группа', on_delete=models.deletion.CASCADE, blank=True, null=True, default=None)
    active = models.BooleanField(blank=True, default=True)


# Записи о бронировании ресурсов
#  confirmed         - подтверждение бронирования
#  confirmed_at      - когда подтверждено
#  confirmed_by      - кем подтверждено
#  confirmation_pin  - пин-код который надо ввести для подтверждения
# todo: уирать бланк=тру на пользователях и начале окончании бронирования
class Booking(Common):
    created_at = models.DateTimeField(help_text='Время создания', auto_now_add=True)
    created_by = models.CharField(help_text= 'Кем создано', max_length=50, null=False, default='')
    changed_at = models.DateTimeField(help_text='Время изменения', auto_now=True)
    changed_by = models.CharField(help_text= 'Кем изменено', max_length=50, null=False, default='')
    resource = models.ForeignKey(Resource, help_text= 'Объект бронирования', on_delete=models.deletion.CASCADE, blank=True, null=True, default=None)
    user = models.ForeignKey(User, help_text= 'Бронирующий', on_delete=models.deletion.CASCADE, blank=True, null=True, default=None)
    start = models.DateTimeField(help_text='Начало брони', blank=True)
    finish = models.DateTimeField(help_text='Окончание брони', blank=True)
    confirmed = models.BooleanField(blank=True, default=False)
    confirmed_at = models.DateTimeField(help_text='Время изменения')
    confirmed_by = models.CharField(help_text= 'Кем подтверждено', max_length=50, null=False, default='')
    confirmation_pin = models.PositiveSmallIntegerField(help_text= 'PIN-код', default=get_pin)
    event = models.ForeignKey(Event, help_text= 'Событие', on_delete=models.deletion.CASCADE, blank=True, null=True, default=None)
    active = models.BooleanField(blank=True, default=True)