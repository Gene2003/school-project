from django.urls import path

from .views import CommissionListView

urlpatterns = [
    path('', CommissionListView.as_view(), name='commission_list'),
]
