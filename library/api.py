from rest_framework.viewsets import GenericViewSet
from rest_framework import mixins, viewsets
from rest_framework.permissions import BasePermission, IsAuthenticated
from django.db.models import Avg, Count, Max, Min
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import serializers
from django.core.cache import cache
import pyotp
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout as django_logout
import pandas as pd
from io import BytesIO
import datetime
from django.http import HttpResponse

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

class OTPRequired(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and cache.get(f'otp_good_{request.user.id}', False))

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
    permission_classes = [IsAuthenticated]

    class OTPSerializer(serializers.Serializer):
        key = serializers.CharField()

    class OTPRequired(BasePermission):
        def has_permission(self, request, view):
            return bool(request.user and cache.get(f'otp_good_{request.user.id}', False))

    def get_queryset(self):
        qs = super().get_queryset()
        
        if self.request.user.is_superuser:
            user_id = self.request.query_params.get('user_id')
            if user_id:
                qs = qs.filter(user_id=user_id)
            return qs
        return qs.filter(user=self.request.user)
        
    @action(detail=False, url_path="check-login", methods=['GET'], permission_classes=[])
    def get_check_login(self, request, *args, **kwargs):
        return Response({
            'is_authenticated': request.user.is_authenticated,
            'username': request.user.username,
            'is_superuser': request.user.is_superuser
        })
    
    @action(detail=False, url_path="login", methods=['POST'], permission_classes=[])
    def use_login(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user:
            login(request, user)
        return Response({
            'is_authenticated': bool(user)
        })

    @action(detail=False, url_path='otp-login', methods=['POST'], serializer_class=OTPSerializer)
    def otp_login(self, request, *args, **kwargs):
        if not request.user.userprofile.totp_key:
            return Response({'success': False, 'error': 'OTP not configured'})
        totp = pyotp.TOTP(request.user.userprofile.totp_key)
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        success = False
        if totp.verify(serializer.validated_data['key']):
            cache.set(f'otp_good_{request.user.id}', True, 600)
            success = True

        return Response({'success': success})
    
    @action(detail=False, url_path='otp-status')
    def get_otp_status(self, request, *args, **kwargs):
        otp_good = cache.get(f'otp_good_{request.user.id}', False)
        return Response({'otp_good': otp_good})
    
    @action(detail=False, url_path='otp-required', permission_classes=[OTPRequired])
    def page_with_otp_required(self, request, *args, **kwargs):
        return Response({'success': True})

    @action(detail=False, url_path="logout", methods=['POST'], permission_classes=[])
    def logout(self, request, *args, **kwargs):
        django_logout(request)
        cache.delete(f'otp_good_{request.user.id}')
        return Response({'success': True})

    class StatsSerializer(serializers.Serializer):
        count = serializers.IntegerField()
        avg_id = serializers.FloatField()
        max_id = serializers.IntegerField()
        min_id = serializers.IntegerField()

    @action(detail=False, methods=["GET"], url_path="stats")
    def get_stats(self, request, *args, **kwargs):
        stats = UserProfile.objects.aggregate(
            count=Count("*"),
            avg_id=Avg("id"),
            max_id=Max("id"),
            min_id=Min("id"),
        )
        
        serializer = self.StatsSerializer(instance=stats)
        return Response(serializer.data)

    @action(detail=False, methods=["GET"], url_path="export-excel")
    def export_excel(self, request):
        profiles = self.get_queryset()
        
        data = []
        for profile in profiles:
            data.append({
                "ID": profile.id,
                "Имя": profile.name if profile.name else "",
                "Телефон": profile.phone if profile.phone else "",
                "Тип": profile.get_type_display() if profile.type else "",
                "ID пользователя": profile.user.id if profile.user else None,
                "Логин": profile.user.username if profile.user else None,
            })
        
        df = pd.DataFrame(data)
        output = BytesIO() 
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Пользователи")
        
        output.seek(0)
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        filename = f"users_{today}.xlsx"   
        response = HttpResponse(
            output.read(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        response["Content-Disposition"] = f"attachment; filename={filename}"   
        return response

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

    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), UserProfileViewSet.OTPRequired()]
        return [IsAuthenticated()]

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

    @action(detail=False, methods=["GET"], url_path="export-excel")
    def export_excel(self, request):
        books = self.get_queryset()
        
        data = []
        for book in books:
            data.append({
                "ID": book.id,
                "Название": book.name,
                "Жанр": book.genre,
                "Год публикации": book.date,
                "Автор": book.author,
            })
        
        df = pd.DataFrame(data)
        output = BytesIO() 
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Книги")
        
        output.seek(0)
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        filename = f"books_{today}.xlsx"
        response = HttpResponse(
            output.read(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        response["Content-Disposition"] = f"attachment; filename={filename}"
        return response

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

    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), UserProfileViewSet.OTPRequired()]
        return [IsAuthenticated()]

    def get_queryset(self):
        qs = super().get_queryset()
        
        if self.request.user.is_superuser:
            user_id = self.request.query_params.get('user_id')
            if user_id:
                qs = qs.filter(record__registrationCard__user_id=user_id).distinct()
            return qs
        return qs.filter(record__registrationCard__user=self.request.user).distinct()

    class StatsSerializer(serializers.Serializer):
        count = serializers.IntegerField()
        avg_amount = serializers.FloatField()
        max_amount = serializers.FloatField()
        min_amount = serializers.FloatField()

    class StatsSerializer(serializers.Serializer):
        count = serializers.IntegerField()
        avg_amount = serializers.FloatField()
        max_amount = serializers.IntegerField()
        min_amount = serializers.IntegerField()

    @action(detail=False, methods=["GET"], url_path="stats")
    def get_stats(self, request, *args, **kwargs):
        stats = Fine.objects.aggregate(
            count=Count("*"),
            avg_amount=Avg("amount"),
            max_amount=Max("amount"),
            min_amount=Min("amount"),
        )
        
        serializer = self.StatsSerializer(instance=stats)
        return Response(serializer.data)

    @action(detail=False, methods=["GET"], url_path="export-excel")
    def export_excel(self, request):
        fines = self.get_queryset()
        
        data = []
        for fine in fines:
            data.append({
                "ID": fine.id,
                "Тип": fine.get_fineType_display(),
                "Сумма": fine.amount,
                "Дата": fine.date,
            })

        df = pd.DataFrame(data)
        output = BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Штрафы")
        
        output.seek(0)
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        filename = f"fines_{today}.xlsx"
        response = HttpResponse(
            output.read(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        response["Content-Disposition"] = f"attachment; filename={filename}"
        return response

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

    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), UserProfileViewSet.OTPRequired()]
        return [IsAuthenticated()]

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

    class StatsSerializer(serializers.Serializer):
        count = serializers.IntegerField()
        avg_id = serializers.FloatField()
        max_id = serializers.IntegerField()
        min_id = serializers.IntegerField()

    @action(detail=False, methods=["GET"], url_path="stats")
    def get_stats(self, request, *args, **kwargs):
        stats = RegistrationCard.objects.aggregate(
            count=Count("*"),
            avg_id=Avg("id"),
            max_id=Max("id"),
            min_id=Min("id"),
        )
        
        serializer = self.StatsSerializer(instance=stats)
        return Response(serializer.data)

    @action(detail=False, methods=["GET"], url_path="export-excel")
    def export_excel(self, request):
        cards = self.get_queryset()
        
        data = []
        for card in cards:
            data.append({
                "ID": card.id,
                "Фото": card.photo.url if card.photo else "Нет фото",
                "ID пользователя": card.user.id if card.user else None,
                "Имя пользователя": card.user.username if card.user else None,
            })
        
        df = pd.DataFrame(data)
        output = BytesIO() 
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Карточки")
        
        output.seek(0)
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        filename = f"registration_cards_{today}.xlsx" 
        response = HttpResponse(
            output.read(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        response["Content-Disposition"] = f"attachment; filename={filename}"  
        return response

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

    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), UserProfileViewSet.OTPRequired()]
        return [IsAuthenticated()]

    def get_queryset(self):
        qs = super().get_queryset()
        
        if not self.request.user.is_superuser:
            qs = qs.filter(registrationCard__user=self.request.user)
        return qs

    class StatsSerializer(serializers.Serializer):
        count = serializers.IntegerField()
        avg_id = serializers.FloatField()
        max_id = serializers.IntegerField()
        min_id = serializers.IntegerField()

    @action(detail=False, methods=["GET"], url_path="stats")
    def get_stats(self, request, *args, **kwargs):
        stats = Record.objects.aggregate(
            count=Count("*"),
            avg_id=Avg("id"),
            max_id=Max("id"),
            min_id=Min("id"),
        )
        
        serializer = self.StatsSerializer(instance=stats)
        return Response(serializer.data)

    @action(detail=False, methods=["GET"], url_path="export-excel")
    def export_excel(self, request):
        records = self.get_queryset()
        
        data = []
        for record in records:
            data.append({
                "ID": record.id,
                "Дата выдачи": record.book_issue_date,
                "Ожидаемая дата возврата": record.expected_book_accept_date,
                "Дата возврата": record.book_accept_date if record.book_accept_date else "не возвращена",
                "Статус штрафа": record.get_fine_status_display(),
                "Карточка ID": record.registrationCard.id if record.registrationCard else None,
                "Книга ID": record.book.id if record.book else None,
                "Штраф ID": record.fine.id if record.fine else None,
            })
        
        df = pd.DataFrame(data)
        output = BytesIO()     
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Записи")
        
        output.seek(0)
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        filename = f"records_{today}.xlsx"  
        response = HttpResponse(
            output.read(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        response["Content-Disposition"] = f"attachment; filename={filename}"     
        return response