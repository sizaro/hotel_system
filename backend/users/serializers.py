from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model=User; fields=("id","email","first_name","last_name","phone","role","preferred_language"); read_only_fields=("id","role")

class RegisterSerializer(serializers.ModelSerializer):
    password=serializers.CharField(write_only=True,validators=[validate_password])
    class Meta: model=User; fields=("email","password","first_name","last_name","phone")
    def create(self,validated_data): return User.objects.create_user(role=User.Role.CUSTOMER,**validated_data)

class ChangePasswordSerializer(serializers.Serializer):
    current_password=serializers.CharField(write_only=True);new_password=serializers.CharField(write_only=True,validators=[validate_password])
    def validate_current_password(self,value):
        if not self.context['request'].user.check_password(value):raise serializers.ValidationError('Current password is incorrect.')
        return value
    def save(self):user=self.context['request'].user;user.set_password(self.validated_data['new_password']);user.save(update_fields=['password']);return user

class StaffUserSerializer(serializers.ModelSerializer):
    password=serializers.CharField(write_only=True,required=False,validators=[validate_password])
    class Meta:model=User;fields=('id','email','first_name','last_name','phone','role','is_active','password','last_login');read_only_fields=('id','last_login')
    def validate_role(self,value):
        if value==User.Role.CUSTOMER:raise serializers.ValidationError('Customer accounts are created through guest registration.')
        return value
    def create(self,data):return User.objects.create_user(password=data.pop('password',None),**data)
    def update(self,instance,data):
        password=data.pop('password',None);instance=super().update(instance,data)
        if password:instance.set_password(password);instance.save(update_fields=['password'])
        return instance
