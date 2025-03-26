from rest_framework import generics
from rest_framework import permissions
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken

from beanserver.users.models import User

from .serializers import UserPasswordUpdateSerializer
from .serializers import UserRegistrationSerializer
from .serializers import UserSerializer


class UserDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes = [JWTAuthentication]  # Use JWT Authentication
    permission_classes = [permissions.IsAuthenticated]  # Only authenticated users
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = "id"  # Important for UUID lookups

    def get_object(self):
        # Ensure the logged-in user can only access their own data
        if str(self.kwargs["id"]) != str(self.request.user.id):  # compare UUID strings
            self.permission_denied(
                self.request,
            )  # Raise 403 Forbidden if not their own data

        return super().get_object()  # Use UUID lookup to get object, 404 if not found

    def destroy(self, request, *args, **kwargs):
        if str(self.kwargs["id"]) != str(self.request.user.id):  # compare UUID strings
            self.permission_denied(
                self.request,
            )  # Raise 403 Forbidden if not their own data

        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            status=status.HTTP_204_NO_CONTENT,
        )  # Return 204 on successful delete


class UserRegisterAPIView(APIView):
    permission_classes = [AllowAny]  # Allow anyone to register
    serializer_class = UserRegistrationSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)

            response_data = {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "user_id": str(
                    user.id,
                ),  # Include user ID if you need it in the frontend.
            }
            return Response(response_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserPasswordUpdateAPIView(generics.UpdateAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserPasswordUpdateSerializer

    def get_object(self):
        return self.request.user  # Only allow updating the logged-in user's password

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(
            raise_exception=True,
        )  # This will raise 400 for validation errors

        user = self.request.user
        old_password = serializer.validated_data["old_password"]  # Access old password
        new_password = serializer.validated_data["new_password"]

        if not user.check_password(old_password):  # Use check_password directly
            return Response(
                {"detail": "Invalid old password."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        user.set_password(new_password)
        user.save()

        return Response({"message": "Password updated successfully."})
