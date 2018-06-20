from django.shortcuts import render
from django.views.generic.base import View


class ContractListView(View):
    def get(self, request):
        return render(request, 'freight/contract_list.html')


class CalculatorView(View):
    def get(self, request):
        return render(request, 'index.html')
