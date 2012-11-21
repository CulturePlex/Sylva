#!/bin/bash
if [ -f "$1.py" ]; then
    echo "Using $1 as settings file..."
    settings="--settings=$1"
elif [ -z "$1"]; then
    settings=""
else
    echo "Sorry, $1 is not a regular file"
    exit;
fi
python ./manage.py dumpdata $settings --format=json --indent=4 auth > backups/auth.json
python ./manage.py dumpdata $settings --format=json --indent=4 contenttypes > backups/contenttypes.json
python ./manage.py dumpdata $settings --format=json --indent=4 sessions > backups/sessions.json
python ./manage.py dumpdata $settings --format=json --indent=4 sites > backups/sites.json
python ./manage.py dumpdata $settings --format=json --indent=4 messages > backups/messages.json
python ./manage.py dumpdata $settings --format=json --indent=4 umessages > backups/umessages.json
python ./manage.py dumpdata $settings --format=json --indent=4 guardian > backups/guardian.json
python ./manage.py dumpdata $settings --format=json --indent=4 easy_thumbnails > backups/easy_thumbnails.json
python ./manage.py dumpdata $settings --format=json --indent=4 base > backups/base.json
python ./manage.py dumpdata $settings --format=json --indent=4 data > backups/data.json
python ./manage.py dumpdata $settings --format=json --indent=4 graphs > backups/graphs.json
python ./manage.py dumpdata $settings --format=json --indent=4 schemas > backups/schemas.json
python ./manage.py dumpdata $settings --format=json --indent=4 engines > backups/engines.json
python ./manage.py dumpdata $settings --format=json --indent=4 accounts > backups/accounts.json
python ./manage.py dumpdata $settings --format=json --indent=4 tools > backups/tools.json
python ./manage.py dumpdata $settings --format=json --indent=4 search > backups/search.json
python ./manage.py dumpdata $settings --format=json --indent=4 operators > backups/operators.json
python ./manage.py dumpdata $settings --format=json --indent=4 south > backups/south.json
