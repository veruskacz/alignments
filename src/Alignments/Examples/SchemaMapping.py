import os
import rdflib
import cStringIO as Buffer
from os.path import isfile, isdir


SUBCLASS = "owl:subClassOf"
EQUIVALENT_CLASS = "owl:equivalentClass"
EQUIVALENT_PROP = "owl:equivalentProperty"
INVERSE_PROP = "owl:inverseOf"
PREFIX = Buffer.StringIO()
triples = Buffer.StringIO()

prefixes_des = """
####################################################################
#    Prefixes Mapping
####################################################################\n\n"""

subclass_des = """
    ####################################################################
    #    Sub-Classes Mapping
    ####################################################################\n\n"""

equivalent_class_des = """
    ####################################################################
    #    Equivalent Classes Mapping
    ####################################################################\n\n"""

equivalent_prop_des = """
    ####################################################################
    #    Equivalent Properties Mapping
    ####################################################################\n\n"""

inverse_prop_des = """
    ####################################################################
    #    Inverse Properties Mapping
    ####################################################################\n\n"""


_format = "%a %b %d %H:%M:%S %Y"


def check_rdf_file(file_path):

    try:

        if not os.path.exists(file_path):
            print "\n\t[Error] The path [{}] does not exist.".format(file_path)
            return

        rdf_file = os.path.basename(file_path)
        extension = os.path.splitext(rdf_file)[1]
        extension = extension.replace(".", "")
        print ""

        graph_format = extension
        if graph_format == 'ttl':
            graph_format = "turtle"
        """
            Check the currently closed RDF file
        """
        print "=======================================================" \
              "======================================================="
        print "    Syntactic check of: ", rdf_file
        print "=======================================================" \
              "======================================================="

        g = rdflib.Dataset()
        print '    Loading ', rdf_file
        # print "    It's a .{} file".format(extension)
        g.load(source=file_path, format=graph_format)
        print "    It's a valid.{} file with a RDF graph of length: {}".format(extension, str(len(g)))

    except Exception as err:
        print "\t[check_rdf_file in checkRDFFile]", err


def prefixes(buffer, tuple_list):

    # buffer.write(prefixes_des)
    PREFIX.write(prefixes_des)
    for prefix, name_space in tuple_list:
        # buffer.write("\t@prefix {:>8}: <{}> .\n".format(prefix, name_space))
        if prefix == "base":
            PREFIX.write("{:>17} <{:30}> .\n".format("@{}".format(prefix), name_space))
        else:
            PREFIX.write("@prefix {:>8}: {:50} .\n".format(prefix, "<{}>".format(name_space)))


def create_triples(buffer, subject_class, object_classes, operator=EQUIVALENT_CLASS):

    for schema_class in object_classes:
        buffer.write("\t\t{:20} {:25} {:20} .\n".format(subject_class, operator, schema_class))


def create_group_triples(buffer, class_tuples, operator=EQUIVALENT_CLASS):

    if operator == EQUIVALENT_CLASS:
        buffer.write(equivalent_class_des)
    elif operator == SUBCLASS:
        buffer.write(subclass_des)
    elif operator == EQUIVALENT_PROP:
        buffer.write(equivalent_prop_des)
    elif operator == INVERSE_PROP:
        buffer.write(inverse_prop_des)

    for subject_class, object_classes in class_tuples:
        create_triples(buffer, subject_class, object_classes, operator=operator)


def create_trig(file_path, graph):

    cur_direct = os.path.dirname(file_path)
    if isdir(cur_direct) is False:
        os.mkdir(cur_direct)
    print "CREATING THE FILE"
    file = open(file_path, "wb")
    file.write(PREFIX.getvalue())
    file.write("\n{} {}\n".format(graph, "{"))
    file.write(triples.getvalue())
    file.write("}")
    file.close()

    check_rdf_file(file_path)


curr_tuple_list = [
    ("rdf", "http://www.w3.org/1999/02/22-rdf-syntax-ns#"),
    ("rdfs", "http://www.w3.org/2000/01/rdf-schema#"),
    ("owl", "http://www.w3.org/2002/07/owl#"),
    ("schema", "http://schema.org/"),
    ("skos", "http://www.w3.org/2004/02/skos/core#"),
    ("dc", "http://purl.org/dc/elements/1.1/"),
    ("dct", "http://purl.org/dc/terms/"),
    ("foaf", "http://xmlns.com/foaf/0.1/"),
    ("ga", "http://www.goldenagents.org/ontology/"),
    ("", "http://www.goldenagents.org/resource/")
]

curr_subclass_tuples = [
    ("ga:CreativeAgent", ["schema:Person"])
]

curr_equivalent_class_tuples = [
    ("ga:CreativeAct", ["schema:Event"]),
    ("ga:Story", ["schema:CreativeWork"])
]

curr_equivalent_prop_tuples = [
    ("ga:authoredBy", ["schema:creator"]),
    ("ga:creationDate", ["schema:dateCreated"]),
    ("ga:hasName", ["schema:name"]),
    ("ga:hasMatch", ["schema:sameAs"]),
    ("ga:hasTitle", ["schema:headline"]),
    ("ga:inLanguage", ["schema:inLanguage"]),

    ("ga:isPrintedAs", ["schema:exampleOfWork"]),

    ("ga:startDate", ["schema:startDate"])
]

curr_inverse_prop_tuples = [
    ("ga:authorOf", ["schema:creator"]),
    ("ga:subEventOf", ["schema:subEvent"]),
    ("ga:performedAs", ["schema:workPerformed"]),
]

# prefixes(triples, curr_tuple_list)
# create_group_triples(triples, curr_subclass_tuples, operator=SUBCLASS)
# create_group_triples(triples, curr_equivalent_class_tuples, operator=EQUIVALENT_CLASS)
# create_group_triples(triples, curr_equivalent_prop_tuples, operator=EQUIVALENT_PROP)
# create_group_triples(triples, curr_inverse_prop_tuples, operator=INVERSE_PROP)
#
#
# name = 'OnStage2GA'
# file_path = "/Users/veruskazamborlini/Dropbox/My projects/Golden Agents/shared/Ecartico-STCN-OnStage/"+name+".trig"
# print PREFIX.getvalue()
# print triples.getvalue()
# create_trig(file_path, ':'+name)
#

# :STCN2GA
# curr_subclass_tuples = [
#     ("ga:CreativeAgent", ["skos:Concept"]),
#     ("schema:Book", ["ga:Printing"]),
#     ("schema:Periodical", ["ga:Printing"]),
# ]
#
# curr_equivalent_prop_tuples = [
#     ("ga:writerOf", ["dc:creator"]),
#     ("ga:printerOf", ["dc:publisher"]),
#     ("ga:hasName", ["skos:prefLabel", "dct:alternative"]),
#     ("ga:hasTitle", ["dc:title", "dct:alternative "]),
#     ("ga:hasMatch", ["skos:exactMatch"]),
#     ("ga:birthDate", ["schema:birthDate"]),
#     ("ga:deathDate", ["schema:deathDate"]),
#     ("ga:creationDate", ["dc:date"]),
#     ("ga:inLanguage", ["dc:language"])
# ]

# Ecartico2GA
# curr_subclass_tuples = [
#     ("ga:CreativeAgent", ["foaf:Person , schema:Person"])
# ]
#
# curr_equivalent_prop_tuples = [
#     ("ga:hasName", ["foaf:name"]),
#     ("ga:hasMatch", ["schema:sameAs"]),
#     ("ga:birthDate", ["schema:birthDate"]),
#     ("ga:deathDate", ["schema:deathDate"])
# ]

import datetime
print str(datetime.timedelta(seconds=2545.32999992))
