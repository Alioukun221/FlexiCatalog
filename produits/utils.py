from mongoengine.queryset.visitor import Q

def construire_filtre_recherche_v2(data):
    filtre = {}

    if 'categorie' in data and data['categorie']:
        filtre['categorie'] = data['categorie']

    if 'prix_min' in data:
        filtre['prix__gte'] = data['prix_min']
    if 'prix_max' in data:
        filtre['prix__lte'] = data['prix_max']

    if 'marque' in data and data['marque']:
        filtre['marque__icontains'] = data['marque']

    filtres_caract = data.get('filtres', {})
    for champ, condition in filtres_caract.items():
        if isinstance(condition, dict):
            for op, val in condition.items():
                mongo_op = {
                    'gte': '__gte',
                    'lte': '__lte',
                    'eq': '',
                    'in': '__in',
                    'contains': '__icontains'
                }.get(op)
                if mongo_op is not None:
                    cle = f'caracteristiques.{champ}{mongo_op}'
                    filtre[cle] = val
        else:
            filtre[f'caracteristiques.{champ}'] = condition

    return filtre

def recherche_filtrée(params):
    """
    params : dict des filtres reçus (ex: {'categorie': 'Smartphones', 'prix_min': 100, 'ram': '8GB'})
    Retourne une QuerySet MongoEngine filtrée selon les critères.
    """

    filtre = Q(is_active=True)  # Toujours filtrer les produits actifs

    # Filtrage classique
    if 'categorie' in params and params['categorie']:
        filtre &= Q(categorie=params['categorie'])

    if 'marque' in params and params['marque']:
        filtre &= Q(marque__icontains=params['marque'])

    if 'prix_min' in params:
        filtre &= Q(prix__gte=params['prix_min'])

    if 'prix_max' in params:
        filtre &= Q(prix__lte=params['prix_max'])

    # Recherche textuelle sur le nom ou description
    if 'q' in params and params['q']:
        filtre &= (Q(nom__icontains=params['q']) | Q(description__icontains=params['q']))

    # Filtrage dynamique selon caractéristiques
    # Parcours des autres paramètres pour chercher dans caracteristiques
    for key, value in params.items():
        if key in ['categorie', 'marque', 'prix_min', 'prix_max', 'q']:
            continue  # Déjà traité

        if value:
            # Filtrer dans caracteristiques.key avec insensible à la casse et contenance
            filtre &= Q(**{f"caracteristiques.{key}__icontains": value})

    # Exécuter la requête
    from .models import Produit
    resultats = Produit.objects(filtre)

    return resultats

