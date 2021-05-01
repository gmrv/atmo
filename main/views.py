from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from api.utils import datetimestring_to_ts
from main.models.core import *


@login_required
def index(request):
    return HttpResponseRedirect(reverse('main:home'))


@login_required
def home(request, area_id=None, target_date=None):
    xuser = request.user.extuser

    if area_id:
        xuser.def_area_id = area_id
        xuser.save()
        return HttpResponseRedirect("/main/home/" + target_date)

    if target_date:
        check = datetimestring_to_ts(target_date, "%Y-%m-%d")
    else:
        target_date = datetime.today().strftime('%Y-%m-%d')

    if not xuser.def_area:
        return HttpResponseRedirect(reverse('main:area_select'))

    seats_query = Seat.objects.filter(area=xuser.def_area).order_by("name")
    seats = []
    for s in seats_query:
        seats.append({"id": s.id, "name": s.name})

    rooms_query = Room.objects.filter(area=xuser.def_area).order_by("name")
    rooms = []
    for r in rooms_query:
        rooms.append({"id": r.id, "name": r.name, "seats": r.capacity })

    context = {
        'user': request.user.extuser,
        'area': xuser.def_area,
        'seats': seats,
        'rooms': rooms,
        'target_date': target_date
    }
    return render(request, 'main/home.html', context)

@login_required
def profile(request, target_date=None):
    xuser = request.user.extuser
    booking = xuser.booking_set.all().order_by("id")
    tasks = Task.objects.filter(created_by=xuser.username).order_by("id")
    context = {
        'user': xuser,
        'booking': booking,
        'tasks': tasks,
        'resource_id': '',
        'target_date': target_date
    }
    return render(request, 'main/profile.html', context)


@login_required
def resource(request, resource_id, target_date=None):
    xuser = request.user.extuser
    xusers = ExtUser.objects.all().exclude(username='root').order_by("username")
    resource = Resource.objects.get(pk=resource_id)
    percent_of_booked_time = resource.get_percent_of_booked_time(target_date)

    calendar = []
    for c in resource.get_calendar(target_date):
        calendar.append(c)

    context = {
        'user': xuser,
        'users': xusers,
        'area': xuser.def_area,
        'resource': resource,
        'calendar': calendar,
        'target_date': target_date,
        'percent_of_booked_time': percent_of_booked_time
    }
    return render(request, 'main/resource.html', context)


@login_required
def area_select(request):
    xuser = request.user.extuser
    area_id = request.POST.get('id-select-area', None)
    if area_id:
        xuser.def_area_id = area_id
        xuser.save()
        return HttpResponseRedirect(reverse('main:home'))

    areas = []
    area_query = Area.objects.filter(company=xuser.company).order_by("name")
    for a in area_query:
        areas.append({'id' : a.id, 'name' : a.name})

    context = {
        'user': xuser,
        'areas': areas,
        'target_date': datetime.today().strftime('%Y-%m-%d')
    }
    return render(request, 'main/area_select.html', context)
