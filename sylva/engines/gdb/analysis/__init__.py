# -*- coding: utf-8 -*-


class BaseAnalysis(object):
    """
    Base class for Analytics with the common API to implement.
    """

    def pagerank(graph, analytic):
        """
        Pagerank method
        """
        raise NotImplementedError("Method has to be implemented")

    def connected_components(graph, analytic):
        """
        Connected components method
        """
        raise NotImplementedError("Method has to be implemented")

    def dump(graph, analytic):
        """
        Dump the content of the graph into an edgelist file
        """
        raise NotImplementedError("Method has to be implemented")
