import urllib
from datetime import datetime
from django.utils import timezone


class PUT:
    """
    Класс для работы с request.body метода PUT
    По аналогии с request.POST и request.GET
    """
    params = {}

    def __init__(self, request):
        for item in request.body.decode("utf-8").split('&'):
            arr = item.split("=")
            self.params[urllib.parse.unquote(arr[0])] = urllib.parse.unquote(arr[1])

    def get(self, key, default):
        if key in self.params:
            return self.params[key]
        else:
            return default


def get_response_template(code='0', result={}, source='unknown') -> object:
    """
    Возвращаем стандартизированный шаблон для ответа
    """
    template = {
        'code': code,
        'result': result,
        'source': source
    }
    return template


def datetimestring_to_ts(datetimestring, template):
    """
    Преобразование строки в тайм-штамп
    time_stamp = datetimestring_to_ts("2021-04-22 00:00", "%Y-%m-%d %H:%M")
    """
    return timezone.make_aware(
        datetime.strptime(datetimestring, template),
        timezone.get_current_timezone()
    )


