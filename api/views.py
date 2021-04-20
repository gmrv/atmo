from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from api.utils import get_response_template, datetimestring_to_ts
from main.models.core import *
from django.utils import timezone
from django.utils.timezone import localtime, now

@login_required
def index(request):
    return HttpResponseRedirect(reverse('api:home'))


@login_required
def home(request):
    return HttpResponse('<a href="/admin/doc/views/#ns|api">Документация модуля</a>')


@login_required
def get_info(request):
    """
    Тестирование документации

    **Контекст**

    ``моямодель``
        Интерфейс для :model:`myapp.MyModel`.

    **Темплейт:**

    :template:`myapp/my_template.html`
    """
    return HttpResponse('info')


@login_required
def get_available_areas(request, username=None):
    """
    Получить список доступных площадок для пользователя
    """
    if username:
        xuser = ExtUser.objects.get(username=username)
    else:
        xuser = request.user.extuser

    areas = []
    area_query = Area.objects.filter(company=xuser.company)
    for a in area_query:
        areas.append({'id' : a.id, 'name' : a.name})

    response = get_response_template(code='ok', source=request.path, result=areas)
    return JsonResponse( response, safe=False)


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
    return JsonResponse( response, safe=False)


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


    response = get_response_template(code='ok', source=request.path, result={})
    response['result'] = {"seats": seats_list, "rooms": rooms_list}


    return JsonResponse( response, safe=False)


@login_required
def create_resource_booking(request,
                            resource_id,
                            date_start=str(timezone.now().date()),
                            time_start=settings.OPEN_TIME,
                            date_end=str(timezone.now().date()),
                            time_end=settings.CLOSE_TIME):
    """
    Создание записи о бронировании
    /api/create_resource_booking/2/2021-04-20/15:00/2021-04-20/17:00/
    """
    print(resource_id, date_start, time_start, date_end, time_end)

    start = date_start + " " + time_start
    end = date_end + " " + time_end
    start_ts = datetimestring_to_ts(start, "%Y-%m-%d %H:%M")
    end_ts = datetimestring_to_ts(end, "%Y-%m-%d %H:%M")
    #end_ts = end_ts + timedelta(minutes=29)
    begin = datetimestring_to_ts(str(timezone.now().date()) + " 00:00" , "%Y-%m-%d %H:%M")

    Booking.objects.create(resource_id=resource_id, user=request.user, start_ts=start_ts, end_ts=end_ts, confirmed=True)

    response = get_response_template(code='ok', source=request.path, result={})
    return JsonResponse( response, safe=False)