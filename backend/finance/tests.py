from datetime import date,timedelta
from decimal import Decimal
from django.test import TestCase
from rest_framework.test import APIClient
from bookings.models import GuestProfile
from hotels.models import Hotel
from rooms.models import Room,RoomType
from users.models import User
from .services import create_stay_with_folio

class StayFinanceFlowTests(TestCase):
    def setUp(self):
        self.hotel=Hotel.objects.create(name='Test Hotel',is_active=True)
        self.user=User.objects.create_user(email='owner@test.local',password='SafePassword123!',role=User.Role.OWNER)
        room_type=RoomType.objects.create(hotel=self.hotel,name='Standard',slug='standard',capacity=2,base_rate=Decimal('100000'))
        self.room=Room.objects.create(hotel=self.hotel,room_type=room_type,number='101')
        self.guest=GuestProfile.objects.create(first_name='Test',last_name='Guest',phone='0700000000',email='guest@test.local')
    def test_stay_creation_creates_balanced_accommodation_folio(self):
        arrival=date.today();departure=arrival+timedelta(days=2)
        stay=create_stay_with_folio(actor=self.user,hotel=self.hotel,guest=self.guest,room=self.room,arrival_date=arrival,departure_date=departure,rate=Decimal('100000'))
        self.assertEqual(stay.folio.total_charges,Decimal('200000'))
        self.assertEqual(stay.folio.balance,Decimal('200000'))
    def test_reception_counter_registration_creates_guest_stay_folio_and_check_in(self):
        client=APIClient();client.force_authenticate(self.user);arrival=date.today();departure=arrival+timedelta(days=1);response=client.post('/api/bookings/counter/',{'first_name':'Walk','last_name':'In','phone':'0700111222','email':'walkin@test.local','room_id':str(self.room.id),'arrival_date':str(arrival),'departure_date':str(departure),'occupants':1,'rate':'100000','purpose_of_visit':'Business','account_payer':'Self','check_in_now':True},format='json')
        self.assertEqual(response.status_code,201,response.data);stay=self.hotel.stays.get(id=response.data['stay_id']);self.assertEqual(stay.status,stay.Status.CHECKED_IN);self.assertEqual(stay.folio.balance,Decimal('100000'));self.room.refresh_from_db();self.assertEqual(self.room.occupancy_status,self.room.Occupancy.OCCUPIED)
