from django.urls import path, include
from rest_framework.routers import DefaultRouter
from users.views import UserDetailView
from records.views import FinancialRecordViewSet
from django.contrib import admin
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView


router = DefaultRouter()
router.register(r'financial-records', FinancialRecordViewSet, basename='financial-record')


urlpatterns = [
    path('', include(router.urls)),
    path('users/', UserDetailView.as_view()),
    path('reports/', include('reports.urls')),
]
