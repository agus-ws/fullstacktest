import uuid

from django.core.exceptions import ValidationError
from django.db import models, transaction as db_transaction
from django.db.models import F
from django.utils import timezone

from graphql_api.wallet.models import Wallet


class TransactionCategory(models.TextChoices):
    MARKETING = ("MARKETING", "MARKETING")
    ENGINEERING = ("ENGINEERING", "ENGINEERING")
    GROWTH = ("GROWTH", "GROWTH")
    PRODUCT = ("PRODUCT", "PRODUCT")


class Transaction(models.Model):
    ''' Parent class for every transaction record. '''
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    amount = models.FloatField(null=False, blank=False, default=0)
    category = models.CharField(
        max_length=100,
        null=False,
        blank=False,
        choices=TransactionCategory.choices,
    )
    created_at = models.DateTimeField(null=True, blank=True, default=None)

    @classmethod
    def create_transaction(cls, source_wallet_pk, target_wallet_pk, amount, category):
        if source_wallet_pk == target_wallet_pk:
            raise ValidationError({
                '__all__': 'source_wallet_pk and target_wallet_pk must be different.',
            })

        if amount < 0:
            raise ValidationError({
                'amount': 'Amount must be a positive number.',
            })
        
        if category not in TransactionCategory:
            raise ValidationError({
                'category': 'Invalid category.',
            })

        with db_transaction.atomic():
            # Acquiring lock on both source wallet and target wallet.
            # Sqlite doesn't support row locking mechanism, only works in fully featured DBMS (Postgres, MySql, etc).
            wallets = Wallet.objects.select_for_update().filter(id__in=[source_wallet_pk, target_wallet_pk])
            source_wallet = None
            target_wallet = None
            for wallet in wallets:
                if wallet.id == source_wallet_pk:
                    source_wallet = wallet
                elif wallet.id == target_wallet_pk:
                    target_wallet = wallet
            
            if source_wallet is None:
                raise ValidationError({
                    'source_wallet_pk': f'Wallet with pk = {source_wallet_pk} is not found.',
                })
            
            if target_wallet is None:
                raise ValidationError({
                    'target_wallet_pk': f'Wallet with pk = {target_wallet} is not found.',
                })

            if source_wallet.balance < amount:
                raise ValidationError({
                    'source_wallet_pk': f'Source wallet has insufficient funds, current balance is {source_wallet.balance} required amount is {amount}.',
                })

            now = timezone.now()
            transaction = Transaction.objects.create(amount=amount, category=category, created_at=now)

            source_wallet.balance = F("balance") - amount
            source_wallet.updated_at = now
            source_wallet.save(update_fields=['balance', 'updated_at'])
            TransactionRecord.objects.create(transaction=transaction, wallet=source_wallet, debit_amount=amount)

            target_wallet.balance = F("balance") + amount
            target_wallet.updated_at = now
            target_wallet.save(update_fields=['balance', 'updated_at'])
            TransactionRecord.objects.create(transaction=transaction, wallet=target_wallet, credit_amount=amount)

        return transaction


class TransactionRecord(models.Model):
    ''' Transaction record maps to debited/credited wallet. '''
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    transaction = models.ForeignKey(Transaction, related_name='records', on_delete=models.CASCADE)
    wallet = models.ForeignKey('wallet.Wallet', related_name='transaction_records', on_delete=models.CASCADE)
    debit_amount = models.FloatField(default=0)
    credit_amount = models.FloatField(default=0)
