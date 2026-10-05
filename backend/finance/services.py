import secrets
from django.db import transaction
from rest_framework.exceptions import ValidationError
from .models import Folio,FolioCharge,Stay

@transaction.atomic
def create_stay_with_folio(*,actor,hotel,guest,room,arrival_date,departure_date,rate,booking=None,**details):
    if Stay.objects.select_for_update().filter(room=room,status__in=[Stay.Status.RESERVED,Stay.Status.CHECKED_IN],arrival_date__lt=departure_date,departure_date__gt=arrival_date).exists():raise ValidationError('This room is unavailable for those dates.')
    stay=Stay.objects.create(hotel=hotel,guest=guest,room=room,arrival_date=arrival_date,departure_date=departure_date,rate=rate,booking=booking,receptionist=actor,**details)
    room.occupancy_status=room.Occupancy.RESERVED;room.save(update_fields=['occupancy_status','updated_at'])
    folio=Folio.objects.create(hotel=hotel,stay=stay,guest=guest,reference=f'FOL-{secrets.token_hex(4).upper()}');nights=max((departure_date-arrival_date).days,1)
    FolioCharge.objects.create(folio=folio,kind=FolioCharge.Kind.ROOM,description=f'{nights} night accommodation',quantity=nights,unit_price=rate,amount=rate*nights,created_by=actor)
    return stay
