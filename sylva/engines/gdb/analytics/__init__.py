# -*- coding: utf-8 -*-


class BaseAnalytics(object):
    """
    Base class for Analytics with the common API to implement.
    """

    def pagerank(graph, analytic):
        """
        Pagerank method
        """
        raise NotImplementedError("Method has to be implemented")

    def dump_graphchi_edgelist(graph):
        """
        Dump the content of the graph into an edgelist file
        """
        raise NotImplementedError("Method has to be implemented")

    def dump_graphchi_adjlist(graph):
        """
        Dump the content of the graph into an adjlist file
        """
        raise NotImplementedError("Method has to be implemented")
