from django.conf import settings
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from guardian.shortcuts import assign_perm, remove_perm

from graphs.models import Graph


NEW_PUBLIC_PERMS = [
    'view_graph_reports',
    'view_graph_queries',
    'view_graph_analytics'
]

NEW_PERMS = [
    'add_graph_reports',
    'change_graph_reports',
    'delete_graph_reports',
    'add_graph_queries',
    'change_graph_queries',
    'delete_graph_queries',
    'add_graph_analytics',
    'delete_graph_analytics'
]


class Command(BaseCommand):

    def handle(self, *args, **options):
        graphs = Graph.objects.all()
        anonymous = User.objects.get(id=settings.ANONYMOUS_USER_ID)

        for graph in graphs:
            owner = graph.owner

            for perm in NEW_PERMS:

                assign_perm(perm, owner, graph)
                self.stdout.write("Assigned perm on {}: {} to {}".format(
                    graph, perm, owner))

            for perm in NEW_PUBLIC_PERMS:

                assign_perm(perm, owner, graph)
                self.stdout.write("Assigned perm on {}: {} to {}".format(
                    graph, perm, owner))

                if graph.public:
                    assign_perm(perm, anonymous, graph)
                    self.stdout.write("Assigned perm on {}: {} to {}".format(
                        graph, perm, owner))

                elif anonymous.has_perm(perm, graph):
                    remove_perm(perm, anonymous, graph)
                    self.stdout.write("Removed perm on {}: {} from {}".format(
                        graph, perm, anonymous))
