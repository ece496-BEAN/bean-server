from rest_framework import serializers

from beanserver.users.models import User


class UserSerializer(
    serializers.ModelSerializer,
):  # Or use your existing serializer if it's appropriate
    class Meta:
        model = User
        fields = ["id", "email", "name"]  # Include the fields you want to expose


class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["email", "name", "password"]  # Include password
        extra_kwargs = {
            "password": {"write_only": True},
        }  # Don't return password in response

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data["email"].lower(),
            name=validated_data["name"],
            password=validated_data["password"],
        )
        user.set_password(validated_data["password"])  # Hash the password
        user.save()
        return user
