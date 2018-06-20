from django.urls import path

import eve_auth.views


app_name = 'eve_auth'


urlpatterns = [
    path('add/character/', eve_auth.views.StandardLogin.as_view(), name='login'),
    path('add/scraper/', eve_auth.views.ScraperLogin.as_view(), name='login_scraper'),
    path('callback/', eve_auth.views.CallbackView.as_view(), name='callback'),
]
