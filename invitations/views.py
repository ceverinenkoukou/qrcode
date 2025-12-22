# views.py
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from .models import Guest
from .service import GuestService
import io
from django.utils import timezone
from django.http import HttpResponse
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .serialier import GuestSerializer, ScanLogSerializer, TableSerializer
from .models import ScanLog, Table


class GuestViewSet(viewsets.ModelViewSet):
    queryset = Guest.objects.all()
    serializer_class = GuestSerializer
    
    @action(detail=False, methods=['post'], url_path='scan/<str:code>')
    def scan(self, request, code=None):
        """Action pour scanner un QR Code"""
        ip_addr = request.META.get('REMOTE_ADDR')
        # On appelle le service mis à jour
        result = GuestService.scan_qr_code(code, ip_addr)
        
        if result['status'] == 'error' and not result.get('already_scanned'):
            return Response(result, status=status.HTTP_404_NOT_FOUND)
            
        return Response(result, status=status.HTTP_200_OK)


class TableViewSet(viewsets.ModelViewSet):
    queryset = Table.objects.all().order_by('name')
    serializer_class = TableSerializer

    def perform_create(self, serializer):
        table = serializer.save()
        # Note: We don't generate QR codes for tables, only for guests

    def get_queryset(self):
        return super().get_queryset().order_by('name')

    @action(detail=True, methods=['get'], url_path='qr-code')
    def get_qr_code(self, request, pk=None):
        # This action doesn't make sense for tables, but keeping it for consistency
        return Response({"message": "QR codes are generated for guests, not tables"}, 
                       status=status.HTTP_400_BAD_REQUEST)


class ScanLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ScanLog.objects.all()
    serializer_class = ScanLogSerializer
    
    def get_queryset(self):
        return super().get_queryset().order_by('-scanned_at')

    def perform_create(self, serializer):
        serializer.save(scanned_at=timezone.now())
        guest = serializer.instance.guest
        guest.scanned = True
        guest.save(update_fields=['scanned'])