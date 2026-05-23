from django.test import TestCase
from rest_framework.test import APIClient
from model_bakery import baker

from library.models import Book, Fine, RegistrationCard, Record, UserProfile


class BookViewSetTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_get_list(self):
        book = Book.objects.create(
            name="Тест_книга",
            date="1950",
            genre="Роман",
            author="Тест_автор"
        )

        r = self.client.get('/api/books/')
        data = r.json()

        assert book.name == data[0]['name']
        assert book.id == data[0]['id']
        assert book.date == data[0]['date']
        assert book.genre == data[0]['genre']
        assert book.author == data[0]['author']

    def test_create_book(self):
        data = {
            "name": "Книга1",
            "genre": "Фантастика",
            "date": "2020",
            "author": "Автор1"
        }
        r = self.client.post('/api/books/', data, format='json')

        assert r.status_code == 201

        books = Book.objects.all()
        assert books.count() == 1
        assert books[0].name == "Книга1"

    def test_update_book(self):
        books = baker.make("Book", 10)
        book = books[2]

        r = self.client.get(f'/api/books/{book.id}/')
        data = r.json()
        assert data['name'] == book.name

        r = self.client.put(f'/api/books/{book.id}/', {
            "name": "Новая_книга",
            "genre": book.genre,
            "date": book.date,
            "author": book.author
        }, format='json')
        assert r.status_code == 200

        r = self.client.get(f'/api/books/{book.id}/')
        data = r.json()
        assert data['name'] == "Новая_книга"

        book.refresh_from_db()
        assert data['name'] == book.name

    def test_delete_book(self):
        books = baker.make("Book", 10)
        r = self.client.get('/api/books/')
        data = r.json()
        assert len(data) == 10

        book_id_to_delete = books[3].id
        self.client.delete(f'/api/books/{book_id_to_delete}/')

        r = self.client.get('/api/books/')
        data = r.json()
        assert len(data) == 9

        assert book_id_to_delete not in [i['id'] for i in data]


class FineViewSetTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_get_list(self):
        fine = Fine.objects.create(
            fineType="Нарушение сроков возврата",
            amount="500",
            date="2024-01-15"
        )

        r = self.client.get('/api/fines/')
        data = r.json()

        assert fine.fineType == data[0]['fineType']
        assert fine.id == data[0]['id']
        assert fine.amount == data[0]['amount']
        assert fine.date == data[0]['date']

    def test_create_fine(self):
        data = {
            "fineType": "Порча книги",
            "amount": "1000",
            "date": "2024-02-20"
        }
        r = self.client.post('/api/fines/', data, format='json')

        assert r.status_code == 201

        fines = Fine.objects.all()
        assert fines.count() == 1
        assert fines[0].fineType == "Порча книги"

    def test_update_fine(self):
        fines = baker.make("Fine", 10)
        fine = fines[2]

        r = self.client.get(f'/api/fines/{fine.id}/')
        data = r.json()
        assert data['fineType'] == fine.fineType

        r = self.client.put(f'/api/fines/{fine.id}/', {
            "fineType": "Нарушение сроков возврата",
            "amount": fine.amount,
            "date": fine.date
        }, format='json')
        assert r.status_code == 200

        r = self.client.get(f'/api/fines/{fine.id}/')
        data = r.json()
        assert data['fineType'] == "Нарушение сроков возврата"

        fine.refresh_from_db()
        assert data['fineType'] == fine.fineType

    def test_delete_fine(self):
        fines = baker.make("Fine", 10)
        r = self.client.get('/api/fines/')
        data = r.json()
        assert len(data) == 10

        fine_id_to_delete = fines[3].id
        self.client.delete(f'/api/fines/{fine_id_to_delete}/')

        r = self.client.get('/api/fines/')
        data = r.json()
        assert len(data) == 9

        assert fine_id_to_delete not in [i['id'] for i in data]


class RegistrationCardViewSetTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_get_list(self):
        registration_card = RegistrationCard.objects.create(
            photo="test_photo.jpg",
            user=None
        )

        r = self.client.get('/api/registrationCards/')
        data = r.json()

        assert registration_card.id == data[0]['id']
        assert "test_photo.jpg" in data[0]['photo']

    def test_create_registration_card(self):
        data = {
            "photo": "new_photo.jpg",
            "user": None
        }
        r = self.client.post('/api/registrationCards/', data, format='json')
        assert r.status_code == 201

    def test_update_registration_card(self):
        cards = baker.make("RegistrationCard", 10)
        card = cards[2]

        r = self.client.get(f'/api/registrationCards/{card.id}/')
        data = r.json()
        assert data['photo'] == card.photo

        r = self.client.put(f'/api/registrationCards/{card.id}/', {
            "photo": "updated_photo.jpg",
            "user": card.user
        }, format='json')
        assert r.status_code == 200

        r = self.client.get(f'/api/registrationCards/{card.id}/')
        data = r.json()
        assert "updated_photo.jpg" in data['photo']

        card.refresh_from_db()
        assert "updated_photo.jpg" in str(card.photo)

    def test_delete_registration_card(self):
        cards = baker.make("RegistrationCard", 10)
        r = self.client.get('/api/registrationCards/')
        data = r.json()
        assert len(data) == 10

        card_id_to_delete = cards[3].id
        self.client.delete(f'/api/registrationCards/{card_id_to_delete}/')

        r = self.client.get('/api/registrationCards/')
        data = r.json()
        assert len(data) == 9

        assert card_id_to_delete not in [i['id'] for i in data]


class RecordViewSetTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.registration_card = RegistrationCard.objects.create(photo="card.jpg")
        self.book = Book.objects.create(
            name="Тест_книга",
            genre="Роман",
            date="2020",
            author="Тест_автор"
        )
        self.fine = Fine.objects.create(
            fineType="Нарушение сроков возврата",
            amount="500",
            date="2024-01-01"
        )

    def test_get_list(self):
        record = Record.objects.create(
            book_issue_date="2024-01-01",
            expected_book_accept_date="2024-01-15",
            book_accept_date="2024-01-14",
            fine_status="Нет",
            registrationCard=self.registration_card,
            book=self.book,
            fine=self.fine
        )

        r = self.client.get('/api/records/')
        data = r.json()

        assert record.book_issue_date == data[0]['book_issue_date']
        assert record.id == data[0]['id']
        assert record.expected_book_accept_date == data[0]['expected_book_accept_date']
        assert record.book_accept_date == data[0]['book_accept_date']
        assert record.fine_status == data[0]['fine_status']

    def test_create_record(self):
        data = {
            "book_issue_date": "2024-03-01",
            "expected_book_accept_date": "2024-03-15",
            "book_accept_date": "",
            "fine_status": "Ожидается",
            "registrationCard": self.registration_card.id,
            "book": self.book.id,
            "fine": self.fine.id
        }
        r = self.client.post('/api/records/', data, format='json')
        assert r.status_code == 201

        records = Record.objects.all()
        assert records.count() == 1
        assert records[0].book_issue_date == "2024-03-01"

    def test_update_record(self):
        record = Record.objects.create(
            book_issue_date="2024-01-01",
            expected_book_accept_date="2024-01-15",
            book_accept_date="",
            fine_status="Нет",
            registrationCard=self.registration_card,
            book=self.book,
            fine=self.fine
        )

        r = self.client.get(f'/api/records/{record.id}/')
        data = r.json()
        assert data['fine_status'] == "Нет"

        r = self.client.put(f'/api/records/{record.id}/', {
            "book_issue_date": record.book_issue_date,
            "expected_book_accept_date": record.expected_book_accept_date,
            "book_accept_date": record.book_accept_date,
            "fine_status": "Оплачен",
            "registrationCard": record.registrationCard.id,
            "book": record.book.id,
            "fine": record.fine.id
        }, format='json')
        assert r.status_code == 200

        r = self.client.get(f'/api/records/{record.id}/')
        data = r.json()
        assert data['fine_status'] == "Оплачен"

        record.refresh_from_db()
        assert record.fine_status == "Оплачен"

    def test_delete_record(self):
        records = baker.make("Record", 10)
        r = self.client.get('/api/records/')
        data = r.json()
        assert len(data) == 10

        record_id_to_delete = records[3].id
        self.client.delete(f'/api/records/{record_id_to_delete}/')

        r = self.client.get('/api/records/')
        data = r.json()
        assert len(data) == 9

        assert record_id_to_delete not in [i['id'] for i in data]


class UserProfileViewSetTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_get_list(self):
        user_profile = UserProfile.objects.create(
            name="Тест_пользователь",
            phone="+79991234567",
            user=None
        )

        r = self.client.get('/api/userProfiles/')
        data = r.json()

        assert user_profile.name == data[0]['name']
        assert user_profile.id == data[0]['id']
        assert user_profile.phone == data[0]['phone']

    def test_create_user_profile(self):
        data = {
            "name": "Новый_пользователь",
            "phone": "89501234567",
            "user": None
        }
        r = self.client.post('/api/userProfiles/', data, format='json')
        assert r.status_code == 201

        profiles = UserProfile.objects.all()
        assert profiles.count() == 1
        assert profiles[0].name == "Новый_пользователь"

    def test_update_user_profile(self):
        profiles = baker.make("UserProfile", 10)
        profile = profiles[2]

        r = self.client.get(f'/api/userProfiles/{profile.id}/')
        data = r.json()
        assert data['name'] == profile.name

        r = self.client.put(f'/api/userProfiles/{profile.id}/', {
            "name": "Имя1",
            "phone": profile.phone,
            "user": profile.user
        }, format='json')
        assert r.status_code == 200

        r = self.client.get(f'/api/userProfiles/{profile.id}/')
        data = r.json()
        assert data['name'] == "Имя1"

        profile.refresh_from_db()
        assert data['name'] == profile.name

    def test_delete_user_profile(self):
        profiles = baker.make("UserProfile", 10)
        r = self.client.get('/api/userProfiles/')
        data = r.json()
        assert len(data) == 10

        profile_id_to_delete = profiles[3].id
        self.client.delete(f'/api/userProfiles/{profile_id_to_delete}/')

        r = self.client.get('/api/userProfiles/')
        data = r.json()
        assert len(data) == 9

        assert profile_id_to_delete not in [i['id'] for i in data]