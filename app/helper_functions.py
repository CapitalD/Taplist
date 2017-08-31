from flask_login import current_user
from .models import Location, Brewery


def get_manageable_locations(type):
    manageable_locations = []
    if type == "brewery":
        if current_user.is_admin:
            manageable_locations = Brewery.query.all()
        elif current_user.is_brewer:
            manageable_locations = Brewery.query.filter(Brewery.brewers.any(id=current_user.id)).all()
    elif type == "location":
        if current_user.is_admin:
            manageable_locations = Location.query.all()
        elif current_user.is_manager:
            manageable_locations = Location.query.filter(Location.managers.any(id=current_user.id)).all()
    return manageable_locations

def get_place(type, id, manageable_locations):
    if type == "brewery":
        if id:
            brewery = Brewery.query.get_or_404(id)
        elif current_user.default_brewery:
            brewery = Brewery.query.get_or_404(current_user.default_brewery)
        else:
            brewery = manageable_locations[0]
        return brewery
    if type == "location":
        if id:
            location = Location.query.get_or_404(id)
        elif current_user.default_location:
            location = Location.query.get_or_404(current_user.default_location)
        else:
            location = manageable_locations[0]
        return location
