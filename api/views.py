from api.handlers import *
from main.models.core import *
from api.utils import *
from django.utils.timezone import localtime, now


@login_required
def index(request):
    """
    Корень эндпоинта API                                            \r\n
    Содержит необходимые для работы сторонних приложений методы.    \r\n
    /admin/doc/views/#ns|api - Документация модуля                  \r\n
    """
    return HttpResponseRedirect(reverse('api:home'))


@login_required
def home(request):
    """
    Корень эндпоинта API                                            \r\n
    Содержит необходимые для работы сторонних приложений методы.    \r\n
    /admin/doc/views/#ns|api - Документация модуля                  \r\n
    """
    return HttpResponse('<a href="/admin/doc/views/#ns|api">Документация модуля</a>')


@login_required
def area(request, area_id=None, username=None, target_date=None):
    """
    Обработка запросов связанных с объектом Площадка (Area).                                        \r\n
    Реализовано только получение т.к. остальные действия будут выполняться только через админку.    \r\n
    **GET**                                                                                         \r\n
        Получение одного , некоторых или всех объектов.                                             \r\n
        /api/area   - Получаем список всех площадок в сокращенном виде (id и имя).                  \r\n
        /api/area/1 - Получаем площадку с заданным идентификатором + список всех ресурсов площадки. \r\n
        /api/area/ivanon-ii - Получаем дочерние площадки компании пользователя user.company.        \r\n
    """
    if request.method == "GET":
        result = area_get(request, area_id, username, target_date)
    else:
        return JsonResponse({}, status=400, safe=False)

    response = get_response_template(code='ok', source=request.path, result=result)
    return JsonResponse(response, status=200, safe=False)


@login_required
def booking(request, booking_id=None, date=None):
    """
    Обработка запросов связанных с объектом Бронирование (Booking). \r\n
    **GET**\r\n
        Получение одного или всех объектов бронирования. \r\n
        /api/booking    - Получить все объекты бронирования; \r\n
        /api/booking/1  - Получить бронирование с идентификатором 1; \r\n
        /api/booking/2021-04-22 - Получить все брони дата начала которых 2021-04-22; \r\n
    **POST**\r\n
        Создание новой записи\r\n
        user_id - Пользователь на которого собрираемся бронировать ресурс\r\n
        resource_id - Ресурс который собираемся забронировать\r\n
        date_start - Дата начала брони (если не задана то текущая)\r\n
        time_start - Время начала брони (если не задано то начало дня из settings.OPEN_TIME)\r\n
        date_end - Дата окончания брони (если не задана то текущая)\r\n
        time_end - Время окончания брони (если не задано то окончание дня из settings.CLOSE_TIME)   \r\n
        todo: description - если задано создаем евент с соответстующим описанием\r\n

    **PUT**\r\n
        todo: Обновление/изменение полей записи, деактивация брони, подтверждение брони\r\n

    **DELETE**\r\n
        Удаление записи о бронировании. \r\n
        /api/booking/1 - Удалить запись с идентификатором 1. \r\n
    """
    if request.method == "GET":
        result = booking_get(request, booking_id, date)

    elif request.method == "POST":
        result = booking_post(request)
        if not result:
            return JsonResponse({}, status=400, safe=False)

    elif request.method == "PUT":
        pass

    elif request.method == "DELETE":
        result = booking_delete(request, booking_id)

    else:
        JsonResponse({}, status=400, safe=False)

    response = get_response_template(code='ok', source=request.path, result=result)
    return JsonResponse(response, status=200, safe=False)


@login_required
def booking_confirmation(request, booking_id, pin):
    """
    Подтверждение брони
    PIN генерируется в момент создания брони и отправляется пользователю через email, sms или личный кабинет.
    /api/booking/confirmation/1/0000 - Подтвердить бронь с идентификатором 1, код подтвержения 0000

    """
    result = {}
    b = Booking.objects.get(pk=booking_id)
    if b.confirmation_pin == pin:
        b.confirmed = True
        b.confirmed_by = request.user.id
        b.confirmed_at = localtime(now())
        b.save()
        result = b.to_json()
    else:
        JsonResponse({}, status=400, safe=False)
    response = get_response_template(code='ok', source=request.path, result=result)
    return JsonResponse(response, status=200, safe=False)


@login_required
def booking_can(request, resource_id, start_date=None, start_time=None, end_date=None, end_time=None):
    """
    Проверка может ли быть забронирован указанный промежуток времени.
    /api/booking/can/2/2021-04-27/08:00/2021-04-27/19:00
    """
    result = Booking.can_it_booked(resource_id, start_date, start_time, end_date, end_time)
    response = get_response_template(code='ok', source=request.path, result=result)
    return JsonResponse(response, status=200, safe=False)



@login_required
def company(request, company_id=None, target_date=None):
    """
    Обработка запросов связанных с объектом Компания
    Компания это вершина иерархии объектов (Компания - Площадка(Area) - Ресурсы)
    Пользователь имеет доступ только к тем ресурсам которые привязаны к его компании.
    """
    result = None
    if request.method == "GET":
        result = company_get(request, company_id=company_id, target_date=target_date)
    else:
        return JsonResponse({}, status=400, safe=False)

    if not result:
        return JsonResponse({}, status=400, safe=False)

    response = get_response_template(code='ok', source=request.path, result=result)
    return JsonResponse(response, status=200, safe=False)


@login_required
def resource(request, resource_id=None):
    """
    Обработка запросов связанных с объектом Ресурс (Resource)                                   \r\n
    Resource это родительский класс для Seat и Room                                             \r\n
    Все основые операции (бронирование ...) выполняются через этот класс                        \r\n
    **GET**                                                                                     \r\n
        Получение одного объекта если всех объектов                                             \r\n
        /api/resource           - Получить всех пользователей;                                      \r\n
        /api/resource/1         - Получить пользователя с id = 1;                                   \r\n
        /api/resource/ivanov-ii - Получить пользователя с username = ivanov-ii;                     \r\n
    """
    result = None
    if request.method == "GET":
        result = resource_get(request, resource_id=resource_id)
    else:
        return JsonResponse({}, status=400, safe=False)

    if not result:
        return JsonResponse({}, status=400, safe=False)

    response = get_response_template(code='ok', source=request.path, result=result)
    return JsonResponse(response, status=200, safe=False)


@login_required
def user(request, user_id=None, username=None):
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
        result = user_get(request, user_id, username)
    elif request.method == "POST":
        result = user_post(request)
    elif request.method == "PUT":
        result = user_put(request)
    elif request.method == "DELETE":
        result = user_delete(request, user_id, username)
    else:
        return JsonResponse({}, status=400, safe=False)

    if not result:
        return JsonResponse({}, status=400, safe=False)

    response = get_response_template(code='ok', source=request.path, result=result)
    return JsonResponse(response, status=200, safe=False)


@login_required
def set_default_area(request, area_id, username=None):
    """
    Установить площадку по умолчанию для пользователя                                                              \r\n
    api/user/set_default_area/1 - Установить площадку с идентификатором 1 как дефолтную для текущего пользователя; \r\n
    api/user/set_default_area/1/ivanov-ii - Установить площадку id = 1, как деволтную для пользователя ivanov-ii.  \r\n
    """
    if username:
        xuser = ExtUser.objects.get(username=username)
    else:
        xuser = request.user.extuser

    xuser.def_area_id = area_id
    xuser.save()

    response = get_response_template(code='ok', source=request.path, result=None)
    return JsonResponse(response, status=200, safe=False)


