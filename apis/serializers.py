from rest_framework import serializers
from apis.models import *
 
 
class UserSerializer(serializers.Serializer):
    class Meta:
        fields = ('email','nick',)

    id = serializers.IntegerField(read_only=True)
    password = serializers.CharField(required=False, max_length=254)
    email = serializers.EmailField(required=False, allow_blank=True, max_length=254)
    age = serializers.IntegerField(required=False)
    nick = serializers.CharField(required=False, allow_blank=True, max_length=10)
    first_name = serializers.CharField(required=False, allow_blank=True, max_length=30)
    last_name = serializers.CharField(required=False, allow_blank=True, max_length=30)
 
    def create(self, validated_data):
        """
        Create and return a new `User` instance, given the validated data.
        """
        password = validated_data['password']
        user = CustomUser.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        return user
 
    def update(self, instance, validated_data):
        """
        Update and return an existing `User` instance, given the validated data.
        """
        instance.email = validated_data.get('email', instance.email)
        instance.set_password(validated_data.get('password', instance.password))
        instance.age = validated_data.get('age', instance.age)
        instance.nick = validated_data.get('nick', instance.nick)
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.save()
        return instance
