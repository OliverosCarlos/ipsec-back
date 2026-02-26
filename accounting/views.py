from rest_framework import generics

from .models import Account
from .serializers import AccountSerializer


class AccountListCreateView(generics.ListCreateAPIView):
	queryset = Account.objects.all()
	serializer_class = AccountSerializer
	search_fields = ['name', 'code']
	filterset_fields = ['account_type', 'is_active']


class AccountRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
	queryset = Account.objects.all()
	serializer_class = AccountSerializer
