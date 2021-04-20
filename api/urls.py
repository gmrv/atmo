from django.urls import path

from . import views

app='main'
urlpatterns = [
    path('', views.index, name='index'),
    path('home/', views.home, name='home'),
    path('get_info/', views.get_info, name='get_info'),

    # Получить список доступных площадок для пользователя
    path('get_available_areas/', views.get_available_areas, name='get_available_areas'),
    path('get_available_areas/<str:username>', views.get_available_areas, name='get_available_areas'),

    # Установить площадку по умолчанию для пользователя
    path('set_default_area/<int:area_id>/', views.set_default_area, name='get_available_areas'),
    path('set_default_area/<int:area_id>/<str:username>', views.set_default_area, name='get_available_areas'),

    #
    path('get_area_resource_list/<int:area_id>/', views.get_area_resource_list, name='get_area_resource_list'),

    #
    path('create_resource_booking/<int:resource_id>/', views.create_resource_booking, name='create_resource_booking'),
    path('create_resource_booking/<int:resource_id>/<date_start>/<time_start>/<date_end>/<time_end>', views.create_resource_booking, name='create_resource_booking'),





]