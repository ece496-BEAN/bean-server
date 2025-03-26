from rest_framework import serializers

from beanserver.users.models import User


class UserSerializer(
    serializers.ModelSerializer,
):
    class Meta:
        model = User
        fields = ["id", "email", "name", "password"]

    def update(self, instance, validated_data):
        instance.email = validated_data.get("email", instance.email)
        instance.name = validated_data.get("name", instance.name)
        instance.save()
        return instance


class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["email", "name", "password"]  # Include password
        extra_kwargs = {
            "password": {"write_only": True},
        }

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data["email"].lower(),
            name=validated_data["name"],
            password=validated_data["password"],
        )
        user.set_password(validated_data["password"])
        user.save()
        return user


class UserPasswordUpdateSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True, min_length=8)
    confirm_new_password = serializers.CharField(
        required=True,
        write_only=True,
        min_length=8,
    )

    def validate(self, data):
        new_password = data.get("new_password")
        confirm_new_password = data.get("confirm_new_password")

        if new_password != confirm_new_password:
            raise serializers.ValidationError({"detail": "Passwords do not match."})
        return data
