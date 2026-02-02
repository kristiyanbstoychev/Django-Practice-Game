from django.http import HttpResponse
# This imports the Character model so the view can look at the data
from .models import Character

# ===== CHARACTER LIST VIEW =====
# This function handles the request to see all heroes
def character_list(request):
    # This asks the database: "Give me every character you have!"
    all_characters = Character.objects.all()
    
    # We will start by creating a simple text string of names
    # Like making a list of names on a piece of paper
    names = ", ".join([c.name for c in all_characters])
    
    # This sends the list back to the user's browser
    return HttpResponse(f"Heroes in this world: {names}")