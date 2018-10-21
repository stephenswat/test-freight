import datetime

from django.shortcuts import render
from django.views.generic.base import View, TemplateView
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.db.models import Count, Sum, Avg, Q, F, Subquery, OuterRef, ExpressionWrapper, fields
from django.db.models.functions import Coalesce, Greatest
from django.conf import settings

from freight.models import Route, Contract, Entity


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
            .annotate(route_price_per_m3=Coalesce(
                Subquery(
                    Route.objects.filter(
                        start=OuterRef('start_location'),
                        end=OuterRef('end_location')
                    ).values('price_per_m3')
                ),
                -1
            ))
            .annotate(suggested_reward=(
                Greatest(
                    5000000.0,
                    F('route_price_per_m3') * F('volume') + F('collateral') * 0.01,
                    output_field=fields.FloatField()
                )
            ))
        )
        return context


class CalculatorView(TemplateView):
    template_name = 'freight/calculator.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['routes'] = Route.objects.order_by('start', 'end')
        context['parameters'] = settings.FREIGHT_PARAMETERS
        return context


class LeaderboardView(View):
    def get(self, request):
        query = (
            Entity.objects
            .filter(accepted_contracts__status=Contract.STATUS_FINISHED)
            .annotate(contracts_completed=Count(
                'accepted_contracts',
            ))
            .filter(contracts_completed__gt=10)
            .annotate(volume_moved=Sum(
                'accepted_contracts__volume',
            ))
            # .annotate(average_ttc=Avg(
            #     Subquery(
            #         Contract.objects
            #         .filter(
            #             status=Contract.STATUS_FINISHED,
            #             acceptor=OuterRef('id')
            #         )
            #         .annotate(
            #             ttc=ExpressionWrapper(
            #                 F('date_completed') - F('date_accepted'),
            #                 output_field=fields.DurationField()
            #             )
            #         )
            #         .values('ttc')
            #     ),
            #     output_field=fields.DurationField()
            # ))
        )

        return render(
            request,
            'freight/leaderboard.html',
            context={
                'ranking_completed': query.order_by('-contracts_completed')[:5],
                'ranking_volume': query.order_by('-volume_moved')[:5],
                # 'ranking_ttc': query.order_by('average_ttc')[:5],
            }
        )


@method_decorator(csrf_exempt, name='dispatch')
class IngameContractView(View):
    def post(self, request, cid):
        for char in request.user.character_set.filter(scope_open_window=True):
            char.open_contract(cid)
        return HttpResponse(status=204)
