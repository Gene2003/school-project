from django.urls import path

from . import views

urlpatterns = [
    path('', views.TransactionListView.as_view(), name='transaction_list'),
    path('initialize/', views.InitializePaymentView.as_view(), name='payment_initialize'),
    path('verify/', views.VerifyPaymentView.as_view(), name='payment_verify'),
]
