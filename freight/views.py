from django.shortcuts import render
from django.views.generic.base import View, TemplateView
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

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


@method_decorator(csrf_exempt, name='dispatch')
class IngameContractView(View):
    def post(self, request, cid):
        for char in request.user.character_set.filter(scope_open_window=True):
            char.open_contract(cid)
        return HttpResponse(status=204)
