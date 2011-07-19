# -*- coding: utf-8 -*-
from django.conf import settings
from django.utils.importlib import import_module
from django.utils.translation import gettext as _


def get_gdb(graph, using="default"):
    gdb_properties = settings.GRAPHDATABASES[using]
    connection_string = get_connection_string(gdb_properties)
    engine = gdb_properties["ENGINE"]
    module = import_module(engine)
    gdb = module.GraphDatabase(connection_string, graph=graph)
    return gdb


def get_connection_string(properties):
    schema = properties["SCHEMA"]
    host = properties["HOST"]
    port = properties["PORT"]
    path = (properties.get("PATH", "")
            or properties.get("NAME", "")).strip("/")
    user = properties["USER"]
    password = properties["PASSWORD"]
    if user and password:
        return "%s://%s:%s@%s:%s/%s/" % (schema, user, password, host, port,
                                         path)
    elif user:
        return "%s://%s@%s:%s/%s/" % (schema, user, host, port, path)
    else:
        return "%s://%s:%s/%s/" % (schema, host, port, path)


def get_engines():
    # TODO: Returns a dict binding the engines names with the proper module
    # {
    #   'neo4j': {
    #         'module': 'engines.gdb.backends.neo4j',
    #         'url': 'http://neo4j.org/',
    #   },
    # }
    pass
