from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse

from main.models import *


@login_required
def check_def_area(request):
    user = request.user.extuser

    if user.def_area:
        return HttpResponseRedirect(reverse('main:home'))
    else:
        return HttpResponseRedirect(reverse('main:area_select'))

