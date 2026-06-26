"""Product listing and management endpoints."""

from rest_framework import viewsets

from users.permissions import IsOwnerOrReadOnly, IsSeller

from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class ProductViewSet(viewsets.ModelViewSet):
    """
    Public read access to active listings; sellers manage their own products.

    Use ?mine=1 to fetch the authenticated seller's own catalogue (including
    inactive items).
    """

    serializer_class = ProductSerializer
    permission_classes = [IsSeller, IsOwnerOrReadOnly]
    owner_field = 'seller'
    filterset_fields = ['category', 'unit', 'seller', 'is_active']
    search_fields = ['name', 'description', 'location']
    ordering_fields = ['price', 'created_at']

    def get_queryset(self):
        qs = Product.objects.select_related('seller', 'category')
        if self.request.query_params.get('mine') and self.request.user.is_authenticated:
            return qs.filter(seller=self.request.user)
        # Public browsing only shows active, in-stock-capable listings.
        if self.action == 'list':
            return qs.filter(is_active=True)
        return qs
