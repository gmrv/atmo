from django.urls import path, re_path

from . import views

app='api'
urlpatterns = [
    path('', views.index, name='index'),
    path('home/', views.home, name='home'),


    # Area
    path('area', views.area, name='area'),
    path('area/<int:id>', views.area, name='area'),
    path('area/<int:id>/<slug:target_date>', views.area, name='area'),
    path('area/<str:username>', views.area, name='area'),


    # Booking
    path('booking', views.booking, name='booking'),
    path('booking/<int:id>', views.booking, name='booking'),
    path('booking/<slug:date>', views.booking, name='booking'),
    path('booking/confirmation/<int:id>/<int:pin>', views.booking_confirmation, name='booking_confirmation'),


    # Resource
    path('resource', views.resource, name='resource'),
    path('resource/<int:resource_id>', views.resource, name='resource'),


    # User
    path('user', views.user, name='user'),
    path('user/<int:id>', views.user, name='user'),
    path('user/<str:username>', views.user, name='user'),
    # Установить площадку по умолчанию для пользователя из request.user
    path('user/set_default_area/<int:area_id>/', views.set_default_area, name='get_available_areas'),
    # Установить площадку по умолчанию для пользователя из url-параметра
    path('user/set_default_area/<int:area_id>/<str:username>', views.set_default_area, name='get_available_areas'),


]