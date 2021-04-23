from django.urls import path, re_path

from . import views

app='main'
urlpatterns = [
    path('', views.index, name='index'),
    path('home/', views.home, name='home'),


    # Area
    path('area', views.area, name='area'),
    path('area/<int:id>', views.area, name='area'),
    path('area/<str:username>', views.area, name='area'),
    # Получить список всех ресурсов для площадки сгруппированные по типу (seat, room)
    path('area/resources/<int:area_id>', views.get_area_resource_list, name='get_area_resource_list'),


    # Booking
    path('booking', views.booking, name='booking'),
    path('booking/<int:id>', views.booking, name='booking'),
    path('booking/<slug:date>', views.booking, name='booking'),
    path('booking/confirmation/<int:id>/<int:pin>', views.booking_confirmation, name='booking_confirmation'),


    # User
    path('user', views.user, name='user'),
    path('user/<int:id>', views.user, name='user'),
    path('user/<str:username>', views.user, name='user'),
    # Установить площадку по умолчанию для пользователя
    path('user/set_default_area/<int:area_id>/', views.set_default_area, name='get_available_areas'),
    path('user/set_default_area/<int:area_id>/<str:username>', views.set_default_area, name='get_available_areas'),


]