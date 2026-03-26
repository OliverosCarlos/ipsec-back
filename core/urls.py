from django.urls import path

from .views import CommentDetail, CommentView, FilteredGroupedCommentView, LoginView, LogoutView, LogoutAllView

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('logout-all/', LogoutAllView.as_view(), name='logout-all'),

    path('comment/',CommentView.as_view(), name='comment'),
    path('comment/<int:pk>',CommentDetail.as_view(), name='comment_details'),
    path('comment/by_content_type_and_object/',FilteredGroupedCommentView.as_view(), name='comment_by_contentType_and_object'),
]
