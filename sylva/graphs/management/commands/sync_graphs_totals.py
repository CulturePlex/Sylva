# -*- coding: utf-8 -*-
from optparse import make_option

from django.core.management.base import BaseCommand
from django.db import transaction

from graphs.models import Graph


class Command(BaseCommand):

    option_list = BaseCommand.option_list + (
        make_option('--graphs',
            type="string",
            dest='graphs',
            help='Allows to set a list of graphs by id or slug.'),
        make_option('--include-types',
            action='store_true',
            dest='include_types',
            default=False,
            help='Also takes into account partial totals per type and per '
                 'allowed relationship. It can be really slow.'),
    )
    help = "\tSynchronize total nodes and total relationships denormalized " \
           "fields to the actual valies in the graph database."
    can_import_settings = True

    def make_list(self, args):
        graphs = []
        sep = " "
        if "," in args:
            sep = ","
        if args:
            for arg in args.split(sep):
                try:
                    try:
                        graph = Graph.objects.get(id=int(arg))
                    except ValueError:
                        graph = Graph.objects.get(slug=arg)
                    graphs.append(graph)
                except Graph.DoesNotExist:
                    self.stderr.write("Graph %s not found!\n" % arg)
        return graphs

    def handle(self, *args, **options):
        graphs = self.make_list(options.get("graphs", ""))
        if not graphs:
            graphs = Graph.objects.all()
        self.stdout.write("Processing %s graphs...\n" % len(graphs))
        for graph in graphs:
            self.stdout.write("\tGraph [%s] '%s': " % (graph.id, graph.slug))
            with transaction.commit_on_success():
                graph.data.total_nodes = graph.nodes.count()
                graph.data.total_relationships = graph.relationships.count()
                self.stdout.write("%s nodes, %s relationships\n" \
                                  % (graph.data.total_nodes,
                                     graph.data.total_relationships))
                graph.data.save()
                if graph.schema and options.get("include_types", False):
                    for nodetype in graph.schema.nodetype_set.all():
                        nodetype.total = nodetype.count()
                        nodetype.save()
                    for reltype in graph.schema.relationshiptype_set.all():
                        reltype.total = reltype.count()
                        reltype.save()
        self.stdout.write("Done\n")
