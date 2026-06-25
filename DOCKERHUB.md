# Todo API

API REST minimale pour gérer des tâches (todos), construite avec **Flask** et
**SQLite**. Image basée sur `python:3.11-alpine`, exécutée en utilisateur
non-root, et scannée avec Trivy (**0 vulnérabilité CRITICAL**).

---

## Utilisation

### Récupérer l'image

```bash
docker pull <utilisateur>/todo-api:latest
```

### Lancer le conteneur

```bash
docker run -d -p 5000:5000 --name todo-api <utilisateur>/todo-api:latest
```

L'API est accessible sur `http://localhost:5000`.

```bash
# Créer une tâche
curl -X POST http://localhost:5000/todos \
  -H "Content-Type: application/json" \
  -d '{"title": "Faire les courses", "description": "Lait, pain"}'

# Lister les tâches
curl http://localhost:5000/todos
```

### Persister la base de données

La base SQLite est stockée dans le conteneur. Pour la conserver entre deux
exécutions, montez un volume et pointez `DB_PATH` dessus :

```bash
docker run -d -p 5000:5000 \
  -e DB_PATH=/data/todos.db \
  -v todo-data:/data \
  --name todo-api <utilisateur>/todo-api:latest
```

---

## Variables d'environnement

| Variable  | Défaut     | Description                                            |
|-----------|------------|--------------------------------------------------------|
| `DB_PATH` | `todos.db` | Chemin du fichier de base de données SQLite utilisé.   |

---

## Ports exposés

| Port   | Protocole | Description                          |
|--------|-----------|--------------------------------------|
| `5000` | TCP/HTTP  | Port d'écoute de l'API Flask.        |

---

## Endpoints

| Méthode | Endpoint      | Description                    |
|---------|---------------|--------------------------------|
| GET     | `/todos`      | Récupère toutes les tâches     |
| POST    | `/todos`      | Crée une nouvelle tâche        |
| GET     | `/todos/<id>` | Récupère une tâche par son ID  |
| PUT     | `/todos/<id>` | Met à jour une tâche existante |
| DELETE  | `/todos/<id>` | Supprime une tâche             |

---

## Tags

- `latest` — dernière version stable (Python 3.11, Alpine).
