from rest_framework import serializers


class SchemaEditSerializer(serializers.Serializer):
    schema_payload = serializers.DictField()


class ValidateDataSerializer(serializers.Serializer):
    schema_payload = serializers.DictField()
    data = serializers.DictField()


class UserCreateSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(max_length=128, write_only=True)
