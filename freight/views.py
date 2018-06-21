import datetime

from django.shortcuts import render
from django.views.generic.base import View, TemplateView
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.db.models import Count, Sum, Avg, Q, F, Subquery, OuterRef, ExpressionWrapper, fields

from freight.models import Route, Contract, Character


class ContractListView(TemplateView):
    template_name = 'freight/contract_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['contracts'] = (
            Contract.objects
            .filter(
                status=Contract.STATUS_OUTSTANDING,
                date_expired__gt=datetime.datetime.now()
            )
        )
        return context


class CalculatorView(TemplateView):
    template_name = 'freight/calculator.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['routes'] = Route.objects.all()
        return context


class LeaderboardView(View):
    def get(self, request):
        query = (
            Character.objects
            .filter(accepted_contracts__status=Contract.STATUS_FINISHED)
            .annotate(contracts_completed=Count(
                'accepted_contracts',
            ))
            .filter(contracts_completed__gt=10)
            .annotate(volume_moved=Sum(
                'accepted_contracts__volume',
            ))
            .annotate(average_ttc=Avg(
                Subquery(
                    Contract.objects
                    .filter(
                        status=Contract.STATUS_FINISHED,
                        acceptor=OuterRef('id')
                    )
                    .annotate(
                        ttc=ExpressionWrapper(
                            F('date_completed') - F('date_accepted'),
                            output_field=fields.DurationField()
                        )
                    )
                    .values('ttc')
                ),
                output_field=fields.DurationField()
            ))
        )

        return render(
            request,
            'freight/leaderboard.html',
            context={
                'ranking_completed': query.order_by('-contracts_completed')[:5],
                'ranking_volume': query.order_by('-volume_moved')[:5],
                'ranking_ttc': query.order_by('average_ttc')[:5],
            }
        )


@method_decorator(csrf_exempt, name='dispatch')
class IngameContractView(View):
    def post(self, request, cid):
        for char in request.user.character_set.filter(scope_open_window=True):
            char.open_contract(cid)
        return HttpResponse(status=204)
