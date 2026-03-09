from django.urls import path

from .views import (
    PartnerListCreateView, PartnerRetrieveUpdateDestroyView,
    PartnerRoleListCreateView, PartnerRoleRetrieveUpdateDestroyView,
    PartnerAddressListCreateView, PartnerAddressRetrieveUpdateDestroyView,
    PartnerContactListCreateView, PartnerContactRetrieveUpdateDestroyView,
    PartnerContactFullRetrieveView,
    PartnerBankAccountListCreateView, PartnerBankAccountRetrieveUpdateDestroyView,
    BankListCreateView, BankRetrieveUpdateDestroyView,
    PersonTitleListCreateView, PersonTitleRetrieveUpdateDestroyView,
    JobPositionListCreateView, JobPositionRetrieveUpdateDestroyView,
)

urlpatterns = [
    # Partners
    path('partners/', PartnerListCreateView.as_view(), name='partner-list-create'),
    path('partners/<int:pk>/', PartnerRetrieveUpdateDestroyView.as_view(), name='partner-detail'),
    path('partner-roles/', PartnerRoleListCreateView.as_view(), name='partner-role-list-create'),
    path('partner-roles/<int:pk>/', PartnerRoleRetrieveUpdateDestroyView.as_view(), name='partner-role-detail'),
    path('partner-addresses/', PartnerAddressListCreateView.as_view(), name='partner-address-list-create'),
    path('partner-addresses/<int:pk>/', PartnerAddressRetrieveUpdateDestroyView.as_view(), name='partner-address-detail'),
    path('partner-contacts/', PartnerContactListCreateView.as_view(), name='partner-contact-list-create'),
    path('partner-contacts/<int:pk>/', PartnerContactRetrieveUpdateDestroyView.as_view(), name='partner-contact-detail'),
    path('partner-contacts/<int:pk>/full/', PartnerContactFullRetrieveView.as_view(), name='partner-contact-full-detail'),
    path('partner-bank-accounts/', PartnerBankAccountListCreateView.as_view(), name='partner-bank-account-list-create'),
    path('partner-bank-accounts/<int:pk>/', PartnerBankAccountRetrieveUpdateDestroyView.as_view(), name='partner-bank-account-detail'),
    path('banks/', BankListCreateView.as_view(), name='bank-list-create'),
    path('banks/<int:pk>/', BankRetrieveUpdateDestroyView.as_view(), name='bank-detail'),
    path('person-titles/', PersonTitleListCreateView.as_view(), name='person-title-list-create'),
    path('person-titles/<int:pk>/', PersonTitleRetrieveUpdateDestroyView.as_view(), name='person-title-detail'),
    path('job-positions/', JobPositionListCreateView.as_view(), name='job-position-list-create'),
    path('job-positions/<int:pk>/', JobPositionRetrieveUpdateDestroyView.as_view(), name='job-position-detail'),
]
