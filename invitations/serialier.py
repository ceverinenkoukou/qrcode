from rest_framework import serializers
from .models import Guest, ScanLog, Table
from .service import INVITATION_TEXT


class GuestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Guest
        fields = '__all__'
        read_only_fields = ('qr_code', 'created_at', 'scanned_at')

    def get_wedding_text(self, obj):
        # Si l'invité a un texte perso, on l'affiche, sinon on prend le texte par défaut du backend
        return obj.wedding_text if obj.wedding_text else INVITATION_TEXT

    def validate_wedding_text(self, value):
        # Permet d'accepter une valeur vide lors de la création/maj sans erreur
        # Mais on laisse le service gérer le texte par défaut
        return value if value is not None else ""


class ScanLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScanLog
        fields = '__all__'
        read_only_fields = ('scanned_at', 'guest')


# serialier.py
class TableSerializer(serializers.ModelSerializer):
    occupancy = serializers.SerializerMethodField()

    class Meta:
        model = Table
        fields = ['id', 'name', 'category', 'capacity', 'occupancy', 'description']

    def get_occupancy(self, obj):
        # Compte les invités réellement assis à cette table
        return obj.guests.count()