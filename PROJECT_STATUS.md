# ERP FSM - État du projet

## Vue d'ensemble

ERP FSM est une application ERP orientée fabrication couvrant le flux complet de la définition des produits jusqu'à l'exécution de la production, avec une interface web et une API REST.

Le périmètre actuel couvre :
- la gestion des clients, produits et matières
- la nomenclature produit (BOM)
- les ordres de fabrication avec cycle de vie validé
- le calcul des besoins matière et la vérification de disponibilité
- la consommation matière et la mise à jour du stock
- l'historique des mouvements de stock (consommation, réception)
- la réception de stock entrant
- une interface web React pour gérer ordres, produits, matières et BOM

---

## Jalons actuels

Le projet couvre le flux complet de planification et d'exécution :

1. définir les produits et les matières (via l'UI)
2. relier les matières aux produits via une nomenclature BOM (via l'UI)
3. créer des ordres de fabrication (via l'UI)
4. calculer les besoins matière
5. vérifier si le stock permet de lancer la production
6. consommer les matières et décrémenter le stock (via l'UI)
7. tracer chaque mouvement de stock
8. réceptionner du stock entrant (via l'UI)
9. faire progresser l'ordre à travers un cycle de vie validé (via l'UI)

---

## Réalisé

### Fondations de l'API
- [x] Endpoint de health check
- [x] Structure de l'application FastAPI
- [x] Modèles SQLAlchemy et intégration base de données
- [x] Schémas Pydantic
- [x] Mise en place des tests automatisés (PostgreSQL, transaction rollback par test)
- [x] Middleware CORS pour le frontend

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

### Interface web (React + Vite + TypeScript)
- [x] Navigation entre les sections (Ordres, Produits, Matières)
- [x] Page Ordres de fabrication : liste avec noms client/produit, badges de statut, transitions, consommation, création
- [x] Page Produits : liste, création, panneau BOM dépliable par produit avec ajout de matières
- [x] Page Matières : liste avec stock (rouge si zéro), réception inline, historique des mouvements dépliable, création
- [x] Dark mode automatique

---

## Prochain jalon

### Écrans manquants et améliorations UI
- [ ] Page Clients (liste + création)
- [ ] Affichage de la disponibilité matière depuis la page ordres
- [ ] Dashboard de base (ordres en cours, alertes stock bas)

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
- [x] Suite de tests OK (75 tests)
- [x] Flux de planification de fabrication implémenté
- [x] Flux de disponibilité matière implémenté
- [x] Flux d'exécution (consommation, réception, mouvements de stock) implémenté
- [x] Cycle de vie des ordres de fabrication implémenté
- [x] Interface web fonctionnelle

> Dernier état vérifié : 75 tests passent