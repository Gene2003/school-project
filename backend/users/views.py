"""Authentication, registration and profile endpoints."""

from django.contrib.auth import get_user_model
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from .permissions import IsAdmin
from .serializers import (
    EmailTokenObtainPairSerializer,
    RegisterSerializer,
    UserSerializer,
)

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    """POST /api/auth/register/ — open registration."""

    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class LoginView(TokenObtainPairView):
    """POST /api/auth/login/ — returns access/refresh tokens + user payload."""

    serializer_class = EmailTokenObtainPairSerializer


class ProfileView(generics.RetrieveUpdateAPIView):
    """GET/PATCH /api/auth/me/ — the authenticated user's own profile."""

    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class UserListView(generics.ListAPIView):
    """GET /api/auth/users/ — admin-only directory of all accounts."""

    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [IsAdmin]
    filterset_fields = ['role']
    search_fields = ['email', 'full_name', 'location']


class UserAdminDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Admin: view / edit role / delete a specific account."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdmin]


class StatsView(APIView):
    """GET /api/auth/stats/ — headline counts for the admin dashboard."""

    permission_classes = [IsAdmin]

    def get(self, request):
        from orders.models import Order
        from products.models import Product

        counts = {role: User.objects.filter(role=role).count()
                  for role, _ in User.Role.choices}
        return Response({
            'users_total': User.objects.count(),
            'users_by_role': counts,
            'products_total': Product.objects.count(),
            'orders_total': Order.objects.count(),
            'orders_paid': Order.objects.filter(status=Order.Status.PAID).count(),
        }, status=status.HTTP_200_OK)
