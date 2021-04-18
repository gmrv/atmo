from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import HttpResponse
from main.models import *


@login_required
def index(request):

    property = Resource.objects.filter(type__name="Место", property__name="Постоянное", property__value_bool=True, ).first()

    return HttpResponse(property)

@login_required
def home(request):
    context = {
        'room': 1,
        'map': "",
        'date': None,
        'all_day': True,
    }
    return render(request, 'main/home.html', context)
