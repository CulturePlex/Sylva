# -*- coding: utf-8 -*-
import string
from random import choice

from django.conf import settings
from django.core.cache import get_cache
from django.utils.importlib import import_module


def get_gdb(graph, using="default"):
    # TODO: Add connection_props like cert_file and key_file
    gdb_key = u"GDB_%s_%s_%s" % (using.upper(), graph.slug, graph.id)
    cache = get_cache("gdb")
    gdb = cache.get(gdb_key, None)
    if not gdb:
        gdb_properties = settings.GRAPHDATABASES[using]
        connection_string = get_connection_string(gdb_properties)
        connection_params = get_connection_params(gdb_properties)
        engine = gdb_properties["ENGINE"]
        module = import_module(engine)
        gdb = module.GraphDatabase(connection_string, connection_params,
                                   graph=graph)
        # We cache all public instances gdb objects
        cache.set(gdb_key, gdb)
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
        uri = "%s://%s:%s@%s:%s/%s/" % (schema, user, password, host, port,
                                        path)
    elif user:
        uri = "%s://%s@%s:%s/%s/" % (schema, user, host, port, path)
    else:
        uri = "%s://%s:%s/%s/" % (schema, host, port, path)
    query = properties.get("QUERY", None)
    if query:
        uri = "%s?%s" % (uri, query)
    fragment = properties.get("FRAGMENT", None)
    if fragment:
        uri = "%s#%s" % (uri, fragment)
    return uri


def get_connection_params(properties):
    return {
        "username": properties.get("USERNAME", None),
        "password": properties.get("PASSWORD", None),
        "key_file": properties.get("KEY_FILE", None),
        "cert_file": properties.get("CERT_FILE", None),
        "options": properties.get("OPTIONS", None),
    }


def deploy(engine, request, user=None, **kwargs):
    try:
        module = import_module(engine)
        return module.deploy(request, user=user, **kwargs)
    except Exception, e:
        raise Exception("Unable to deploy %s: %s" % (engine, e))


def generate_password(length=14, punctuation=False, extra_chars=""):
    chars = string.letters + string.digits + extra_chars
    if punctuation:
        chars += string.punctuation
    return ''.join(choice(chars) for x in range(length))
