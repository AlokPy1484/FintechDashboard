from rest_framework import serializers


class SummaryReportSerializer(serializers.Serializer):
    """Response shape for /reports/summary/"""
    total_income = serializers.DecimalField(max_digits=14, decimal_places=2)
    total_expenses = serializers.DecimalField(max_digits=14, decimal_places=2)
    net_balance = serializers.DecimalField(max_digits=14, decimal_places=2)
    record_count = serializers.IntegerField()


class TypeDetailSerializer(serializers.Serializer):
    """Nested shape for each record type (income / expense)."""
    total = serializers.DecimalField(max_digits=14, decimal_places=2)
    count = serializers.IntegerField()


class ByTypeReportSerializer(serializers.Serializer):
    """Response shape for /reports/by-type/"""
    income = TypeDetailSerializer()
    expense = TypeDetailSerializer()


class MonthlyEntrySerializer(serializers.Serializer):
    """Single month entry inside the monthly report."""
    month = serializers.CharField()
    income = serializers.DecimalField(max_digits=14, decimal_places=2)
    expenses = serializers.DecimalField(max_digits=14, decimal_places=2)
    net = serializers.DecimalField(max_digits=14, decimal_places=2)


class MonthlyReportSerializer(serializers.Serializer):
    """Response shape for /reports/monthly/"""
    results = MonthlyEntrySerializer(many=True)
