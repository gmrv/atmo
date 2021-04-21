from django.urls import path, re_path

from . import views

app='main'
urlpatterns = [
    path('', views.index, name='index'),
    path('home/', views.home, name='home'),

    # Установить площадку по умолчанию для пользователя
    path('set_default_area/<int:area_id>/', views.set_default_area, name='get_available_areas'),
    path('set_default_area/<int:area_id>/<str:username>', views.set_default_area, name='get_available_areas'),

    #
    path('get_area_resource_list/<int:area_id>/', views.get_area_resource_list, name='get_area_resource_list'),

    # Area
    path('area', views.area, name='area'),
    path('area/<int:id>', views.area, name='area'),
    path('area/<str:username>', views.area, name='area'),

    # Booking
    path('booking', views.booking, name='booking'),
    path('booking/<int:id>', views.booking, name='booking'),
    path('booking/<str:username>', views.booking, name='booking'),

    # User



]