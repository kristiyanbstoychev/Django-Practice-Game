from django.db import models

# ===== LOCATION MODEL =====
class Location(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.name

class Enemy(models.Model):
    name = models.CharField(max_length=100)
    level = models.IntegerField(default=1, max_length=100)
    mana = models.IntegerField(default=50)
    armor = models.IntegerField(default=50)
    magic_armor = models.IntegerField(default=20)
    health = models.IntegerField(default=50)
    attack_power = models.IntegerField(default=10)
    xp_reward = models.IntegerField(default=20)
    is_defeated = models.BooleanField(default=False)

# This allows the quest_detail page to find its enemies
    quest = models.ForeignKey(
        'Quest', 
        on_delete=models.CASCADE, 
        related_name='enemies', 
        null=True, 
        blank=True
    )

    def __str__(self):
        return self.name

# ===== CHARACTER MODEL =====
class Character(models.Model):
    # This stores the character's name as text
    name = models.CharField(max_length=100)
    
    # This stores health as a whole number - starts at 100
    health = models.IntegerField(default=100)

    max_health = models.IntegerField(default=100)
    
    mana = models.IntegerField(default=50)

    armor = models.IntegerField(default=50)

    gold_amount = models.IntegerField(default=0)

    strength = models.IntegerField(default=50)

    xp = models.IntegerField(default=0)

    # This stores the level - starts at level 1
    level = models.IntegerField(default=1)
    
    current_enemy = models.ForeignKey(
        Enemy, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )

    current_location = models.ForeignKey(
        Location, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )

    # This makes the character show their name in the admin panel
    def __str__(self):
        return self.name
    
# ===== ITEM MODEL =====
# This represents equipment or loot
class Item(models.Model):
    name = models.CharField(max_length=100)
    power = models.IntegerField(default=5)
    
    # This is the "Tether" (ForeignKey)
    # It links the item to a specific Character
    # 'on_delete=models.CASCADE' means if the hero is deleted, the item is too
    owner = models.ForeignKey(Character, on_delete=models.CASCADE, related_name="items")

    def __str__(self):
        return f"{self.name} (Owned by {self.owner.name})"
    
# ===== QUEST MODEL =====
class Quest(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    xp_reward = models.IntegerField(default=20)
    is_completed = models.BooleanField(default=False)
    
    # Updated to allow null (database level) and blank (form level)
    assigned_to = models.ForeignKey(
        Character, 
        on_delete=models.CASCADE, 
        related_name="quests",
        null=True,   # Allows the database to store a NULL value
        blank=True   # Allows the Django admin/forms to leave this empty
    )

    def __str__(self):
        status = "Done" if self.is_completed else "Active"
        # Handle the case where the quest isn't assigned yet
        owner = self.assigned_to.name if self.assigned_to else "Unassigned"
        return f"{self.title} ({owner}) - {status}"
    