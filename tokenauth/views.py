import datetime
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework import permissions, serializers, status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from tokenauth.serializers import (
    RegistrationSerializer,
    UserLoginResponse,
    UserLoginSerializer,
)


class RegistrationView(APIView):
    """Registeration View"""

    def post(self, request, *args, **kwargs):
        """Handles post request logic"""
        registration_serializer = RegistrationSerializer(data=request.data)

        # Generate tokens for existing users
        for user in User.objects.all():
            if not user:
                break
            else:
                try:
                    Token.objects.get(user_id=user.id)
                except Token.DoesNotExist:
                    Token.objects.create(user=user)

        if registration_serializer.is_valid():
            user = registration_serializer.save()
            token = Token.objects.create(user=user)

            return Response(
                {
                    "user": {
                        "id": registration_serializer.data["id"],
                        "first_name": registration_serializer.data["first_name"],
                        "last_name": registration_serializer.data["last_name"],
                        "username": registration_serializer.data["username"],
                        "email": registration_serializer.data["email"],
                        "is_active": registration_serializer.data["is_active"],
                        "is_staff": registration_serializer.data["is_staff"],
                    },
                    "status": {
                        "message": "User created",
                        "code": f"{status.HTTP_200_OK} OK",
                    },
                    "token": token.key,
                }
            )
        return Response(
            {
                "error": registration_serializer.errors,
                "status": f"{status.HTTP_203_NON_AUTHORITATIVE_INFORMATION} NON AUTHORITATIVE INFORMATION",
            },
            status=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION,
        )


class HelloView(APIView):
    permission_classes = [
        IsAuthenticated
    ]  # Only authenticated users can access this view

    def get(self, request):
        context = {"message": "Hello, World!"}
        return Response(context)


class LoginView(APIView):
    """Login View"""

    permissions_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        login_serializer = UserLoginSerializer(data=request.data)
        if login_serializer.is_valid():
            user = authenticate(request, **login_serializer.data)
        if user is not None:
            response_class = UserLoginResponse(user)
            token, created = Token.objects.get_or_create(user_id=user.id)
            utc_now = datetime.datetime.now(datetime.timezone.utc)
        if isinstance(token, Token):
            # if token hasn't been just created and it was created more than 24hrs ago
            # refresh it with a new one
            if not created and token.created < (utc_now - datetime.timedelta(hours=24)):
                token.delete()
                token = Token.objects.create(user_id=user.id)
                token.created = datetime.datetime.utcnow()
                token.save()
            return Response(
                {
                    "user": response_class.data,
                    "status": {
                        "message": "User Authenticated",
                        "code": status.HTTP_200_OK,
                    },
                    "token": token.key,
                },
                status=status.HTTP_200_OK,
            )

        else:
            raise serializers.ValidationError(
                {
                    "error": {
                        "message": "Invalid Username or Password. Please try again",
                        "status": f"{status.HTTP_400_BAD_REQUEST} BAD REQUEST",
                    }
                }
            )
            return {
                "error": serializer.errors,
                "status": f"{status.HTTP_403_FORBIDDEN} FORBIDDEN",
            }
