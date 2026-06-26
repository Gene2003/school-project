"""Serializers for registration, authentication and profile."""

from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Public representation of a user / profile."""

    referrals_count = serializers.IntegerField(source='referrals.count', read_only=True)

    class Meta:
        model = User
        fields = (
            'id', 'email', 'full_name', 'role', 'phone_number', 'location',
            'referral_code', 'referrals_count', 'is_seller', 'date_joined',
        )
        read_only_fields = ('id', 'email', 'referral_code', 'date_joined')


class RegisterSerializer(serializers.ModelSerializer):
    """Create a new account, optionally crediting a referrer."""

    password = serializers.CharField(write_only=True, min_length=8)
    referral_code = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = (
            'id', 'email', 'full_name', 'role', 'phone_number',
            'location', 'password', 'referral_code',
        )

    def validate_role(self, value):
        # Prevent self-registration as an administrator.
        if value == User.Role.ADMIN:
            raise serializers.ValidationError('You cannot register as an administrator.')
        return value

    def create(self, validated_data):
        referral_code = validated_data.pop('referral_code', '') or ''
        password = validated_data.pop('password')

        referrer = None
        if referral_code:
            referrer = User.objects.filter(referral_code=referral_code).first()

        user = User(**validated_data)
        user.referred_by = referrer
        user.set_password(password)
        user.save()
        return user


class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    """JWT login that embeds the user's role and basic profile in the response."""

    username_field = User.USERNAME_FIELD

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['role'] = user.role
        token['full_name'] = user.full_name
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data['user'] = UserSerializer(self.user).data
        return data
