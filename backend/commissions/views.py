"""Commission endpoints: a user's own earnings; admins see everything."""

from django.db.models import Sum
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from users.models import User

from .models import Commission
from .serializers import CommissionSerializer


class CommissionListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.role == User.Role.ADMIN or user.is_staff:
            qs = Commission.objects.all()
        else:
            qs = Commission.objects.filter(beneficiary=user)
        qs = qs.select_related('order', 'beneficiary')

        summary = {
            'total_earned': qs.filter(
                kind=Commission.Kind.REFERRAL
            ).aggregate(s=Sum('amount'))['s'] or 0,
            'platform_fees': qs.filter(
                kind=Commission.Kind.PLATFORM
            ).aggregate(s=Sum('amount'))['s'] or 0,
        }
        return Response({
            'summary': summary,
            'results': CommissionSerializer(qs, many=True).data,
        })
