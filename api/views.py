from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from api.utils import get_response_template
from main.models.core import *


@login_required
def index(request):
    return HttpResponseRedirect(reverse('api:home'))

@login_required
def home(request):
    return HttpResponse('home')

@login_required
def get_info(request):
    return HttpResponse('info')

# Получить список доступных площадок для пользователя
@login_required
def get_available_areas(request, username=None):
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

# Установить площадку по умолчанию для пользователя
@login_required
def set_default_area(request, area_id, username=None):
    if username:
        xuser = ExtUser.objects.get(username=username)
    else:
        xuser = request.user.extuser

    xuser.def_area_id = area_id
    xuser.save()

    response = get_response_template(code='ok', source=request.path, result=None)
    return JsonResponse( response, safe=False)