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
        resource_set = a.resource_set.all()
        res_arr = []
        for r in resource_set:
            res_arr.append({"id": r.id, "type": r.type,"name": r.name})

        result = a.to_json()

    else:
        # Если нет идентификатора возвращаем все
        area_query = Area.objects.all()
        if username:
            # Возвращаем только площадки компании пользователя
            xuser = ExtUser.objects.get(username=username)
            area_query = area_query.exclude(~Q(company=xuser.company))
        area_list = []
        for a in area_query:
            area_list.append(a.to_json(is_short=True))
        result = area_list
    return result


def booking_get(request, id, date):
    """
    Получаем одну или все записи о бронировании
    Бронирование по пользователю доступно через эндпоинт User
    """
    if id:
        b = Booking.objects.get(pk=id)
        result = b.to_json()
    else:
        if date:
            ts_start = datetimestring_to_ts(date + " 00:00", "%Y-%m-%d %H:%M")
            ts_end = ts_start + timedelta(days=1)
            booking_query = Booking.objects.filter(Q(start_ts__gte=ts_start) & Q(start_ts__lte=ts_end))
        else:
            booking_query = Booking.objects.all()
        result = []
        for b in booking_query:
            result.append(b.to_json())
    return result


def booking_post(request):
    """
    Создание записи о бронировании
    """
    user_id = request.POST.get("user_id", None)
    resource_id = request.POST.get("resource_id", None)
    date_start = request.POST.get("date_start", str(timezone.now().date()))
    time_start = request.POST.get("time_start", settings.OPEN_TIME)
    date_end = request.POST.get("date_end", str(timezone.now().date()))
    time_end = request.POST.get("time_end", settings.CLOSE_TIME)

    start = date_start + " " + time_start
    end = date_end + " " + time_end
    start_ts = datetimestring_to_ts(start, "%Y-%m-%d %H:%M")
    end_ts = datetimestring_to_ts(end, "%Y-%m-%d %H:%M")

    if (not user_id) or (not resource_id):
        return None

    b = Booking.objects.create(
        resource_id=resource_id,
        user_id=user_id,
        start_ts=start_ts,
        end_ts=end_ts,
        confirmed=True
    )

    return b.to_json()


def booking_put(request):
    pass


def booking_delete(request, id):
    """
    Удаление брони по id
    """
    b = Booking.objects.get(pk=id)
    b.delete()
    return {"id": id}


def resource_get(request, resource_id=None, area_id=None):
    """
    Получаем один или все ресурсы
    Если задан area_id получаем все ресурсы закрепленные за этой площадкой
    """
    if resource_id:
        if Resource.objects.filter(pk=resource_id).count() < 1:
            return None
        r = Resource.objects.get(pk=resource_id)
        return r.to_json()
    else:
        if area_id:
            resource_query = Area.objects.get(pk=area_id).resource_set.all().order_by("name")
        else:
            resource_query = Resource.objects.all().order_by("name")
        seats_list = []
        rooms_list = []
        for r in resource_query:
            if r.type == Resource.RESOURCE_TYPE_SEAT:
                seats_list.append(r.to_json(is_short=True))
            elif r.type == Resource.RESOURCE_TYPE_ROOM:
                rooms_list.append(r.to_json(is_short=True))
            else:
                pass
        result = {"seats": seats_list, "rooms": rooms_list}
        return result


def user_get(request, id, username):
    """
    Получаем одного или всех пользователей
    """
    if id or username:
        if id:
            if ExtUser.objects.filter(pk=id).count() < 1:
                return None
            xuser = ExtUser.objects.get(pk=id)
        else:
            if ExtUser.objects.filter(username=username).count() < 1:
                return None
            xuser = ExtUser.objects.get(username=username)
        return xuser.to_json(is_short=False)
    else:
        xusers = ExtUser.objects.filter(is_active=True)
        result = []
        for u in xusers:
            result.append(u.to_json(is_short=True))
        return result


def user_post(request):
    """
    Создание пользователя
    см. описание api.views.user
    """
    id = request.POST.get("id", None)
    username = request.POST.get("username", None)
    password = request.POST.get("password", None)
    first_name= request.POST.get("first_name", None)
    middle_name= request.POST.get("middle_name", None)
    last_name= request.POST.get("last_name", None)
    email= request.POST.get("email", None)
    is_superuser= request.POST.get("is_superuser", False)
    is_staff= request.POST.get("is_staff", False)
    is_active= request.POST.get("is_active", True)
    company_id= request.POST.get("company_id", None)

    # Создать
    if (not username) or (not password) or (not first_name): return None
    xuser = ExtUser.objects.create(
        username=username,
        first_name=first_name,
        middle_name=middle_name,
        last_name=last_name,
        email=email,
        is_superuser=is_superuser,
        is_staff=is_staff,
        is_active=is_active,
        company_id=company_id,
    )
    if password:
        xuser.set_password(password)

    xuser.save()
    return xuser.to_json()


def user_put(request):
    """
    Обновление пользователя
    см. описание api.views.user
    """
    put = PUT(request)
    id = put.get("id", None)
    username = put.get("username", None)
    password = put.get("password", None)
    first_name= put.get("first_name", None)
    middle_name= put.get("middle_name", None)
    last_name= put.get("last_name", None)
    email= put.get("email", None)
    company_id= put.get("company_id", None)

    if id or username:
        # Обновить
        if id:
            xuser = ExtUser.objects.get(pk=id)
        else:
            xuser = ExtUser.objects.get(username=username)
        if username: xuser.username = username
        if first_name: xuser.first_name = first_name
        if middle_name: xuser.middle_name = middle_name
        if last_name: xuser.last_name = last_name
        if email: xuser.email = email
        if company_id: xuser.company_id = company_id
    else:
        return None
    if password:
        xuser.set_password(password)
    xuser.save()
    return xuser.to_json()


def user_delete(request, username):
    """
    Не удаляем, помечаем как не активного
    см. описание api.views.user
    """
    if ExtUser.objects.filter(username=username).count() < 1:
        return None
    xuser = ExtUser.objects.get(username=username)
    xuser.is_active = False
    xuser.save()
    return xuser.to_json()