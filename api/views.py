from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from api.models import Classroom

from .serializers import ClassroomSerializer


class ListCreateClassroom(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        classrooms = Classroom.objects.filter(teacher=request.user)
        serializer = ClassroomSerializer(classrooms, many=True)
        return Response(serializer.data)

    def post(self, request):
        request.data.update({"teacher": request.user.id})

        serializer = ClassroomSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
