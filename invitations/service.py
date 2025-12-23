import qrcode
from io import BytesIO
from django.core.files import File
from django.utils import timezone
from .models import Guest, WeddingConfig, ScanLog, Table
from django.db import transaction

# Le message complet tel que vous l'avez fourni
INVITATION_TEXT = """✨ INVITATION ✨\n

🙏 Avec la grâce de Dieu et la bénédiction de nos ancêtres 🙏\n

Les familles Feu Ndong Nsolo Joseph, Feu Nkounkou Malonga Marcel, Feu Minko Mi Ndong Patrice.\n
Ainsi que les familles feu Inama Théophile, feu Missono Auguste, Moukoumbi Inama Jean-Christophe, Manguedi Rosalie Ep Inama,\n

 ont l'immense joie de vous annoncer l'union coutumière de leurs enfants :\n\n

💍 Gaëlle Denise Ekombeng Minko & Théophile Crépin Hinama Moukoumbi 💍\n

Cette grande célébration selon nos us et coutumes gabonaises se tiendra le samedi 27 décembre 2025\n à Nzeng-Ayong (ancienne cité, face restaurant Tsoumou), suivie d'un dîner à la salle des fêtes d'Avorbam (Rond-point Avorbam, panier Mbeto). 🥂\n

Votre présence sera la bienvenue.\n
Nous espérons vous compter parmi nos convives. ❤️\n

✨ PROGRAMME ✨\n

⭐ 09 h 30 : Mise en place terminée à Nzeng-Ayong.\n
⭐ 10 h 00 : Début des pourparlers.\n
⭐ 15 h 00 : Fin de la cérémonie.\n
⭐ 17 h 30 : Mise en place terminée à la salle d'Avorbam.\n
⭐ 18 h 00 : Arrivée des mariés.\n
⭐ 18 h 30 : Début de la soirée."""

class GuestService:

    @staticmethod
    def generer_image_qr_code(guest):
        """
        Génère l'image physique du QR Code.
        Appelé par Guest.save() lors de la création.
        """
        # Définir le texte de mariage par défaut s'il n'est pas déjà défini
        if not guest.wedding_text:
            guest.wedding_text = INVITATION_TEXT
            guest.save(update_fields=['wedding_text'])
            
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        # On encode le code unique (ex: QR-XXXXXXXXXXXX)
        qr.add_data(guest.qr_code)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        blob = BytesIO()
        img.save(blob, 'PNG')
        
        filename = f"qr_{guest.qr_code}.png"
        guest.qr_code_image.save(filename, File(blob), save=False)
        guest.save(update_fields=['qr_code_image'])
        
    @staticmethod
    @transaction.atomic
    def scan_qr_code(qr_code_str, ip_addr=None):
        try:
            guest = Guest.objects.get(qr_code=qr_code_str)
            
            if guest.scanned:
                return {
                    "status": "error",
                    "already_scanned": True,
                    "message": f"Déjà scanné à {guest.scanned_at.strftime('%H:%M')}",
                    "affichage_ecran": {
                        "nom": guest.name,
                        "table": guest.table.name if guest.table else "N/A"
                    }
                }

            guest.scanned = True
            guest.scanned_at = timezone.now()
            guest.save()

            return {
                "status": "success",
                "affichage_ecran": {
                    "nom": guest.name,
                    "table": guest.table.name if guest.table else "Sans table",
                    # On ajoute la catégorie ici pour le frontend
                    "table_category": guest.table.category if guest.table else "STAND",
                    "status": guest.get_status_display(),
                    "wedding_text": guest.wedding_text or INVITATION_TEXT,
                }
            }
        except Guest.DoesNotExist:
            return {"status": "error", "message": "Code inconnu"}


class TableService:
    @staticmethod
    def get_tables():
        return Table.objects.all().order_by('name')

    @staticmethod
    def get_table(name):
        return Table.objects.get(name=name) 
    
    @transaction.atomic
    @staticmethod
    def create_table(name, capacity, description=None):
        return Table.objects.create(name=name, capacity=capacity, description=description)