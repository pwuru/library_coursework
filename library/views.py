from django.shortcuts import render
from django.http import HttpResponse
from django.views import View

from library.models import Book
from library.models import Fine
from library.models import RegistrationCard
from library.models import Record
from library.models import UserProfile
from django.views.generic import TemplateView
from typing import Any

class ShowUserProfilesView(TemplateView):
    def get(self, request, *args, **kwargs):
        userProfiles = UserProfile.objects.all()

        result = ""
        for s in userProfiles:
            result += s.name + "<br>"

        return HttpResponse(result)

class ShowBooksView(TemplateView):
    def get(self, request, *args, **kwargs):
        books = Book.objects.all()

        result = ""
        for s in books:
            result += s.name + "<br>"

        return HttpResponse(result)

class ShowFinesView(TemplateView):
    def get(self, request, *args, **kwargs):
        fines = Fine.objects.all()

        result = ""
        for s in fines:
            result += s.name + "<br>"

        return HttpResponse(result)

class ShowRegistrationCardsView(TemplateView):
    def get(self, request, *args, **kwargs):
        registrationCards = RegistrationCard.objects.all()

        result = ""
        for s in registrationCards:
            result += s.name + "<br>"

        return HttpResponse(result)

class ShowRecordsView(TemplateView):
    def get(self, request, *args, **kwargs):
        records = Record.objects.all()

        result = ""
        for s in records:
            result += s.name + "<br>"

        return HttpResponse(result)

