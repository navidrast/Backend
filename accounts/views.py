# accounts/views.py
from rest_framework.views import APIView
from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import get_user_model
from .serializers import (
    CustomerSerializer, 
    CustomerRegistrationSerializer,
    PasswordChangeSerializer
)

class CurrentUserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = CustomerSerializer(request.user)
        return Response(serializer.data)

Customer = get_user_model()

class CustomerViewSet(viewsets.ModelViewSet):
    """
    客户视图集
    """
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action == 'create':
            return CustomerRegistrationSerializer
        return CustomerSerializer

    @action(detail=False, methods=['get'])
    def me(self, request):
        """获取当前用户信息"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def change_password(self, request):
        """修改密码"""
        serializer = PasswordChangeSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            if not user.check_password(serializer.data.get('old_password')):
                return Response({'old_password': ['旧密码错误']},
                              status=status.HTTP_400_BAD_REQUEST)
            user.set_password(serializer.data.get('new_password'))
            user.save()
            return Response({'message': '密码修改成功'}, 
                          status=status.HTTP_200_OK)
        return Response(serializer.errors, 
                       status=status.HTTP_400_BAD_REQUEST)