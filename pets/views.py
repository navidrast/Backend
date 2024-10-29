# pets/views.py

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import Pet, PetHealthRecord
from .serializers import (
    PetSerializer,
    PetDetailSerializer,
    PetHealthRecordSerializer
)
from services.models import DogSize

class PetViewSet(viewsets.ModelViewSet):
    """宠物视图集"""
    serializer_class = PetSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """只返回当前用户的宠物"""
        return Pet.objects.filter(owner=self.request.user)

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return PetDetailSerializer
        return PetSerializer

    def perform_create(self, serializer):
        """创建时自动设置主人为当前用户"""
        serializer.save(owner=self.request.user)

    @action(detail=False, methods=['get'])
    def sizes(self, request):
        """获取所有狗狗体型"""
        return Response(dict(DogSize.choices))

    @action(detail=True, methods=['get'])
    def health_records(self, request, pk=None):
        """获取宠物的健康记录"""
        pet = self.get_object()
        records = pet.health_records.all()
        serializer = PetHealthRecordSerializer(records, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def add_health_record(self, request, pk=None):
        """添加健康记录"""
        pet = self.get_object()
        serializer = PetHealthRecordSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save(pet=pet)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PetHealthRecordViewSet(viewsets.ModelViewSet):
    """健康记录视图集"""
    serializer_class = PetHealthRecordSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """只返回当前用户宠物的健康记录"""
        return PetHealthRecord.objects.filter(pet__owner=self.request.user)

    def perform_create(self, serializer):
        """创建健康记录时验证宠物归属"""
        pet_id = self.request.data.get('pet')
        pet = get_object_or_404(Pet, id=pet_id, owner=self.request.user)
        serializer.save(pet=pet)