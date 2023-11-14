from decimal import Decimal
import string

from django.core.exceptions import ValidationError
from django.db import models, transaction, IntegrityError
from django.utils.crypto import get_random_string
from django.utils.translation import gettext_lazy as _
from django.utils.timezone import now


class Wallet(models.Model):
    ACCOUNT_NUMBER_LENGTH = 10

    id = models.CharField(primary_key=True, max_length=ACCOUNT_NUMBER_LENGTH, verbose_name=_('account number'), editable=False)
    name = models.CharField(verbose_name=_('name'), max_length=30)
    # use DecimalField for better numerical precision
    balance = models.DecimalField(verbose_name=_('balance'), default=Decimal("0"), decimal_places=2, max_digits=15)

    updated_at = models.DateTimeField(editable=False, default=now)
    created_at = models.DateTimeField(editable=False, default=now)

    def __str__(self):
        return f'ID: {self.id}, Name: {self.name}, Balance: {self.balance}'

    @classmethod
    def create_wallet(cls, name, balance):
        if balance < 0:
            raise ValidationError({
                'balance': 'Balance must be a positive number.',
            })
    
        with transaction.atomic():
            wallet = cls.objects.create(name=name, balance=balance)

        return wallet

    def save(self, *args, **kwargs):
        if not self.pk:
            while True:
                self.id = get_random_string(Wallet.ACCOUNT_NUMBER_LENGTH, string.digits)
                try:
                    super().save(*args, **kwargs)
                    break
                except IntegrityError as err:
                    pass
        else:
            super().save(*args, **kwargs)
