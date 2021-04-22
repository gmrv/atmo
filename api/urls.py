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
    # Получить площадки доступные для компании пользователя
    path('area/get_area_by_username/<str:username>', views.get_area_by_username, name='area'),
    # Получить список всех ресурсов для площадки
    path('area/get_area_resource_list/<int:area_id>/', views.get_area_resource_list, name='get_area_resource_list'),


    # Booking
    path('booking', views.booking, name='booking'),
    path('booking/<int:id>', views.booking, name='booking'),
    path('booking/<str:username>', views.booking, name='booking'),


    # User
    path('user', views.user, name='user'),
    path('user/<str:username>', views.user, name='user'),
    # Установить площадку по умолчанию для пользователя
    path('user/set_default_area/<int:area_id>/', views.set_default_area, name='get_available_areas'),
    path('user/set_default_area/<int:area_id>/<str:username>', views.set_default_area, name='get_available_areas'),


]