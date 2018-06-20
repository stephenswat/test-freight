from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import UserPassesTestMixin
from django.views.generic.base import View
from django.shortcuts import redirect, render

from eve_esi import ESI

class StandardLogin(View):
    def get(self, request):
        return redirect(
            ESI.get_security().get_auth_uri(scopes=[
                'esi-ui.open_window.v1'
            ])
        )


class ScraperLogin(UserPassesTestMixin, View):
    def get(self, request):
        return redirect(
            ESI.get_security().get_auth_uri(scopes=[
                'esi-contracts.read_corporation_contracts.v1'
            ])
        )

    def test_func(self):
        # TODO: It may be possible for users to forge this by modifying the
        # redirect URL returned by this view.
        return self.request.user.is_superuser



class CallbackView(View):
    def get(self, request):
        security = ESI.get_security()

        tokens = security.auth(request.GET['code'])
        data = security.verify()

        login(request, authenticate(request, info=data, tokens=tokens))

        return redirect('/')
