from django.urls import path
from .views import *

app_name = 'staff'
urlpatterns = [
    path('', index, name='index'),
    path('home/', home, name='home'),
    path('members/', members, name='members'),
    path('bookings/', bookings, name='bookings'),
    path('add_users/', add_users, name='add_users'),
]
