# APP DEPLOYEE SECURISEE ICI  : https://efrei-pipeline.quentin-doulcet.fr/todos

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

## Publier l'image sur Docker Hub

L'image est versionnée avec deux tags : un tag de version immuable (`v1.0.0`)
et le tag mobile `latest`.

```bash
# Se connecter à Docker Hub
docker login

# Tagger l'image construite localement avec le namespace Docker Hub
docker tag todo-api:latest <utilisateur>/todo-api:v1.0.0
docker tag todo-api:latest <utilisateur>/todo-api:latest

# Pousser les deux tags
docker push <utilisateur>/todo-api:v1.0.0
docker push <utilisateur>/todo-api:latest
```

Repository : `https://hub.docker.com/r/<utilisateur>/todo-api`

---

## Déploiement

### 1. Docker (sur un serveur)

```bash
docker pull <utilisateur>/todo-api:v1.0.0

docker run -d \
  -p 80:5000 \
  -e DB_PATH=/data/todos.db \
  -v todo-data:/data \
  --restart unless-stopped \
  --name todo-app <utilisateur>/todo-api:v1.0.0
```

> `DB_PATH` pointe vers un volume nommé pour persister la base SQLite entre
> les redémarrages (évite de bind-monter un fichier inexistant).

### 2. Docker Compose

`docker-compose.yml` :

```yaml
version: '3.8'
services:
  todo-api:
    image: <utilisateur>/todo-api:v1.0.0
    ports:
      - "80:5000"            # hote:conteneur (l'app ecoute sur 5000)
    environment:
      - DB_PATH=/data/todos.db
    volumes:
      - todo-data:/data
    restart: unless-stopped

volumes:
  todo-data:
```

```bash
docker compose up -d
```

### 3. Kubernetes

`k8s-deployment.yml` :

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: todo-api
spec:
  replicas: 2
  selector:
    matchLabels:
      app: todo-api
  template:
    metadata:
      labels:
        app: todo-api
    spec:
      containers:
        - name: todo-api
          image: <utilisateur>/todo-api:v1.0.0
          ports:
            - containerPort: 5000
          env:
            - name: DB_PATH
              value: /data/todos.db
          volumeMounts:
            - name: todo-data
              mountPath: /data
      volumes:
        - name: todo-data
          emptyDir: {}
---
apiVersion: v1
kind: Service
metadata:
  name: todo-api
spec:
  selector:
    app: todo-api
  ports:
    - port: 80
      targetPort: 5000
  type: ClusterIP
```

```bash
kubectl apply -f k8s-deployment.yml
```

> Déploiement actuel : l'application tourne sur **Dokploy** (reverse proxy
> Traefik), avec le *container port* configuré sur `5000` et HTTPS automatique.

---

## Bonnes pratiques appliquées

- **Tagging** : tag de version immuable (`v1.0.0`) en plus de `latest`, pour
  garantir des déploiements reproductibles.
- **Image minimale** : base `python:3.11-alpine` → surface d'attaque réduite et
  **0 vulnérabilité CRITICAL** (vérifié avec Trivy).
- **Utilisateur non-root** : le conteneur s'exécute en tant que `appuser`.
- **`.dockerignore`** : exclut la base de données, les rapports, les SBOM et les
  fichiers de test → image plus légère et sans données sensibles embarquées.
- **SBOM** : génération d'un inventaire des composants (SPDX + CycloneDX) pour la
  traçabilité de la chaîne d'approvisionnement.
- **Persistance** : base SQLite externalisée via un volume (`DB_PATH`).
- **Pas de secret dans l'image** : aucune variable sensible (token, mot de passe)
  n'est intégrée à l'image ni versionnée.
- **HTTPS** : terminaison TLS assurée par le reverse proxy en production.

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
