"""Root URL configuration for the Web-Based Supply Chain Platform API."""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path


def api_root(_request):
    return JsonResponse({
        'platform': 'Web-Based Supply Chain Platform',
        'status': 'ok',
        'endpoints': {
            'auth': '/api/auth/',
            'products': '/api/products/',
            'orders': '/api/orders/',
            'payments': '/api/payments/',
            'commissions': '/api/commissions/',
            'notifications': '/api/notifications/',
            'admin': '/admin/',
        },
    })


urlpatterns = [
    path('', api_root),
    path('admin/', admin.site.urls),
    path('api/auth/', include('users.urls')),
    path('api/products/', include('products.urls')),
    path('api/orders/', include('orders.urls')),
    path('api/payments/', include('payments.urls')),
    path('api/commissions/', include('commissions.urls')),
    path('api/notifications/', include('notifications.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
