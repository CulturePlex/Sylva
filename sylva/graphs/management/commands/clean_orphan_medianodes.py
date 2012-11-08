# -*- coding: utf-8 -*-
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.db import transaction

from data.models import MediaNode

from engines.gdb.backends import NodeDoesNotExist


class Command(BaseCommand):
    help = "\tDelete empty MediaNodes with no files nor links, and orphan " \
           "MediaNodes with no nodes existing in the backend"

    def handle(self, *args, **options):
        file_name = '__emptydummyfile__'
        file_path = ''
        if default_storage.exists(file_name):
            file_path = default_storage.open(file_name)
        else:
            file_path = default_storage.save(file_name, ContentFile('_'))

        self.stdout.write("Searching for empty and orphan MediaNodes...\n")
        for media_node in MediaNode.objects.all():
            with transaction.commit_on_success():
                if not media_node.links.exists() and \
                        not media_node.files.exists():
                    self.stdout.write("Deleting empty MediaNode [%s]\n"
                                      % media_node.id)
                    media_node.delete()
                else:
                    try:
                        gdb = media_node.data.get_gdb()
                        gdb.get_node_label(media_node.node_id)
                    except NodeDoesNotExist:
                        self.stdout.write("Deleting orphan MediaNode [%s]\n"
                                          % media_node.id)
                        try:
                            media_node.delete()
                        except Exception:
                            for file in media_node.files.all():
                                file.media_file = file_name
                                file.save()
                            media_node.delete()
        default_storage.delete(file_path)
        self.stdout.write("Done\n")
