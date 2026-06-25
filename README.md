# Todo API

API REST simple pour gérer des tâches (todos), construite avec Flask et SQLite.

---

## Installation

### Prérequis

- Python 3.8+

### Étapes

```bash
# Cloner le dépôt
git clone <url-du-depot>
cd todo-api

# Créer et activer un environnement virtuel
python3 -m venv env
source env/bin/activate

# Installer les dépendances
pip install -r requirements.txt
```

---

## Lancer l'application

```bash
python app.py
```

L'API est accessible sur `http://localhost:5000`.

---

## Exécuter les tests

```bash
pytest test_app.py -v
```

Résultat attendu :

```
test_app.py::test_get_todos_empty PASSED
test_app.py::test_create_todo PASSED
test_app.py::test_create_todo_missing_title PASSED
test_app.py::test_get_todo_by_id PASSED
test_app.py::test_get_todo_not_found PASSED
test_app.py::test_update_todo PASSED
test_app.py::test_update_todo_not_found PASSED
test_app.py::test_delete_todo PASSED
test_app.py::test_delete_todo_not_found PASSED
```

---

## Conteneurisation Docker

L'application est packagée dans une image Docker basée sur `python:3.11-alpine`
(image minimale, exécution en utilisateur non-root).

### Construire l'image

```bash
docker build -t todo-api:latest .
```

### Lancer le conteneur

```bash
docker run -d -p 5000:5000 --name todo-api todo-api:latest
```

L'API est alors accessible sur `http://localhost:5000`.

```bash
# Vérifier que l'API répond
curl http://localhost:5000/todos

# Voir les logs / arrêter le conteneur
docker logs todo-api
docker rm -f todo-api
```

> Le fichier `.dockerignore` exclut la base `todos.db`, les rapports et les SBOM
> afin qu'ils ne soient pas embarqués dans l'image.

---

## Scan de sécurité avec Trivy

L'image est analysée avec [Trivy](https://github.com/aquasecurity/trivy) pour
détecter les vulnérabilités connues (OS + dépendances Python).

```bash
# Scan affiché dans la console
trivy image todo-api:latest

# Limiter aux vulnérabilités élevées et critiques
trivy image --severity HIGH,CRITICAL todo-api:latest

# Générer les rapports de rendu
trivy image --format json  -o trivy-report.json todo-api:latest
trivy image --format table -o trivy-report.txt  todo-api:latest
```

Le choix de l'image `alpine` (au lieu de `slim`) supprime les vulnérabilités
**CRITICAL** issues de `perl-base`. Résultat : **0 vulnérabilité CRITICAL**.

---

## Génération du SBOM

Le SBOM (Software Bill of Materials) liste tous les composants de l'image. Il est
généré avec Trivy aux formats **SPDX** et **CycloneDX**.

```bash
# Format SPDX
trivy image --format spdx-json -o sbom.spdx.json todo-api:latest

# Format CycloneDX
trivy image --format cyclonedx -o sbom.cdx.json todo-api:latest
```

---

## Endpoints de l'API

| Méthode | Endpoint      | Description                    |
|---------|---------------|--------------------------------|
| GET     | `/todos`      | Récupère toutes les tâches     |
| POST    | `/todos`      | Crée une nouvelle tâche        |
| GET     | `/todos/<id>` | Récupère une tâche par son ID  |
| PUT     | `/todos/<id>` | Met à jour une tâche existante |
| DELETE  | `/todos/<id>` | Supprime une tâche             |

---

### GET /todos

Récupère la liste de toutes les tâches.

```bash
curl http://localhost:5000/todos
```

Réponse `200` :
```json
[
  {
    "id": 1,
    "title": "Faire les courses",
    "description": "Lait, pain, oeufs",
    "done": false,
    "created_at": "2026-06-25 10:00:00"
  }
]
```

---

### POST /todos

Crée une nouvelle tâche. Le champ `title` est obligatoire.

```bash
curl -X POST http://localhost:5000/todos \
  -H "Content-Type: application/json" \
  -d '{"title": "Faire les courses", "description": "Lait, pain, oeufs"}'
```

Réponse `201` :
```json
{
  "id": 1,
  "title": "Faire les courses",
  "description": "Lait, pain, oeufs",
  "done": false
}
```

Réponse `400` si `title` est absent :
```json
{
  "error": "Title is required"
}
```

---

### GET /todos/\<id\>

Récupère une tâche par son ID.

```bash
curl http://localhost:5000/todos/1
```

Réponse `200` :
```json
{
  "id": 1,
  "title": "Faire les courses",
  "description": "Lait, pain, oeufs",
  "done": false,
  "created_at": "2026-06-25 10:00:00"
}
```

Réponse `404` si introuvable :
```json
{
  "error": "Todo not found"
}
```

---

### PUT /todos/\<id\>

Met à jour une tâche existante.

```bash
curl -X PUT http://localhost:5000/todos/1 \
  -H "Content-Type: application/json" \
  -d '{"title": "Faire les courses", "description": "Lait, pain, oeufs", "done": true}'
```

Réponse `200` :
```json
{
  "message": "Todo updated"
}
```

Réponse `404` si introuvable :
```json
{
  "error": "Todo not found"
}
```

---

### DELETE /todos/\<id\>

Supprime une tâche.

```bash
curl -X DELETE http://localhost:5000/todos/1
```

Réponse `200` :
```json
{
  "message": "Todo deleted"
}
```

Réponse `404` si introuvable :
```json
{
  "error": "Todo not found"
}
```
