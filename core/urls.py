from django.urls import path

from .views import (
    AccountPlatformSettingsByAccountView,
    AccountPlatformSettingsMeView,
    CommentDetail, CommentView, FilteredGroupedCommentView,
    LoginView, LogoutView, LogoutAllView,
    EntityModelListView, EntityModelDetailView, EntityModelByCodeView,
)

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('logout-all/', LogoutAllView.as_view(), name='logout-all'),

    path('comment/', CommentView.as_view(), name='comment'),
    path('comment/<int:pk>', CommentDetail.as_view(), name='comment_details'),
    path('comment/by_content_type_and_object/', FilteredGroupedCommentView.as_view(), name='comment_by_contentType_and_object'),

    # EntityModel
    path('entity-models/', EntityModelListView.as_view(), name='entity-model-list'),
    path('entity-models/<int:pk>/', EntityModelDetailView.as_view(), name='entity-model-detail'),
    path('entity-models/by-code/<slug:code>/', EntityModelByCodeView.as_view(), name='entity-model-by-code'),

    # Account platform settings
    path('account-settings/me/', AccountPlatformSettingsMeView.as_view(), name='account-settings-me'),
    path('account-settings/account/<int:account_id>/', AccountPlatformSettingsByAccountView.as_view(), name='account-settings-by-account'),
]
