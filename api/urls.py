from django.urls import path, re_path

from . import views

app='api'
urlpatterns = [
    path('', views.index, name='index'),
    path('home/', views.home, name='home'),


    # Area
    path('area', views.area, name='area'),
    path('area/<int:area_id>', views.area, name='area'),
    path('area/<int:area_id>/<slug:target_date>', views.area, name='area'),
    path('area/<str:username>', views.area, name='area'),


    # Booking
    path('booking', views.booking, name='booking'),
    path('booking/<int:booking_id>', views.booking, name='booking'),
    path('booking/<slug:date>', views.booking, name='booking'),
    path('booking/confirmation/<int:booking_id>/<str:pin>', views.booking_confirmation, name='booking_confirmation'),
    path('booking/can/<int:resource_id>', views.booking_can, name='booking_can'),
    path('booking/can/<int:resource_id>/<str:start_time>/<str:end_time>', views.booking_can, name='booking_can'),
    path('booking/can/<int:resource_id>/<slug:start_date>/<str:start_time>/<slug:end_date>/<str:end_time>', views.booking_can, name='booking_can'),


    # Cоmpany
    path('company', views.company, name='company'),
    path('company/<int:company_id>', views.company, name='company'),
    path('company/<int:company_id>/<slug:target_date>', views.company, name='company'),


    # Resource
    path('resource', views.resource, name='resource'),
    path('resource/<int:resource_id>', views.resource, name='resource'),


    # ServiceRequest
    path('service', views.service, name='service'),
    path('service/<int:service_id>', views.service, name='service'),
    path('service/byuser/<int:user_id>', views.service, name='service'),
    path('service/byresource/<int:resource_id>', views.service, name='service'),


    # User
    path('user', views.user, name='user'),
    path('user/<int:user_id>', views.user, name='user'),
    path('user/<str:username>', views.user, name='user'),
    # Установить площадку по умолчанию для пользователя из request.user
    path('user/set_default_area/<int:area_id>/', views.set_default_area, name='get_available_areas'),
    # Установить площадку по умолчанию для пользователя из url-параметра
    path('user/set_default_area/<int:area_id>/<str:username>', views.set_default_area, name='get_available_areas'),


]