import parsley
#from pprint import pprint


class Counter(dict):

    def __init__(self, *args, **kwargs):
        super(Counter, self).__init__(*args, **kwargs)
        self.types = dict()

    def get(self, type, default=None):
        if default and type not in self.types:
            return default
        self.types.setdefault(type, -1)
        self.types[type] += 1
        return self.types[type]


class QueryParser(object):

    def __init__(self, graph):
        self.graph = graph
        self.schema = graph.schema
        self.counter = Counter()
        self.types = {}

    def parse(self, query):
        grammar = self.build_grammar()
        query_dict = grammar(query).dict()
        return query_dict

    def build_grammar(self):
        self.counter = Counter()
        self.types = {}
        node_type_rules = self.get_node_type_rules()
        relationship_type_rules = self.get_relationship_type_rules()
        rules = ["""
facet = (('with' | 'that' ws ('has' | 'have') | 'who' ws ('has' | 'have')) (ws ('a' | 'the'))?) -> ""
conditions = "and" -> "and"
           | "or" -> "or"
           | -> "and"
op = "that" ws "starts" ws "with" ws -> 'startswith'
   | "that" ws "ends" ws "with" ws  -> 'endswith'
   | "greater" ws "than" ws  -> 'gt'
   | "lower" ws "than" ws  -> 'lt'
   | -> 'iexact'
        """]
        rules += node_type_rules
        rules += relationship_type_rules
        rules += ["""
dict = n_types:item
     -> item
     | n_types:source ws n_types:rel ws n_types:target
     -> {
        "origin": [source["origin"], rel, target["origin"]],
        "pattern": {"source": source["origin"], "target": target["origin"], "relation": rel},
        "conditions": source["conditions"] + target["conditions"],
        "result": [source["result"], target["result"]],
     }
     | -> None
        """]
        return "\n".join(rules)

    def get_relationship_type_rules(self):
        rules = []

        rel_type_rule_codes = []
        rules_template = u"""
r{rel_type_id} = ('{rel_type_names}')
        -> {{'type': types.get({rel_type_id}), 'alias': "r{rel_type_id}_{{0}}".format(counter.get('r{rel_type_id}', 0))}}
r{rel_type_id}_facet = (conditions:cond)? (ws ("who" | "that")?)? ws r{rel_type_id}:rel ws ("a" | "the")? ws
        -> {{'origin': rel, 'result': {{"alias": t['alias'], "properties": r}}}}
        """
        rel_types = self.schema.relationshiptype_set.all().select_related()
        for rel_type in rel_types:
            self.types[rel_type.id] = rel_type
            rel_type_rule_codes.append(u"r{0}_facet".format(rel_type.id))
            properties = []
            for prop in rel_type.properties.all().values("key"):
                property_name = prop["key"]
                property_names = [
                    property_name,
                    property_name.lower(),
                    property_name.upper(),
                    property_name.capitalize(),
                    u"{0}s".format(property_name),
                    u"{0}s".format(property_name).lower(),
                    u"{0}s".format(property_name).upper(),
                    u"{0}s".format(property_name).capitalize()
                ]
                rule = u"('{0}') -> '{1}'"
                property_rule = rule.format(
                    u"' | '".join(property_names),
                    property_name
                )
                properties.append(property_rule)
            rel_type_names = [rel_type.name, rel_type.name.lower(),
                              rel_type.name.upper(),
                              rel_type.name.capitalize()]
            if rel_type.plural_name:
                rel_type_names += [rel_type.plural_name,
                                   rel_type.plural_name.lower(),
                                   rel_type.plural_name.upper(),
                                   rel_type.plural_name.capitalize()]
            else:
                rel_type_names += [u"{0}s".format(rel_type.name),
                                   u"{0}s".format(rel_type.name).lower(),
                                   u"{0}s".format(rel_type.name).upper(),
                                   u"{0}s".format(rel_type.name).capitalize()]
            rel_type_rules = rules_template.format(
                rel_type_id=rel_type.id,
                rel_type_names=u"' | '".join(rel_type_names),
                rel_type_properties=u"\n    | ".join(properties),
            )
            rules.append(rel_type_rules)
        rule = u"r_types = ({0})"
        rules.append(rule.format(" | ".join(rel_type_rule_codes)))
        return rules

    def get_node_type_rules(self):
        rules = []
        node_type_rule_codes = []
        rules_template = u"""
n{node_type_id}_value = ('James' | 'John')
n{node_type_id} = ('{node_type_names}')
       -> {{'type': types.get({node_type_id}), 'alias': "n{node_type_id}_{{0}}".format(counter.get('n{node_type_id}', 0))}}
n{node_type_id}_property = {node_type_properties}
n{node_type_id}_properties = n{node_type_id}_property:first (ws (',' | "and") ws n{node_type_id}_property)*:rest
                  -> [first] + rest
                  | -> []
n{node_type_id}_facet = (n{node_type_id}_properties:r ws ("of" | "from") ws ("the" ws)?)? n{node_type_id}:t ws facet ws n{node_type_id}_property:p "of"? ws (op)?:f ws n{node_type_id}_value:v ws
             -> {{'conditions': [(f, ('property', t['alias'], p), v)], 'origin': t, 'result': {{"alias": t['alias'], "properties": r}}}}
             | n{node_type_id}_facet:left ws 'and' ws n{node_type_id}_facet:right
             -> ('and', left, right)
             | n{node_type_id}_facet:left ws 'or' ws n{node_type_id}_facet:right
             -> ('or', left, right)
        """
        for node_type in self.schema.nodetype_set.all().select_related():
            self.types[node_type.id] = node_type
            node_type_rule_codes.append(u"n{0}_facet".format(node_type.id))
            properties = []
            for prop in node_type.properties.all().values("key"):
                property_name = prop["key"]
                property_names = [
                    property_name,
                    property_name.lower(),
                    property_name.upper(),
                    property_name.capitalize(),
                    u"{0}s".format(property_name),
                    u"{0}s".format(property_name).lower(),
                    u"{0}s".format(property_name).upper(),
                    u"{0}s".format(property_name).capitalize()
                ]
                rule = u"('{0}') -> '{1}'"
                property_rule = rule.format(
                    u"' | '".join(property_names),
                    property_name
                )
                properties.append(property_rule)
            node_type_names = [node_type.name, node_type.name.lower(),
                               node_type.name.upper(),
                               node_type.name.capitalize()]
            if node_type.plural_name:
                node_type_names += [node_type.plural_name,
                                    node_type.plural_name.lower(),
                                    node_type.plural_name.upper(),
                                    node_type.plural_name.capitalize()]
            else:
                node_type_names += [u"{0}s".format(node_type.name),
                                    u"{0}s".format(node_type.name).lower(),
                                    u"{0}s".format(node_type.name).upper(),
                                    u"{0}s".format(node_type.name).capitalize()]
            node_type_rules = rules_template.format(
                node_type_id=node_type.id,
                node_type_names=u"' | '".join(node_type_names),
                node_type_properties=u"\n    | ".join(properties),
            )
            rules.append(node_type_rules)
        rule = u"n_types = ({0})"
        rules.append(rule.format(" | ".join(node_type_rule_codes)))
        return rules


def query_generator(query_dict):
    conditions_list = []
    for lookup, property_tuple, match in query_dict["conditions"]:
        #if property_tuple == u"property":
        type_property = u"{0}.{1}".format(*property_tuple[1:])
        if lookup == "exact":
            lookup = u"="
            match = u"'{0}'".format(match)
        elif lookup == "iexact":
            lookup = u"=~"
            match = u"'(?i){0}'".format(match)
        elif lookup == "contains":
            lookup = u"=~"
            match = u".*{0}.*".format(match)
        elif lookup == "icontains":
            lookup = u"=~"
            match = u"(?i).*{0}.*".format(match)
        elif lookup == "startswith":
            lookup = u"=~"
            match = u"{0}.*".format(match)
        elif lookup == "istartswith":
            lookup = u"=~"
            match = u"(?i){0}.*".format(match)
        elif lookup == "endswith":
            lookup = u"=~"
            match = u".*{0}".format(match)
        elif lookup == "iendswith":
            lookup = u"=~"
            match = u"(?i).*{0}".format(match)
        elif lookup == "regex":
            lookup = u"=~"
            match = u"{0}".format(match)
        elif lookup == "iregex":
            lookup = u"=~"
            match = u"(?i){0}".format(match)
        elif lookup == "gt":
            lookup = u">"
            match = u"{0}".format(match)
        elif lookup == "gte":
            lookup = u">"
            match = u"{0}".format(match)
        elif lookup == "lt":
            lookup = u"<"
            match = u"{0}".format(match)
        elif lookup == "lte":
            lookup = u"<"
            match = u"{0}".format(match)
        # elif lookup in ["in", "inrange"]:
        #     lookup = u"IN"
        #     match = u"['{0}']".format(u"', '".join([_escape(m)
        #                               for m in match]))
        # elif lookup == "isnull":
        #     if match:
        #         lookup = u"="
        #     else:
        #         lookup = u"<>"
        #     match = u"null"
        # elif lookup in ["eq", "equals"]:
        #     lookup = u"="
        #     match = u"'{0}'".format(_escape(match))
        # elif lookup in ["neq", "notequals"]:
        #     lookup = u"<>"
        #     match = u"'{0}'".format(_escape(match))
        else:
            lookup = lookup
            match = u""
        condition = u"{0} {1} {2}".format(type_property, lookup, match)
        conditions_list.append(condition)
    conditions = u" AND ".join(conditions_list)
    origins_list = []
    for origin_dict in query_dict["origin"]:
        origin = u"{alias}=node(\"label:{type}\")".format(**origin_dict)
        origins_list.append(origin)
    origins = u", ".join(origins_list)
    results_list = []
    for result_dict in query_dict["result"]:
        for property_name in result_dict["properties"]:
            result = u"{0}.{1}".format(result_dict["alias"], property_name)
            results_list.append(result)
    resutls = u", ".join(results_list)
    return u"START {0} WHERE {1} RETURN {2}".format(origins, conditions, resutls)
