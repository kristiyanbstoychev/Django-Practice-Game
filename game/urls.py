from django.urls import path
from . import views

urlpatterns = [
    path('', views.main_menu, name='main_menu'),
    path('characters_listing/', views.characters_listing, name='characters_listing'),
    path('create/', views.create_character, name='create_character'),
    path('quests/<int:char_id>/', views.quest_log, name='quest_log'),
    path('refresh_quests/<int:char_id>/', views.refresh_quests, name='refresh_quests'),
    path('combat/<int:char_id>/', views.basic_combat, name='basic_combat'),
    path('levelup/<int:char_id>/', views.level_up, name='level_up'),
    path('rest/<int:char_id>/', views.rest, name='rest'),
    path('recover/<int:char_id>/<int:quest_id>', views.recover_health, name='recover_health'),
    path('assign-quest/<int:char_id>/<int:quest_id>', views.assign_quest, name='assign_quest'),
    path('complete-quest/<int:char_id>/<int:quest_id>/', views.complete_quest, name='complete_quest'),
    path('buy-item/<int:char_id>/<int:item_id>', views.buy_item, name='buy_item'),
    path('travel/<int:char_id>/<int:loc_id>/', views.travel, name='travel'),
    path('character/<int:char_id>/', views.character_detail, name='character_detail'),
    path('rename_hero/<int:char_id>/<str:new_name>', views.rename_hero, name='rename_hero'),
    path('battle/start/<int:char_id>/<int:enemy_id>/', views.start_battle, name='start_battle'),
    path('select_enemy/<int:char_id>/', views.select_enemy, name='select_enemy'),
    path('attack_enemy/<int:char_id>/', views.attack_enemy, name='attack_enemy'),
    path('generate-enemy/<int:char_id>/', views.generate_new_enemy, name='generate_new_enemy'),
    path('battle/<int:char_id>/<int:enemy_id>/', views.battle_arena, name='battle_arena'),
    path('quest-detail/<int:char_id>/<int:quest_id>/', views.quest_detail, name='quest_detail'),
    path('shop/<int:char_id>/', views.shop_page, name='shop_page'),
    path('equip-item/<int:char_id>/<int:item_id>/', views.equip_item, name='equip_item'),
    path('unequip-item/<int:char_id>/<int:item_id>/', views.unequip_item, name='unequip_item'),
]