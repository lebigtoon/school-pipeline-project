# Image de base minimale : Alpine n'embarque pas perl,
# ce qui supprime les vulnerabilites CRITICAL de perl-base (image -slim)
FROM python:3.11-alpine

# Repertoire de travail
WORKDIR /app

# Installer les dependances en premier (optimisation du cache de couches)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier les sources de l'application
COPY . .

# Utilisateur non-root (securite)
RUN adduser -D appuser && chown -R appuser /app
USER appuser

# Port expose (documentation)
EXPOSE 5000

# Lancer l'application
CMD ["python", "app.py"]
