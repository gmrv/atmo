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


]