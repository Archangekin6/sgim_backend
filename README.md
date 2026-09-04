# SGIM — Backend

Système de Gestion des Incidents Maritimes — MRCC Abidjan / MRSC San Pedro.

API REST construite avec Django + Django REST Framework, authentification JWT, base de données MySQL.

## Stack technique

- Python 3.12 + Django
- Django REST Framework + Simple JWT (authentification par token)
- MySQL (via XAMPP en développement)
- django-unfold (thème admin)
- drf-spectacular (documentation API interactive)

## Prérequis

- Python 3.10+ installé
- [XAMPP](https://www.apachefriends.org/) installé (pour MySQL + phpMyAdmin)
- Un éditeur de code (VS Code recommandé)

## Installation

### 1. Cloner le projet

```bash
git clone <url-du-repo>
cd sgim_backend
```

### 2. Créer et activer l'environnement virtuel

```bash
python -m venv venv
```

Windows (PowerShell) :

```powershell
venv\Scripts\activate
```

Mac / Linux :

```bash
source venv/bin/activate
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 4. Créer la base de données

- Démarre le module **MySQL** dans le panneau de contrôle XAMPP
- Va sur `http://localhost/phpmyadmin`
- Crée une nouvelle base nommée `sgim`, interclassement `utf8mb4_unicode_ci`

### 5. Configurer les variables d'environnement

Copie `.env.example` vers `.env` :

```bash
cp .env.example .env
```

Remplis `.env` avec tes propres valeurs (mot de passe MySQL local, identifiants email si tu dois tester l'envoi de rapports).

### 6. Appliquer les migrations et initialiser les données de base

```bash
python manage.py migrate
python manage.py seed_references
python manage.py createsuperuser
```

**Important** : après `createsuperuser`, connecte-toi sur `/admin/`, va dans **Users**, ouvre ton compte, et mets le champ **Role** sur **Super Administrateur** (par défaut il est créé en "Opérateur").

### 7. Lancer le serveur

```bash
python manage.py runserver
```

## Accès utiles

| Ressource                               | URL                                        |
| --------------------------------------- | ------------------------------------------ |
| Interface d'administration              | http://127.0.0.1:8000/admin/               |
| Documentation API interactive (Swagger) | http://127.0.0.1:8000/api/docs/            |
| Documentation API alternative (Redoc)   | http://127.0.0.1:8000/api/redoc/           |
| Connexion (obtenir un token JWT)        | POST http://127.0.0.1:8000/api/auth/token/ |

## Authentification (pour le développeur frontend)

1. `POST /api/auth/token/` avec `{"username": "...", "password": "..."}` → retourne `access` et `refresh`
2. Envoyer `access` dans l'en-tête de chaque requête : `Authorization: Bearer <token>`
3. Quand `access` expire (8h), échanger `refresh` contre un nouveau via `POST /api/auth/token/refresh/`

## Règle importante : les listes déroulantes

Tous les champs de type "liste déroulante" (catégorie d'alerte, priorité, type de navire, etc.) attendent l'**identifiant (UUID)** de l'entrée choisie, jamais son libellé texte. Récupérer les options via `GET /api/references/...` avant de construire un formulaire.

## Structure des applications

| App          | Rôle                                                                      |
| ------------ | ------------------------------------------------------------------------- |
| `accounts`   | Comptes utilisateurs (Super Admin / Admin / Opérateur) + équipes de quart |
| `centers`    | MRCC Abidjan / MRSC San Pedro                                             |
| `references` | Toutes les listes déroulantes                                             |

|
