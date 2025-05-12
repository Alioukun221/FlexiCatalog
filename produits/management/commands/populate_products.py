from django.core.management.base import BaseCommand
from produits.models import Produit
import random
from decimal import Decimal
import os
import requests
from django.conf import settings
from pathlib import Path

class Command(BaseCommand):
    help = 'Peuple la base de données avec des produits de test'

    def download_image(self, url, filename):
        try:
            response = requests.get(url)
            if response.status_code == 200:
                img_path = Path(settings.BASE_DIR) / 'static' / 'img' / filename
                with open(img_path, 'wb') as f:
                    f.write(response.content)
                return filename
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'Erreur lors du téléchargement de l\'image {url}: {str(e)}'))
        return None

    def handle(self, *args, **kwargs):
        # Nettoyage de la base de données
        Produit.objects.delete()

        # Liste de produits de test avec plus de détails et images
        produits = [
            {
                'nom': 'iPhone 14 Pro Max',
                'description': 'Le dernier iPhone avec un écran Super Retina XDR de 6,7 pouces, triple appareil photo 48MP, et puce A16 Bionic.',
                'prix': Decimal('1299.99'),
                'stock': 50,
                'categorie': 'Smartphones',
                'marque': 'Apple',
                'image_url': 'https://store.storeimages.cdn-apple.com/4668/as-images.apple.com/is/iphone-14-pro-finish-select-202209-6-7inch-deeppurple?wid=5120&hei=2880&fmt=p-jpg&qlt=80&.v=1663703841896',
                'caracteristiques': {
                    'ecran': '6.7 pouces Super Retina XDR',
                    'processeur': 'A16 Bionic',
                    'ram': '6GB',
                    'stockage': '128GB',
                    'couleur': 'Noir',
                    'appareil_photo': 'Triple 48MP + 12MP + 12MP',
                    'batterie': '4323 mAh',
                    'systeme': 'iOS 16'
                }
            },
            {
                'nom': 'Samsung Galaxy S23 Ultra',
                'description': 'Smartphone Android haut de gamme avec appareil photo 200MP et S Pen intégré.',
                'prix': Decimal('1199.99'),
                'stock': 35,
                'categorie': 'Smartphones',
                'marque': 'Samsung',
                'image_url': 'https://images.samsung.com/is/image/samsung/p6pim/fr/2302/gallery/fr-galaxy-s23-ultra-s918-sm-s918bzgdeub-537088187',
                'caracteristiques': {
                    'ecran': '6.8 pouces Dynamic AMOLED 2X',
                    'processeur': 'Snapdragon 8 Gen 2',
                    'ram': '12GB',
                    'stockage': '256GB',
                    'couleur': 'Noir',
                    'appareil_photo': '200MP + 12MP + 10MP + 10MP',
                    'batterie': '5000 mAh',
                    'systeme': 'Android 13'
                }
            },
            {
                'nom': 'MacBook Pro M2',
                'description': 'Ordinateur portable professionnel avec puce M2, écran Liquid Retina XDR de 14 pouces.',
                'prix': Decimal('1999.99'),
                'stock': 25,
                'categorie': 'Ordinateurs',
                'marque': 'Apple',
                'image_url': 'https://store.storeimages.cdn-apple.com/4668/as-images.apple.com/is/mbp14-spacegray-select-202301?wid=904&hei=840&fmt=jpeg&qlt=90&.v=1671304673202',
                'caracteristiques': {
                    'ecran': '14 pouces Liquid Retina XDR',
                    'processeur': 'M2 Pro',
                    'ram': '16GB',
                    'stockage': '512GB SSD',
                    'carte_graphique': 'M2 Pro 16-core',
                    'systeme': 'macOS Ventura',
                    'connectivite': 'Wi-Fi 6E, Bluetooth 5.3'
                }
            },
            {
                'nom': 'Dell XPS 15',
                'description': 'Ordinateur portable premium avec écran OLED 4K et processeur Intel Core i9.',
                'prix': Decimal('2499.99'),
                'stock': 20,
                'categorie': 'Ordinateurs',
                'marque': 'Dell',
                'image_url': 'https://i.dell.com/is/image/DellContent/content/dam/ss2/product-images/dell-client-products/notebooks/xps-notebooks/xps-15-9520/media-gallery/black/laptop-xps-15-9520-t-black-gallery-1.psd?fmt=png-alpha&pscan=auto&scl=1&hei=402&wid=402&qlt=100,1&resMode=sharp2&size=402,402&chrss=full',
                'caracteristiques': {
                    'ecran': '15.6 pouces OLED 4K',
                    'processeur': 'Intel Core i9-12900HK',
                    'ram': '32GB',
                    'stockage': '1TB SSD',
                    'carte_graphique': 'NVIDIA RTX 3050 Ti',
                    'systeme': 'Windows 11 Pro',
                    'connectivite': 'Wi-Fi 6E, Thunderbolt 4'
                }
            },
            {
                'nom': 'Sony WH-1000XM5',
                'description': 'Casque sans fil premium avec réduction de bruit active, son haute résolution.',
                'prix': Decimal('399.99'),
                'stock': 100,
                'categorie': 'Audio',
                'marque': 'Sony',
                'image_url': 'https://www.sony.fr/image/5d02da5df552836db894d0c4c4c0c0f0?fmt=pjpeg&bgcolor=FFFFFF&bgc=FFFFFF&wid=2515&hei=1320',
                'caracteristiques': {
                    'type': 'Over-ear',
                    'connectivite': 'Bluetooth 5.2',
                    'autonomie': '30 heures',
                    'reduction_bruit': 'Active',
                    'couleur': 'Noir',
                    'puissance': 'NC'
                }
            },
            {
                'nom': 'Samsung Galaxy Watch 6 Pro',
                'description': 'Montre connectée avec écran AMOLED, suivi d\'activité avancé, et compatibilité Android et iOS.',
                'prix': Decimal('449.99'),
                'stock': 75,
                'categorie': 'Wearables',
                'marque': 'Samsung',
                'caracteristiques': {
                    'ecran': '1.4 pouces AMOLED',
                    'autonomie': '40 heures',
                    'resistance': 'IP68',
                    'systeme': 'Wear OS',
                    'couleur': 'Noir'
                }
            },
            {
                'nom': 'iPad Pro M2',
                'description': 'Tablette professionnelle avec puce M2, écran Liquid Retina XDR de 12,9 pouces, et support Apple Pencil 2.',
                'prix': Decimal('1099.99'),
                'stock': 40,
                'categorie': 'Tablettes',
                'marque': 'Apple',
                'caracteristiques': {
                    'ecran': '12.9 pouces Liquid Retina XDR',
                    'processeur': 'M2',
                    'ram': '8GB',
                    'stockage': '256GB',
                    'couleur': 'Gris sidéral'
                }
            },
            {
                'nom': 'Bose SoundLink Revolve+',
                'description': 'Enceinte Bluetooth portable avec son 360°, résistance à l\'eau IPX4, et jusqu\'à 17 heures d\'autonomie.',
                'prix': Decimal('299.99'),
                'stock': 60,
                'categorie': 'Audio',
                'marque': 'Bose',
                'caracteristiques': {
                    'puissance': '30W',
                    'autonomie': '17 heures',
                    'resistance': 'IPX4',
                    'connectivite': 'Bluetooth 4.2',
                    'couleur': 'Noir'
                }
            },
            {
                'nom': 'Canon EOS R6 Mark II',
                'description': 'Appareil photo hybride professionnel avec capteur CMOS 24,2MP, stabilisation d\'image 5 axes, et enregistrement vidéo 4K.',
                'prix': Decimal('2499.99'),
                'stock': 30,
                'categorie': 'Photo',
                'marque': 'Canon',
                'caracteristiques': {
                    'capteur': '24.2MP CMOS',
                    'video': '4K 60fps',
                    'stabilisation': '5 axes',
                    'connectivite': 'Wi-Fi, Bluetooth',
                    'couleur': 'Noir'
                }
            },
            {
                'nom': 'Logitech MX Master 3S',
                'description': 'Souris sans fil premium pour professionnels avec capteur 8K DPI, défilement ultra-rapide, et jusqu\'à 70 jours d\'autonomie.',
                'prix': Decimal('99.99'),
                'stock': 45,
                'categorie': 'Périphériques',
                'marque': 'Logitech',
                'caracteristiques': {
                    'capteur': '8K DPI',
                    'connectivite': 'Bluetooth, USB',
                    'autonomie': '70 jours',
                    'boutons': '7 boutons programmables',
                    'couleur': 'Gris'
                }
            },
            {
                'nom': 'Samsung 49" Odyssey G9',
                'description': 'Moniteur gaming incurvé avec écran QHD, taux de rafraîchissement 240Hz, et technologie HDR1000.',
                'prix': Decimal('1299.99'),
                'stock': 20,
                'categorie': 'Moniteurs',
                'marque': 'Samsung',
                'caracteristiques': {
                    'ecran': '49 pouces QHD',
                    'rafraichissement': '240Hz',
                    'courbure': '1000R',
                    'hdr': 'HDR1000',
                    'couleur': 'Blanc'
                }
            },
            {
                'nom': 'Samsung T7 Shield',
                'description': 'Disque SSD externe portable avec protection IP65, jusqu\'à 2TB de stockage, et vitesses de transfert jusqu\'à 1050 Mo/s.',
                'prix': Decimal('149.99'),
                'stock': 55,
                'categorie': 'Stockage',
                'marque': 'Samsung',
                'caracteristiques': {
                    'capacite': '2TB',
                    'vitesse': '1050 Mo/s',
                    'resistance': 'IP65',
                    'interface': 'USB 3.2',
                    'couleur': 'Noir'
                }
            }
        ]

        # Création des produits
        for produit_data in produits:
            # Extraction des caractéristiques et de l'URL de l'image
            caracteristiques = produit_data.pop('caracteristiques', {})
            image_url = produit_data.pop('image_url', None)
            
            # Téléchargement de l'image si une URL est fournie
            image_filename = None
            if image_url:
                image_filename = f"{produit_data['nom'].lower().replace(' ', '_')}.jpg"
                self.download_image(image_url, image_filename)
            
            # Création du produit
            produit = Produit.objects.create(
                **produit_data,
                image_url=image_filename,
                caracteristiques=caracteristiques
            )
            
            self.stdout.write(
                self.style.SUCCESS(f'Produit créé avec succès : {produit_data["nom"]}')
            )

        self.stdout.write(
            self.style.SUCCESS(f'Base de données peuplée avec {len(produits)} produits')
        ) 