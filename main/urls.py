from django.urls import path
from .views import index, other_page, BbLoginView, profile, BbLogoutView, ProfileEditView, PasswordEditView, \
    RegisterDoneView, RegisterView, user_activate, ProfileDeleteView, ProfilePasswordResetView, \
    ProfilePasswordResetDoneView, ProfilePasswordResetConfirmView, ProfilePasswordResetCompleteView, rubric_bbs, \
    bb_detail, profile_bb_detail, profile_bb_add, profile_bb_edit, profile_bb_delete, comment_delete

app_name = 'main'

urlpatterns = [
    path('<int:rubric_pk>/<int:pk>/', bb_detail, name='bb_detail'),
    path('<int:pk>/', rubric_bbs, name='rubric_bbs'),
    path('comment_delete/<int:pk>/', comment_delete, name='comment_delete'),

    path('<str:page>/', other_page, name='other'),
    path('accounts/login/', BbLoginView.as_view(), name='login'),
    path('accounts/logout/', BbLogoutView.as_view(), name='logout'),
    path('accounts/register/done/', RegisterDoneView.as_view(), name='register_done'),
    path('accounts/register/', RegisterView.as_view(), name='register'),
    path('accounts/activate/<str:sign>/', user_activate, name='activate'),

    path('accounts/password_reset/done/', ProfilePasswordResetDoneView.as_view(), name='password_reset_done'),
    path('accounts/password_reset/', ProfilePasswordResetView.as_view(), name='password_reset'),
    path('accounts/reset/<uidb64>/<token>/', ProfilePasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('accounts/reset/done/', ProfilePasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('accounts/password/edit/', PasswordEditView.as_view(), name='password_edit'),

    path('accounts/profile/<int:pk>/', profile_bb_detail, name='profile_bb_detail'),
    path('accounts/profile/edit/<int:pk>', profile_bb_edit, name='profile_bb_edit'),
    path('accounts/profile/delete/<int:pk>', profile_bb_delete, name='profile_bb_delete'),
    path('accounts/profile/add/', profile_bb_add, name='profile_bb_add'),
    path('accounts/profile/', profile, name='profile'),
    path('accounts/profile/edit/', ProfileEditView.as_view(), name='profile_edit'),
    path('accounts/profile/delete/', ProfileDeleteView.as_view(), name='profile_delete'),

    path('', index, name='index'),
]
