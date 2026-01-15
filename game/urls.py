from django.urls import path
from . import views

urlpatterns = [
    path('', views.game_table, name='game_table'),
    path('new/', views.new_game, name='new_game'),
    path('hit/', views.hit, name='hit'),
    path('stand/', views.stand, name='stand'),
    path('history/', views.game_history, name='game_history'),
]
