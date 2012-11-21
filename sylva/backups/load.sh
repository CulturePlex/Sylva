#!/bin/bash
if [ -f "$1.py" ]; then
    echo "Using $1 as settings file..."
    settings="--settings=$1"
    backend=`python -c "from $1 import *; print DATABASES['default']['ENGINE']"`
elif [ -z "$1"]; then
    settings="--settings=settings"
    backend=`python -c "from settings import *; print DATABASES['default']['ENGINE']"`
else
    echo "Sorry, $1 is not a regular file"
    exit;
fi
python manage.py syncdb $settings --noinput
python manage.py migrate $settings
echo "Before loading, check that tables 'auth_permission', 'django_content_type', 'accounts_account' and 'accounts_userprofile' are empty"

if [ "$backend" == "django.db.backends.sqlite3" ]; then
    echo "SQLite..."
    echo "
    TRUNCATE CASCADE FROM accounts_userprofile WHERE 1=1;
    TRUNCATE CASCADE FROM accounts_account WHERE 1=1;
    TRUNCATE CASCADE FROM auth_permission WHERE 1=1;
    TRUNCATE CASCADE FROM django_content_type WHERE 1=1;
    " | python manage.py dbshell $settings
elif [ "$backend" == "django.db.backends.postgresql_psycopg2" ]; then
    echo "PostgreSQL..."
    echo "Remember the ALTER SEQUENCE command in PostgreSQL (try select 'pg_stat_reset();')"
    echo "
    TRUNCATE TABLE accounts_userprofile CASCADE;
    TRUNCATE TABLE accounts_account CASCADE;
    TRUNCATE TABLE auth_permission CASCADE;
    TRUNCATE TABLE django_content_type CASCADE;
    ALTER SEQUENCE accounts_userprofile_id_seq RESTART WITH 1;
    ALTER SEQUENCE accounts_account_id_seq RESTART WITH 1;
    " | python manage.py dbshell $settings
else
    echo "Please, add 'django.db.backends.sqlite3' or 'django.db.backends.postgresql_psycopg2' to your settings"
    exit;
fi
python manage.py loaddata $settings backups/contenttypes.json
python manage.py loaddata $settings backups/sessions.json
python manage.py loaddata $settings backups/sites.json
python manage.py loaddata $settings backups/messages.json
python manage.py loaddata $settings backups/umessages.json
python manage.py loaddata $settings backups/south.json
python manage.py loaddata $settings backups/auth.json
python manage.py loaddata $settings backups/guardian.json
python manage.py loaddata $settings backups/accounts.json
python manage.py loaddata $settings backups/easy_thumbnails.json
python manage.py loaddata $settings backups/base.json
python manage.py loaddata $settings backups/engines.json
python manage.py loaddata $settings backups/data.json
python manage.py loaddata $settings backups/schemas.json
python manage.py loaddata $settings backups/graphs.json
python manage.py loaddata $settings backups/tools.json
python manage.py loaddata $settings backups/search.json
python manage.py loaddata $settings backups/operators.json

