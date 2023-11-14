import graphene
from graphene import Node
from graphene_django.filter import DjangoFilterConnectionField
from graphene_django.types import DjangoObjectType

from .filters import TransactionFilter
from .models import Transaction, TransactionRecord, TransactionCategory

TransactionCategoryEnum = graphene.Enum.from_enum(TransactionCategory)


class TransactionNode(DjangoObjectType):
    class Meta:
        model = Transaction
        interfaces = (Node,)
        fields = ('id', 'amount', 'category', 'records', 'created_at',)
        filterset_class = TransactionFilter
        convert_choices_to_enum = False

    pk = graphene.String()


class TransactionRecordNode(DjangoObjectType):
    class Meta:
        model = TransactionRecord
        interfaces = (Node,)
        fields = ('id', 'transaction', 'wallet', 'debit_amount', 'credit_amount',)
        filter_fields = []

    pk = graphene.String()


class TransactionQueries(graphene.ObjectType):
    transaction = Node.Field(TransactionNode)
    transactions = DjangoFilterConnectionField(TransactionNode)

    transaction_record = Node.Field(TransactionRecordNode)
    transaction_records = DjangoFilterConnectionField(TransactionRecordNode)

    def resolve_transactions(root, info, **kwargs):
        return Transaction.objects.all().order_by("-created_at")
    
    def resolve_transaction_records(root, info):
        return TransactionRecord.objects.all().order_by("-transaction__created_at")


class CreateTransaction(graphene.Mutation):
    class Arguments:
        source_wallet_pk = graphene.String(required=True)
        target_wallet_pk = graphene.String(required=True)
        amount = graphene.Float(required=True)
        category = TransactionCategoryEnum(required=True)

    transaction = graphene.Field(TransactionNode)

    @classmethod
    def mutate(cls, root, info, source_wallet_pk, target_wallet_pk, amount, category):
        transaction = Transaction.create_transaction(
            source_wallet_pk=source_wallet_pk, target_wallet_pk=target_wallet_pk,
            amount=amount, category=category
        )
        return cls(transaction=transaction)


class TransactionMutation(graphene.ObjectType):
    create_transaction = CreateTransaction.Field()
