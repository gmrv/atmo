from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse


@login_required
def root(request):
    user = request.user.extuser

    if user.def_area:
        return HttpResponseRedirect(reverse('main:home'))
    else:
        return HttpResponseRedirect(reverse('main:area_select'))

