from django.urls import path

from .views import (
    CompanyView, CompanyDetailView,
    CompanyFullSetupView,
    CompanyAddressDetailView, CompanyAddressListCreateView,
    CompanyContactDetailView, CompanyContactListCreateView,
    CompanyBankAccountDetailView, CompanyBankAccountListCreateView,
    CompanyCertificateDetailView, CompanyCertificateListCreateView,
)

urlpatterns = [
    path('company/', CompanyView.as_view(), name='company'),
    path('company/<uuid:pk>/', CompanyDetailView.as_view(), name='company-detail'),

    path('companies/setup/', CompanyFullSetupView.as_view(), name='company-setup'),

    path('addresses/', CompanyAddressListCreateView.as_view(), name='company-address-list'),
    path('addresses/<uuid:pk>/', CompanyAddressDetailView.as_view(), name='company-address-detail'),

    path('contacts/', CompanyContactListCreateView.as_view(), name='company-contact-list'),
    path('contacts/<uuid:pk>/', CompanyContactDetailView.as_view(), name='company-contact-detail'),

    path('bank-accounts/', CompanyBankAccountListCreateView.as_view(), name='company-bank-list'),
    path('bank-accounts/<uuid:pk>/', CompanyBankAccountDetailView.as_view(), name='company-bank-detail'),

    path('certificates/', CompanyCertificateListCreateView.as_view(), name='company-cert-list'),
    path('certificates/<uuid:pk>/', CompanyCertificateDetailView.as_view(), name='company-cert-detail'),
]
