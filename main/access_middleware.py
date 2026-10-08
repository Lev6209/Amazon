import os
import secrets

from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse


class SiteAccessMiddleware:
    COOKIE_NAME = 'amazon_site_access'

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        password = os.environ.get('SITE_ACCESS_PASSWORD')

        # Если пароль не задан — защита отключена.
        # Поэтому локальная разработка продолжит работать как раньше.
        if not password:
            return self.get_response(request)

        access_url = reverse('main:site_access')

        # Саму страницу ввода пароля пропускаем.
        if request.path == access_url:
            return self.get_response(request)

        # Статические файлы должны загружаться и до авторизации.
        if request.path.startswith('/static/'):
            return self.get_response(request)

        cookie = request.COOKIES.get(self.COOKIE_NAME)

        if cookie and secrets.compare_digest(cookie, password):
            return self.get_response(request)

        return redirect('main:site_access')