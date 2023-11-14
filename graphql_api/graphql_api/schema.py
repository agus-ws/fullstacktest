import graphene
from graphene_django.debug import DjangoDebug

from graphql_api.transaction.schema import TransactionQueries, TransactionMutation
from graphql_api.wallet.schema import WalletQueries, WalletMutation


class Query(TransactionQueries, WalletQueries, graphene.ObjectType):
    debug = graphene.Field(DjangoDebug, name="_debug")

class Mutation(TransactionMutation, WalletMutation, graphene.ObjectType):
    debug = graphene.Field(DjangoDebug, name="_debug")


schema = graphene.Schema(query=Query, mutation=Mutation)
