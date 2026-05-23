from django.db import models
from django.contrib.auth.models import User

class TimeStampModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True) 

    class Meta:
        abstract = True

class UserProfile(TimeStampModel):
    class Type:
        employee = 'employee', 'работник'
        reader = 'reader', 'читатель'

    name = models.TextField(null=True)
    phone = models.TextField(null=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)

    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            UserProfile.objects.create(user=instance)

class RegistrationCard(models.Model):
    photo = models.ImageField("Фото", default = "Нет фото")
    user = models.ForeignKey("UserProfile", on_delete=models.CASCADE, null=True)

    class Meta:
        verbose_name = "Учетная карточка"
        verbose_name_plural = "Учетные карточки"

class Record(models.Model):
    book_issue_date = models.TextField("Дата выдачи книги")
    expected_book_accept_date = models.TextField("Ожидаемая дата возврата книги")
    book_accept_date = models.TextField("Дата возврата книги")
    fine_status = models.TextField("Статус штрафа")
    registrationCard = models.ForeignKey("RegistrationCard", on_delete=models.CASCADE, null=True)
    book = models.ForeignKey("Book", on_delete=models.CASCADE, null=True)
    fine = models.ForeignKey("Fine", on_delete=models.CASCADE, null=True)

    class Meta:
        verbose_name = "Запись в учетной карточке"
        verbose_name_plural = "Записи в учетных карточках"

class Fine(models.Model):
    fineType = models.TextField("Тип")
    amount = models.TextField("Сумма")
    date = models.TextField("Дата")

    class Meta:
        verbose_name = "Штраф"
        verbose_name_plural = "Штрафы"

class Book(models.Model):
    name = models.TextField("Название")
    genre = models.TextField("Жанр")
    date = models.TextField("Дата публикации")
    author = models.TextField("Автор")

    class Meta:
        verbose_name = "Книга"
        verbose_name_plural = "Книги"