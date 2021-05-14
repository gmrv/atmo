from django.shortcuts import render

from datetime import datetime, timedelta
from dateutil.tz import tzlocal
from django.conf import settings
from django.utils.timezone import localtime, now
from django.db.models import Q, F

from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.template import RequestContext
from api.utils import datetimestring_to_ts
from main.models.core import *

from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages

from .forms import *


tz = tzlocal()

@staff_member_required
def index(request): 
    return HttpResponseRedirect(reverse('staff:home'))


@staff_member_required
def home(request):
    tasks = Task.objects.all().order_by("created_at")

    #бронирования, выпадающие на текущую дату
    currentDate = datetime.now(tz=tz).date()
    tommorowDate = currentDate + timedelta(days=1)

    bookings_1 = Booking.objects.filter((Q(start_ts__gte=currentDate) & Q(start_ts__lte=tommorowDate)), Q(end_ts__gte=tommorowDate))
    bookings_2 = Booking.objects.filter(Q(start_ts__lte=currentDate), Q(end_ts__gte=tommorowDate))
    bookings_3 = Booking.objects.filter(Q(start_ts__lte=currentDate), (Q(end_ts__lte=tommorowDate) & Q(end_ts__gte=currentDate)))
    bookings_4 = Booking.objects.filter(Q(start_ts__gte=currentDate), Q(end_ts__lte=tommorowDate))
    bookings = bookings_1 | bookings_2 | bookings_3 | bookings_4
    bookings = bookings.order_by('start_ts')

    context = {
        'tasks': tasks,
        'bookings': bookings,
        'today': currentDate,
    }
    return render(request, 'staff/home.html', context)


@staff_member_required
def members(request):
    today = localtime(now())
    days_back = 30
    if 'days_back' in request.GET:
        days_back = int(request.GET.get('days_back'))
    new_users = ExtUser.objects.filter(date_joined__range=(today - timedelta(days=days_back), today)).order_by('-date_joined')

    context = {
        'new_users': new_users,
        'days_back': days_back,
    }
    return render(request, 'staff/members.html', context)

@staff_member_required
def bookings(request):
    if request.method == 'POST':
        form = BookingReportForm(request.POST, request.FILES)
    else:
        form = getDefaultBookingsForm()

    report = BookingsReport(form)
    bookings = report.get_bookings()

    context = {
        'form': form,
        'bookings': bookings,
        # 'today': currentDate,
    }
    return render(request, 'staff/bookings.html', context)


@staff_member_required
def add_users(request):
    if request.method == "POST":
        form = AddUserForm(request.POST)
        try:
            if form.is_valid():
                user = form.save()
                messages.success(request, "Пользователь: '%s' создан." % user.username)
                return HttpResponseRedirect(reverse('staff:add_users'))
        except Exception as e:
            messages.error(request, str(e))
    else:
        form = AddUserForm()

    today = localtime(now())
    days_back = 7
    if 'days_back' in request.GET:
        days_back = int(request.GET.get('days_back'))
    new_users = ExtUser.objects.filter(date_joined__range=(today - timedelta(days=days_back), today)).order_by('-date_joined')

    context = {
        'add_user_form': form,
        'new_users': new_users,
        'days_back': days_back,
        'companies': companies,
    }
    return render(request, 'staff/add_users.html', context)
