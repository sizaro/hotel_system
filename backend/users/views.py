from rest_framework import generics,permissions,viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import User
from .serializers import ChangePasswordSerializer,RegisterSerializer,StaffUserSerializer,UserSerializer
from .permissions import IsOwnerAdmin

class RegisterView(generics.CreateAPIView):
    serializer_class=RegisterSerializer; permission_classes=[permissions.AllowAny]
class MeView(APIView):
    def get(self,request): return Response(UserSerializer(request.user).data)
    def patch(self,request):
        serializer=UserSerializer(request.user,data=request.data,partial=True); serializer.is_valid(raise_exception=True); serializer.save(); return Response(serializer.data)
class ChangePasswordView(APIView):
    def post(self,request):serializer=ChangePasswordSerializer(data=request.data,context={'request':request});serializer.is_valid(raise_exception=True);serializer.save();return Response({'detail':'Password updated successfully.'})
class StaffUserViewSet(viewsets.ModelViewSet):
    serializer_class=StaffUserSerializer;permission_classes=[IsOwnerAdmin];queryset=User.objects.exclude(role=User.Role.CUSTOMER).order_by('first_name','last_name','email')
