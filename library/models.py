from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class TimeStampModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True) 

    class Meta:
        abstract = True

class UserProfile(TimeStampModel):
    class Type(models.TextChoices):
        ADMIN = 'admin', 'администратор'
        EMPLOYEE = 'employee', 'работник'
        READER = 'reader', 'читатель'

    name = models.TextField(null=True)
    phone = models.TextField(null=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    type = models.CharField(
        max_length=20,
        choices=Type.choices,
        default=Type.READER,
        null=True,
        blank=True
    )

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
        if created:
            UserProfile.objects.create(user=instance)

class RegistrationCard(models.Model):
    photo = models.ImageField("Фото", upload_to="registration_cards", null=True, blank=True)
    user = models.OneToOneField("UserProfile", on_delete=models.CASCADE, null=True)

    class Meta:
        verbose_name = "Учетная карточка"
        verbose_name_plural = "Учетные карточки"

class Record(models.Model):
    class FineStatus(models.TextChoices):
        NO_FINE = 'no_fine', 'Нет'
        UNPAID = 'unpaid', 'Не оплачен'
        PAID = 'paid', 'Оплачен'

    book_issue_date = models.DateField("Дата выдачи книги")
    expected_book_accept_date = models.DateField("Ожидаемая дата возврата книги")
    book_accept_date = models.DateField("Дата возврата книги", null=True, blank=True)
    fine_status = models.CharField(
        "Статус штрафа",
        max_length=20,
        choices=FineStatus.choices,
        default=FineStatus.NO_FINE
    )
    registrationCard = models.ForeignKey("RegistrationCard", on_delete=models.CASCADE, null=True)
    book = models.ForeignKey("Book", on_delete=models.CASCADE, null=True)
    fine = models.ForeignKey("Fine", on_delete=models.CASCADE, null=True)

    class Meta:
        verbose_name = "Запись в учетной карточке"
        verbose_name_plural = "Записи в учетных карточках"

class Fine(models.Model):
    class FineType(models.TextChoices):
        OVERDUE = 'overdue', 'Нарушение сроков возврата'
        DAMAGE = 'damage', 'Порча книги'
        LOST = 'lost', 'Потеря книги'

    fineType = models.CharField(
        "Тип",
        max_length=20,
        choices=FineType.choices,
        default=FineType.OVERDUE
    )
    amount = models.TextField("Сумма")
    date = models.DateField("Дата")

    class Meta:
        verbose_name = "Штраф"
        verbose_name_plural = "Штрафы"

class Book(models.Model):
    name = models.TextField("Название")
    genre = models.TextField("Жанр")
    date = models.IntegerField("Дата публикации", null=True, blank=True)
    author = models.TextField("Автор")

    class Meta:
        verbose_name = "Книга"
        verbose_name_plural = "Книги"