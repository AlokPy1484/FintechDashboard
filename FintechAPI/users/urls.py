from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views

urlpatterns = [ 

    #Auth Endpoints
    path('auth/register/', views.RegisterView.as_view(), name='register'),
    path('auth/login/', TokenObtainPairView.as_view(),name='login'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='refresh_token'),
    path('auth/logout/', views.LogoutView.as_view(), name='logout'),
    path('auth/me/', views.MeView.as_view(), name='me'),
    path('auth/change-password/', views.ChangePasswordView.as_view(), name='change_password'),


    #Admin's Endpoint
    path('', views.UserListCreateView.as_view(), name='user_list_create'),
    path('<int:pk>/', views.UserDetailView.as_view(), name='user_details'),
    path('<int:pk>/status/', views.UserSatusView.as_view(), name='user_status'),
]




#User Model Endpoints

# OpenAPI Swagger documentation at GET  /api/docs/

# POST  /api/users/auth/register/         → Create a new user
# POST  /api/users/auth/login/            → Get access + refresh tokens
# GET   /api/users/auth/me/               → View profile (send Bearer token)
# PATCH /api/users/auth/change-password/  → Change password
# POST  /api/users/auth/logout/           → Blacklist refresh token

# GET   /api/users/                       → List all users (Admin only)
# POST  /api/users/                       → Create user (Admin only)
# GET   /api/users/<id>/                  → Get user detail (Admin only)
# PATCH /api/users/<id>/                  → Update user (Admin only)
# DELETE /api/users/<id>/                 → Delete user (Admin only)
# PATCH /api/users/<id>/status/           → Activate/deactivate (Admin only)