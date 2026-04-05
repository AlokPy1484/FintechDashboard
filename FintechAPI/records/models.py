from django.db import models
from django.conf import settings

class FinancialRecord(models.Model):

    class RecordType(models.TextChoices):
        INCOME = 'INCOME', 'Income'
        EXPENSE = 'EXPENSE', 'Expense'

    title = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    record_type = models.CharField(max_length=10, choices=RecordType.choices, default=RecordType.EXPENSE)
    date = models.DateField()
    description = models.CharField(max_length=500)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    edited_at = models.DateTimeField(auto_now=True)


    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.title} ({self.record_type}) - {self.amount} "