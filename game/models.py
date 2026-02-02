from django.db import models

# ===== CHARACTER MODEL =====
class Character(models.Model):
    # This stores the character's name as text
    name = models.CharField(max_length=100)
    
    # This stores health as a whole number - starts at 100
    health = models.IntegerField(default=100)
    
    # This stores the level - starts at level 1
    level = models.IntegerField(default=1)

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