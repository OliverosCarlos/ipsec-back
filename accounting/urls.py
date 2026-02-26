from django.urls import path

from .views import AccountListCreateView, AccountRetrieveUpdateDestroyView

urlpatterns = [
    path('accounts/', AccountListCreateView.as_view(), name='account-list-create'),
    path('accounts/<int:pk>/', AccountRetrieveUpdateDestroyView.as_view(), name='account-detail'),
]
