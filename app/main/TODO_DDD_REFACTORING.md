# TODO: Refactoring DDD - Plan d'Action

## Résumé de l'Analyse Architecture DDD

### ✅ Points Positifs Identifiés
1. **Structure en couches** bien définie (domain, application, interface, architecture)
2. **Séparation des contextes métier** (general, private, public, manager, moderator)
3. **Patterns DDD présents** : Repository, Factory, Strategy, Exceptions du domaine
4. **Organisation cohérente** des énumérations et utilitaires dans le domaine

### ⚠️ Problèmes Majeurs Identifiés

#### 1. **Couche Application Manquante**
- Dossier `application/` vide
- Services d'orchestration mélangés dans `service/` racine
- **Action** : Créer la structure application/services/, commands/, queries/, handlers/

#### 2. **Mélange des Couches**
- Django Forms dans le domaine → Déplacer vers interface/ui/forms/
- Django Views dans le domaine → Déplacer vers interface/ui/controllers/
- Infrastructure dans le domaine (Email, Celery) → Déplacer vers architecture/

#### 3. **Couplage Fort Infrastructure**
- Repositories utilisent directement Django ORM
- Services dépendent d'HttpRequest
- **Action** : Créer des interfaces et injection de dépendances

#### 4. **Agrégats Non Définis**
- Relations entre entités floues
- Pas de racines d'agrégats claires
- **Action** : Définir Playlist, User, SoundBoard comme agrégats

## Plan de Refactoring Par Priorité

### Phase 1: Restructuration de Base
1. Créer `application/services/` et déplacer les Application Services
2. Créer `interface/ui/controllers/` et déplacer les vues Django
3. Créer `interface/ui/forms/` et déplacer les Django Forms
4. Déplacer admin.py vers interface/admin/

### Phase 2: Découplage Infrastructure
1. Créer interfaces dans `domain/common/repositories/interfaces/`
2. Déplacer implémentations vers `architecture/persistence/repositories/`
3. Créer `architecture/messaging/` pour email et tasks Celery
4. Implémenter injection de dépendances

### Phase 3: Entités et Agrégats
1. Créer entités domaine dans `domain/common/entities/`
2. Définir agrégats dans `domain/common/aggregates/`
3. Créer Value Objects dans `domain/common/valueobjects/`
4. Implémenter mappers entre entités et modèles Django

### Phase 4: CQRS et Events
1. Créer Commands/Queries dans `application/commands/` et `application/queries/`
2. Implémenter handlers dans `application/handlers/`
3. Créer Domain Events dans `domain/common/events/`
4. Implémenter Event Bus pour communication entre contextes

## Structure Cible Recommandée

```
app/main/
├── application/
│   ├── commands/         # Commands CQRS
│   ├── queries/          # Queries CQRS
│   ├── handlers/         # Command/Query handlers
│   └── services/         # Application Services
├── domain/
│   ├── common/
│   │   ├── aggregates/   # Racines d'agrégats
│   │   ├── entities/     # Entités du domaine
│   │   ├── valueobjects/ # Value Objects
│   │   ├── events/       # Domain Events
│   │   ├── services/     # Domain Services
│   │   ├── repositories/
│   │   │   └── interfaces/ # Abstractions repositories
│   │   ├── exceptions/   # ✅ Déjà bien placé
│   │   ├── enums/        # ✅ Déjà bien placé
│   │   └── specifications/ # Spécifications métier
│   ├── general/          # Bounded Context General
│   ├── private/          # Bounded Context Private
│   ├── public/           # Bounded Context Public
│   ├── manager/          # Bounded Context Manager
│   └── moderator/        # Bounded Context Moderator
├── interface/
│   ├── ui/
│   │   ├── controllers/  # Django Views
│   │   ├── forms/        # Django Forms
│   │   └── templates/    # Templates HTML
│   ├── api/              # API REST/GraphQL
│   └── admin/            # Django Admin
└── architecture/
    ├── persistence/
    │   ├── models/       # ✅ Déjà bien placé
    │   ├── repositories/ # Implémentations Django
    │   └── migrations/   # ✅ Déjà bien placé
    ├── messaging/
    │   ├── email/        # Services email
    │   ├── tasks/        # Tâches Celery
    │   └── events/       # Event handlers
    ├── middleware/       # ✅ Déjà bien placé
    └── config/           # Configuration infrastructure
```

## Bénéfices Attendus

1. **Séparation claire** des responsabilités par couche
2. **Testabilité** améliorée grâce au découplage
3. **Maintenabilité** renforcée par la structure DDD
4. **Scalabilité** facilitée par les bounded contexts
5. **Réutilisabilité** des Domain Services entre contextes

## Notes d'Implémentation

- Utiliser l'injection de dépendances (ex: dependency-injector)
- Implémenter progressivement pour éviter les disruptions
- Maintenir la rétrocompatibilité durant la transition
- Tests unitaires obligatoires pour chaque refactoring
- Documentation des décisions architecturales (ADR)
