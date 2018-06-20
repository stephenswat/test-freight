from django.shortcuts import render
from django.views.generic.base import View, TemplateView

from freight.models import Route, Contract


class ContractListView(TemplateView):
    template_name = 'freight/contract_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['contracts'] = (
            Contract.objects
            .filter(status=Contract.STATUS_OUTSTANDING)
        )
        return context


class CalculatorView(TemplateView):
    template_name = 'freight/calculator.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['routes'] = Route.objects.all()
        return context
