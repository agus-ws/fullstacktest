import json

import pytest

from graphql_api.transaction.models import Wallet


@pytest.mark.django_db
def test_create_wallet(client_query):
    response = client_query(
        """
        mutation {
            createWallet(name:"john", balance:"100"){
                wallet {
                    id
                    pk
                    name
                    balance
                }
            }
        }
        """,
    )
    content = json.loads(response.content)
    assert content['data']['createWallet']['wallet'] is not None
    pk = content['data']['createWallet']['wallet']['pk']
    assert Wallet.objects.filter(pk=pk).exists()


@pytest.mark.django_db
def test_create_wallet_negative_balance(client_query):
    response = client_query(
        """
        mutation {
            createWallet(name:"john", balance:"-100"){
                wallet {
                    id
                    pk
                    name
                    balance
                }
            }
        }
        """,
    )
    content = json.loads(response.content)
    assert 'errors' in content
    for error in content['errors']:
        if error['path'][0] == 'createWallet':
            assert 'Balance must be a positive number.' in error['message']
