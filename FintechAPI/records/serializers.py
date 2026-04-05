from rest_framework import serializers
from .models import FinancialRecord

class FinancialRecordSerializer(serializers.ModelSerializer):
    def validate_record_type(self, value):
        allowed_types = ['income', 'expense']  # adjust based on your choices
        if value not in allowed_types:
            raise serializers.ValidationError("Invalid record type")
        return value

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    class Meta:
        model = FinancialRecord
        fields = '__all__'
        read_only_fields = ['created_by']


