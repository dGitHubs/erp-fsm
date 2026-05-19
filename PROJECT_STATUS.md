# ERP FSM - État du projet

## Vue d’ensemble

ERP FSM est une API ERP orientée fabrication, centrée sur le flux opérationnel allant de la définition des produits jusqu’à la préparation et la faisabilité de la production.

Le périmètre actuel couvre :
- la gestion des clients
- la gestion des produits
- la gestion des matières
- la nomenclature produit (BOM)
- les ordres de fabrication
- le calcul du coût matière
- le calcul des besoins matière
- la vérification de la disponibilité matière

---

## Jalons actuels

Le projet permet maintenant de couvrir le flux de planification suivant pour un ordre de fabrication :

1. définir les produits et les matières
2. relier les matières aux produits via une nomenclature (BOM)
3. créer des ordres de fabrication
4. calculer les besoins matière
5. vérifier si le stock actuel permet de lancer la production

Cela constitue une base solide pour passer ensuite à la consommation de stock et à l’exécution de la fabrication.

---

## Réalisé

### Fondations de l’API
- [x] Endpoint de health check
- [x] Structure de l’application FastAPI
- [x] Modèles SQLAlchemy et intégration base de données
- [x] Schémas Pydantic
- [x] Mise en place des tests automatisés

### Clients
- [x] Créer un client
- [x] Lister les clients
- [x] Obtenir un client par identifiant
- [x] Validations et tests automatisés

### Produits
- [x] Créer un produit
- [x] Lister les produits
- [x] Obtenir un produit par identifiant
- [x] Validation des unités et des dimensions
- [x] Tests automatisés

### Matières
- [x] Créer une matière
- [x] Lister les matières
- [x] Obtenir une matière par identifiant
- [x] Validation des unités et du coût unitaire
- [x] Support du champ `quantity_on_hand`
- [x] Tests automatisés

### Nomenclature produit (Product Materials / BOM)
- [x] Lier des matières à des produits
- [x] Définir les quantités de matière requises par produit
- [x] Lister les liens produit-matière
- [x] Obtenir un lien produit-matière par identifiant
- [x] Tests automatisés

### Ordres de fabrication
- [x] Créer un ordre de fabrication
- [x] Lister les ordres de fabrication
- [x] Obtenir un ordre de fabrication par identifiant
- [x] Validation du statut et de la quantité
- [x] Tests automatisés

### Calcul des coûts
- [x] Calculer le coût matière d’un produit
- [x] Support des produits sans lignes de nomenclature
- [x] Tests automatisés

### Planification de fabrication
- [x] Calculer les besoins matière d’un ordre de fabrication
- [x] Calculer la disponibilité matière d’un ordre de fabrication
- [x] Déterminer si un ordre peut être produit avec le stock actuel
- [x] Tests automatisés

---

## Prochain jalon

### Consommation matière
La prochaine étape logique est de passer de la planification à l’exécution.

Travaux prévus :
- [ ] Ajouter un endpoint pour consommer les matières d’un ordre de fabrication
- [ ] Décrémenter `quantity_on_hand` en fonction de la nomenclature × la quantité de l’ordre
- [ ] Empêcher la consommation si le stock est insuffisant
- [ ] Retourner un récapitulatif de consommation matière
- [ ] Ajouter les tests automatisés

Cette évolution permettra au système non seulement de vérifier la faisabilité de la production, mais aussi de refléter la consommation réelle de stock au moment du lancement ou de l’exécution d’un ordre.

---

## Backlog futur

### Gestion d’inventaire
- [ ] Historique des mouvements de stock
- [ ] Réception / réapprovisionnement de matières
- [ ] Ajustements d’inventaire
- [ ] Réservation de matière pour les ordres de fabrication

### Exécution de fabrication
- [ ] Cycle de vie plus riche des ordres de fabrication
- [ ] Opérations / gammes de fabrication
- [ ] Suivi du temps et de la main-d’œuvre
- [ ] Workflow de fin de production

### Fonctions supply et business
- [ ] Support des achats
- [ ] Devis de vente
- [ ] Règles de tarification
- [ ] Suivi des marges

### Front-end
- [ ] Ajouter une interface web pour consommer l’API
- [ ] Créer un dashboard de base
- [ ] Ajouter les écrans Clients, Produits, Matières
- [ ] Ajouter les écrans Ordres de fabrication
- [ ] Afficher les besoins matière et la disponibilité matière
- [ ] Préparer la base pour la consommation matière

---

## État qualité

État validé à ce jour :
- [x] Linting OK
- [x] Suite de tests OK
- [x] Flux de planification de fabrication implémenté
- [x] Flux de disponibilité matière implémenté

> Dernier état vérifié : 54 tests passent