# -*- coding: utf-8 -*-
# coding=utf-8

import re
import os
import codecs
import rdflib
import Alignments.Query as Qry
import Alignments.Utility as Ut
import Alignments.Settings as St
import Alignments.NameSpace as Ns
import Alignments.Server_Settings as Svr
from kitchen.text.converters import to_unicode, to_bytes


def export_flat_alignment(alignment):

    alignment = str(alignment).strip()
    row_alignment = alignment
    alignment = alignment if Ut.is_nt_format(alignment) is True else "<{}>".format(alignment)
    # CONSTRUCT QUERY
    query = """
    PREFIX ll: <{}>
    CONSTRUCT {{ ?x ll:mySameAs ?z }}
    WHERE
    {{
        GRAPH {}
        {{
            ?x ?y ?z
        }}
    }}
    """.format(Ns.alivocab, alignment)
    # print query
    # FIRE THE CONSTRUCT AGAINST THE TRIPLE STORE
    alignment_construct = Qry.endpointconstruct(query)
    # REMOVE EMPTY LINES
    triples = len(re.findall('ll:mySameAs', alignment_construct))
    alignment_construct = "\n".join([line for line in  alignment_construct.splitlines() if line.strip()])
    result = "### TRIPLE COUNT: {}\n### LINKSET: {}\n".format(triples, alignment) + alignment_construct
    message = "You have just downloaded the graph [{}] which contains [{}] correspondences. ".format(
        row_alignment, triples)
    return {'result': result, 'message':message}


def export_flat_alignment_and_metadata(alignment):

    alignment = str(alignment).strip()
    row_alignment = alignment
    alignment = alignment if Ut.is_nt_format(alignment) is True else "<{}>".format(alignment)
    # CONSTRUCT QUERY
    query = """
    PREFIX ll: <{0}>
    PREFIX linkset: <{1}>
    PREFIX lens: <{2}>
    PREFIX singletons: <{3}>
    CONSTRUCT
    {{
        ?srcCorr  ll:mySameAs ?trgCorr .
        ?trgCorr  ll:mySameAs ?srcCorr .
        ?alignment ?pred  ?obj .
        ?obj  ?predicate ?object .
    }}
    WHERE
    {{
        BIND( {4} as ?alignment )
        # THE ALIGNMENT GRAPH WITH EXPLICIT SYMMETRY
        GRAPH ?alignment
        {{
            ?srcCorr ?singleton ?trgCorr .
        }}

         # THE METADATA
        ?alignment  ?pred  ?obj .
        OPTIONAL {{ ?obj  ?predicate ?object . }}
    }}
    """.format(Ns.alivocab, Ns.linkset, Ns.lens, Ns.singletons, alignment, )
    # print query

    # FIRE THE CONSTRUCT AGAINST THE TRIPLE STORE
    alignment_construct = Qry.boolean_endpoint_response(query)

    # REMOVE EMPTY LINES
    triples = 0
    # triples = len(re.findall('ll:mySameAs', alignment_construct))
    # alignment_construct = "\n".join([line for line in  alignment_construct.splitlines() if line.strip()])
    result = "### TRIPLE COUNT: {}\n### LINKSET: {}\n".format(triples, alignment) + alignment_construct
    message = "You have just downloaded the graph [{}] which contains [{}] correspondences. ".format(
        row_alignment, triples)
    return {'result': result, 'message':message}


def export_flat_alignment_service(alignment):

    alignment = str(alignment).strip()
    row_alignment = alignment
    alignment = alignment if Ut.is_nt_format(alignment) is True else "<{}>".format(alignment)
    # CONSTRUCT QUERY
    query = """
    PREFIX ll: <{0}>
    PREFIX linkset: <{1}>
    PREFIX lens: <{2}>
    PREFIX singletons: <{3}>
    CONSTRUCT
    {{
        ?srcCorr  ll:mySameAs ?trgCorr .
        ?trgCorr  ll:mySameAs ?srcCorr .
    }}
    WHERE
    {{
        BIND( {4} as ?alignment )
        # THE ALIGNMENT GRAPH WITH EXPLICIT SYMMETRY
        GRAPH ?alignment
        {{
            ?srcCorr ?singleton ?trgCorr .
        }}
    }} ;

    CONSTRUCT
    {{
        ?alignment ?pred  ?obj .
        ?obj  ?predicate ?object .
    }}
    WHERE
    {{
        # THE METADATA
        BIND( {4} as ?alignment )
        ?alignment  ?pred  ?obj .
        OPTIONAL {{ ?obj  ?predicate ?object . }}
    }}

    """.format(Ns.alivocab, Ns.linkset, Ns.lens, Ns.singletons, alignment, )
    print query
    exit(0)
    # FIRE THE CONSTRUCT AGAINST THE TRIPLE STORE
    alignment_construct = Qry.endpointconstruct(query)
    # REMOVE EMPTY LINES
    triples = len(re.findall('ll:mySameAs', alignment_construct))
    alignment_construct = "\n".join([line for line in  alignment_construct.splitlines() if line.strip()])
    result = "### TRIPLE COUNT: {}\n### LINKSET: {}\n".format(triples, alignment) + alignment_construct
    message = "You have just downloaded the graph [{}] which contains [{}] correspondences. ".format(
        row_alignment, triples)
    return {'result': result, 'message':message}


def federate():
    # http://linkedgeodata.org/OSM
    query = """
    ### 1. LOADING SOURCE AND TARGET TO A TEMPORARY GRAPH
    PREFIX geo: <http://www.opengis.net/def/function/geosparql/>
    PREFIX geof: <http://www.opengis.net/def/function/geosparql/>
    PREFIX bif: <http://www.openlinksw.com/schemas/bif#>
    SELECT DISTINCT ?subject ?level
    WHERE
    {
        ### SOURCE DATASET
        service <http://sparql.sms.risis.eu>
        {
            graph <http://geo.risis.eu/gadm>
            {
                # ?subj ?pred ?obj .
                ?subject <http://www.w3.org/2003/01/geo/wgs84_pos#geometry> ?geo ;
                    <http://geo.risis.eu/vocabulary/gadm/level> ?level .
                Filter(geof:nearby (?geo, "Point(-77.03653 38.897676 )"^^geo:wktLiteral, 0.1))
            }
       }
    } limit 1000
    """

    # construct = Qry.sparql_xml_to_matrix(query)
    # Qry.display_result(query, is_activated=True)

    # print construct


def enrich_query(specs, limit=0, offset=0, isCount=True):

    if isCount is True:
        count_comment = ""
        get_comment = "#"
    else:
        count_comment = "#"
        get_comment = ""

    virtuoso = """
    PREFIX ll: <{0}>
    PREFIX gadm: <http://geo.risis.eu/vocabulary/gadm/>
    {1}SELECT (count(?dataset) as ?TOTAL)
    {2}CONSTRUCT
    {2}{{
    {2}    ?dataset  a <{3}> .
    {2}    ?dataset  ll:intersects ?gadm .
    {2}    #?gadm     gadm:level    ?level .
    {2}}}
    WHERE
    {{
       GRAPH <{4}>
       {{
            ?dataset {5} ?long .
            ?dataset {6} ?lat .
            FILTER(contains(str(?long), ".") && contains(str(?lat), "."))
       }}
       GRAPH <http://geo.risis.eu/gadm>
       {{
            ?gadm geo:geometry ?geo .
            ?gadm gadm:level   ?level .
            FILTER(?level = 2)
       }}
       FILTER(bif:st_intersects (?geo, bif:st_point (?long, ?lat)))
    }}
    {2}LIMIT {7}
    {2}OFFSET {8}
    """.format(Ns.alivocab, count_comment, get_comment, specs[St.entity_datatype], specs[St.graph],
               specs['long_predicate'], specs['lat_predicate'], limit, offset)
    return virtuoso


def enrich(specs):

    specs[St.graph] = "http://grid.ac/20170712"
    print specs[St.graph]
    print specs[St.entity_datatype]
    print specs[St.long_predicate]
    print specs[St.lat_predicate]
    # return {St.message:"OK", St.result: "ok"}


    total = 0
    limit = 20000
    enriched_graph = None
    f_path = "C:\Users\Al\PycharmProjects\AlignmentUI\src\UploadedFiles\enriched_graph.ttl"
    b_path = "C:\Users\Al\PycharmProjects\AlignmentUI\src\UploadedFiles\enriched_graph{}".format(Ut.batch_extension())

    print "0. GETTING THE TOTAL NUMBER OF TRIPLES."
    count = enrich_query(specs, limit=0, offset=0, isCount=True)
    print count
    count_res = Qry.virtuoso(count)
    result = count_res['result']

    # GET THE TOTAL NUMBER OF TRIPLES
    if result is None:
        print "NO RESULT FOR THIS ENRICHMENT."
        return count_res

    g = rdflib.Graph()
    g.parse(data=result, format="turtle")
    property = rdflib.URIRef("http://www.w3.org/2005/sparql-results#value")
    for subject, predicate, object in g.triples((None, property, None)):
        total = int(object)

    # NUMBER OF REQUEST NEEDED
    iterations = total / limit if total % limit == 0 else total / limit + 1
    print "TOTAL TRIPLES TO RETREIVE  : {} \nTOTAL NUMBER OF ITERATIONS : {}\n".format(total, iterations)


    writer = codecs.open(f_path, "wb", "utf-8")
    batch_writer = codecs.open(b_path, "wb", "utf-8")

    print "3. GENERATING THE BATCH FILE TEXT"
    enriched_graph = "{}_enriched".format(specs[St.graph])
    stardog_path = '' if Ut.OPE_SYS == "windows" else Svr.settings[St.stardog_path]
    load_text = """echo "Loading data"
            {}stardog data add risis -g {} "{}"
            """.format(stardog_path, enriched_graph, f_path)
    batch_writer.write(to_unicode(load_text))
    batch_writer.close()



    # RUN THE ITERATIONS
    for i in range(0, iterations):

        offset = i * 20000 + 1
        print "ROUND: {} OFFSET: {}".format(i, offset)

        print "1. GENERATING THE ENRICHMENT QUERY"
        virtuoso = enrich_query(specs, limit=limit, offset=offset, isCount=False)
        print virtuoso
        # exit(0)
        # print Qry.virtuoso(virtuoso)["result"]

        print "2. RUNNING THE QUERY + WRITE THE RESULT TO FILE"
        writer.write(Qry.virtuoso(virtuoso)["result"])

    writer.close()
    print "4. RUNNING THE BATCH FILE"
    print "THE DATA IS BEING LOADED OVER HTTP POST." if Svr.settings[St.split_sys] is True \
        else "THE DATA IS BEING LOADED AT THE STARDOG LOCAL HOST FROM BATCH."
    os.system(b_path)

    # TODO 1. REGISTER THE DATASET TO BE ENRICHED IF NOT YET REGISTER
    # TODO 2. ADD THE ENRICHED DATASET TO THE RESEARCH QUESTION (REGISTER).
    # TODO 3. MAYBE, CREATE THE LINKSET BETWEEN THE SOURCE AND THE RESULTING

    print "JOB DONE...!!!!!!"

    return {St.message: "The select dataset was enriched with the GADM boundary as {}".format(enriched_graph),
            St.result: enriched_graph}


def import_gadm_query(limit=0, offset=0, isCount=False):

    if isCount is True:
        count_comment = ""
        get_comment = "#"
    else:
        count_comment = "#"
        get_comment = ""

    query = """
    PREFIX gadm: <http://geo.risis.eu/vocabulary/gadm/>
    {0}SELECT (COUNT (DISTINCT ?gadm ) AS ?TOTAL)
    {1}CONSTRUCT
    {1}{{
    {1}    ?gadm geo:geometry ?geo .
    {1}    ?gadm gadm:level   ?level .
    {1}}}
    WHERE
    {{
        GRAPH <http://geo.risis.eu/gadm>
        {{
            ?gadm geo:geometry ?geo .
            ?gadm gadm:level   ?level .
            #FILTER(?level = 2)
        }}
    }}
    {1}LIMIT {2} OFFSET {3}
    """.format(count_comment, get_comment, limit, offset)
    # print query
    return query


def import_gadm():

    total = 0
    limit = 10000
    f_path = "C:\Users\Al\PycharmProjects\AlignmentUI\src\UploadedFiles\gadm.ttl"
    b_path = "C:\Users\Al\PycharmProjects\AlignmentUI\src\UploadedFiles\gadm".format(Ut.batch_extension())

    # CREATE THE WRITERS
    writer = codecs.open(f_path, "wb", "utf-8")
    batch_writer = codecs.open(b_path, "wb", "utf-8")

    # GENERATING THE BATCH FILE TEXT
    graph = "{}gadm".format(Ns.dataset)
    stardog_path = '' if Ut.OPE_SYS == "windows" else Svr.settings[St.stardog_path]
    load_text = """echo "Loading data"
                {}stardog data add risis -g {} "{}"
                """.format(stardog_path, graph, f_path)
    batch_writer.write(to_unicode(load_text))
    batch_writer.close()

    print "1. GET THE TOTAL NUMBER OF TRIPLES TO LOAD"
    count_query = import_gadm_query(isCount=True)
    # print count_query
    count_res = Qry.virtuoso(count_query)
    result = count_res['result']
    if result is None:
        print "NO RESULT FOR THIS ENRICHMENT."
        return count_res

    print "2. PROCESSING THE COUNT RESULT"
    g = rdflib.Graph()
    g.parse(data=result, format="turtle")
    property = rdflib.URIRef("http://www.w3.org/2005/sparql-results#value")
    for subject, predicate, object in g.triples((None, property, None)):
        total = int(object)
    iterations = total / limit if total % limit == 0 else total / limit + 1
    print "\tTOTAL TRIPLES TO RETREIVE  : {} \n\tTOTAL NUMBER OF ITERATIONS : {}\n".format(total, iterations)


    # RUN THE ITERATIONS
    try:
        for i in range(0, iterations):

            offset = i * 20000 + 1
            print "ROUND: {} OFFSET: {}".format(i, offset)

            print "\tRUNNING THE QUERY"
            import_query = import_gadm_query(limit=limit, offset=offset, isCount=False)
            response = Qry.virtuoso(import_query)

            print "\tWRITING THE RESULT TO FILE"
            writer.write(response["result"])

    except Exception as err:
        print str(err.message)

    # CLOSE THE IMPORT WRITER
    writer.close()
    print "4. RUNNING THE BATCH FILE"
    print "THE DATA IS BEING LOADED OVER HTTP POST." if Svr.settings[St.split_sys] is True \
        else "THE DATA IS BEING LOADED AT THE STARDOG LOCAL HOST FROM BATCH."
    os.system(b_path)


specs = {
    St.graph: "http://grid.ac/20170712",
    St.entity_datatype: "http://xmlns.com/foaf/0.1/Organization",
    St.long_predicate: "<http://www.grid.ac/ontology/hasAddress>/<http://www.w3.org/2003/01/geo/wgs84_pos#long>",
    St.lat_predicate: "<http://www.grid.ac/ontology/hasAddress>/<http://www.w3.org/2003/01/geo/wgs84_pos#lat>" }

# text = export_flat_alignment("http://risis.eu/linkset/orgreg_2017_grid_20171712_approxStrSim_Organisation_Char_legal_name_P147291413")
# text = export_flat_alignment("http://risis.eu/lens/union_Orgreg_2017_Grid_20171712_N1952841170")
# print text
# http://stardog.risis.d2s.labs.vu.nl/annex/risis/sparql/query

"""
PREFIX bif: <http://www.openlinksw.com/schemas/bif#>
select distinct ?subject ?level where
{
   GRAPH <http://geo.risis.eu/gadm>
   {
     ?subject <http://www.w3.org/2003/01/geo/wgs84_pos#geometry> ?geo ;
        <http://geo.risis.eu/vocabulary/gadm/level> ?level .
     #    point(long, lat)
     Filter(bif:st_intersects (?geo, bif:st_point(117.379737854, 40.226871490479), 0.1))
   }
}
"""

# enrich(specs)
# federate()
# X = {'message': 'OK', 'result': '@prefix res: <http://www.w3.org/2005/sparql-results#> .\n@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .\n_:_ a res:ResultSet .\n_:_ res:resultVariable "TOTAL" .\n_:_ res:solution [\n      res:binding [ res:variable "TOTAL" ; res:value 363101 ] ] .\n'}
# print X['result']
# g = rdflib.Graph()
# g.parse(data=None, format="turtle")
# print len(g)
# print str(g)
# print list(g[rdflib.URIRef('_:_ ')])
# property = rdflib.URIRef("http://www.w3.org/2005/sparql-results#value")
# for subject, predicate, object in g.triples((None, property, None)):
#     print int(object)
#

# exp = export_flat_alignment_and_metadata("http://risis.eu/linkset/eter_2014_grid_20170712_exactStrSim_University_English_Institution_Name_P1141790218")
# print exp[St.result]
# print Qry.virtuoso(virtuoso)["result"]

# import_gadm()


# line = reader.readline()
# line = reader.readline()
# print line.startswith(to_bytes(codecs.BOM_UTF8))
# print reader.readline()
# print reader.readline()
# print reader.readline()


def get_bom_type(line):

    path = "C:\Users\Al\Google Drive\RISIS-Project-VU\WP 7 - datasets\OrgReg\OrgReg 2017 (new)\ORGREG_20170718__Entities.txt"
    path2 = "E:\Linking2GRID\Data\OrgReg 20170718\ORGREG_20170718__Entities.txt"
    reader = open(path2, "rb")
    line = reader.readline()

    bom_type = None
    text = None

    if line.startswith(to_bytes(codecs.BOM_BE)):
        bom_type = to_bytes(codecs.BOM_BE)
        text = "BOM_BE"
    elif line.startswith(to_bytes(codecs.BOM32_BE)):
        bom_type = to_bytes(codecs.BOM32_LE)
        text = "BOM32_BE"
    elif line.startswith(to_bytes(codecs.BOM64_BE)):
        bom_type = to_bytes(codecs.BOM64_LE)
        text = "BOM64_BE"
    elif line.startswith(to_bytes(codecs.BOM_UTF16_BE)):
        bom_type = to_bytes(codecs.BOM_UTF16_BE)
        text = "BOM_UTF16_BE"
    elif line.startswith(to_bytes(codecs.BOM_UTF32_BE)):
        bom_type = to_bytes(codecs.BOM_UTF32_BE)
        text = "BOM_UTF32_BE"

    elif line.startswith(to_bytes(codecs.BOM_LE)):
        bom_type = to_bytes(codecs.BOM_LE)
        text = "BOM_LE"
    elif line.startswith(to_bytes(codecs.BOM32_LE)):
        bom_type = to_bytes(codecs.BOM32_LE)
        text = "BOM32_LE"
    elif line.startswith(to_bytes(codecs.BOM64_LE)):
        bom_type = to_bytes(codecs.BOM64_LE)
        text = "BOM64_LE"
    elif line.startswith(to_bytes(codecs.BOM_UTF16_LE)):
        bom_type = to_bytes(codecs.BOM_UTF16_LE)
        text = "BOM_UTF16_LE"
    elif line.startswith(to_bytes(codecs.BOM_UTF32_LE)):
        bom_type = to_bytes(codecs.BOM_UTF32_LE)
        text = "BOM_UTF32_LE"

    elif line.startswith(to_bytes(codecs.BOM_UTF8)):
        bom_type = to_bytes(codecs.BOM_UTF8)
        text = "BOM_UTF8"
    elif line.startswith(to_bytes(codecs.BOM_UTF16)):
        bom_type = to_bytes(codecs.BOM_UTF16)
        text = "BOM_UTF16"
    elif line.startswith(to_bytes(codecs.BOM_UTF32)):
        bom_type = to_bytes(codecs.BOM_UTF32)
        text = "BOM_UTF32"

    # bom = ""
    # for i in range(len(bom_type)):
    #     bom += line[i]
    # line = line.replace(bom, '')
    # line = line.decode("utf_8")

    # print len(bom_type)
    line = line[len(bom_type):]
    print "line: {}".format(line)

    if text is None:
        print "THE LINE IS ENCODED WITH NONE OF THE FOLLOWING FORMATS:\n" \
              "\tBOM_BE - BOM32_BE - BOM64_BE - BOM_UTF16_BE - BOM_UTF32_BE\n" \
              "\tBOM_LE - BOM32_LE - BOM64_LE - BOM_UTF16_LE - BOM_UTF32_LE\n" \
              "\tBOM_UTF8 - BOM_UTF16 - BOM_UTF32"
    else:
        print text

    return bom_type


def extractor(record, separator):
    record= """BG0001;South-West University Neofit Rilski;1976;"Data from ETER. Different foudation year on the website;1976";a;;http://www.swu.bg/?lang=en 	 """
    #record = """﻿Entity ID;Entity current name (English);Entity foundation year;Remarks on foundation year;Entity closure year;Remarks on closure year;Website of entity """
    separator = ";"
    td = '"'
    attributes = []
    temp = ""

    # print record
    i = 0
    while i < len(record):

        if record[i] == td:
            j = i + 1
            while j < len(record):
                if record[j] != td:
                    temp += record[j]
                elif j + 1 < len(record) and record[j + 1] != separator:
                    if record[j] != td:
                        temp += record[j]
                elif j + 1 < len(record) and record[j + 1] == separator:
                    j += 2
                    break
                j += 1

            attributes.append(temp)
            temp = ""
            i = j

        else:
            while i < len(record):

                # Enqueue if you encounter the separator
                if record[i] == separator:
                    attributes.append(temp)
                    # print "> separator " + temp
                    temp = ""

                # Append if the current character is not a separator
                if record[i] != separator:
                    temp += record[i]
                    # print "> temp " + temp

                # Not an interesting case. Just get oit :-)
                else:
                    i += 1
                    break

                # Increment the iterator
                i += 1

    # Append the last attribute
    if temp != "":
        attributes.append(temp)

    # print "EXTRACTOR RETURNED: {}".format(attributes)
    return attributes

# terms = extractor("", "")
# print len(terms)
# for i in range(0, len(terms)):
#     print "{} - {}".format(i+1, terms[i])
