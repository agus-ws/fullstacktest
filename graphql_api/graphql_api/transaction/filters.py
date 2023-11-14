import django_filters

from .models import Transaction


class TransactionFilter(django_filters.FilterSet):

    class Meta:
        model = Transaction
        fields = {
            'amount': ['exact', 'lt', 'gt'],
            'category': ['exact'],
            'created_at': ['lt', 'gt'],
        }
