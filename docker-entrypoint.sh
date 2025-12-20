#!/bin/bash
set -e

echo "Attente de la base de données PostgreSQL..."
while ! pg_isready -h ${POSTGRES_HOST:-db} -p ${POSTGRES_PORT:-5432} -U ${POSTGRES_USER:-postgres}; do
  sleep 1
done

echo "PostgreSQL est prêt!"


# echo "Application des migrations de la base de données..."
# python manage.py migrate --noinput

# echo "Verification/Creation du superutilisateur par defaut..."
# python manage.py create_default_admin

echo "Démarrage de l'application..."
exec "$@"
#!/bin/bash
set -e

echo "Attente de la base de données PostgreSQL..."
while ! pg_isready -h ${POSTGRES_HOST:-db} -p ${POSTGRES_PORT:-5432} -U ${POSTGRES_USER:-postgres}; do
  sleep 1
done

echo "PostgreSQL est prêt!"

echo "Démarrage de l'application..."
exec "$@"
# echo "Application des migrations de la base de données..."