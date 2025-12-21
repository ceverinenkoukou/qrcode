#!/bin/bash
set -e

echo "Attente de la base de données PostgreSQL..."
while ! PGPASSWORD=vN7ukQ75uUh1xXUrGUoqdqEevPyP2DQo psql -h dpg-d53r0u95pdvs73fodibg-a.oregon-postgres.render.com -U maraige_db_user maraige_db; do
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
while ! PGPASSWORD=vN7ukQ75uUh1xXUrGUoqdqEevPyP2DQo psql -h dpg-d53r0u95pdvs73fodibg-a.oregon-postgres.render.com -U maraige_db_user maraige_db; do
  sleep 1
done

echo "PostgreSQL est prêt!"

echo "Démarrage de l'application..."
exec "$@"
# echo "Application des migrations de la base de données..."