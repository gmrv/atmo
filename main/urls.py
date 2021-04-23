from django.urls import path

from . import views

app='main'
urlpatterns = [
    path('', views.index, name='index'),

    path('home/', views.home, name='home'),

    path('area_select/', views.area_select, name='area_select'),
]
