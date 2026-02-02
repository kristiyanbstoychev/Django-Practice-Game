from django.urls import path
from . import views

urlpatterns = [
    # This says: "If the user types 'characters/', show them the character_list"
    path('characters/', views.character_list, name='character_list'),
    path('quests/<int:char_id>/', views.quest_log, name='quest_log'),
    path('combat/<int:char_id>/', views.basic_combat, name='basic_combat'),
    path('levelup/<int:char_id>/', views.level_up, name='level_up'),
    path('rest/<int:char_id>/', views.rest, name='rest'),
    path('assign-quest/<int:char_id>/<int:quest_id>', views.assign_quest, name='assign_quest'),
    path('complete-quest/<int:quest_id>/', views.complete_quest, name='complete_quest'),
    path('buy-item/<int:char_id>/<int:item_id>', views.buy_item, name='buy_item'),
    path('travel/<int:char_id>/<int:loc_id>/', views.travel, name='travel'),
    path('character/<int:char_id>/', views.character_detail, name='character_detail'),
]