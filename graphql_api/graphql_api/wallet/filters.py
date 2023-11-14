import django_filters

from .models import Wallet


class WalletFilter(django_filters.FilterSet):

    class Meta:
        model = Wallet
        fields = {
            'name': ['exact', 'icontains'],
            'balance': ['exact', 'lt', 'gt'],
            'updated_at': ['lt', 'gt'],
            'created_at': ['lt', 'gt'],
        }
