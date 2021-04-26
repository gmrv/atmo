from django.urls import path

from . import views

app='main'
urlpatterns = [
    path('', views.index, name='index'),

    path('area_select/', views.area_select, name='area_select'),

    path('home/', views.home, name='home'),
    path('home/<int:area_id>', views.home, name='home'),
    path('home/<int:area_id>/<slug:target_date>', views.home, name='home'),
    path('home/<slug:target_date>', views.home, name='home'),


    path('booking/<int:resource_id>', views.booking, name='booking'),
    path('booking/<int:resource_id>/<slug:target_date>', views.booking, name='booking'),

    path('profile/', views.profile, name='profile'),
    path('profile/<slug:target_date>', views.profile, name='profile'),
]
