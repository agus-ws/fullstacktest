import json

import pytest

from graphql_api.conftest import WALLET1_PK, WALLET2_PK
from graphql_api.transaction.models import Transaction, TransactionRecord, TransactionCategory


CREATE_TRANSACTION_QUERY_TPL = (
    '''
    mutation createTransaction($sourceWalletPk: String!, $targetWalletPk: String!, $amount: Float!, $category: TransactionCategory!) {
        createTransaction(
          sourceWalletPk: $sourceWalletPk
          targetWalletPk: $targetWalletPk
          amount: $amount
          category: $category
        ) {
          transaction {
            id
            pk
            amount
            category
            createdAt
            records {
              edges {
                node {
                  id
                  pk
                  wallet {
                    id
                    pk
                    name
                    balance
                  }
                  debitAmount
                  creditAmount
                }
              }
            }
          }
        }
      }
    '''
)


@pytest.mark.django_db
def test_create_transaction(client_query, init_wallet):
    amount = 50
    category = TransactionCategory.ENGINEERING
    response = client_query(
        CREATE_TRANSACTION_QUERY_TPL,
        op_name='createTransaction',
        variables={'sourceWalletPk': WALLET1_PK, 'targetWalletPk': WALLET2_PK, 'amount': amount, 'category': category}
    )

    content = json.loads(response.content)
    assert 'errors' not in content

    transaction = content['data']['createTransaction']['transaction']
    transaction = Transaction.objects.get(pk=transaction['pk'])
    assert transaction.amount == amount
    assert transaction.category == category

    assert TransactionRecord.objects.filter(transaction_id=transaction.pk,
                                            wallet_id=WALLET1_PK,
                                            debit_amount=amount).exists()
    assert TransactionRecord.objects.filter(transaction_id=transaction.pk,
                                            wallet_id=WALLET2_PK,
                                            credit_amount=amount).exists()


@pytest.mark.django_db
def test_create_transaction_insufficient_funds(client_query, init_wallet):
    amount = 101
    category = TransactionCategory.ENGINEERING
    response = client_query(
        CREATE_TRANSACTION_QUERY_TPL,
        op_name='createTransaction',
        variables={'sourceWalletPk': WALLET1_PK, 'targetWalletPk': WALLET2_PK, 'amount': amount, 'category': category}
    )

    content = json.loads(response.content)
    assert 'errors' in content

    for error in content['errors']:
        if error['path'][0] == 'createTransaction':
            assert 'insufficient funds' in error['message']


@pytest.mark.django_db
def test_create_transaction_same_wallet(client_query, init_wallet):
    amount = 50
    category = TransactionCategory.ENGINEERING
    response = client_query(
        CREATE_TRANSACTION_QUERY_TPL,
        op_name='createTransaction',
        variables={'sourceWalletPk': WALLET1_PK, 'targetWalletPk': WALLET1_PK, 'amount': amount, 'category': category}
    )

    content = json.loads(response.content)
    assert 'errors' in content

    for error in content['errors']:
        if error['path'][0] == 'createTransaction':
            assert 'source_wallet_pk and target_wallet_pk must be different.' in error['message']


@pytest.mark.django_db
def test_create_transaction_negative_amount(client_query, init_wallet):
    amount = -50
    category = TransactionCategory.ENGINEERING
    response = client_query(
        CREATE_TRANSACTION_QUERY_TPL,
        op_name='createTransaction',
        variables={'sourceWalletPk': WALLET1_PK, 'targetWalletPk': WALLET2_PK, 'amount': amount, 'category': category}
    )

    content = json.loads(response.content)
    assert 'errors' in content

    for error in content['errors']:
        if error['path'][0] == 'createTransaction':
            assert 'Amount must be a positive number.' in error['message']
