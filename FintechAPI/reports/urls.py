from django.urls import path
from .views import SummaryReportView, ByTypeReportView, MonthlyReportView

urlpatterns = [
    path('summary/', SummaryReportView.as_view(), name='report-summary'),
    path('by-type/', ByTypeReportView.as_view(), name='report-by-type'),
    path('monthly/', MonthlyReportView.as_view(), name='report-monthly'),
]
