from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from main.models import *


@login_required
def index(request):
    return HttpResponseRedirect(reverse('main:home'))

@login_required
def home(request):
    user = request.user.extuser
    seats_query = Resource.objects.filter(type=ResourceType.objects.get(name='Место'), area=user.def_area)
    seats = []
    for s in seats_query:
        seats.append({"id": s.id, "name": s.name})

    rooms_query = Resource.objects.filter(type=ResourceType.objects.get(name='Переговорная'), area=user.def_area)
    rooms = []
    for r in rooms_query:
        # todo: save query r.property_set.get(name='Мест').value_real
        rooms.append({"id": r.id, "name": r.name, "seats": r.property_set.get(name='Мест').value_real })

    context = {
        'area': user.def_area.name,
        'seats': seats,
        'rooms': rooms,
        'all_day': True,
    }
    return render(request, 'main/home.html', context)

@login_required
def area_select(request):
    user = request.user.extuser
    area_id = request.POST.get('id-select-area', None)
    if area_id:
        user.def_area_id = area_id
        user.save()
        return HttpResponseRedirect(reverse('main:home'))

    areas = []
    area_query = Area.objects.filter(company=user.company)
    for a in area_query:
        areas.append({'id' : a.id, 'name' : a.name})

    context = {
        'areas': areas,
    }
    return render(request, 'main/area_select.html', context)
