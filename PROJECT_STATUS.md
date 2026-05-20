# ERP FSM - État du projet

## Vue d'ensemble

ERP FSM est une API ERP orientée fabrication, centrée sur le flux opérationnel allant de la définition des produits jusqu'à l'exécution de la production et la traçabilité du stock.

Le périmètre actuel couvre :
- la gestion des clients
- la gestion des produits
- la gestion des matières
- la nomenclature produit (BOM)
- les ordres de fabrication
- le calcul du coût matière
- le calcul des besoins matière
- la vérification de la disponibilité matière
- la consommation matière et la mise à jour du stock
- l'historique des mouvements de stock
- la réception de stock
- les transitions de statut validées des ordres de fabrication

---

## Jalons actuels

Le projet couvre maintenant le flux complet de planification et d'exécution pour un ordre de fabrication :

1. définir les produits et les matières
2. relier les matières aux produits via une nomenclature (BOM)
3. créer des ordres de fabrication
4. calculer les besoins matière
5. vérifier si le stock actuel permet de lancer la production
6. consommer les matières et décrémenter le stock
7. tracer chaque mouvement de stock (consommation, réception)
8. réceptionner du stock entrant
9. faire progresser l'ordre à travers un cycle de vie validé

---

## Réalisé

### Fondations de l'API
- [x] Endpoint de health check
- [x] Structure de l'application FastAPI
- [x] Modèles SQLAlchemy et intégration base de données
- [x] Schémas Pydantic
- [x] Mise en place des tests automatisés (PostgreSQL, transaction rollback par test)

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
- [x] Transitions de statut validées (draft → confirmed → in_progress → done / cancelled)
- [x] Tests automatisés

### Calcul des coûts
- [x] Calculer le coût matière d'un produit
- [x] Support des produits sans lignes de nomenclature
- [x] Tests automatisés

### Planification de fabrication
- [x] Calculer les besoins matière d'un ordre de fabrication
- [x] Calculer la disponibilité matière d'un ordre de fabrication
- [x] Déterminer si un ordre peut être produit avec le stock actuel
- [x] Tests automatisés

### Consommation matière
- [x] Consommer les matières d'un ordre de fabrication (`POST /manufacturing-orders/{id}/consume`)
- [x] Décrémenter `quantity_on_hand` selon la nomenclature × la quantité de l'ordre
- [x] Vérification préalable du stock (tout ou rien)
- [x] Passage automatique de l'ordre au statut `done` après consommation
- [x] Protection contre la double consommation (erreur 409 si ordre déjà `done` ou `cancelled`)
- [x] Tests automatisés

### Gestion des mouvements de stock
- [x] Modèle `StockMovement` avec quantité signée, type et référence
- [x] Création automatique d'un mouvement à chaque consommation (type `consumption`)
- [x] Réception de stock (`POST /materials/{id}/receive`) avec création d'un mouvement (type `receipt`)
- [x] Historique des mouvements par matière (`GET /materials/{id}/stock-movements`)
- [x] Tests automatisés

---

## Prochain jalon

### Front-end
La prochaine étape logique est de donner une interface utilisable à l'API.

Travaux prévus :
- [ ] Ajouter les écrans Clients, Produits, Matières
- [ ] Ajouter les écrans Ordres de fabrication avec statut et actions (confirmer, consommer, annuler)
- [ ] Afficher les besoins matière et la disponibilité matière
- [ ] Afficher l'historique des mouvements de stock par matière
- [ ] Créer un dashboard de base

---

## Backlog futur

### Gestion d'inventaire
- [ ] Ajustements d'inventaire (type `adjustment`)
- [ ] Réservation de matière pour les ordres de fabrication

### Exécution de fabrication
- [ ] Opérations / gammes de fabrication
- [ ] Suivi du temps et de la main-d'œuvre

### Fonctions supply et business
- [ ] Support des achats
- [ ] Devis de vente
- [ ] Règles de tarification
- [ ] Suivi des marges

---

## État qualité

État validé à ce jour :
- [x] Linting OK
- [x] Suite de tests OK
- [x] Flux de planification de fabrication implémenté
- [x] Flux de disponibilité matière implémenté
- [x] Flux d'exécution (consommation, réception, mouvements de stock) implémenté
- [x] Cycle de vie des ordres de fabrication implémenté

> Dernier état vérifié : 75 tests passent