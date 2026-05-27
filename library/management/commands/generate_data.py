from django.core.management.base import BaseCommand

from faker import Faker
import random

from library.models import Book, Fine, UserProfile, RegistrationCard, Record
from django.contrib.auth.models import User


class Command(BaseCommand):
    def handle(self, *args, **options):
        fake = Faker(['ru_RU'])
        genres = ['Роман', 'Детектив', 'Фантастика', 'Поэзия', 'Драма', 'Приключения', 'Комедия', 'Фэнтези']
        for _ in range(1000):
            Book.objects.create(
                name=fake.word(),
                genre=random.choice(genres),
                date=fake.year(),
                author=fake.name()
            )

        fine_types = ['overdue', 'damage', 'lost']
        for _ in range(1000):
            Fine.objects.create(
                fineType=random.choice(fine_types),
                amount=random.randint(100, 5000),
                date=fake.date()
            )

        user_types = ['admin', 'employee', 'reader']
        for i in range(10):
            username = f'user_{i+1}'
            user, created = User.objects.get_or_create(
                username=username,
                defaults={'password': '1234'}
            )
            UserProfile.objects.get_or_create(
                user=user,
                defaults={
                    'name': fake.name(),
                    'phone': fake.phone_number(),
                    'type': random.choice(user_types)
                }
            )

        for user in User.objects.all():
            RegistrationCard.objects.get_or_create(user=user)

        cards = list(RegistrationCard.objects.all())
        books = list(Book.objects.all())
        fines = list(Fine.objects.all())

        for _ in range(1000):
            issue = fake.date_object()
            expected = fake.date_between(start_date=issue, end_date='+30d')
            actual = random.choice([None, fake.date_between(start_date=issue, end_date=expected)])
            
            if actual and actual <= expected:
                fine_status = 'no_fine'
                fine_obj = None
            elif actual and actual > expected:
                fine_status = random.choice(['unpaid', 'paid'])
                fine_obj = random.choice(fines)
            else:
                fine_status = random.choice(['unpaid', 'paid'])
                fine_obj = random.choice(fines)
            
            Record.objects.create(
                book_issue_date=issue,
                expected_book_accept_date=expected,
                book_accept_date=actual,
                fine_status=fine_status,
                registrationCard=random.choice(cards),
                book=random.choice(books),
                fine=fine_obj
            )