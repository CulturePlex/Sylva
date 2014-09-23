# -*- coding: utf-8 -*-
from pyparsing import *  # noqa


def parse_query(query):
    """
    Search query parser
    """
    start_ = CaselessLiteral('start:')
    match_ = CaselessLiteral('match:')
    where_ = CaselessLiteral('where:')

    startExpr = Group(start_ + dblQuotedString.setParseAction(removeQuotes))
    matchExpr = Group(match_ + dblQuotedString.setParseAction(removeQuotes))
    whereExpr = Group(where_ + dblQuotedString.setParseAction(removeQuotes))
    searchExpr = startExpr.setResultsName('start') \
                    + Optional(matchExpr.setResultsName('match')) \
                    + Optional(whereExpr.setResultsName('where'))

    parsedQuery = searchExpr.parseString(query)

    data = dict()
    data['start'] = parsedQuery['start'][1]
    if 'match' in parsedQuery.keys():
        data['match'] = parsedQuery['match'][1]
    if 'where' in parsedQuery.keys():
            data['where'] = parsedQuery['where'][1]

    return data
