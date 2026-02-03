from django.contrib import admin
from django.urls import path, include
from game import views as game_views

urlpatterns = [
    path('admin/', admin.site.urls),
    # This makes http://127.0.0.1:8000/ show the main menu
    path('', game_views.main_menu, name='root_menu'),
    path('game/', include('game.urls')),
]