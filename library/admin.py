from django.contrib import admin

from library.models import TimeStampModel, UserProfile, Record, RegistrationCard, Book, Fine

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'phone']

@admin.register(Record)
class RecordAdmin(admin.ModelAdmin):
    list_display = ['id', 'book_issue_date', 'expected_book_accept_date', 'book_accept_date', 'fine_status']

@admin.register(RegistrationCard)
class RegistrationCardAdmin(admin.ModelAdmin):
    list_display = ['id', 'photo', 'user']

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'genre', 'date', 'author']

@admin.register(Fine)
class FineAdmin(admin.ModelAdmin):
    list_display = ['id', 'fineType', 'amount', 'date']
