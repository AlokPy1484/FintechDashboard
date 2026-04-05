from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import FinancialRecord
from .serializers import FinancialRecordSerializer
from users.permissions import IsAdmin, IsAnalystOrAbove, IsViewer


class FinancialRecordViewSet(viewsets.ModelViewSet):
    queryset = FinancialRecord.objects.all().order_by('-date')
    serializer_class = FinancialRecordSerializer

    def get_permissions(self):
        """
        Map actions to permission classes:
        - list, retrieve  → IsViewer (and above)
        - create, update  → IsAnalystOrAbove
        - destroy         → IsAdmin only
        """
        if self.action in ['list', 'retrieve']:
            permission_classes = [IsAuthenticated, IsViewer]

        elif self.action in ['create', 'update', 'partial_update']:
            permission_classes = [IsAuthenticated, IsAnalystOrAbove]

        elif self.action == 'destroy':
            permission_classes = [IsAuthenticated, IsAdmin]

        else:
            # Fallback — deny access to any unlisted action
            permission_classes = [IsAuthenticated, IsAdmin]

        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        """Auto-assign the currently logged-in user as created_by."""
        serializer.save(created_by=self.request.user)

    def update(self, request, *args, **kwargs):
        """Handle both PUT and PATCH cleanly."""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        """Delete a record — IsAdmin only (enforced via get_permissions)."""
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {"detail": "Financial record deleted successfully."},
            status=status.HTTP_204_NO_CONTENT
        )