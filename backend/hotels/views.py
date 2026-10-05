from django.core.cache import cache
import os
from rest_framework import permissions,status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Hotel
from .serializers import HotelSerializer
from users.permissions import IsHotelStaff,IsOwnerAdmin

class HotelSettingsView(APIView):
    def get_permissions(self): return [permissions.AllowAny()] if self.request.method=="GET" else [IsOwnerAdmin()]
    def get(self,request):
        cached=cache.get("active-hotel-settings")
        if cached: return Response(cached)
        hotel=Hotel.objects.prefetch_related("services").filter(is_active=True).first()
        if not hotel: return Response({"name":"Hotel Management Platform","short_name":"Hotel","currency":"UGX","timezone":"Africa/Kampala","services":[]})
        data=HotelSerializer(hotel).data; cache.set("active-hotel-settings",data,300); return Response(data)
    def patch(self,request):
        hotel=Hotel.objects.filter(is_active=True).first()
        if not hotel: return Response({"detail":"No active hotel is configured."},status=404)
        serializer=HotelSerializer(hotel,data=request.data,partial=True); serializer.is_valid(raise_exception=True); serializer.save(); cache.delete("active-hotel-settings"); return Response(serializer.data)

class MediaUploadView(APIView):
    permission_classes=[IsHotelStaff]
    def post(self,request):
        import cloudinary.uploader
        file=request.FILES.get('file')
        if not file:return Response({'detail':'Choose a file to upload.'},status=400)
        if file.size>15*1024*1024:return Response({'detail':'Files must not exceed 15 MB.'},status=400)
        allowed=('image/','video/','application/pdf')
        if not any(file.content_type.startswith(x) for x in allowed):return Response({'detail':'Only images, videos and PDF documents are supported.'},status=400)
        try:
            result=cloudinary.uploader.upload(file,resource_type='auto',folder=os.getenv('CLOUDINARY_FOLDER','hotel-platform'))
        except Exception:return Response({'detail':'Media upload is unavailable. Check the backend Cloudinary configuration.'},status=status.HTTP_503_SERVICE_UNAVAILABLE)
        return Response({'url':result.get('secure_url'),'public_id':result.get('public_id'),'resource_type':result.get('resource_type'),'format':result.get('format'),'bytes':result.get('bytes')},status=201)
