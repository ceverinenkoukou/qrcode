from django.db import models
import uuid
import os
from django.conf import settings


class Table(models.Model):
    CATEGORIES = [
        ('VIP', 'VIP'),
        ('STAND', 'Standard'),
        ('FAM', 'Famille'),
        ('AMI', 'Amis'),
        ('AUTRE', 'Autre'),
    ]
    
    name = models.CharField(max_length=100, unique=True)
    category = models.CharField(max_length=10, choices=CATEGORIES, default='STAND')
    capacity = models.IntegerField(default=10)
    description = models.TextField(blank=True, null=True, default='Aucune description')
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date de création"
    )
   
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Date de mise à jour"
    )
    deleted_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="Date de suppression"
    )
    
    class Meta:
        ordering = ['name']
        verbose_name = "Table"
        verbose_name_plural = "Tables"
    
    def __str__(self):
        return self.name


class WeddingConfig(models.Model):
    """Stocke la configuration globale"""
    total_capacity = models.IntegerField(default=390)
    current_occupancy = models.IntegerField(default=0)

    def remaining_seats(self):
        return self.total_capacity - self.current_occupancy
    

class Guest(models.Model):
    """Modèle pour les invités du mariage"""
    
    STATUS_CHOICES = [
        ('VIP', 'VIP'),
        ('STAND', 'Standard'),
        ('FAM', 'Famille'),
        ('AMI', 'Amis'),
        ('AUTRE', 'Autre'),
    ]
    
    STATUT_GUEST = [
        ('COUPLE', 'Couple'),
        ('SINGLE', 'Célibataire'),
        ('FAMILY', 'Famille'),
    ]
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    name = models.CharField(
        max_length=200,
        verbose_name="Nom de l'invité",blank=True,null=True,default="Nom de l'invité"
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='STAND',
        verbose_name="Statut"
    )
    
    wedding_text = models.TextField(
        blank=True,
        null=True,
        verbose_name="Texte de mariage"
    )
    
    statut_guest = models.CharField(
        max_length=20,
        choices=STATUT_GUEST,
        default='COUPLE',
        verbose_name="Statut"
    )
    
    table = models.ForeignKey(
        Table,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='guests',
        verbose_name="Table assignée"
    )
    
    scanned = models.BooleanField(
        default=False,
        verbose_name="QR Code scanné"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date de création"
    )
    
    scanned_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Date du scan"
    )
    
    qr_code = models.CharField(
        max_length=100,
        unique=True,
        editable=False,
        verbose_name="Code QR unique"
    )
    
    qr_code_image = models.ImageField(
        upload_to='qr_codes/',
        null=True,
        blank=True,
        verbose_name="Image QR Code"
    )
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Invité"
        verbose_name_plural = "Invités"
    
    def __str__(self):
        return f"{self.name} - {self.table}"
    
    def save(self, *args, **kwargs):
        if not self.qr_code:
            self.qr_code = f"QR-{uuid.uuid4().hex[:12].upper()}"
        
        # Générer le QR code si c'est une nouvelle création
        if not self.pk or not self.qr_code_image:
            super().save(*args, **kwargs)  # Sauvegarder d'abord pour avoir un ID
            # Générer l'image QR code après la sauvegarde
            from .service import GuestService
            GuestService.generer_image_qr_code(self)
        else:
            super().save(*args, **kwargs)
    
    def get_qr_code_url(self):
        """Retourne l'URL de l'image QR code"""
        if self.qr_code_image:
            return self.qr_code_image.url
        return None
    
    def delete(self, *args, **kwargs):
        """Supprime également le fichier image lors de la suppression"""
        if self.qr_code_image:
            if os.path.isfile(self.qr_code_image.path):
                os.remove(self.qr_code_image.path)
        super().delete(*args, **kwargs)


class ScanLog(models.Model):
    """Historique des scans pour audit"""
    
    guest = models.ForeignKey(
        Guest,
        on_delete=models.CASCADE,
        related_name='scan_history'
    )
    
    scanned_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date et heure du scan"
    )
    
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name="Adresse IP"
    )
    
    success = models.BooleanField(
        default=True,
        verbose_name="Scan réussi"
    )
    
    class Meta:
        ordering = ['-scanned_at']
        verbose_name = "Log de scan"
        verbose_name_plural = "Logs de scan"
    
    def __str__(self):
        return f"Scan: {self.guest.name} - {self.scanned_at}"