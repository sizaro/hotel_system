import os
from django.core.management.base import BaseCommand
from hotels.models import Hotel, HotelService
from rooms.models import Amenity, Room, RoomType
from users.models import User
from events.models import EventType,Venue
from inventory.models import Outlet,Product,ProductCategory,StockLocation

class Command(BaseCommand):
    help="Idempotently creates generic hotel development/reference data."
    def handle(self,*args,**options):
        hotel,_=Hotel.objects.get_or_create(is_active=True,defaults={"name":os.getenv("HOTEL_NAME","The Grand Stay Hotel"),"short_name":os.getenv("HOTEL_SHORT_NAME","Grand Stay"),"tagline":"Stay well. Meet beautifully. Return often.","description":"A welcoming destination for restful stays, memorable dining and thoughtfully hosted events.","city":"Kampala","country":"Uganda","currency":"UGX","timezone":os.getenv("HOTEL_TIMEZONE","Africa/Kampala"),"hero_image_url":"https://images.unsplash.com/photo-1566073771259-6a8506099945?auto=format&fit=crop&w=1800&q=85"})
        services=[("Accommodation","accommodation","Comfortable rooms designed for restorative stays."),("Dining","dining","Fresh local and international dining throughout your stay."),("Events & conferences","events-conferences","Flexible venues for meetings, weddings and celebrations."),("Guest experiences","guest-experiences","Thoughtful services that make every visit effortless.")]
        for order,(name,slug,description) in enumerate(services): HotelService.objects.get_or_create(hotel=hotel,slug=slug,defaults={"name":name,"short_description":description,"display_order":order,"is_featured":True})
        wifi,_=Amenity.objects.get_or_create(name="High-speed Wi-Fi"); breakfast,_=Amenity.objects.get_or_create(name="Breakfast available"); workspace,_=Amenity.objects.get_or_create(name="Work desk")
        room_types=[("Classic Room","classic-room",2,"Quiet comfort with everything needed for a relaxed stay.",180000,"https://images.unsplash.com/photo-1618773928121-c32242e63f39?auto=format&fit=crop&w=1200&q=85"),("Executive Suite","executive-suite",3,"Additional space, refined finishes and a separate sitting area.",350000,"https://images.unsplash.com/photo-1590490360182-c33d57733427?auto=format&fit=crop&w=1200&q=85"),("Family Room","family-room",5,"A generous setup for families and small groups travelling together.",480000,"https://images.unsplash.com/photo-1566665797739-1674de7a421a?auto=format&fit=crop&w=1200&q=85")]
        for order,(name,slug,capacity,description,rate,image) in enumerate(room_types):
            room_type,_=RoomType.objects.get_or_create(hotel=hotel,slug=slug,defaults={"name":name,"capacity":capacity,"description":description,"base_rate":rate,"image_url":image,"display_order":order,"bed_description":"Premium bedding"}); room_type.amenities.add(wifi,breakfast,workspace)
            Room.objects.get_or_create(hotel=hotel,number=str(101+order),defaults={"room_type":room_type,"floor":"1"})
        outlets=[('Restaurant',Outlet.Kind.RESTAURANT),('Bar',Outlet.Kind.BAR),('Room Service',Outlet.Kind.ROOM_SERVICE)]
        for name,kind in outlets:
            outlet,_=Outlet.objects.get_or_create(hotel=hotel,name=name,defaults={'kind':kind});StockLocation.objects.get_or_create(hotel=hotel,outlet=outlet,defaults={'name':f'{name} Stock'})
        beverages,_=ProductCategory.objects.get_or_create(hotel=hotel,name='Beverages');supplies,_=ProductCategory.objects.get_or_create(hotel=hotel,name='Guest supplies')
        Product.objects.get_or_create(hotel=hotel,sku='SAMPLE-WATER',defaults={'category':beverages,'name':'Bottled Water','unit':'bottle','purchase_cost':800,'selling_price':1500,'reorder_level':24})
        Product.objects.get_or_create(hotel=hotel,sku='SAMPLE-AMENITY',defaults={'category':supplies,'name':'Guest Amenity Kit','unit':'kit','purchase_cost':4000,'selling_price':0,'reorder_level':10})
        for name,capacity,rate in [('Conference Hall',150,1500000),('Meeting Room',30,350000),('Garden Venue',250,2000000)]:Venue.objects.get_or_create(hotel=hotel,name=name,defaults={'capacity':capacity,'base_rate':rate})
        for name in ['Conference','Wedding','Meeting','Workshop','Party','Seminar']:EventType.objects.get_or_create(hotel=hotel,name=name)
        email=os.getenv("BOOTSTRAP_ADMIN_EMAIL"); password=os.getenv("BOOTSTRAP_ADMIN_PASSWORD")
        if email and password and not User.objects.filter(email=email.lower()).exists(): User.objects.create_superuser(email=email.lower(),password=password,first_name="Hotel",last_name="Owner")
        self.stdout.write(self.style.SUCCESS("Hotel settings and reference data are ready."))
