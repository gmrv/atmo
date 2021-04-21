import json
from api.utils import *
from main.models.core import *
from django.db.models import Q
from django.utils import timezone
from django.core import serializers
from django.urls import reverse
from django.utils.timezone import localtime, now
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse


def area_get(request, id, username):
    """
    Получаем инфо площадки по ее id
    Получаем инфо о всех площадках если id не задан
    Получаем инфо о всех площадках доступных пользователю через компанию
    """
    if id:
        # Если есть идентификатор возвращаем одну
        a = Area.objects.get(pk=id)
        result = {"id": a.id, "name": a.name}

    else:
        # Если нет идентификатора возвращаем все
        area_query = Area.objects.all()
        if username:
            # Возвращаем только площадки компании пользователя
            xuser = ExtUser.objects.get(username=username)
            area_query = area_query.exclude(~Q(company=xuser.company))
        area_list = []
        for a in area_query:
            area_list.append({"id": a.id, "name": a.name})
        result = area_list
    return result


def booking_get(request, id):
    """
    Получаем одну или все записи о бронировании
    Бронирование по пользователю доступно через эндпоинт User
    """
    if id:
        b = Booking.objects.get(pk=id)
        data = serializers.serialize('json', [b, ])
        result = json.loads(data)[0]
    else:
        booking_query = Booking.objects.all()
        data = serializers.serialize('json', booking_query)
        result = json.loads(data)
    return result


def booking_post(request):
    resource_id = request.POST.get("resource_id", None)
    date_start = request.POST.get("date_start", str(timezone.now().date()))
    time_start = request.POST.get("time_start", settings.OPEN_TIME)
    date_end = request.POST.get("date_end", str(timezone.now().date()))
    time_end = request.POST.get("time_end", settings.CLOSE_TIME)

    start = date_start + " " + time_start
    end = date_end + " " + time_end
    start_ts = datetimestring_to_ts(start, "%Y-%m-%d %H:%M")
    end_ts = datetimestring_to_ts(end, "%Y-%m-%d %H:%M")

    if not resource_id:
        return None

    b = Booking.objects.create(
        resource_id=resource_id,
        user=request.user,
        start_ts=start_ts,
        end_ts=end_ts,
        confirmed=True
    )

    data = serializers.serialize('json', [b, ])
    result = json.loads(data)[0]
    return result


def booking_delete(request, id):
    """
    Удаление брони по id
    """
    b = Booking.objects.get(pk=id)
    b.delete()
    return {"id": id}