from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status

from .models import Room
from .serializers import RoomSerializer


# =========================
# LIST ALL + CREATE ROOM
# =========================
@api_view(['GET', 'POST'])
def room_list_create(request):

    # GET ALL ROOMS
    if request.method == 'GET':
        rooms = Room.objects.all()
        serializer = RoomSerializer(rooms, many=True)
        return Response(serializer.data)

    # CREATE ROOM
    elif request.method == 'POST':
        serializer = RoomSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# =========================
# GET ONE + UPDATE + DELETE
# =========================
@api_view(['GET', 'PUT', 'DELETE'])
def room_detail(request, pk):

    try:
        room = Room.objects.get(id=pk)
    except Room.DoesNotExist:
        return Response({'error': 'Room not found'}, status=status.HTTP_404_NOT_FOUND)

    # GET ONE ROOM
    if request.method == 'GET':
        serializer = RoomSerializer(room)
        return Response(serializer.data)

    # UPDATE ROOM
    elif request.method == 'PUT':
        serializer = RoomSerializer(room, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # DELETE ROOM
    elif request.method == 'DELETE':
        room.delete()
        return Response({'message': 'Room deleted successfully'}, status=status.HTTP_204_NO_CONTENT)