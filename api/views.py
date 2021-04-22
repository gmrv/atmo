from api.handlers import *
from main.models.core import *
from api.utils import *
from django.utils import timezone


@login_required
def index(request):
    return HttpResponseRedirect(reverse('api:home'))


@login_required
def home(request):
    return HttpResponse('<a href="/admin/doc/views/#ns|api">Документация модуля</a>')


@login_required
def area(request, id=None, username=None):
    """
    Обработка запросов связанных с объектом Площадка\r\n
    **GET**\r\n
        Получение одного объекта если всех объектов\r\n
        id - Если задан, возвращается заданный объект если не задан возвращаются все\r\n
        username - если задан возвращаем только площадки компании пользователя.\r\n
        ``*username получаем из параметра а не из request``
    """
    if request.method == "GET":
        # Обработка получения объектов
        result = area_get(request, id, username)
    else:
        # 400 Bad Request
        return JsonResponse({}, status=400, safe=False)

    response = get_response_template(code='ok', source=request.path, result=result)
    return JsonResponse(response, status=200, safe=False)


@login_required
def get_area_by_username(request, username):
    return area(request, id=None, username=username)


@login_required
def booking(request, id=None, username=None):
    """
    Обработка запросов связанных с объектом Бронирование\r\n
    **GET**\r\n
        Получение одного объекта если всех объектов\r\n
        id - Если задан, возвращается заданный объект если не задан возвращаются все\r\n

    **POST**\r\n
        Создание новой записи\r\n
        resource_id - Ресурс который собираемся забронировать\r\n
        date_start - Дата начала брони (если не задана то текущая)\r\n
        time_start - Время начала брони (если не задано то начало дня из settings.OPEN_TIME)\r\n
        date_end - Дата окончания брони (если не задана то текущая)\r\n
        time_end - Время окончания брони (если не задано то окончание дня из settings.CLOSE_TIME)\r\n
        todo: description - если задано создаем евент с соответстующим описанием\r\n

    **PUT**\r\n
        todo: Обновление/изменение полей записи, деактивация брони, подтверждение брони\r\n

    **DELETE**\r\n
        Удаление записи о бронировании\r\n
        id - Идентификатор удаляемой записи\r\n
    """
    if request.method == "GET":
        result = booking_get(request, id)

    elif request.method == "POST":
        result = booking_post(request)
        if not result:
            return JsonResponse({}, status=400, safe=False)

    elif request.method == "PUT":
        pass

    elif request.method == "DELETE":
        result = booking_delete(request, id)

    else:
        # 400 Bad Request
        JsonResponse({}, status=400, safe=False)

    response = get_response_template(code='ok', source=request.path, result=result)
    return JsonResponse(response, status=200, safe=False)


@login_required
def user(request, id=None, username=None):
    """
    Обработка запросов связанных с объектом Пользователь                                        \r\n
    **GET**                                                                                     \r\n
        Получение одного объекта если всех объектов                                             \r\n
        /api/user           - Получить всех пользователей;                                      \r\n
        /api/user/1         - Получить пользователя с id = 1;                                   \r\n
        /api/user/ivanov-ii - Получить пользователя с username = ivanov-ii;                     \r\n
    **POST**                                                                                    \r\n
        Cоздать пользователя                                                                    \r\n
        /api/user                                                                               \r\n
        username - Логин;                                                                       \r\n
        password - Пароль;                                                                      \r\n
        first_name - Имя;                                                                       \r\n
        middle_name - Отчество;                                                                 \r\n
        last_name - Фамилия;                                                                    \r\n
        email - Электронная почта;                                                              \r\n
        is_superuser - Флаг администратора;                                                     \r\n
        is_staff - Флаг персонала;                                                              \r\n
        is_active - Фдаг активности пользователя;                                               \r\n
        company_id - Идентификатора комании.                                                    \r\n
    **PUT**                                                                                     \r\n
        Обновить пользователя                                                                   \r\n
        Параметры посыдаются через тело запроса, как в POST                                     \r\n
        /api/user                                                                               \r\n
        id  - Если задан, значит обновить пользователя с этим id. Приоритетнее чем username;    \r\n
        username - Если задан, значит обновить пользователя с этим username;                    \r\n
        Остальные поля как в POST                                                               \r\n
    **DELETE**                                                                                  \r\n
        Удаление пользователя с заданным id или username                                        \r\n
        Фактически не удаляем. Помечаем is_active = False                                       \r\n
        /api/user/1                                                                             \r\n
        /api/user/ivanov-ii                                                                     \r\n
    """
    result = None
    if request.method == "GET":
        result = user_get(request, id, username)
    elif request.method == "POST":
        result = user_post(request)
    elif request.method == "PUT":
        result = user_put(request)
    elif request.method == "DELETE":
        result = user_delete(request, id, username)
    else:
        return JsonResponse({}, status=400, safe=False)

    if not result:
        return JsonResponse({}, status=400, safe=False)

    response = get_response_template(code='ok', source=request.path, result=result)
    return JsonResponse(response, status=200, safe=False)


@login_required
def set_default_area(request, area_id, username=None):
    """
    Установить площадку по умолчанию для пользователя
    """
    if username:
        xuser = ExtUser.objects.get(username=username)
    else:
        xuser = request.user.extuser

    xuser.def_area_id = area_id
    xuser.save()

    response = get_response_template(code='ok', source=request.path, result=None)
    return JsonResponse(response, status=200, safe=False)


@login_required
def get_area_resource_list(request, area_id, resource_type=Resource.RESOURCE_TYPE_ALL):
    """
    Список ресурсов закрепленных для площадки
    /api/get_area_resource_list/1/resource
    """
    area = Area.objects.get(pk=area_id)
    seats_list = []
    rooms_list = []
    for r in area.resource_set.all():
        if r.type == Resource.RESOURCE_TYPE_SEAT:
            seats_list.append({"id" : r.id, "name": r.name, "calendar": r.get_calendar()})
        else:
            rooms_list.append({"id": r.id, "name": r.name, "calendar": r.get_calendar()})

    result = {"seats": seats_list, "rooms": rooms_list}
    response = get_response_template(code='ok', source=request.path, result=result)

    return JsonResponse(response, status=200, safe=False)