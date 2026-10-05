import uuid
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models

class UserManager(BaseUserManager):
    use_in_migrations = True
    def create_user(self, email, password=None, **extra_fields):
        if not email: raise ValueError("An email address is required")
        user = self.model(email=self.normalize_email(email).lower(), **extra_fields)
        user.set_password(password); user.save(using=self._db); return user
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True); extra_fields.setdefault("is_superuser", True); extra_fields.setdefault("role", User.Role.OWNER)
        return self.create_user(email, password, **extra_fields)

class User(AbstractUser):
    class Role(models.TextChoices):
        OWNER="OWNER","Owner"; ADMIN="ADMIN","Administrator"; MANAGER="MANAGER","Manager"; RECEPTIONIST="RECEPTIONIST","Receptionist"; FINANCE="FINANCE","Finance staff"; BAR="BAR","Bar staff"; RESTAURANT="RESTAURANT","Restaurant staff"; HOUSEKEEPING="HOUSEKEEPING","Housekeeping staff"; EVENTS="EVENTS","Events staff"; MARKETING="MARKETING","Marketing staff"; EMPLOYEE="EMPLOYEE","Employee"; CUSTOMER="CUSTOMER","Customer"
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = None
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=24, choices=Role.choices, default=Role.CUSTOMER, db_index=True)
    phone = models.CharField(max_length=32, blank=True)
    preferred_language = models.CharField(max_length=12, default="en")
    USERNAME_FIELD = "email"; REQUIRED_FIELDS = []; objects = UserManager()
    def __str__(self): return self.get_full_name() or self.email
