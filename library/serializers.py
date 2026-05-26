from rest_framework import serializers

from library.models import Book
from library.models import Fine
from library.models import RegistrationCard
from library.models import Record
from library.models import UserProfile

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['id', 'name', 'phone', 'user', 'type']

class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ['id', 'name', 'genre', 'date', 'author']

class FineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fine
        fields = ['id', 'fineType', 'amount', 'date']

class RegistrationCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = RegistrationCard
        fields = ['id', 'photo', 'user']

class RecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = Record
        fields = ['id', 'book_issue_date', 'expected_book_accept_date', 'book_accept_date', 'fine_status']