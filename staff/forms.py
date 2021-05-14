import os
from datetime import datetime, timedelta, date

from django import forms
from django.core.files.base import ContentFile
from django.forms import modelformset_factory
from django.forms.formsets import BaseFormSet
from django.contrib.auth.models import User
from django.conf import settings
from django.core.files.base import ContentFile
from django.utils.timezone import localtime, now
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext as _

from main.models.core import *

### ADD USER

COMPANY_KEYS = [
    (None, '-')
]

companies = list(Company.objects.all().values('id', 'name'))
for c in companies:
    COMPANY_KEYS.append((c['id'], c['name']))

class AddUserForm(forms.Form):
    last_name = forms.CharField(max_length=100, label=_("Фамилия *"), required=True, widget=forms.TextInput(attrs={'autocapitalize': "words"}))
    first_name = forms.CharField(max_length=100, label=_("Имя *"), required=True, widget=forms.TextInput(attrs={'autocapitalize': "words"}))
    middle_name = forms.CharField(max_length=100, label=_("Отчество"), required=False, widget=forms.TextInput(attrs={'autocapitalize': "words"}))
    
    email = forms.EmailField(max_length=100, label=_("Email *"), required=True)
    
    username = forms.CharField(max_length=100, label=_("Логин *"), required=True)
    password = forms.CharField(max_length=100, label=_("Пароль *"), required=True)

    company_id = forms.ChoiceField(label=_("Компания"), choices=COMPANY_KEYS, required=False)

    staff = forms.BooleanField(label=_("Персонал коворкинга"), required=False, initial=False)

    def clean_first_name(self):
        return self.cleaned_data['first_name'].strip().title()
    
    def clean_middle_name(self):
        return self.cleaned_data['middle_name'].strip().title()

    def clean_last_name(self):
        return self.cleaned_data['last_name'].strip().title()

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        if ExtUser.objects.filter(email=email).count() > 0:
            raise forms.ValidationError(_("Почтовый ящик '%s' уже используется.") % email)
        return email

    def create_user(self, username, password, first_name=None, middle_name=None, last_name=None, company=None, is_staff=False, email=None):
        try:
            user = ExtUser.objects.create(username=username, email=email, company=company,
                    first_name=first_name, middle_name=middle_name, last_name=last_name, is_staff=is_staff)
            user.set_password(password)
            user.save()

        except Exception as e:
            print(e)

        return user

    def save(self):
        "Creates the User and Profile records with the field data and returns the user"
        if not self.is_valid():
            raise Exception(_('Форма не прошла проверку'))

        first = self.cleaned_data['first_name']
        middle = self.cleaned_data['middle_name']
        last = self.cleaned_data['last_name']
        email = self.cleaned_data['email']
        username = self.cleaned_data['username']
        password = self.cleaned_data['password']
        company = None if ((self.cleaned_data['company_id'] == '') or (self.cleaned_data['company_id'] == None)) else Company.objects.get(pk=self.cleaned_data['company_id'])
        staff = self.cleaned_data['staff']

        user = self.create_user(username, password, first, middle, last, company=company, is_staff=staff, email=email)

        return user

    class Meta:
        widgets = {
            'last_name': forms.TextInput(attrs={'autocapitalize': 'on', 'autocorrect': 'off'}),
            'first_name': forms.TextInput(attrs={'autocapitalize': 'on', 'autocorrect': 'off'}),
            'middle_name': forms.TextInput(attrs={'autocapitalize': 'on', 'autocorrect': 'off'}),
        }

### BOOKING REPORT

REPORT_FIELDS = (
    ('AREA', 'Площадка'),
    ('SEAT', 'Место'),
    ('NAME', 'Имя пользователя'),
    ('LOGIN', 'Логин'),
    ('BOOKING_START', 'Время начала'),
    ('BOOKING_END', 'Время окончания'),
    ('IS_CONFIRMED', 'Присутствие'),
    ('CREATED', 'Время создания'),
)

def getDefaultBookingsForm():
    start = localtime(now()).date() - timedelta(days=1)
    end = localtime(now()).date() + timedelta(days=1)
    form_data = {'order_by': 'BOOKING_START', 'desc': False, 'start_date': start, 'end_date': end}
    return BookingReportForm(form_data)

class BookingReportForm(forms.Form):
    start_date = forms.DateField(label=_("Начальная дата"), required=True, widget=forms.TextInput(attrs={'class': 'datepicker',}))
    end_date = forms.DateField(label=_("Конечная дата"), required=True, widget=forms.TextInput(attrs={'class': 'datepicker',}))
    order_by = forms.ChoiceField(label=_("Сортировка"), choices=REPORT_FIELDS, required=True)
    desc = forms.BooleanField(label=_("По убыванию"), required=False)

class BookingsReport(models.Model):
    def __init__(self, form):
        self.order_by = form.data['order_by']
        self.desc = 'desc' in form.data
        self.start_date = form.data['start_date']
        self.end_date = form.data['end_date']
        if not self.end_date:
            self.end_date = localtime(now()).date()

    def get_bookings(self):
        bookings = None
        
        if isinstance(self.start_date, date):
            start = self.start_date
        else:
            start = datetime.strptime(self.start_date, '%Y-%m-%d')

        if isinstance(self.end_date, date):
            end = self.end_date + timedelta(days=1)
        else:
            end = datetime.strptime(self.end_date, '%Y-%m-%d') + timedelta(days=1)

        bookings = Booking.objects.filter(start_ts__range=(start, end))

        if not bookings:
            return Booking.objects.none()

        if self.desc:
            prefix = '-'
        else:
            prefix = ''

        if self.order_by == "NAME":
            bookings = bookings.order_by(prefix + "user__first_name").order_by(prefix + "user__last_name")
        elif self.order_by == "LOGIN":
            bookings = bookings.order_by(prefix + "user")
        elif self.order_by == "AREA":
            bookings = bookings.order_by(prefix + "resource__area__name")
        elif (self.order_by == "SEAT"):
            bookings = bookings.order_by(prefix + "resource__name")
        elif self.order_by == "BOOKING_START":
            bookings = bookings.order_by(prefix + "start_ts")
        elif self.order_by == "BOOKING_END":
            bookings = bookings.order_by(prefix + "end_ts")
        elif self.order_by == "IS_CONFIRMED":
            bookings = bookings.order_by(prefix + "is_confirmed")
        elif self.order_by == "CREATED":
            bookings = bookings.order_by(prefix + "created_at")

        return bookings
