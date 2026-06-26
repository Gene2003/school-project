"""Order endpoints: buyers checkout & track; sellers see incoming sales."""

from rest_framework import mixins, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from users.models import User

from .models import Order, OrderItem
from .serializers import CheckoutSerializer, OrderItemSerializer, OrderSerializer


class OrderViewSet(mixins.CreateModelMixin,
                   mixins.RetrieveModelMixin,
                   mixins.ListModelMixin,
                   viewsets.GenericViewSet):
    """List/create orders for the authenticated buyer."""

    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        return CheckoutSerializer if self.action == 'create' else OrderSerializer

    def get_queryset(self):
        user = self.request.user
        if user.role == User.Role.ADMIN or user.is_staff:
            return Order.objects.all().prefetch_related('items')
        return Order.objects.filter(buyer=user).prefetch_related('items')

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        return Response(OrderSerializer(order).data, status=201)

    @action(detail=False, methods=['get'])
    def sales(self, request):
        """Incoming order items for the authenticated seller."""
        items = (OrderItem.objects
                 .filter(seller=request.user)
                 .select_related('order', 'product')
                 .order_by('-order__created_at'))
        return Response(OrderItemSerializer(items, many=True).data)
