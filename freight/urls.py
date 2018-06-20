from django.urls import path

import freight.views


app_name = 'freight'


urlpatterns = [
    path('', freight.views.ContractListView.as_view(), name='contract_list'),
    path('calculator/', freight.views.CalculatorView.as_view(), name='calculator'),
]
