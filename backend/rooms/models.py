from django.db import models


class Room(models.Model):
    number = models.CharField(max_length=10)
    room_type = models.CharField(max_length=20)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, default='available')

    def __str__(self):
        return self.number