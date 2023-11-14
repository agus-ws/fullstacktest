import datetime

from django.utils import timezone

import graphene
from graphene import Node
from graphene_django import DjangoListField
from graphene_django.filter import DjangoFilterConnectionField
from graphene_django.types import DjangoObjectType

from graphql_api.transaction.models import TransactionRecord
from graphql_api.transaction.schema import TransactionRecordNode
from .filters import WalletFilter
from .models import Wallet



class WalletNode(DjangoObjectType):
    class Meta:
        model = Wallet
        interfaces = (Node,)
        fields = ('id', 'name', 'balance', 'updated_at', 'created_at', 'transaction_records',)
        filterset_class = WalletFilter

    pk = graphene.String()
    monthly_transactions = DjangoListField(TransactionRecordNode,
                                           month=graphene.Int(required=True),
                                           year=graphene.Int(required=True))

    def resolve_monthly_transactions(root, info, month, year):
        return TransactionRecord.objects.filter(wallet=root.pk,
                                                transaction__created_at__month=month,
                                                transaction__created_at__year=year
                                                ).order_by("-transaction__created_at")

class WalletQueries(graphene.ObjectType):
    wallet = Node.Field(WalletNode)
    wallets = DjangoFilterConnectionField(WalletNode)
    dormant_wallets = DjangoFilterConnectionField(WalletNode)

    def resolve_wallets(root, info, **kwargs):
        return Wallet.objects.all().prefetch_related('transaction_records__transaction').order_by("-updated_at")

    def resolve_dormant_wallets(root, info, **kwargs):
        ''' Wallet is considered dormant after 1 year of inactivity. '''
        one_year_ago = timezone.now() - datetime.timedelta(days=365)
        return Wallet.objects.filter(updated_at__lt=one_year_ago).prefetch_related('transaction_records__transaction').order_by("-updated_at")


class CreateWallet(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        balance = graphene.Decimal()

    wallet = graphene.Field(WalletNode)

    @classmethod
    def mutate(cls, root, info, name, balance):
        wallet = Wallet.create_wallet(name=name, balance=balance)
        return cls(wallet=wallet)


class WalletMutation(graphene.ObjectType):
    create_wallet = CreateWallet.Field()
