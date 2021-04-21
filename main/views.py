from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from main.models.core import *


@login_required
def index(request):
    return HttpResponseRedirect(reverse('main:home'))


@login_required
def home(request):
    xuser = request.user.extuser

    if not xuser.def_area:
        return HttpResponseRedirect(reverse('main:area_select'))

    seats_query = Seat.objects.filter(area=xuser.def_area)
    seats = []
    for s in seats_query:
        seats.append({"id": s.id, "name": s.name})

    rooms_query = Room.objects.filter(area=xuser.def_area)
    rooms = []
    for r in rooms_query:
        rooms.append({"id": r.id, "name": r.name, "seats": r.capacity })

    context = {
        'area': xuser.def_area.name,
        'seats': seats,
        'rooms': rooms,
        'all_day': True,
    }
    return render(request, 'main/home.html', context)


@login_required
def area_select(request):
    xuser = request.user.extuser
    area_id = request.POST.get('id-select-area', None)
    if area_id:
        xuser.def_area_id = area_id
        xuser.save()
        return HttpResponseRedirect(reverse('main:home'))

    areas = []
    area_query = Area.objects.filter(company=xuser.company)
    for a in area_query:
        areas.append({'id' : a.id, 'name' : a.name})

    context = {
        'username': request.user.username,
        'areas': areas,
    }
    return render(request, 'main/area_select.html', context)
