from django.shortcuts import render
from django.views.generic.base import View, TemplateView

from freight.models import Route


class ContractListView(View):
    def get(self, request):
        return render(request, 'freight/contract_list.html')


class CalculatorView(TemplateView):
    template_name = 'freight/calculator.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['routes'] = Route.objects.all()
        return context
