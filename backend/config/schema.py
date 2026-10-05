import strawberry
from typing import Optional
from hotels.models import Hotel
from rooms.models import RoomType

@strawberry.type
class HotelType:
    id:strawberry.ID; name:str; short_name:str; tagline:str; description:str; logo_url:str; hero_image_url:str; phone:str; email:str; address:str; city:str; country:str; currency:str; timezone:str
@strawberry.type
class PublicRoomType:
    id:strawberry.ID; name:str; slug:str; description:str; capacity:int; base_rate:float; image_url:str

@strawberry.type
class Query:
    @strawberry.field
    def hotel(self)->Optional[HotelType]:
        item=Hotel.objects.filter(is_active=True).first()
        return None if not item else HotelType(id=str(item.id),name=item.name,short_name=item.short_name,tagline=item.tagline,description=item.description,logo_url=item.logo_url,hero_image_url=item.hero_image_url,phone=item.phone,email=item.email,address=item.address,city=item.city,country=item.country,currency=item.currency,timezone=item.timezone)
    @strawberry.field
    def room_types(self)->list[PublicRoomType]:
        return [PublicRoomType(id=str(x.id),name=x.name,slug=x.slug,description=x.description,capacity=x.capacity,base_rate=float(x.base_rate),image_url=x.image_url) for x in RoomType.objects.filter(is_active=True,hotel__is_active=True)]
schema=strawberry.Schema(query=Query)
