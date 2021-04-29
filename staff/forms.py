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
            u = ExtUser.objects.create(username=username, email=email, company=company,
                    first_name=first_name, middle_name=middle_name, last_name=last_name, is_staff=is_staff)
            u.set_password(password)
            u.save()

        except Exception as e:
            print('***** ***** *****')
            print(e)
            print('***** ***** *****')

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