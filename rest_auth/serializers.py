import email
from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from rest_auth.helpers import send_confirmation_email


User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(min_length=6, required=True, write_only=True)

    class Meta:
        model = User
        fields = ('email', 'password')
    
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('User with given email already exists')
        return value
    
    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class LoginSerializer(TokenObtainPairSerializer):
    pass


class ActivationSerializer(serializers.Serializer):
    activation_code = serializers.CharField(required=True, write_only=True, max_length=255)


class LostPasswordSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('email', )

    def validate_email(self, email):
        if not User.objects.filter(email=email).exists():
            raise serializers.ValidationError('User with given email not found')
        return email

    def send_activation(self):
        email = self.validated_data.get('email')
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError('User not found')
        user.create_activation_code()
        # send_activation_mail(user)
        send_confirmation_email(user)


class CreateNewPasswordSerializer(serializers.ModelSerializer):
    password = serializers.CharField(min_length=6, read_only=True, )
    password_confirmation = serializers.CharField(min_length=6, read_only=True, )

    class Meta:
        model = User
        fields = ('email', 'activation_code', 'password', 'password_confirmation')

    def validate_email(self, email):
        if not User.objects.filter(email=email).exists():
            raise serializers.ValidationError(_('User with given email not found'))
        return email

    def validate(self, validated_data):
        password = validated_data.get('password')
        password_confirmation = validated_data.get('password_confirmation')
        if password != password_confirmation:
            raise serializers.ValidationError(_('Passwords don\'t match'))
        email = validated_data.get('email')
        activation_code = validated_data.get('activation_code')
        if not User.objects.filter(email=email, activation_code=activation_code).exists():
            raise serializers.ValidationError(_('User not found'))
        return validated_data

    def set_new_password(self):
        user = User.objects.get(email=self.validated_data.get('email'))
        user.activate_with_code(self.validated_data.get('activation_code'))
        user.set_password(self.validated_data.get('password'))


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    new_password_confirm = serializers.CharField(required=True)

    def validate(self, validated_data):
        new_password = validated_data.get('new_password')
        new_password_confirm = validated_data.get('new_password_confirm')
        if new_password != new_password_confirm:
            raise serializers.ValidationError(_('Passwords don\'t match'))
        return validated_data

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'