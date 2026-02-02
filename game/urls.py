from django.urls import path
from . import views

urlpatterns = [
    # This says: "If the user types 'characters/', show them the character_list"
    path('characters/', views.character_list, name='character_list'),
]