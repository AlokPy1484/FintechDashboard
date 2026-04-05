from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FinancialRecordViewSet

router = DefaultRouter()
router.register(r'financial-records', FinancialRecordViewSet, basename='financial-record')

urlpatterns = [
    path('', include(router.urls)),
]