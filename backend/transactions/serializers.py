from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password#builtin password validator to check password policies
from rest_framework import serializers


class RetrieveRequestSerializer(serializers.Serializer):
    question = serializers.CharField(required=True, allow_blank=False)
    k = serializers.IntegerField(
        required=False,
        default=settings.RAG_TOP_K,
        min_value=1,
        error_messages={
            "invalid": "k must be an integer",
            "min_value": "k must be greater than 0",
        },
    )

    def validate_question(self, value):
        question = value.strip()
        if not question:
            raise serializers.ValidationError("question is required")
        return question


class AskQuestionRequestSerializer(serializers.Serializer):
    question = serializers.CharField(required=True, allow_blank=False)
    k = serializers.IntegerField(
        required=False,
        default=settings.RAG_TOP_K,
        min_value=1,
        error_messages={
            "invalid": "k must be an integer",
            "min_value": "k must be greater than 0",
        },
    )

    def validate_question(self, value):
        question = value.strip()
        if not question:
            raise serializers.ValidationError("question is required")
        return question


class RegisterRequestSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=100)
    email = serializers.EmailField(required=True, allow_blank=False)
    password = serializers.CharField(write_only=True, min_length=8)

    def validate_username(self, value):
        username = value.strip()
        if not username:
            raise serializers.ValidationError("username is required")
        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError("username already exists")
        return username

    def validate_password(self, value):
        validate_password(value)
        return value
