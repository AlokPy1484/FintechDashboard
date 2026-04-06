from datetime import datetime
from decimal import Decimal
from collections import defaultdict

from django.db.models import Sum, Count
from django.db.models.functions import TruncMonth
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from records.models import FinancialRecord
from users.permissions import IsAdmin, IsAnalystOrAbove, IsViewer
from .serializers import (
    SummaryReportSerializer,
    ByTypeReportSerializer,
    MonthlyReportSerializer,
)


class ReportBaseView(APIView):
    """
    Base view providing shared query-param parsing / filtering logic
    for all report endpoints.
    """

    def get_filtered_queryset(self, request):
        """
        Apply date-range and created_by filters to the FinancialRecord
        queryset. Returns (queryset, error_response).
        If error_response is not None, the caller should return it immediately.
        """
        qs = FinancialRecord.objects.all()
        errors = {}

        # --- Date range filters ---
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        if start_date:
            try:
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            except ValueError:
                errors['start_date'] = 'Invalid date format. Use YYYY-MM-DD.'

        if end_date:
            try:
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            except ValueError:
                errors['end_date'] = 'Invalid date format. Use YYYY-MM-DD.'

        if errors:
            return None, Response(errors, status=status.HTTP_400_BAD_REQUEST)

        if start_date and end_date:
            if start_date > end_date:
                return None, Response(
                    {'detail': 'start_date must be before or equal to end_date.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            qs = qs.filter(date__range=[start_date, end_date])
        elif start_date:
            qs = qs.filter(date__gte=start_date)
        elif end_date:
            qs = qs.filter(date__lte=end_date)

        # --- created_by filter (Admin only) ---
        created_by = request.query_params.get('created_by')
        if created_by is not None:
            if not IsAdmin().has_permission(request, self):
                return None, Response(
                    {'detail': 'Only admins can filter by created_by.'},
                    status=status.HTTP_403_FORBIDDEN,
                )
            qs = qs.filter(created_by_id=created_by)

        return qs, None


class SummaryReportView(ReportBaseView):
    """
    GET /reports/summary/
    Returns total income, total expenses, net balance, and record count.
    Permission: IsViewer (any authenticated user)
    """
    permission_classes = [IsViewer]

    def get(self, request):
        qs, error = self.get_filtered_queryset(request)
        if error:
            return error

        total_income = (
            qs.filter(record_type=FinancialRecord.RecordType.INCOME)
            .aggregate(total=Sum('amount'))['total']
        ) or Decimal('0.00')

        total_expenses = (
            qs.filter(record_type=FinancialRecord.RecordType.EXPENSE)
            .aggregate(total=Sum('amount'))['total']
        ) or Decimal('0.00')

        record_count = qs.aggregate(count=Count('id'))['count']

        data = {
            'total_income': total_income,
            'total_expenses': total_expenses,
            'net_balance': total_income - total_expenses,
            'record_count': record_count,
        }

        serializer = SummaryReportSerializer(data)
        return Response(serializer.data)


class ByTypeReportView(ReportBaseView):
    """
    GET /reports/by-type/
    Returns totals and counts grouped by INCOME / EXPENSE.
    Permission: IsViewer (any authenticated user)
    """
    permission_classes = [IsViewer]

    def get(self, request):
        qs, error = self.get_filtered_queryset(request)
        if error:
            return error

        grouped = (
            qs.values('record_type')
            .annotate(total=Sum('amount'), count=Count('id'))
        )

        result = {
            'income': {'total': Decimal('0.00'), 'count': 0},
            'expense': {'total': Decimal('0.00'), 'count': 0},
        }

        for row in grouped:
            key = row['record_type'].lower()  # INCOME -> income, EXPENSE -> expense
            result[key] = {
                'total': row['total'] or Decimal('0.00'),
                'count': row['count'],
            }

        serializer = ByTypeReportSerializer(result)
        return Response(serializer.data)


class MonthlyReportView(ReportBaseView):
    """
    GET /reports/monthly/
    Returns income and expense totals grouped by month.
    Permission: IsAnalystOrAbove
    """
    permission_classes = [IsAnalystOrAbove]

    def get(self, request):
        qs, error = self.get_filtered_queryset(request)
        if error:
            return error

        monthly = (
            qs.annotate(month=TruncMonth('date'))
            .values('month', 'record_type')
            .annotate(total=Sum('amount'))
            .order_by('month')
        )

        # Pivot: group by month, then split income vs expense
        months = defaultdict(lambda: {'income': Decimal('0.00'), 'expenses': Decimal('0.00')})

        for row in monthly:
            month_str = row['month'].strftime('%Y-%m')
            amount = row['total'] or Decimal('0.00')
            if row['record_type'] == FinancialRecord.RecordType.INCOME:
                months[month_str]['income'] = amount
            else:
                months[month_str]['expenses'] = amount

        results = []
        for month_str in sorted(months.keys()):
            entry = months[month_str]
            results.append({
                'month': month_str,
                'income': entry['income'],
                'expenses': entry['expenses'],
                'net': entry['income'] - entry['expenses'],
            })

        serializer = MonthlyReportSerializer({'results': results})
        return Response(serializer.data)
