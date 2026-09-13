from rest_framework import serializers

from library.models import Book
from library.models import Fine
from library.models import RegistrationCard
from library.models import Record
from library.models import UserProfile

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile # какую модель используем
        fields = ['id', 'name', 'phone', 'user', 'type'] # какие поля включать в json

class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ['id', 'name', 'genre', 'date', 'author', 'photo']

class FineSerializer(serializers.ModelSerializer):
    registrationCard_id = serializers.SerializerMethodField() # добавляем поле registrationCard.id в сериалайзер для фильтрации
    def get_registrationCard_id(self, obj):
        record = obj.record_set.filter(registrationCard__isnull=False).first() # берем первую запись со связанной карточкой
        if record and record.registrationCard:
            return record.registrationCard.id
        return None

    class Meta:
        model = Fine
        fields = ['id', 'fineType', 'amount', 'date', 'registrationCard_id']

class RegistrationCardSerializer(serializers.ModelSerializer):
    def create(self, validated_data): 
        # когда в api создается сериалайзер, 
        # то заполняется специальное поле сериалайзера которое называется context
        # в него добавляется инфомрация по запросе, и доступна эта инфа
        # через self.context['request'], в частности там есть информация о пользовате
        if 'request' in self.context:
            # заполняем validated_data который используется для создания сущности в БД
            # данными из запроса
            validated_data['user'] = self.context['request'].user
            
        return super().create(validated_data)

    class Meta:
        model = RegistrationCard
        fields = ['id', 'photo', 'user']

class RecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = Record
        fields = ['id', 'book_issue_date', 'expected_book_accept_date', 'book_accept_date', 'fine_status', 'registrationCard', 'book', 'fine']