from rest_framework.permissions import BasePermission
from .models import User

STAFF_ROLES={User.Role.OWNER,User.Role.ADMIN,User.Role.MANAGER,User.Role.RECEPTIONIST,User.Role.FINANCE,User.Role.BAR,User.Role.RESTAURANT,User.Role.HOUSEKEEPING,User.Role.EVENTS,User.Role.MARKETING,User.Role.EMPLOYEE}
class IsHotelStaff(BasePermission):
    def has_permission(self,request,view): return bool(request.user and request.user.is_authenticated and request.user.role in STAFF_ROLES)
class IsManagement(BasePermission):
    def has_permission(self,request,view): return bool(request.user and request.user.is_authenticated and request.user.role in {User.Role.OWNER,User.Role.ADMIN,User.Role.MANAGER})
class IsFinanceStaff(BasePermission):
    def has_permission(self,request,view): return bool(request.user and request.user.is_authenticated and request.user.role in {User.Role.OWNER,User.Role.ADMIN,User.Role.MANAGER,User.Role.FINANCE,User.Role.RECEPTIONIST})
class IsOwnerAdmin(BasePermission):
    def has_permission(self,request,view): return bool(request.user and request.user.is_authenticated and request.user.role in {User.Role.OWNER,User.Role.ADMIN})
class IsReceptionStaff(BasePermission):
    def has_permission(self,request,view): return bool(request.user and request.user.is_authenticated and request.user.role in {User.Role.OWNER,User.Role.ADMIN,User.Role.MANAGER,User.Role.RECEPTIONIST})
