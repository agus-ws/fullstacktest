from graphene_django.utils.testing import graphql_query
import pytest

from graphql_api.wallet.models import Wallet

WALLET1_PK = '0123456789'
WALLET2_PK = '1234567890'


@pytest.fixture
def client_query(client):
    def func(*args, **kwargs):
        return graphql_query(*args, **kwargs, client=client, graphql_url='/graphql')

    return func


@pytest.fixture
def init_wallet(db):
    Wallet.objects.create(pk=WALLET1_PK, name='john', balance=100)
    Wallet.objects.create(pk=WALLET2_PK, name='jane', balance=100)
