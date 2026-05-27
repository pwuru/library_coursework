from rest_framework.viewsets import GenericViewSet
from rest_framework import mixins, viewsets
from rest_framework.permissions import IsAuthenticated
from django.db.models import Avg, Count, Max, Min
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import serializers

from library.models import Book
from library.models import Fine
from library.models import RegistrationCard
from library.models import Record
from library.models import UserProfile
from library.serializers import BookSerializer
from library.serializers import FineSerializer
from library.serializers import RegistrationCardSerializer
from library.serializers import RecordSerializer
from library.serializers import UserProfileSerializer

class UserProfileViewSet(
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin, 
    mixins.DestroyModelMixin,
    GenericViewSet,
):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer

class BookViewSet(
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin, 
    mixins.DestroyModelMixin,
    GenericViewSet,
):
    queryset = Book.objects.all()
    serializer_class = BookSerializer

    class StatsSerializer(serializers.Serializer):
        count = serializers.IntegerField();
        avg_year = serializers.FloatField();
        max_year = serializers.IntegerField();
        min_year = serializers.IntegerField();

    @action(detail=False, methods=["GET"], url_path="stats")
    def get_stats(self, request, *args, **kwargs):
        stats = Book.objects.aggregate(
            count=Count("*"),
            avg_year=Avg("date"),
            max_year=Max("date"),
            min_year=Min("date"),
        )
        
        serializer = self.StatsSerializer(instance=stats)

        return Response(serializer.data)

class FineViewSet(
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin, 
    mixins.DestroyModelMixin,
    GenericViewSet,
):
    queryset = Fine.objects.all()
    serializer_class = FineSerializer

class RegistrationCardViewSet(
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin, 
    mixins.DestroyModelMixin,
    GenericViewSet,
):
    queryset = RegistrationCard.objects.all()
    serializer_class = RegistrationCardSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        
        if self.request.user.is_superuser:
            user_id = self.request.query_params.get('user_id')
            if user_id:

                qs = qs.filter(user_id=user_id)
            return qs
        # фильтруем по текущему юзеру
        return qs.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class RecordViewSet(
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin, 
    mixins.DestroyModelMixin,
    GenericViewSet,
):
    queryset = Record.objects.all()
    serializer_class = RecordSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        
        if not self.request.user.is_superuser:
            qs = qs.filter(registrationCard__user=self.request.user)
        return qs