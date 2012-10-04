# -*- coding: utf-8 -*-
# Based on: https://github.com/scholrly/lucene-querybuilder/blob/master/lucenequerybuilder/query.py


class Q(object):
    """ Q is a query builder for the Neo4j Cypher language backend"""

    specialchars = r'+-!(){}[]^"~*?\:'
    doublechars = '&&||'

    def __init__(self, property=None, match=None, lookup=None, nullable=False,
                 **kwargs):
        self._and = None
        self._or = None
        self._not = None
        self.inrange = None
        self.exrange = None
        self.nullable = nullable
        # Q("Nombre de la Obra", startswith=, nullable=True)
        if kwargs.get('inrange'):
            self.inrange = tuple(kwargs['inrange'])
        elif kwargs.get('exrange'):
            self.exrange = tuple(kwargs['exrange'])
        elif kwargs.get('fuzzy'):
            fuzzy = kwargs['fuzzy']
            if Q._check_whitespace(fuzzy):
                raise ValueError('No whitespace allowed in fuzzy queries.')
            if isinstance(fuzzy, basestring):
                self.fuzzy = (fuzzy, None)
            elif hasattr(fuzzy, '__iter__') and len(fuzzy) == 2\
                    and 0 <= float(fuzzy[1]) <= 1:
                self.fuzzy = tuple(fuzzy)
            else:
                raise ValueError('fuzzy should be a string or two element '
                                 'term/similarity ratio sequence. The '
                                 'ratio, cast to float,  should be between'
                                 ' 0 and 1.')

    @property
    def fielded(self):
        """Returns whether any part of the query has a field."""
        return self.field is not None or\
                any(Q._has_field(l) for l in [self.must, self.must_not,
                                              self.should, self._and, self._or,
                                              self._not])
    @staticmethod
    def _has_field(val):
        if hasattr(val, '__iter__'):
            return any(Q._has_field(t) for t in val)
        else:
            return hasattr(val, 'field') and val.field is not None


    @classmethod
    def _check_whitespace(cls, s):
        import string
        if isinstance(s, basestring):
            for c in string.whitespace:
                if c in s:
                    return True
        return False

    def _escape(self, s):
        if isinstance(s, basestring):
            rv = ''
            specialchars = self.specialchars.translate(None,'*?')\
                    if self.allow_wildcard else self.specialchars
            for c in s:
                if c in specialchars:
                    rv += '\\' + c
                else:
                    rv += c
            return rv
        return s

    def _make_and(q1, q2):
        q = Q()
        q._and = (q1, q2)
        return q

    def _make_not(q1):
        q = Q()
        q._not = q1
        return q

    def _make_or(q1, q2):
        q = Q()
        q._or = (q1, q2)
        return q

    def _make_must(q1):
        q = Q()
        q.must.append(q1)
        return q

    def _make_must_not(q1):
        q = Q()
        q.must_not.append(q1)
        return q

    def __and__(self, other):
        return Q._make_and(self, other)

    def __or__(self, other):
        return Q._make_or(self, other)

    def __invert__(self):
        return Q._make_not(self)

    def __pos__(self):
        return Q._make_must(self)

    def __neg__(self):
        return Q._make_must_not(self)

    def __add__(self, other):
        return self | Q._make_must(other)

    def __sub__(self, other):
        return self | Q._make_must_not(self)

    def __eq__(self, other):
        return hash(self) == hash(other)

    def __hash__(self):
        return hash((tuple(self.should), tuple(self.must),tuple(self.must_not),
                     self.exrange, self.inrange, self.field, self.fuzzy))

    def __str__(self):
        if self._and is not None:
            rv = '(' + str(self._and[0]) + ' AND ' + str(self._and[1]) + ')'
        elif self._not is not None:
            rv = 'NOT ' + str(self._not)
        elif self._or is not None:
            if self._or[0].field is not None or self._or[1].field is not None\
               or self._or[0].must or self._or[1].must or self._or[0].must_not\
               or self._or[1].must_not:
                rv = str(self._or[0]) + ' ' + str(self._or[1])
            else:
                rv = '(' + str(self._or[0]) + ' OR ' + str(self._or[1]) + ')'
        elif self.inrange is not None:
            rv = '[' + str(self.inrange[0]) + ' TO ' + str(self.inrange[1]) + ']'
        elif self.exrange is not None:
            rv = '{' + str(self.exrange[0]) + ' TO ' + str(self.exrange[1]) + '}'
        elif self.fuzzy:
            try:
                rv = '{0!s}~'.format(self.fuzzy[0])
            except AttributeError:
                rv = '%s~' % self.fuzzy[0]
            if self.fuzzy[1] is not None:
                try:
                    rv += '{0:.3f}'.format(self.fuzzy[1])
                except AttributeError:
                    rv += '%.3f' % self.fuzzy[1]

        else:
            rv = ''
            for o in self.must:
                rv += '+' + str(o)
            for o in self.must_not:
                rv += str(o)
            for o in self.should:
                rv += str(o)

        if self.field is not None:
            try:
                rv = '{0}:({1})'.format(self.field, rv)
            except AttributeError:
                rv = '%s:(%s)' % (self.field, rv)
        return rv


    def __unicode__(self):
        if self._and is not None:
            rv = u'(' + unicode(self._and[0]) + u' AND ' + unicode(self._and[1]) + u')'
        elif self._not is not None:
            rv = u'NOT ' + unicode(self._not)
        elif self._or is not None:
            if self._or[0].field is not None or self._or[1].field is not None\
               or self._or[0].must or self._or[1].must or self._or[0].must_not\
               or self._or[1].must_not:
                rv = unicode(self._or[0]) + u' ' + unicode(self._or[1])
            else:
                rv = u'(' + unicode(self._or[0]) + u' OR ' + unicode(self._or[1]) + u')'
        elif self.inrange is not None:
            rv = u'[' + unicode(self.inrange[0]) + u' TO ' + unicode(self.inrange[1]) + u']'
        elif self.exrange is not None:
            rv = u'{' + unicode(self.exrange[0]) + u' TO ' + unicode(self.exrange[1]) + u'}'
        elif self.fuzzy:
            try:
                rv = u'{0!s}~'.format(self.fuzzy[0])
            except AttributeError:
                rv = u'%s~' % self.fuzzy[0]
            if self.fuzzy[1] is not None:
                try:
                    rv += '{0:.3f}'.format(self.fuzzy[1])
                except AttributeError:
                    rv += '%.3f' % self.fuzzy[1]
        else:
            rv = u''
            for o in self.must:
                rv += u'+' + unicode(o)
            for o in self.must_not:
                rv += unicode(o)
            for o in self.should:
                rv += unicode(o)

        if self.field is not None:
            try:
                rv = u'{0}:({1})'.format(self.field, rv)
            except AttributeError:
                rv = u'%s:(%s)' % (self.field, rv)
        return rv
