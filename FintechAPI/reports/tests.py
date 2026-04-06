from datetime import date
from decimal import Decimal

from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

from records.models import FinancialRecord

User = get_user_model()


class ReportTestMixin:
    """Shared setup: create users with different roles and sample records."""

    def setUp(self):
        self.client = APIClient()

        # Users
        self.admin = User.objects.create_user(
            username='admin', password='pass1234', email='admin@test.com', role='ADMIN'
        )
        self.analyst = User.objects.create_user(
            username='analyst', password='pass1234', email='analyst@test.com', role='ANALYST'
        )
        self.viewer = User.objects.create_user(
            username='viewer', password='pass1234', email='viewer@test.com', role='VIEWER'
        )

        # Sample records
        FinancialRecord.objects.create(
            title='Salary', amount=Decimal('5000.00'), record_type='INCOME',
            date=date(2024, 1, 15), description='Jan salary', created_by=self.viewer,
        )
        FinancialRecord.objects.create(
            title='Rent', amount=Decimal('1500.00'), record_type='EXPENSE',
            date=date(2024, 1, 20), description='Jan rent', created_by=self.viewer,
        )
        FinancialRecord.objects.create(
            title='Freelance', amount=Decimal('2000.00'), record_type='INCOME',
            date=date(2024, 2, 10), description='Feb freelance', created_by=self.admin,
        )
        FinancialRecord.objects.create(
            title='Groceries', amount=Decimal('300.00'), record_type='EXPENSE',
            date=date(2024, 2, 15), description='Feb groceries', created_by=self.admin,
        )


class SummaryReportTests(ReportTestMixin, TestCase):
    """Tests for GET /reports/summary/"""

    url = '/reports/summary/'

    def test_unauthenticated_returns_401(self):
        resp = self.client.get(self.url)
        self.assertIn(resp.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

    def test_viewer_gets_summary(self):
        self.client.force_authenticate(user=self.viewer)
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(Decimal(resp.data['total_income']), Decimal('7000.00'))
        self.assertEqual(Decimal(resp.data['total_expenses']), Decimal('1800.00'))
        self.assertEqual(Decimal(resp.data['net_balance']), Decimal('5200.00'))
        self.assertEqual(resp.data['record_count'], 4)

    def test_date_range_filter(self):
        self.client.force_authenticate(user=self.viewer)
        resp = self.client.get(self.url, {'start_date': '2024-02-01', 'end_date': '2024-02-28'})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(Decimal(resp.data['total_income']), Decimal('2000.00'))
        self.assertEqual(Decimal(resp.data['total_expenses']), Decimal('300.00'))
        self.assertEqual(resp.data['record_count'], 2)

    def test_invalid_date_returns_400(self):
        self.client.force_authenticate(user=self.viewer)
        resp = self.client.get(self.url, {'start_date': 'not-a-date'})
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_created_by_non_admin_returns_403(self):
        self.client.force_authenticate(user=self.viewer)
        resp = self.client.get(self.url, {'created_by': self.admin.id})
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_created_by_admin_allowed(self):
        self.client.force_authenticate(user=self.admin)
        resp = self.client.get(self.url, {'created_by': self.admin.id})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['record_count'], 2)

    def test_empty_result_returns_zeros(self):
        self.client.force_authenticate(user=self.viewer)
        resp = self.client.get(self.url, {'start_date': '2099-01-01', 'end_date': '2099-12-31'})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(Decimal(resp.data['total_income']), Decimal('0.00'))
        self.assertEqual(Decimal(resp.data['total_expenses']), Decimal('0.00'))
        self.assertEqual(Decimal(resp.data['net_balance']), Decimal('0.00'))
        self.assertEqual(resp.data['record_count'], 0)


class ByTypeReportTests(ReportTestMixin, TestCase):
    """Tests for GET /reports/by-type/"""

    url = '/reports/by-type/'

    def test_viewer_gets_by_type(self):
        self.client.force_authenticate(user=self.viewer)
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(Decimal(resp.data['income']['total']), Decimal('7000.00'))
        self.assertEqual(resp.data['income']['count'], 2)
        self.assertEqual(Decimal(resp.data['expense']['total']), Decimal('1800.00'))
        self.assertEqual(resp.data['expense']['count'], 2)

    def test_empty_result_returns_zeros(self):
        self.client.force_authenticate(user=self.viewer)
        resp = self.client.get(self.url, {'start_date': '2099-01-01'})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(Decimal(resp.data['income']['total']), Decimal('0.00'))
        self.assertEqual(resp.data['income']['count'], 0)


class MonthlyReportTests(ReportTestMixin, TestCase):
    """Tests for GET /reports/monthly/"""

    url = '/reports/monthly/'

    def test_viewer_denied(self):
        self.client.force_authenticate(user=self.viewer)
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_analyst_gets_monthly(self):
        self.client.force_authenticate(user=self.analyst)
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        results = resp.data['results']
        self.assertEqual(len(results), 2)
        # January
        self.assertEqual(results[0]['month'], '2024-01')
        self.assertEqual(Decimal(results[0]['income']), Decimal('5000.00'))
        self.assertEqual(Decimal(results[0]['expenses']), Decimal('1500.00'))
        self.assertEqual(Decimal(results[0]['net']), Decimal('3500.00'))
        # February
        self.assertEqual(results[1]['month'], '2024-02')
        self.assertEqual(Decimal(results[1]['income']), Decimal('2000.00'))
        self.assertEqual(Decimal(results[1]['expenses']), Decimal('300.00'))
        self.assertEqual(Decimal(results[1]['net']), Decimal('1700.00'))

    def test_admin_gets_monthly(self):
        self.client.force_authenticate(user=self.admin)
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_date_filter_works(self):
        self.client.force_authenticate(user=self.analyst)
        resp = self.client.get(self.url, {'start_date': '2024-02-01'})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data['results']), 1)
        self.assertEqual(resp.data['results'][0]['month'], '2024-02')
