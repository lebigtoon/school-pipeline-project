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
