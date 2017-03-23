# encoding=utf-8

# https://appear.in/risis-meeting
# from SparqlRequests import jrc_names
# from JRCNameLinker import links
# import SPARQLWrapper
# https://github.com/KRRVU/linksets
# https://www.sourcetreeapp.com/
# url = b"http://{}:{}/annex/{}/sparql/query?".format("localhost", "5820", "linkset")
# url = b"http://{}/annex/{}/sparql/query?".format("stardog.risis.d2s.labs.vu.nl", "risis")

import src.Alignments.NameSpace as Ns
import src.Alignments.Query as Qry
import src.Alignments.Settings as St
import cStringIO
import time
import os
import datetime
import codecs
import rdflib
import xmltodict
from os import listdir
from os.path import isfile, join
from src.Alignments.CheckRDFFile import check_rdf_file
from kitchen.text.converters import to_bytes, to_unicode
import re
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)
handler = logging.StreamHandler()
logger.addHandler(handler)

linksetpath = "E:\datasets\Linksets"
write_to_path = "C:\Users\Al\Dropbox\Linksets\ExactName"
_linktype_label = 'linktype_label'
_entity_datatype = 'entity_datatype'
_entity_ns = 'entity_ns'
_graph_ns = 'graph_ns'
_graph_name = 'graph_name'
_graph = 'graph'
_aligns_prefix = 'aligns_prefix'
aligns_ns = 'aligns_ns'
_aligns_name = 'aligns_name'
_aligns = 'aligns'

_link = 'link'
_old_link = 'old_link'
_link_comment = 'link_comment'
_link_subpropertyof = 'link_subpropertyof'

_linkset = 'linkset'
_linkset_label = 'linkset_label'
_singleton = 'singleton'
_assertion_method = 'assertion_method'
_justification = 'justification'
_justification_comment = 'justification_comment'
_linkset_comment = 'linkset_comment'
_insert_query = 'insert_query'
_mechanism = "mechanism"
_context_code = 'context_code'
_sameAsCount = "sameAsCount"


def get_URI_local_name(uri):
    # print "URI: {}".format(uri)
    # print type(uri)

    if uri is None:
        return None

    if len(uri) == 0:
        return None

    # if type(uri) is not str:
    #     return None

    else:
        non_alphanumeric_str = re.sub('[ \w]', '', uri)
        if non_alphanumeric_str == "":
            return uri
        else:
            last_char = non_alphanumeric_str[-1]
            index = uri.rindex(last_char)
            name = uri[index + 1:]
            return name


def get_URI_NS_local_name(uri):
    if (uri is None) or (uri == ""):
        return None
    else:
        non_alphanumeric_str = re.sub('[ \w]', '', uri)
        if non_alphanumeric_str == "":
            return uri
        else:
            last_char = non_alphanumeric_str[-1]
            index = uri.rindex(last_char)
            name = uri[index + 1:]
            ns = uri[:index+1]
            return [ns, name]


def update_specification(specs):

    # print "Specs update"
    # print specs

    if St.graph in specs:
        specs[St.graph_name] = get_URI_local_name(specs[St.graph])
        specs[St.graph_ns] = get_URI_NS_local_name(specs[St.graph])[0]
        # print specs[St.graph_name]

    if St.entity_datatype in specs:
        specs[St.entity_name] = get_URI_local_name(specs[St.entity_datatype])
        specs[St.entity_ns] = str(specs[St.entity_datatype]).replace(specs[St.entity_name], '')
        # print specs[St.entity_name]

    if St.aligns in specs:
        specs[St.aligns_name] = get_URI_local_name(specs[St.aligns])
        specs[St.aligns_ns] = str(specs[St.aligns]).replace(specs[St.aligns_name], '')
        # print specs[St.aligns_name]

    if St.lens in specs:
        specs[St.lens_name] = get_URI_local_name(specs[St.lens])
        specs[St.lens_ns] = str(specs[St.lens]).replace(specs[St.lens_name], '')

    if St.linkset in specs:
        specs[St.linkset_name] = get_URI_local_name(specs[St.linkset])
        specs[St.linkset_ns] = str(specs[St.linkset]).replace(specs[St.linkset_name], '')


#################################################################
"""
    ABOUT INSERTING NAMED GRAPHS
"""
#################################################################


def insertgraph(host, database_name, dataset_name, f_path, file_count, save=True):

    limit = 70000
    date = datetime.date.isoformat(datetime.date.today()).replace('-', '')
    f_path = f_path.replace("\\", "/")
    ds = rdflib.Dataset()
    name = os.path.basename(f_path)

    new_dir = "{}/Inserted_{}_On_{}".format(os.path.dirname(f_path), name, date)

    try:
        if not os.path.exists(new_dir):
            os.makedirs(new_dir)
    except OSError as err:
        print "\n\t[__init__ in RDF]", err
        return

    print "loading : [{}]".format(file_count)
    print "\n\tFile: {}".format(name)
    start_time = time.time()
    ds.parse(source=f_path, format="trig", encoding='utf-8')
    print "\tLoading completed in{:>8} {} seconds".format(":", str(time.time() - start_time))
    print "\tSize                {:>8} {} triples".format(":", len(ds))

    count = 1
    # count_chunk = 0
    for graph in ds.graphs():
        count_lines = 0

        # rdflib.graph.Graph
        if len(graph) > 0:
            name = re.findall("<.*>", str(graph))[0]
            if name.__contains__("file:") is not True:
                print "\t>>> Named-graph [{}]{:>15} {}".format(count, ":", name)
                count_chunk = 0
                qrybldr = cStringIO.StringIO()
                qrybldr.write("INSERT DATA\n{{\n\tGRAPH {}\n".format(name))
                qrybldr.write("\t{\n")

                for subj, pred, obj in graph:
                    count_lines += 1

                    #  If literal
                    if type(obj) == rdflib.term.Literal:
                        if len(obj) == 1:
                            # obj = to_bytes(obj)
                            obj = obj.replace("\\", "\\\\")
                        obj = "\"\"\"{}\"\"\"".format(to_bytes(obj))
                        # print obj

                    #  if URI
                    elif type(obj) == rdflib.term.URIRef:
                        obj = "<{}>".format(to_bytes(obj))

                    # triple
                    qrybldr.write("\t\t<{}> <{}> {} .\n".format(to_bytes(subj), to_bytes(pred), obj))

                    if count_lines == limit:
                        count_chunk += 1
                        qrybldr.write("\t}\n}\n")
                        query_time = time.time()
                        if save is True:
                            wr = codecs.open("{}/Insert-{}_chunk{}_{}.txt".format(
                                new_dir, dataset_name, count_chunk, date), "wb")
                            wr.write(qrybldr.getvalue())
                            wr.close()
                        qres = Qry.endpoint(qrybldr.getvalue(), database_name, host)

                        if qres is not None:
                            doc = xmltodict.parse(qres)
                            print "\t>>> Response of chunk {:<12}: {}".format(count_chunk, doc['sparql']['boolean'])
                            print "\t>>> Inserted in {:>19} {} seconds".format(":", str((time.time() - query_time)))

                        # Reset
                        qrybldr.close()
                        qrybldr = cStringIO.StringIO()
                        qrybldr.write("INSERT DATA\n{{\n\tGRAPH {}\n".format(name))
                        qrybldr.write("\t{\n")
                        count_lines = 0
                        # qres = ""

                qrybldr.write("\t}\n}\n")
                query_time = time.time()
                final = qrybldr.getvalue()
                qrybldr.close()
                if len(final) > 0:
                    count_chunk += 1
                    if save is True:
                        wr = codecs.open("{}/Insert-{}_chunk{}_{}.txt".format(
                            new_dir, dataset_name, count_chunk, date), "wb")
                        wr.write(final)
                        wr.close()
                    qres = Qry.endpoint(final, database_name, host)
                    if qres is not None:
                        doc = xmltodict.parse(qres)
                        print "\t>>> Response of chunk {:<12}: {}".format(count_chunk, doc['sparql']['boolean'])
                        print "\t>>> Inserted in {:>19} {} seconds".format(":", str(time.time() - query_time))
                count += 1

    print "\tProcess completed in {} {} seconds\n".format(":", str(time.time() - start_time))


def insertgraphs(host, database_name, dataset_name, dir_path):

    _format = "%a %b %d %H:%M:%S %Y"
    builder = cStringIO.StringIO()
    files = [f for f in listdir(dir_path) if isfile(join(dir_path, f))]

    print "\n\n{:>114}".format(datetime.datetime.today().strftime(_format))
    builder.write("\n--------------------------------------------------------"
                  "----------------------------------------------------------\n")
    builder.write("    Inserting graphs contained in :\n\t\t{}\n".format(dir_path))
    builder.write("    \tThe folder contains [ {} ] files.\n".format(len(files)))
    builder.write("--------------------------------------------------------"
                  "----------------------------------------------------------\n")

    print builder.getvalue()

    file_count = 1
    for f in listdir(dir_path):
        path = join(dir_path, f)
        extension = os.path.splitext(path)[1]

        if isfile(path) & (extension.lower() == ".trig"):
            # print path
            insertgraph(host, database_name, dataset_name, path, file_count)
            file_count += 1


#################################################################
"""
    LINKSETS
"""
#################################################################


def spa_linksets(source, target, context_code, database_name, host, display=False, activated=False):

    # This function is designed for EXACT NAME SIMILARITY RUN AS SPARQL QUERIES

    same_as_count = Qry.get_same_as_count(source[_mechanism], database_name, host)
    # print same_as_count
    # exit(0)
    info = "{}{}{}{}{}{}{}".\
        format("\n====================================================================================\n",
               "Results for creating the linkset between {} and {}.\n".
               format(source[_graph_name], target[_graph_name], context_code, source[_mechanism]),

               "\t   Linksets GRAPH             : linkset:{}_{}_C{}_{}\n".
               format(source[_graph_name], target[_graph_name], context_code, source[_mechanism]),

               "\t   Metadata GRAPH            : lsMetadata:{}_{}_C{}_{}\n".
               format(source[_graph_name], target[_graph_name], context_code, source[_mechanism]),

               "\t   Singleton Metadata GRAPH  : GRAPH singMetadata:{}_{}_C{}_{}\n".
               format(source[_graph_name], target[_graph_name], context_code, source[_mechanism]),

               "\t   LINKTYPE                  : alivocab:{}{}\n".format(source[_mechanism], same_as_count),
               "====================================================================================\n")

    if activated is True:

        # Check whether this linkset was already generated. If yes, delete it or change the context code
        ls = "linkset:{}_{}_C{}_{}".format(source[_graph_name], target[_graph_name], context_code, source[_mechanism])
        ask_query = "PREFIX linkset: <http://risis.eu/linkset/> ASK {{ {} ?p ?o . }}".format(ls)
        ask = Qry.boolean_endpoint_response(ask_query, database_name, host)
        ask = True if ask == "true" else False

        if ask is True:
            logger.warning("\n{} ALREADY EXISTS. \nTO PROCEED ANYWAY, PLEASE DELETE "
                           "THE LINKSET FIRST OR CHANGE THE CONTEXT CODE\n".format(ls))
            return

        if source[_mechanism] != target[_mechanism]:
            logger.warning("\nSOURCE & TARGET MUST HAVE THE SAME MECHANISM FOR CREATING A LINKSET.\n")
            return

        print info

        # Linksets graph name
        g_linkset = "{}_{}_C{}_{}".format(source[_graph_name], target[_graph_name], context_code, _linktype_label)

        # Generating insert quarries
        insertqueries = spa_linkset_ess_query(source, target, context_code, source[_mechanism], same_as_count)

        # LINKSET insert Query
        insert_queries = "{}\n{}\n{}".format(insertqueries[1], insertqueries[2], insertqueries[3])
        data = {'context_code': context_code, 'sameAsCount': same_as_count, _insert_query: insert_queries}
        # print insertqueries[0], '\n', insertqueries[1], '\n', insertqueries[2], '\n', insertqueries[3]

        # print time.time()
        #########################################################################
        """ 1. SAFETY GRAPHS DROPS                                            """
        ########################################################################
        Qry.boolean_endpoint_response(insertqueries[0], database_name, host)

        ########################################################################
        """ 2. TEMPORARY GRAPHS                                              """
        ########################################################################
        Qry.boolean_endpoint_response(insertqueries[1], database_name, host)

        ########################################################################
        """ 3. LINKSET & METADATA                                            """
        ########################################################################
        Qry.boolean_endpoint_response(insertqueries[2], database_name, host)

        ########################################################################
        """ 4. DROPPING TEMPORARY GRAPHS                                     """
        ########################################################################
        Qry.boolean_endpoint_response(insertqueries[3], database_name, host)

        ########################################################################
        """ 5. GENERATING LINKSET METADATA                                   """
        ########################################################################
        metadata = linkset_metadata(source, target, data, database_name, host)
        Qry.boolean_endpoint_response(metadata, database_name, host)

        ########################################################################
        """ 6. WRITING TO FILE                                               """
        ########################################################################
        src = [source[_graph_name], "", source[_entity_ns]]
        trg = [target[_graph_name], "", target[_entity_ns]]
        print "WRITING TO FILE"
        # linkset_path = "D:\datasets\Linksets\ExactName"
        linkset_path = write_to_path
        writelinkset(src, trg, g_linkset, linkset_path, metadata, database_name, host)

        print "\n*** JOB DONE! ***\n"

    elif display is True:

        # Generating insert quarries
        insertqueries = spa_linkset_ess_query(source, target, context_code, source[_mechanism], same_as_count)
        # LINKSET insert Query
        insert_queries = "{}\n{}\n{}".format(insertqueries[1], insertqueries[2], insertqueries[3])
        data = {'context_code': context_code, 'sameAsCount': same_as_count, _insert_query: insert_queries}
        # print insertqueries[0], '\n', insertqueries[1], '\n', insertqueries[2], '\n', insertqueries[3]
        metadata = linkset_metadata(source, target, data, database_name, host)
        print metadata


def spa_linkset_ess_query(source, target, context_code, mechanism, same_as_count):

    # Single Predicate Alignment with Exact String Similarity
    """
    :param source:
    :param target:
    :param context_code:
    :param mechanism:
    :param same_as_count:
    :return:
    """

    """
        NAMESPACE
    """
    prefix = "\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}".format(
            "##################################################################",
            "### Linking {{{}}} to {{{}}} based on exact name".format(source[_graph_name], target[_graph_name]),
            "##################################################################",
            "prefix dataset:    <{}>".format(Ns.dataset),
            "prefix linkset:    <{}>".format(Ns.linkset),
            "prefix singleton:  <{}>".format(Ns.singletons),
            "prefix alivocab:   <{}>".format(Ns.alivocab),
            "prefix tmpgraph:   <{}>".format(Ns.tmpgraph),
            "prefix tmpvocab:   <{}>".format(Ns.tmpvocab))
    '''
        DROPPING GRAPHS
    '''
    drop_tmp = "DROP SILENT GRAPH tmpgraph:load"
    drop_tmp00 = "DROP SILENT GRAPH tmpgraph:load00"
    drop_tmp01 = "DROP SILENT GRAPH tmpgraph:load01"
    # drop_ls = "DROP SILENT GRAPH linkset:{}_{}_ExactName".format(src_dataset_name, trg_dataset_name)
    # drop_metadata = "DROP SILENT GRAPH lsMetadata:{}_{}_ExactName_metadata".format(src_dataset_name, trg_dataset_name)

    drop_ls = "DROP SILENT GRAPH linkset:{}_{}_C{}_{}".format(
        source[_graph_name],  target[_graph_name], context_code, mechanism)
    drop_metadata = "DROP SILENT GRAPH singleton:{}_{}_C{}_{}".format(
        source[_graph_name], target[_graph_name], context_code, mechanism)

    '''
        LOADING SOURCE TO TEMPORARY GRAPH tmpgraph:load00
    '''
    load_temp00 = "{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}".\
        format("\tINSERT",
               "\t{",
               "\t  GRAPH tmpgraph:load00",
               "\t  {",
               "\t    ?source <{}> ?label .".format(source[_aligns]),
               "\t  }",
               "\t}",

               "\tWHERE",
               "\t{",
               "\t  ### Selecting source data instances based on name",
               "\t  GRAPH <{}>".format(source[_graph]),
               "\t  {",
               "\t    ?source <{}> ?aLabel .".format(source[_aligns]),
               "\t    BIND(lcase(str(?aLabel)) as ?label)",
               "\t  }",
               "\t}")

    '''
        LOADING TARGET TO TEMPORARY GRAPH tmpgraph:load01
    '''
    load_temp01 = "{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}".\
        format("\tINSERT",
               "\t{",
               "\t  GRAPH tmpgraph:load01",
               "\t  {",
               "\t    ?target <{}>  ?label .".format(target[_aligns]),
               "\t  }",
               "\t}",

               "\tWHERE",
               "\t{",
               "\t  ### Selecting target data instances based on exact name",
               "\t  graph <{}>".format(target[_graph]),
               "\t  {",
               "\t    ?target <{}>  ?bLabel .".format(target[_aligns]),
               "\t    BIND(lcase(str(?bLabel)) as ?label)",
               "\t  }",
               "\t}")

    '''
        LOADING CORRESPONDENCE TO TEMPORARY GRAPH tmpgraph:load
    '''
    load_temp = "{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}".\
        format("\tINSERT",
               "\t{",
               "\t  GRAPH tmpgraph:load",
               "\t  {",
               "\t    ?source tmpvocab:exactName ?target ;",
               "\t            tmpvocab:evidence  ?label .",
               "\t  }",
               "\t}",
               # Load
               "\tWHERE",
               "\t{",
               "\t  ### Selecting source data instances based on name",
               "\t  GRAPH tmpgraph:load00",
               "\t  {",
               "\t    ?source <{}> ?label .".format(source[_aligns]),
               "\t  }",

               "\t  ### Selecting target data instances based on exact name",
               "\t  graph tmpgraph:load01",
               "\t  {",
               "\t    ?target <{}>  ?label .".format(target[_aligns]),
               "\t  }",

               "\t}", )

    '''
        CREATING THE LINKSET & METADATA GRAPHS lsMetadata
    '''
    load_linkset = "{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}"\
                   "\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}".\
        format("\tINSERT",
               "\t{",
               "\t  GRAPH linkset:{}_{}_C{}_{}".
               format(source[_graph_name], target[_graph_name], context_code, mechanism),
               "\t  {",
               "\t    ### Correspondence triple with singleton",
               "\t    ?source ?singPre ?target.",
               "\t  }",

               "\t  GRAPH singleton:{}_{}_C{}_{}".format(
                   source[_graph_name], target[_graph_name], context_code, mechanism),
               "\t  {",
               "\t    ### Singleton metadata",
               "\t    ?singPre rdf:singletonPropertyOf     alivocab:exactStrSim{} ;".format(same_as_count),
               "\t             alivocab:hasEvidence        ?label .",
               "\t  }",

               "\t}",
               "\tWHERE",
               "\t{",
               "\t  ### Selecting from tmpgraph:load",
               "\t  GRAPH tmpgraph:load",
               "\t  {",
               "\t    ?source tmpvocab:exactName ?target ;",
               "\t            tmpvocab:evidence  ?label .",
               "\t            ",
               "\t    ### Create A SINGLETON URI",
               "\t    BIND( replace(\"{}{}{}_#\",\"#\",".format(Ns.alivocab, mechanism, same_as_count),
               "\t        STRAFTER(str(UUID()),\"uuid:\")) as ?pre )",
               "\t    BIND(iri(?pre) as ?singPre)",
               "\t  }",
               "\t}")

    '''
        PUTTING IT ALL TOGETHER
    '''
    query01 = "{}\n\n{}\n\t{} ;\n\n{}\n\t{} ;\n\n{}\n\t{} ;\n\n{}\n{} ;\n\n{}\n\t{}".format(
        prefix,
        "### 1.0 DROP temporary graph",
        drop_tmp,
        "### 1.1 DROP SOURCE temporary graph 00",
        drop_tmp00,
        "### 1.2 DROP TARGET temporary graph 01",
        drop_tmp01,
        "### 1.3 DROP LINKSET graph",
        drop_ls,
        "### 1.4 DROP METADATA graph",
        drop_metadata
     )

    query02 = "{}\n\n{}\n{} ;\n\n{}\n{} ;\n\n{}\n{} ".format(
        prefix,
        "### 2.0 INSERT SOURCE into tmpgraph:load00",
        load_temp00,
        "### 2.1 INSERT TARGET into tmpgraph:load01",
        load_temp01,
        "### 2.3 INSERT CORRESPONDENCE [match] into tmpgraph:load",
        load_temp,
    )

    query03 = "{}\n\n{}\n{}".format(
        prefix,
        "### 3.0 CREATING AND LOADING THE LINKSET AND ITS METADATA",
        load_linkset,
    )

    query04 = "{}\n\n{}\n\t{} ;\n\t{} ;\n\t{}".format(
        prefix,
        "### 4.0 DROP temporary graphs",
        drop_tmp00,
        drop_tmp01,
        drop_tmp
    )

    queries = [query01, query02, query03, query04]

    return queries


def linkset_metadata(source, target, data, database, host):

    data['name'] = "{}_{}_C{}_{}".\
        format(source[_graph_name], target[_graph_name], data[_context_code], source['mechanism'])
    data[_linkset] = "{}{}".format(Ns.linkset, data['name'])
    data[_singleton] = "{}{}".format(Ns.singletons, data['name'])
    data[_link] = "{}{}{}".format(Ns.alivocab, "exactStrSim", data[_sameAsCount])
    data[_assertion_method] = "{}{}".format(Ns.method, data['name'])
    data[_justification] = "{}{}".format(Ns.justification, data['name'])
    data[_link_comment] = "The predicate <{}> used in this linkset is a property that reflects an entity " \
                          "linking approach based on the <{}{}> mechanism.".\
        format(data[_link], Ns.mechanism, source[_mechanism])

    if str(source[_mechanism]).lower() == "exactstrsim":
        data[_linktype_label] = "Exact String Similarity"
        data[_link_subpropertyof] = "http://risis.eu/linkset/predicate/{}".format(source[_mechanism])
        data[_justification_comment] = "We assume that entities with the aligned predicates sharing the " \
                                       "exact same content are same. This assumption applies when dealing " \
                                       "with entities such as Organisation."
        data['linkset_comment'] = "Linking <{}> to <{}> by aligning <{}> with <{}> using the mechanism: {}". \
            format(source[_graph], target[_graph], source[_aligns], target[_aligns], source[_mechanism])

    size = Qry.get_namedgraph_size(data[_linkset], database, host, isdistinct=False)

    query = "\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}" \
            "\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}" \
            "\n{}\n{}\n{}\n{}\n{}" \
            "\n{}\n{}\n{}" \
            "\n{}\n{}\n{}\n{}\n{}".\
        format("##################################################################",
               "### METADATA FOR {}".format(data[_linkset]),
               "##################################################################",
               "PREFIX alivocab:    <{}>".format(Ns.alivocab),
               "PREFIX rdfs:        <{}>".format(Ns.rdfs),
               "PREFIX void:        <{}>".format(Ns.void),
               "PREFIX bdb:         <{}>".format(Ns.bdb),

               "INSERT DATA",
               "{",
               "    <{}>".format(data[_linkset]),
               "        a                           void:Linksets ;",
               "        void:triples                {} ;".format(size),
               "        alivocab:sameAsCount        {} ;".format(data[_sameAsCount]),
               "        alivocab:alignsMechanism    <{}{}> ;".format(Ns.mechanism, source[_mechanism]),
               "        void:subjectsTarget         <{}> ;".format(source[_graph]),
               "        void:objectsTarget          <{}> ;".format(target[_graph]),
               "        void:linkPredicate          <{}> ;".format(data[_link]),
               "        bdb:subjectsDatatype        <{}> ;".format(source[_entity_datatype]),
               "        bdb:objectsDatatype         <{}> ;".format(target[_entity_datatype]),
               "        alivocab:singletonGraph     <{}> ;".format(data[_singleton]),
               "        bdb:assertionMethod         <{}> ;".format(data[_assertion_method]),
               "        bdb:linksetJustification    <{}> ;".format(data[_justification]),
               "        alivocab:alignsSubjects     <{}> ;".format(source[_aligns]),
               "        alivocab:alignsObjects      <{}> ;".format(target[_aligns]),
               "        rdfs:comment                \"\"\"{}\"\"\" .".format(data[_linkset_comment]),

               "\n    ### METADATA ABOUT THE LINKTYPE",
               "      <{}>".format(data[_link]),
               "        rdfs:comment                \"\"\"{}\"\"\" ;".format(data[_link_comment]),
               "        rdfs:label                  \"{} {}\" ;".format(data[_linktype_label], data[_sameAsCount]),
               "        rdfs:subPropertyOf          <{}> .".format(data[_link_subpropertyof]),

               "\n    ### METADATA ABOUT THE LINKSET JUSTIFICATION",
               "    <{}>".format(data[_justification]),
               "        rdfs:comment              \"\"\"{}\"\"\" .".format(data[_justification_comment]),

               "\n    ### ASSERTION METHOD",
               "    <{}>".format(data[_assertion_method]),
               "        alivocab:sparql           \"\"\"{}\"\"\" .".format(data[_insert_query]),

               "}")
    print query
    return query


def writelinkset(source, target, linkset_graph_name, outputs_path, metadata_triples, database_name, host):

    # print "CALL A CONSTRUCT ON: {}".format(linkset_graph_name)

    linkset_query = "\n{}\n{}\n{}\n{}\n\n{}\n{}\n\n".format(
        "PREFIX linkset: <{}>".format(Ns.linkset),
        "PREFIX {}: <{}>".format(source[0], source[2]),
        "PREFIX predicate: <{}>".format(Ns.alivocab),
        "PREFIX {}: <{}>".format(target[0], target[2]),
        "construct { ?x ?y ?z }",
        "where     {{ graph linkset:{} {{ ?x ?y ?z }} }}".format(linkset_graph_name),
    )

    # print linkset_query

    singleton_metadata_query = "\n{}\n{}\n{}\n{}\n\n{}\n{}\n{}\n\n".format(
        "PREFIX singMetadata:   <{}>".format(Ns.singletons),
        "PREFIX predicate:      <{}>".format(Ns.alivocab),
        "PREFIX rdf:            <{}>".format(Ns.rdf),
        "PREFIX {}:             <{}>".format(source[0], source[2]),
        "PREFIX {}:             <{}>".format(target[0], target[2]),
        "construct { ?x ?y ?z }",
        "where     {{ graph <{}{}> {{ ?x ?y ?z }} }}".format(Ns.singletons, linkset_graph_name),
    )
    # print singleton_metadata_query

    """
        1. RUN SPARQL CONSTRUCT QUERIES AGAINST ENDPOINT
    """
    linkset_construct = Qry.endpointconstruct(linkset_query, database_name, host)
    if linkset_construct is not None:
        linkset_construct = linkset_construct.replace('{', "linkset:{}\n{{".format(linkset_graph_name), 1)

    singleton_metadata_construct = Qry.endpointconstruct(singleton_metadata_query, database_name, host)
    if singleton_metadata_construct is not None:
        singleton_metadata_construct = singleton_metadata_construct.\
            replace('{', "singMetadata:{}\n{{".format(linkset_graph_name), 1)

    """
        2. FILE NAME SETTINGS
    """
    date = datetime.date.isoformat(datetime.date.today()).replace('-', '')
    dir_name = outputs_path  # os.path.dirname(f_path)
    linkset_file = "{}(Linksets)-{}.trig".format(linkset_graph_name, date)
    metadata_file = "{}(Metadata)-{}.trig".format(linkset_graph_name, date)
    singleton_metadata_file = "{}(SingletonMetadata)-{}.trig".format(linkset_graph_name, date)
    dir_name = dir_name.replace("\\", "/")
    linkset_output = "{}/{}".format(dir_name, linkset_file)
    metadata_output = "{}/{}".format(dir_name, metadata_file)
    singleton_metadata_output = "{}/{}".format(dir_name, singleton_metadata_file)
    try:
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
    except OSError as err:
        print "\n\t[__init__ in RDF]", err
        return
    # print "output file is :\n\t{}".format(output_path)

    """
        3. WRITE LINKSET TO FILE
    """
    linkset_disc = codecs.open(linkset_output, "wb", "utf-8")
    if linkset_construct is not None:
        linkset_disc.write(linkset_construct)
    linkset_disc.close()

    """
        4. WRITE METADATA TO FILE
    """
    metadata_disc = codecs.open(metadata_output, "wb", "utf-8")
    metadata_disc.write(metadata_triples.replace("INSERT DATA", "") + "\n\n")
    metadata_disc.close()

    """
        5. WRITE SINGLETON METADATA TO FILE
    """
    sing_metadata_disc = codecs.open(singleton_metadata_output, "wb", "utf-8")
    if singleton_metadata_construct is not None:
        sing_metadata_disc.write(to_unicode(singleton_metadata_construct) + "\n\n")
    sing_metadata_disc.close()

    """
        6. CHECK THE WRITTEN FILES
    """
    check_rdf_file(linkset_output)
    check_rdf_file(metadata_output)


def write_to_file(graph_name, metadata=None, correspondences=None, singletons=None):

    # print graph_name

    """
        2. FILE NAME SETTINGS
    """
    date = datetime.date.isoformat(datetime.date.today()).replace('-', '')
    dir_name = write_to_path  # os.path.dirname(f_path)
    linkset_file = "{}(Linksets)-{}.trig".format(graph_name, date)
    metadata_file = "{}(Metadata)-{}.trig".format(graph_name, date)
    singleton_metadata_file = "{}(SingletonMetadata)-{}.trig".format(graph_name, date)
    dir_name = dir_name.replace("\\", "/")

    linkset_output = "{}/{}".format(dir_name, linkset_file)
    metadata_output = "{}/{}".format(dir_name, metadata_file)
    singleton_metadata_output = "{}/{}".format(dir_name, singleton_metadata_file)
    try:
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
    except OSError as err:
        print "\n\t[__init__ in RDF]", err
        return
    # print "output file is :\n\t{}".format(output_path)

    """
        3. WRITE LINKSET TO FILE
    """

    if metadata is not None:
        document = codecs.open(metadata_output, "wb", "utf-8")
        document.write(to_unicode(metadata))
        document.close()

    if correspondences is not None:
        document = codecs.open(linkset_output, "wb", "utf-8")
        document.write(to_unicode(correspondences))
        document.close()

    if singletons is not None:
        document = codecs.open(singleton_metadata_output, "wb", "utf-8")
        document.write(to_unicode(singletons))
        document.close()


def get_writers(graph_name):

    # print graph_name

    """
        2. FILE NAME SETTINGS
    """
    date = datetime.date.isoformat(datetime.date.today()).replace('-', '')
    dir_name = write_to_path  # os.path.dirname(f_path)
    batch_file = "{}_batch)_{}.bat".format(graph_name, date)
    linkset_file = "{}(Linksets)-{}.trig".format(graph_name, date)
    metadata_file = "{}(Metadata)-{}.trig".format(graph_name, date)
    singleton_metadata_file = "{}(SingletonMetadata)-{}.trig".format(graph_name, date)
    dir_name = dir_name.replace("\\", "/")

    batch_output  = "{}/{}".format(dir_name, batch_file)
    linkset_output = "{}/{}".format(dir_name, linkset_file)
    metadata_output = "{}/{}".format(dir_name, metadata_file)
    singleton_metadata_output = "{}/{}".format(dir_name, singleton_metadata_file)
    try:
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
    except OSError as err:
        print "\n\t[__init__ in RDF]", err
        return
    # print "output file is :\n\t{}".format(output_path)

    """
        3. WRITE LINKSET TO FILE
    """
    writers = dict()
    writers[St.meta_writer] = codecs.open(metadata_output, "wb", "utf-8")
    writers[St.crpdce_writer] = codecs.open(linkset_output, "wb", "utf-8")
    writers[St.singletons_writer] = codecs.open(singleton_metadata_output, "wb", "utf-8")
    writers[St.batch_writer] = codecs.open(batch_output, "wb", "utf-8")
    writers[St.meta_writer_path] = metadata_output
    writers[St.crpdce_writer_path] = linkset_output
    writers[St.singletons_writer_path] = singleton_metadata_output
    writers[St.batch_output_path] = batch_output

    return writers


#################################################################
"""
    LINKSETS BY SUBSET
"""
#################################################################


def spa_linkset_subset(source, target, data, database_name, host, activated=False):

    data[_sameAsCount] = Qry.get_same_as_count(data[_mechanism], database_name, host)
    # print data[_sameAsCount]

    # Check whether this linkset was already generated. If yes, delete it or change the context code
    ask_query = "\nPREFIX linkset: <http://risis.eu/linkset/> \nASK {{ <{}> ?p ?o . }}".format(data[_linkset])
    # print ask_query
    ask = Qry.boolean_endpoint_response(ask_query, database_name, host)
    ask = True if ask == "true" else False

    if ask is True:
        logger.warning("\n{} ALREADY EXISTS. \nTO PROCEED ANYWAY, PLEASE DELETE "
                       "THE LINKSET FIRST OR CHANGE THE CONTEXT CODE\n".format(data[_linkset]))
        return

    ##########################################################
    """ 1. GENERATE SUBSET LINKSET INSERT QUERY            """
    ##########################################################
    insert_query = spa_subset_insert(source, data)

    #############################################################
    """ 2. EXECUTING INSERT SUBSET LINKSET QUERY AT ENDPOINT  """
    #############################################################
    if activated is True:
        Qry.endpoint(insert_query, database_name, host)

    #############################################################
    """ 3. LINKSET SIZE (NUMBER OF TRIPLES)                   """
    #############################################################
    # LINKSET SIZE (NUMBER OF TRIPLES)
    size = Qry.get_namedgraph_size(data[_linkset], database_name, host)
    print "\t>>> {} TRIPLES INSERTED".format(size)

    construct_query = "\n{}\n{}\n".format(
        "construct { ?x ?y ?z }",
        "where     {{ graph <{}> {{ ?x ?y ?z }} }}".format(data[_linkset]),
    )
    # print construct_query
    construct_response = Qry.endpointconstruct(construct_query, database_name, host)
    if construct_response is not None:
        construct_response = construct_response.replace('{', "<{}>\n{{".format(data[_linkset]), 1)

    #############################################################
    """ 4. LINKSET METADATA                                   """
    #############################################################
    # METADATA
    data[_insert_query] = insert_query
    metadata = spa_subset_metadata(source, target, data, size)
    ###############################################################
    """ 5. EXECUTING INSERT LINKSET METADATA QUERY AT ENDPOINT  """
    ###############################################################
    # EXECUTING METADATA QUERY AT ENDPOINT
    if activated is True:
        Qry.endpoint(metadata, database_name, host)

    write_to_file(graph_name=data[_linkset_label], metadata=metadata, correspondences=construct_response)
    print "\n*** JOB DONE! ***\n"


def spa_subset_insert(source, data):

    insert_query = """
        ###### INSERT SUBSET LINKSET
        INSERT
        {{
            GRAPH <{}>
            {{
                ?subject   ?singPre  ?object .
            }}
        }}
        WHERE
        {{
            GRAPH <{}>
            {{
                ?subject <{}>  ?object .
            }}

            ### Create A SINGLETON URI
            BIND( replace("{}{}_#", "#", STRAFTER(str(UUID()),"uuid:")) as ?pre )
            BIND(iri(?pre) as ?singPre)
        }}
        """.format(data[_linkset], source[_graph], data[_old_link], Ns.linkset, data[St.linkset_name])
    # print insert_query
    return insert_query


def spa_subset_metadata(source, target, data, size):

    metadata = "\n{}\n{}\n{}\n{}\n{}\n{}\n{}" \
               "\n{}\n{}\n{}\n{}" \
               "\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}" \
               "\n{}\n{}\n{}\n{}\n{}\n{}" \
               "\n{}\n{}\n{}\n{}\n{}\n{}". \
        format("\t###### METADATA",
               "\tPREFIX rdfs:      <{}>".format(Ns.rdfs),
               "\tPREFIX void:      <{}>".format(Ns.void),
               "\tPREFIX alivocab:  <{}>".format(Ns.alivocab),
               "\tPREFIX bdb:       <{}>".format(Ns.bdb),
               "\tINSERT DATA",
               "\t{",
               "\t     ### [SUBSET of {}]".format(source[_graph]),
               "\t     ### METADATA ABOUT THE SUBSET LINKSET",
               "\t     <{}>".format(data[_linkset]),
               "\t       a                         void:Linksets ;",
               "\t       alivocab:alignsMechanism  <{}{}> ;".format(Ns.mechanism, data[_mechanism]),
               "\t       alivocab:sameAsCount      {} ;".format(data[_sameAsCount]),
               "\t       void:subset               <{}> ;".format(source[_graph]),
               "\t       void:subjectsTarget       <{}> ;".format(source[_graph]),
               "\t       void:objectsTarget        <{}> ;".format(target[_graph]),
               "\t       void:triples              {} ;".format(size),
               "\t       void:linkPredicate        <{}{}> ;".format(data[_link], data[_sameAsCount]),
               "\t       bdb:subjectsDatatype      <{}> ;".format(source[_entity_datatype]),
               "\t       bdb:objectsDatatype       <{}> ;".format(target[_entity_datatype]),
               "\t       bdb:assertionMethod       <{}> ;".format(data[_assertion_method]),
               "\t       bdb:linksetJustification  <{}> ;".format(data[_justification]),
               "\t       alivocab:alignsSubjects   <{}> ;".format(data[_old_link]),
               "\t       rdfs:comment              \"\"\"{}\"\"\" .".format(data[_linkset_comment]),

               "\n\t     ### METADATA ABOUT THE LINKSET JUSTIFICATION",
               "\t     <{}>".format(data[_justification]),
               "\t       rdfs:comment              \"\"\"{}\"\"\" .".format(data[_justification_comment]),
               "\n\t     ### METADATA ABOUT THE LINKTYPE",
               "\t     <{}{}>".format(data[_link], data[_sameAsCount]),
               "\t       rdfs:comment              \"\"\"{}\"\"\" ;".format(data[_link_comment]),
               "\t       rdfs:label                \"{} {}\" ;".format(data[_linktype_label], data[_sameAsCount]),
               "\t       rdfs:subPropertyOf        <{}> .".format(data[_link_subpropertyof]),

               "\n\t     ### ASSERTION METHOD",
               "\t     <{}>".format(data[_assertion_method]),
               "\t       alivocab:sparql           \"\"\"{}\"\"\" .".format(data[_insert_query]),

               "\t}")
    print metadata
    return metadata


#################################################################
"""
    LENS BY UNION
"""
#################################################################


def lens_union(data, database_name, host, is_activated=False):

    """
    FOR A UNION OF LINKSETS, ALL LINKSET CORRESPONDENCES MUST HAVE THE SAME
    SUBJECT DATASET AND OBJECT DATASET.
    :param data:
    :param database_name:
    :param host:
    :param is_activated:
    :return:
    """

    insert_query = ""
    target_triple = ""
    datasets = data[St.datasets]

    # Check whether this linkset was already generated. If yes, delete it or change the context code
    check_01 = "\nASK {{ <{}> ?p ?o . }}".format(data[St.lens])
    print check_01
    ask = Qry.boolean_endpoint_response(check_01, database_name, host)
    ask = True if ask == "true" else False
    if ask is True:
        logger.warning("\n{} ALREADY EXISTS. \nTO PROCEED ANYWAY, PLEASE DELETE "
                       "THE LINKSET FIRST OR CHANGE THE CONTEXT CODE\n".format(data[St.lens]))
        return

    # CHECK WHETHER ALL LINKSETS HAVE THE SAME MECHANISM AND ARE ALL LINKSETS
    check_02 = Qry.get_type_mechanism(datasets[0], database_name, host)
    for i in range(1, len(datasets)):
        if check_02 == Qry.get_type_mechanism(datasets[i], database_name, host):
            print i, "True"
        else:
            print logger.warning("ALL GRAPHS MUST BE OF THE SAME TYPE AND MUST HAVE THE SAME MECHANISM.")
            return

    same_as_count = Qry.get_same_as_count(check_02[1][1], database_name, host)
    # print ame_as_count

    check_03 = Qry.get_linkset_datatypes(datasets[0], database_name, host)
    if check_03 is None:
        logger.warning("WE CAN NOT ACCESS THE DATA SOURCES OF THE LINKSET: {}".format(datasets[0]))

    else:
        # print "1. {}".format(base_matrix)
        for i in range(len(datasets)):
            # print "2. {}".format(datasets[i])

            # PROCEED WITH INTERSECTION CHECK
            if i > 0:

                cur_matrix = Qry.get_linkset_datatypes(datasets[i], database_name, host)
                # print "Current matrix: ", cur_matrix

                check = intersect(check_03[1][4:6], cur_matrix[1][4:6])
                # print "Check: \n\t{} against \n\t{}".format(base_matrix[1][4:6], cur_matrix[1][4:6])
                # print "Check result: {}".format(check)

                if len(check) < 2:
                    logger.warning("THE CURRENT LINKSET: {} HAS PROPERTIES THAT ARE\n DIFFERENT FROM THOSE OF THE "
                                   "BASE DATASET: {}.\n THEREFORE, WE ARE AFRAID TO NOT BE ABLE TO PROCEED WITH THE "
                                   "LINKSET UNION TASK REQUESTED AT THIS\nTIME. ".format(datasets[i], datasets[0]))
                    return

                if check_03[1][4] == cur_matrix[1][4]:
                    print "IT'S ALL GOOD, THE UNION CAN BE PERFORMED."

                else:
                    logger.warning("THE CURRENT LINKSET: {} HAS PROPERTIES THAT ARE\nDIFFERENT FROM THOSE OF "
                                   "THE BASE DATASET: {}.\nBECAUSE THE LINKSETS DO NOT SHARE THE SAME DATASET "
                                   "SOURCE AND OBJECT,\nWE ARE AFRAID TO NOT BE ABLE TO PROCEED WITH THE LINKSET "
                                   "UNION TASK REQUESTED AT THIS TIME.".format(datasets[i], datasets[0]))

            # GOOD TO GO
            # GET THE QUERIES THAT COPY THE GRAPH TO THE UNION DESTINATION
            query = Qry.q_copy_graph(data[St.lens],
                                     data[St.singleton], datasets[i], database_name, host)

            if i == 0:
                insert_query = query
                # GATHER METADATA INFO
                target_triple = "void:target                 <{}> ;".format(datasets[i])
            else:
                insert_query += " ;\n{}".format(query)
                # GATHER METADATA INFO
                target_triple += "\n        void:target                 <{}> ;".format(datasets[i])

        data['target_triple'] = target_triple
        data['insert_query'] = insert_query
        # INSERT LINKSET UNION
        if is_activated is True:
            Qry.boolean_endpoint_response(insert_query, database_name, host)

        triples = Qry.get_namedgraph_size(data[St.lens], database_name, host, isdistinct=False)

        # CONSTRUCT THE CORRESPONDENCE NAMED-GRAPH INSERTED TO WRITE TO FILE
        construct_query = Qry.construct_namedgraph(data[St.lens])
        construct_response = Qry.endpointconstruct(construct_query, database_name, host)
        if construct_response is not None:
            construct_response = construct_response.replace('{', "<{}>\n{{".format(data[St.lens]), 1)

        # CONSTRUCT THE SINGLETON METADATA MANED-GRAPH INSERTED TO WRITE TO FIE
        construct_singleton_query = Qry.construct_namedgraph(data[St.singleton])
        construct_sing_response = Qry.endpointconstruct(construct_singleton_query, database_name, host)
        if construct_sing_response is not None:
            construct_sing_response = construct_sing_response.\
                replace('{', "<{}>\n{{".format(construct_singleton_query), 1)

        # METADATA FOR GENERATING THE LINKSET GENERAL METADATA
        metadata = union_metadata(data, triples, same_as_count)

        if is_activated is True:
            Qry.boolean_endpoint_response(metadata, database_name, host)

        print metadata

        if is_activated is True:
            write_to_file(graph_name=data[St.link_name], metadata=metadata,
                          correspondences=construct_response, singletons=construct_sing_response)

        if is_activated is False:
            logger.warning("THE FUNCTION IS NOT ACTIVATED BUT THE METADATA THAT IS "
                           "SUPPOSED TO BE ENTERED IS WRITEN TO THE CONSOLE.")


def union_metadata(data, triples, same_as_count):

    metadata = "\n{}\n{}\n{}\n{}" \
               "\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}" \
               "\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}" \
               "\n{}\n{}\n{}\n{}\n{}" \
               "\n{}\n{}\n{}" \
               "\n{}\n{}\n{}\n{}". \
        format("##################################################################",
               "### METADATA ",
               "### in the linkset: {}".format(data[St.lens]),
               "##################################################################",

               "PREFIX rdfs:        <{}>".format(Ns.rdfs),
               "PREFIX alivocab:    <{}>".format(Ns.alivocab),
               "PREFIX void:        <{}>".format(Ns.void),
               "PREFIX bdb:         <{}>".format(Ns.bdb),
               "PREFIX lensOp:      <{}>".format(Ns.lensOp),

               "INSERT DATA",
               "{",
               "    <{}>".format(data[St.lens]),
               "        a                           bdb:Lenses ;",
               "        alivocab:operator           lensOp:union ;",
               "        alivocab:alignsMechanism    <{}{}> ;".format(Ns.mechanism, data[St.mechanism]),
               "        alivocab:sameAsCount        {} ;".format(same_as_count),
               "        void:triples                {} ;".format(triples),
               "        void:linkPredicate          <{}{}> ;".format(data[St.link], same_as_count),
               "        {}".format(data['target_triple']),
               "        alivocab:singletonGraph     <{}> ;".format(data[St.singleton]),
               "        bdb:linksetJustification    <{}> ;".format(data[St.justification]),
               "        bdb:assertionMethod         <{}> ;".format(data[St.assertion_method]),
               "        rdfs:comment                \"\"\"{}\"\"\" .".format(data[St.lens_comment]),

               "\n    ### METADATA ABOUT THE LINKTYPE",
               "      <{}{}>".format(data[St.link], same_as_count),
               "        rdfs:comment                \"\"\"{}\"\"\" ;".format(data[St.link_comment]),
               "        rdfs:label                  \"{}\" ;".format(data[St.link_name]),
               "        rdfs:subPropertyOf          <{}> .".format(data[St.link_subpropertyof]),

               "\n    ### METADATA ABOUT THE LINKSET JUSTIFICATION",
               "    <{}>".format(data[St.justification]),
               "        rdfs:comment              \"\"\"{}\"\"\" .".format(data[St.justification_comment]),

               "\n    ### ASSERTION METHOD",
               "    <{}>".format(data[St.assertion_method]),
               "        alivocab:sparql           \"\"\"{}\"\"\" .".format(data[St.insert_query]),

               "}")

    return metadata


#################################################################
"""
    LENS BY TRANSITIVITY
"""
#################################################################


def intersect(a, b):

    if (a is not None) and (b is not None):
        return list(set(a) & set(b))

    return None


def lens_transitive(data, database_name, host, activated=False):

    # CHECK BOTH DATASETS FOR SAME MECHANISM

    same_as_count = Qry.get_same_as_count(data[St.mechanism], database_name, host)
    # print same_as_count

    # GENERATE THE INSERT QUERY FOR TRANSITIVITY
    transitive_analyses = lens_transitive_query(data, database_name, host)
    if transitive_analyses is None:
        return

    insert_query = transitive_analyses[1]
    # print insert_query
    # exit(0)
    data['is_transitive_by'] = transitive_analyses[0]

    # RUN THE QUERY AT THE END POINT
    if activated is True:
        Qry.boolean_endpoint_response(insert_query, database_name, host)

    # GET THE SIZE OF THE LENS JUST CREATED ABOVE
    size = Qry.get_namedgraph_size(data['lens_uri'], database_name, host, isdistinct=False)

    # GENERATE THE METADATA ABOUT THE LENS JUST CREATED
    metadata = transitive_metadata(data, size, insert_query, same_as_count)
    print metadata

    # IF ACTIVATED, INSERT THE METADATA
    if activated is True:
        Qry.boolean_endpoint_response(metadata, database_name, host)

    # RUN A CORRESPONDENCE CONSTRUCT QUERY FOR BACKING UP THE DATA TO DISC
    construct_correspondence = Qry.endpointconstruct(Qry.construct_namedgraph(
        data['lens_uri']), database_name, host)

    if construct_correspondence is not None:
        construct_correspondence = construct_correspondence.replace('{', "<{}>\n{{".format(data['lens_uri']), 1)

    # RUN A SINGLETON METADATA CONSTRUCT QUERY FOR BACKING UP THE DATA TO DISC
    construct_singletons = Qry.endpointconstruct(Qry.construct_namedgraph(
        data['singleton_graph']), database_name, host)

    if construct_singletons is not None:
        construct_singletons = construct_singletons. \
            replace('{', "<{}>\n{{".format(data['singleton_graph']), 1)

    # WRITE TO FILE
    if activated is True:
        write_to_file(graph_name=data['link_label'], metadata=metadata,
                      correspondences=construct_correspondence, singletons=construct_singletons)

    if activated is False:
        logger.warning("THE FUNCTION IS NOT ACTIVATED BUT THE METADATA THAT IS "
                       "SUPPOSED TO BE ENTERED IS WRITEN TO THE CONSOLE.")


def lens_transitive_query(data, database_name, host):

    """
    :param data:
    :param database_name:
    :param host:
    :return: a list of:
        is transitive by : the graph by with the other are transitive
        the insert query : that is used to generate the transitive LS
    """

    # print "TRANSITIVITY"
    insert_query = ""
    is_transitive_by = ""
    pattern = re.compile('[^a-zA-Z]')

    # CHECK WHETHER THE GRAPH ALREADY EXIST
    ask_lens = Qry.graph_exists(data[St.lens], database_name, host)
    # print "lens: {}".format(data[ST.lens_uri])
    if ask_lens is True:
        logger.warning("\n{} ALREADY EXISTS. \nTO PROCEED ANYWAY, PLEASE DELETE "
                       "THE LINKSET FIRST OR CHANGE THE CONTEXT CODE\n".format(data[St.lens]))
        return

    # CHECK WHETHER THE GRAPHS EXIST
    ask_src = Qry.graph_exists(data[St.src_dataset], database_name, host)
    ask_trg = Qry.graph_exists(data[St.trg_dataset], database_name, host)
    if (ask_src is False) or (ask_trg is False):
        print "source: {} [{}]".format(data[St.src_dataset], ask_src)
        print "target: {} [{}]".format(data[St.trg_dataset], ask_trg)
        logger.warning("\nWE CAN NOT POSSIBLY RUN A TRANSITIVITY OPERATION OVER NON EXITING GRAPH".
                       format(data[St.lens]))
        return

    # #####################################################################
    """ RECONSTRUCTION OF THE WHERE QUERIES                            """
    # ###############################2#####################################

    s_predicate = "s_predicate"
    o_predicate = "o_predicate"
    result1 = reconstruct(data[St.src_dataset], data[St.src_graph_type], s_predicate, database_name, host)
    result2 = reconstruct(data[St.trg_dataset], data[St.trg_graph_type], o_predicate, database_name, host)

    # #####################################################################
    """ EXIT IF ONE OF THE DATASETS INPUT IS NOT COMPLIANT             """
    # ###############################2#####################################
    if (result1 is None) or (result2 is None):
        print "\nWE CANNOT PROCEED BECAUSE THERE IS NO TRANSITIVITY HERE :)"
        return None

    intersection_result = intersect(result1[0], result2[0])

    if intersection_result is None:
        print "\tSource:", result1[0]
        print "\tTarget:", result2[0]
        print "\nWE CANNOT PROCEED BECAUSE WE COULD NOT FIND ANY INTERSECTION BETWEEN THE DATASETS."
        return None

    if intersection_result is not None:

        if len(intersection_result) > 0:

            # print "VALUE", result1[0]
            is_transitive = intersect(result1[0], result2[0])
            # print is_transitive
            if len(is_transitive) > 1:
                print is_transitive
                print "\nWE CANNOT PROCEED BECAUSE THERE IS NO TRANSITIVITY HERE :)"
                return None

            is_transitive_by = is_transitive[0]

            # #####################################################################
            """ ACCESS SINGLETON GRAPH                                         """
            # #####################################################################
            subject_sing_query = ""
            string = "\t\t?{:50} ?{:20} ?{} .".format("subject", "sing_predicate", "object")
            singleton_gph_count = 0
            alternative1 = ""
            alternative2 = ""

            # THE SUBJECT DATASET CONTAINS A SINGLETON NAMED GRAPH
            if result1[1].__contains__(string):
                singleton_gph_count += 1
                alternative1 = "\n\t\t\t?{:20} ?{} ;".format("sing_predicate1", "object1")

            if result2[1].__contains__(string):
                singleton_gph_count += 1
                alternative2 = "\n\t\t\t?{:20} ?{} .".format("sing_predicate2", "object2")

            if alternative2 == "":
                alternative1 = "\n\t\t\t?{:20} ?{} .".format("sing_predicate1", "object1")

            linktype = "singPre"
            # object_sing_query = ""
            if singleton_gph_count > 0:
                subject_sing_query = "\n{}\n{}\n{}{}{}\n{}"\
                    .format("\tGRAPH tmpgraph:sing",
                            "\t{",
                            "\t\t?{}".format(s_predicate),
                            "{}".format(alternative1),
                            "{}".format(alternative2),
                            "\t}")

            # elif singleton_graph_count == 0:
            #     linktype = "<{}>".format(linktype)

            _subject = list(set(result1[0]).difference(result2[0]))
            if len(_subject) > 0:
                _subject = pattern.sub("", str(_subject[0]))

                _object = list(set(result2[0]).difference(result1[0]))
                if len(_object) > 0:
                    _object = pattern.sub("", str(_object[0]))

                    print "\nTRANSITIVITY ANALYSES"
                    print "\t{:15}: {}".format("SUBJECT", _subject)
                    print "\t{:15}: {}".format("OBJECT", _object)
                    print "\t{:15}: {}".format("TRANSITIVE by", is_transitive[0])

                string1 = "\t\t?{:50} ?{:20} ?{} .".format(s_predicate, "sing_predicate1", "object1")
                string2 = "\t\t?{:50} ?{:20} ?{} .".format(o_predicate, "sing_predicate2", "object2")
                insert_query = "\n{}\n{}" \
                               "\n\n###### PART 1: {} \n{}" \
                               "\n\n###### PART 2: {}\n{}" \
                               "\n\n###### PART 3: {}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}" \
                               "\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}" \
                               "\n\n###### PART 4: {}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}" \
                               "\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}" \
                               "\n\n###### PART 5: {}\n{}\n{}\n{}\n{}\n{}\n{}\n{}" \
                               "\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}" \
                               "\n\n###### PART 6: {}\n{}\n{}\n{}\n{}\n{}" \
                    .format("prefix tmpgraph:<{}>".format(Ns.tmpgraph),
                            "prefix tmpvocab:<{}>".format(Ns.tmpvocab),

                            # ### PART 1 ##########################################
                            # #####################################################
                            "LOAD SUBJECT CORRESPONDENCES AND SINGLETON METADATA (TEMPORARILY)",
                            "{} ;".format(result1[1].replace(string, string1)),

                            # ### PART 2 ##########################################
                            # #####################################################
                            "LOAD OBJECT CORRESPONDENCES AND SINGLETON METADATA (TEMPORARILY)",
                            "{} ;".format(result2[1].replace(string, string2)),

                            # ### PART 3 ##########################################
                            # #####################################################
                            "LOAD TEMPORARY CORRESPONDENCE  GRAPH",
                            # INSERT CORRESPONDENCE IN TEMPORARY GRAPH
                            "INSERT",
                            "{",
                            "\tGRAPH tmpgraph:corr01",
                            "\t{",
                            "\t\t?{} ?{} ?{} .".format(_subject, s_predicate, _object),
                            "\t}",
                            "{}".format(subject_sing_query),
                            "}",
                            "WHERE",
                            "{",
                            # WHERE SUBJECT CORRESPONDENCES  AND METADATA
                            "\tGRAPH tmpgraph:{}".format(s_predicate),
                            "\t{",
                            "\t\t?{:50} ?{:20} ?{} .".
                            format(pattern.sub("", result1[0][0]), s_predicate, pattern.sub("", result1[0][1])),
                            "\t\t?{:50} ?{:20} ?{} .".format(s_predicate, "sing_predicate1", "object1"),
                            "\t}",
                            # WHERE OBJECT CORRESPONDENCES AND METADATA
                            "\tGRAPH tmpgraph:{}".format(o_predicate),
                            "\t{",
                            "\t\t?{:50} ?{:20} ?{} .".
                            format(pattern.sub("", result2[0][0]), o_predicate, pattern.sub("", result2[0][1])),
                            "\t\t?{:50} ?{:20} ?{} .".format(o_predicate, "sing_predicate2", "object2"),
                            "\t}",
                            "} ;",

                            # ### PART 4 ##########################################
                            # #####################################################
                            "LOAD THE DEFINITIVE CORRESPONDENCE GRAPH",
                            "INSERT",
                            "{",
                            # INSERT DEFINITE CORRESPONDENCES
                            "\tGRAPH <{}>".format(data['lens_uri']),
                            "\t{",
                            "\t\t?{:50} ?{:20} ?{} .".format(_subject, linktype, _object),
                            "\t}",
                            # INSERT TEMPORALLY THE MAPPING BETWEEN NEWLY GENERATED SINGLETONS AND OLD ONCE
                            "\tGRAPH tmpgraph:sing_replaced",
                            "\t{",
                            "\t\t?{:50} {:20} ?{} .".format(linktype, "tmpvocab:replaced", s_predicate),
                            "\t}",

                            "}",
                            "WHERE",
                            "{",
                            # LOAD FROM TEMPORARY CORRESPONDENCE GRAPH
                            "\tGRAPH tmpgraph:corr01",
                            "\t{",
                            "\t\t?{} ?{} ?{} .".format(_subject, s_predicate, _object),
                            "\t\t### Create A SINGLETON URI",
                            "\t\tBIND( replace(\"{}_#\",\"#\",".format(data['link_predicate']),
                            "\t\tSTRAFTER(str(UUID()),\"uuid:\")) as ?pre )",
                            "\t\tBIND(iri(?pre) as ?singPre)",
                            "\t}",
                            "} ;",

                            # ### PART 5 ##########################################
                            # #####################################################
                            "###### LOAD THE DEFINITIVE SINGLETON GRAPH",
                            "INSERT",
                            "{",
                            "\tGRAPH <{}>".format(data['singleton_graph']),
                            "\t{",
                            "\t\t?{:50} ?{:20} ?{} .".format(linktype, "predicate", "object"),
                            "\t}",
                            "}",

                            "WHERE",
                            "{",
                            "\tGRAPH tmpgraph:sing",
                            "\t{",
                            "\t\t?{:50} ?{:20} ?{} .".format(s_predicate, "predicate", "object"),

                            "\t}",

                            "\tGRAPH tmpgraph:sing_replaced",
                            "\t{",
                            "\t\t?{:50} {:20} ?{} .".format(linktype, "tmpvocab:replaced", s_predicate),
                            "\t}",
                            "} ;",

                            # #### PART 5 ##########################################
                            # #####################################################
                            "DROP ALL TEMPORARY GRAPHS",
                            "DROP SILENT GRAPH tmpgraph:{} ;".format(o_predicate),
                            "DROP SILENT GRAPH tmpgraph:{} ;".format(s_predicate),
                            "DROP SILENT GRAPH tmpgraph:corr01 ;",
                            "DROP SILENT GRAPH tmpgraph:sing ;",
                            "DROP SILENT GRAPH tmpgraph:sing_replaced")

        # print "\n### INSERT QUERY"
        # print insert_query
        return is_transitive_by, insert_query


def reconstruct(linkset, gr_type, predicate, database_name, host):

    pattern = re.compile('[^a-zA-Z]')
    graph_format = "\t{:40} {}"
    sub_obj = None
    source = ""
    target = ""
    correspondence = ""
    singleton = ""
    singleton_triple = "\n\t\t?{:50} ?{:20} ?{} .".format("subject", "sing_predicate", "object")

    singleton_matrix = Qry.sparql_xml_to_matrix(Qry.get_singleton_graph(linkset), database_name, host)
    # print "Singleton graph of {}".format(linkset), singleton_matrix
    # exit(0)
    # SINGLETON EXAMPLE
    # GRAPH <http://risis.eu/lens/singletonMetadata/transitive_C000_ExactName>
    # {
    # 	?subject            sing_predicate          ?object .
    # }
    if singleton_matrix is not None:
        singleton_graph = singleton_matrix[1][0]
        if singleton_graph is not None:
            singleton = "\n{}\n{}\n{}\n{}\n" \
                .format("\tGRAPH <{}>".format(singleton_graph),
                        "\t{",
                        "\t\t?{:50} ?{:20} ?{} .".format("subject", "sing_predicate", "object"),
                        "\t}")
            # print  "\t", singleton

    # print str(graph_type).upper()
    # print str(graph_type).upper() == "LINKSET"
    # ABOUT LINKSET UNION
    if str(gr_type).upper() == "LINKSET":

        print "\nRECONSTRUCTING CASE: Linksets"

        datatype_matrix = Qry.get_linkset_datatypes(linkset, database_name, host)
        # print datatype_matrix

        if datatype_matrix is not None:
            sub_obj = datatype_matrix[1][4:6]
            source = pattern.sub("", str(datatype_matrix[1][4]))
            target = pattern.sub("", str(datatype_matrix[1][5]))

            # CORRESPONDENCE EXAMPLE
            # GRAPH <http://risis.eu/lens/transitive_C000_ExactName>
            # {
            # 	?leidenRanking ?singPre ?eter .
            # }
            correspondence = "{}\n{}\n{}\n{}".\
                format("\tGRAPH <{}>".format(linkset),
                       "\t{",
                       "\t\t?{:50} ?{:20} ?{} .".format(source, predicate, target),
                       "\t}")

    # DETERMINING WHETHER A LENS IS STEMMED FROM THE SAME subjectsTarget & objectsTarget
    elif str(gr_type).upper() == "LENS":
        print "\nRECONSTRUCTING CASE: Lenses"

        query = """
        PREFIX bdb: <http://vocabularies.bridgedb.org/ops#>
        PREFIX void: <http://rdfs.org/ns/void#>
        SELECT ?target ?subjectsTarget ?objectsTarget
        {{
          <{}> void:target ?target .
          ?target
            void:subjectsTarget     ?subjectsTarget ;
            void:objectsTarget      ?objectsTarget .
        }}
        """.format(linkset)
        # print query
        evaluation = False

        datatype_matrix = Qry.sparql_xml_to_matrix(query, database_name, host)
        # print "DATATYPE: ", datatype_matrix
        # print len(datatype_matrix)

        if datatype_matrix is None:
            print "THERE IS NO METADATA FOR THIS DATASET. "
            print "\nNO POSSIBLE RECONSTRUCTION FOR {}: {}".format(gr_type, linkset)
            print "ARE YOU SURE THE GRAPH IS OF TYPE [{}]?".format(gr_type)
            return None

        elif (datatype_matrix is not None) and (len(datatype_matrix) > 1):
            element = datatype_matrix[1][1:]
            # print element
            for i in range(1, len(datatype_matrix)):
                check = datatype_matrix[i][1:]
                evaluation = element == check
                # print check
                # print "result: ", evaluation
                if evaluation is not True:
                    evaluation = False
                    break
                else:
                    evaluation = True

            if evaluation is True:

                # singleton_matrix = sparql_xml_to_matrix(singleton_graph_query, database_name, host)

                sub_obj = element
                source = pattern.sub("", str(element[0]))
                target = pattern.sub("", str(element[1]))

                correspondence = "{}\n{}\n{}\n{}" \
                    .format("\tGRAPH <{}>".format(linkset),
                            "\t{",
                            "\t\t?{:50} ?{:20} ?{} .".format(source, predicate, target),
                            "\t}")

                print graph_format.format(sub_obj[0], sub_obj[1])

            else:
                return None

    # TEMPORARY GRAPH EXAMPLE
    # INSERT
    # {
    #   GRAPH temp:load001
    #   {
    #       ?leidenRanking  ?singPre                ?eter .
    #       ?subject        ?sing_predicate         ?object .
    #   }
    # }
    # WHERE
    # {
    #   GRAPH <http://risis.eu/lens/transitive_C000_ExactName>
    #   {
    # 	    ?leidenRanking  ?singPre                ?eter .
    #   }
    #   GRAPH <http://risis.eu/lens/singletonMetadata/transitive_C000_ExactName>
    #   {
    # 	    ?subject        ?sing_predicate          ?object .
    #   }
    # }
    insert_q = "{}\n{}\n{}\n{}\n{}{}\n{}\n{}" \
               "\n{}\n{}\n{}\n{}{}". \
        format("INSERT",
               "{",
               "   GRAPH tmpgraph:{}".format(predicate),
               "   {",
               "\t\t?{:50} ?{:20} ?{} .".format(source, predicate, target),
               "{}".format(singleton_triple),
               "    }",
               "}",

               "WHERE",
               "{",
               "{}".format(correspondence),
               "{}".format(singleton),
               "}")

    if singleton is not None:
        correspondence += singleton

    if sub_obj is not None:
        print graph_format.format(sub_obj[0], sub_obj[1])

    return [sub_obj, insert_q]


def transitive_metadata(data, size, insert_query, same_as_count):

    metadata = "\n{}\n{}\n{}\n{}" \
               "\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}" \
               "\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}" \
               "\n{}\n{}\n{}\n{}\n{}" \
               "\n{}\n{}\n{}" \
               "\n{}\n{}\n{}\n{}". \
        format("##################################################################",
               "### METADATA ",
               "### in the linkset: {}".format(data['lens_uri']),
               "##################################################################",

               "PREFIX rdfs:        <{}>".format(Ns.rdfs),
               "PREFIX alivocab:    <{}>".format(Ns.alivocab),
               "PREFIX void:        <{}>".format(Ns.void),
               "PREFIX bdb:         <{}>".format(Ns.bdb),
               "PREFIX lensOp:      <{}>".format(Ns.lensOp),

               "INSERT DATA",
               "{",
               "    <{}>".format(data['lens_uri']),
               "        a                           bdb:Lenses ;",
               "        alivocab:operator           lensOp:transitivity ;",
               "        void:triples                {} ;".format(size),
               "        alivocab:alignsMechanism    <{}{}> ;".format(Ns.mechanism, data[St.mechanism]),
               "        alivocab:sameAsCount        {} ;".format(same_as_count),
               "        void:linkPredicate          <{}{}> ;".format(data['link_predicate'], same_as_count),
               "        void:subjectsTarget         <{}> ;".format(data['src_dataset']),
               "        void:objectsTarget          <{}> ;".format(data['trg_dataset']),
               "        alivocab:isTransitiveBy     <{}> ;".format(data['is_transitive_by']),
               "        alivocab:singletonGraph     <{}> ;".format(data['singleton_graph']),
               "        bdb:linksetJustification    <{}> ;".format(data['lens_justification_uri']),
               "        bdb:assertionMethod         <{}> ;".format(data['assertion_method']),
               "        rdfs:comment                \"\"\"{}\"\"\" .".format(data['lens_comment']),

               "\n    ### METADATA ABOUT THE LINKTYPE",
               "    <{}{}>".format(data['link_predicate'], same_as_count),
               "        rdfs:comment                \"\"\"{}\"\"\" ;".format(data['link_comment']),
               "        rdfs:label                  \"{}\" ;".format(data['link_label']),
               "        rdfs:subPropertyOf          <{}> .".format(data['link_subpropertyof']),

               "\n    ### METADATA ABOUT THE LINKSET JUSTIFICATION",
               "    <{}>".format(data['lens_justification_uri']),
               "        rdfs:comment              \"\"\"{}\"\"\" .".format(data['justification']),

               "\n    ### ASSERTION METHOD",
               "    <{}>".format(data['assertion_method']),
               "        alivocab:sparql           \"\"\"{}\"\"\" .".format(insert_query),

               "}")

    return metadata
