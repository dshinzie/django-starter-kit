from django.contrib.auth import get_user_model
from rest_framework import serializers
User = get_user_model()


class UserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'unique_id', 'random_field')
