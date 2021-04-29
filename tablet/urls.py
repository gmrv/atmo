from django.urls import path

from . import views

app='tablet'
urlpatterns = [
    path('', views.index, name='index'),

    path('home/', views.home, name='home'),
    path('qr/', views.qr, name='home'),
    path('room/<int:room_id>', views.room, name='room'),
    path('room/<int:room_id>/<slug:target_date>', views.room, name='room'),
]
