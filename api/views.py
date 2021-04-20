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
    """
    area = Area.objects.get(pk=area_id)
    resource_list = []
    resource_list_all = []
    for r in area.resource_set.all():
        resource_list_all.append({"id" : r.id, "name": r.name})
        if r.type == resource_type:
            resource_list.append({"id" : r.id, "name": r.name})

    response = get_response_template(code='ok', source=request.path, result={})
    if resource_type==Resource.RESOURCE_TYPE_ALL:
        response['result'] = resource_list_all
    else:
        response['result']  = resource_list

    return JsonResponse( response, safe=False)