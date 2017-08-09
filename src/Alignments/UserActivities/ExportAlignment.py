# -*- coding: utf-8 -*-
# coding=utf-8

import re
import os
import codecs
import rdflib
import cStringIO as Buffer
import Alignments.Query as Qry
import Alignments.Utility as Ut
import Alignments.Settings as St
import Alignments.NameSpace as Ns
import Alignments.Server_Settings as Svr
from kitchen.text.converters import to_unicode, to_bytes


# FLAT ALIGNMENT
def export_flat_alignment(alignment):

    print "Export for: {}".format(alignment)
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
    }} order by ?x
    """.format(Ns.alivocab, alignment)
    # print query
    # FIRE THE CONSTRUCT AGAINST THE TRIPLE STORE
    alignment_construct = Qry.endpointconstruct(query)

    # REMOVE EMPTY LINES
    triples = len(re.findall('ll:mySameAs', alignment_construct))
    alignment_construct = "\n".join([line for line in alignment_construct.splitlines() if line.strip()])

    # RESULTS
    result = "### TRIPLE COUNT: {}\n### LINKSET: {}\n".format(triples, alignment) + alignment_construct
    message = "You have just downloaded the graph [{}] which contains [{}] correspondences. ".format(
        row_alignment, triples)

    return {'result': result, 'message': message}


# EXPORT ALIGNMENT WITH GENERIC METADATA
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
    }} #LIMIT 10
    """.format(Ns.alivocab, Ns.linkset, Ns.lens, Ns.singletons, alignment, )
    # print query

    # FIRE THE CONSTRUCT AGAINST THE TRIPLE STORE
    alignment_construct = Qry.endpointconstruct(query, clean=False)

    # REMOVE EMPTY LINES
    triples = 0
    # triples = len(re.findall('ll:mySameAs', alignment_construct))
    alignment_construct = "\n".join([line for line in  alignment_construct.splitlines() if line.strip()])
    result = "### TRIPLE COUNT: {}\n### LINKSET: {}\n{}".format(triples, alignment, alignment_construct)
    message = "You have just downloaded the graph [{}] which contains [{}] correspondences. ".format(
        row_alignment, triples)
    print result
    return {'result': result, 'message': message}


# ALIGNMENT FOR VISUALISATION
def export_alignment(alignment):
    use = alignment
    alignment = str(alignment).strip()
    row_alignment = alignment
    alignment = alignment if Ut.is_nt_format(alignment) is True else "<{}>".format(alignment)
    src_dataset = None
    trg_dataset = None
    mec_dataset = None

    meta = """
    PREFIX ll: <{0}>
    CONSTRUCT {{ {1} ?y ?z }}
    WHERE
    {{
        {1} ?y ?z
    }} order by ?y
    """.format(Ns.alivocab, alignment)

    meta_construct = Qry.endpointconstruct(meta, clean=False)
    meta_construct = meta_construct.replace("{", "").replace("}", "")
    # print meta_construct

    sg = rdflib.Graph()
    sg.parse(data=meta_construct, format="turtle")
    sbj = rdflib.URIRef(use)
    source = rdflib.URIRef("http://rdfs.org/ns/void#subjectsTarget")
    target = rdflib.URIRef("http://rdfs.org/ns/void#objectsTarget")
    mechanism = rdflib.URIRef("http://risis.eu/alignment/predicate/alignsMechanism")

    for item in sg.objects(sbj, source):
        src_dataset = item

    for item in sg.objects(sbj, target):
        trg_dataset = item

    for item in sg.objects(sbj, mechanism):
        mec_dataset = item

    # CONSTRUCT QUERY
    query = """
    PREFIX ll: <{}>
    CONSTRUCT {{ ?x ?y ?z }}
    WHERE
    {{
        GRAPH {}
        {{
            ?x ?y ?z
        }}
    }} order by ?x #LIMIT 100
    """.format(Ns.alivocab, alignment)
    # print query
    # FIRE THE CONSTRUCT AGAINST THE TRIPLE STORE
    alignment_construct = Qry.endpointconstruct(query, clean=False)

    # REMOVE EMPTY LINES
    # triples = len(re.findall('ll:mySameAs', alignment_construct))
    # alignment_construct = "\n".join([line for line in  alignment_construct.splitlines() if line.strip()])
    triples = 0
    result = None
    # RESULTS

    if alignment_construct is not None:
        result = "### TRIPLE COUNT: {}\n### LINKSET: {}\n".format(triples, alignment) + alignment_construct
        result = result.replace("{", "").replace("}", "")
    message = "You have just downloaded the graph [{}] which contains [{}] correspondences. ".format(
        row_alignment, triples)

    # result = result
    # print result
    print "Done with graph: {}".format(alignment)
    return {
        'result': result,
        'message': message,
        'source': src_dataset,
        "target": trg_dataset,
        'mechanism': mec_dataset}


# ALIGNMENT FOR VISUALISATION: THE MAIN FUNCTION
def visualise(graphs):
    # uri_10 = "http://risis.eu/linkset/eter_2014_grid_20170712_exactStrSim_University_English_Institution_Name_P1141790218"
    uri_20 = "http://risis.eu/linkset/eter_2014_grid_20170712_exactStrSim_University_English_Institution_Name_N622708676"
    uri_30 = "http://risis.eu/linkset/eter_2014_grid_20170712_approxStrSim_University_English_Institution_Name_N81752458"
    uri_22 = "http://risis.eu/linkset/refined_eter_2014_grid_20170712_exactStrSim_University_English_Institution_Name_N622708676_exactStrSim_Country_Code"
    uri_33 = "http://risis.eu/linkset/refined_eter_2014_grid_20170712_approxStrSim_University_English_Institution_Name_N81752458_exactStrSim_Country_Code"
    graphs = [uri_20, uri_22, uri_30, uri_33]
    writer = Buffer.StringIO()
    # file = open("C:\Users\Al\PycharmProjects\AlignmentUI\src\UploadedFiles\plot.ttl", 'wb')
    g = rdflib.Graph()
    source = {}
    target = {}
    attribute = {}
    src_count = 0
    trg_count = 0
    prd_count = 0
    singletons = {}
    triples = 0
    datasets = (None, None)

    code = 0
    for graph in graphs:
        # print graph

        code = +1

        links = export_alignment(graph)
        mechanism = links['mechanism']
        # print "mechanism", mechanism
        if datasets == (None, None):
            datasets = (links["source"], links['target'])
        elif datasets != (links["source"], links['target']):
            print "No visualisation for different set of source-target"
            return None

        # print links['result']
        if links['result'] is not None:

            g.parse(data=links['result'], format="turtle")
            sg = rdflib.Graph()
            sg.parse(data=links['result'], format="turtle")
            triples += len(sg)

            for subject, predicate, obj in sg.triples((None, None, None)):
                if predicate not in singletons:
                    mech = "{}_{}".format(mechanism, code)
                    singletons[predicate] = [mech]
                elif mech not in singletons[mech]:
                    singletons[mech] += [mech]

    # prefix = """
    # PREFIX link: <http://risis.eu/alignment/link/>
    # PREFIX plot: <http://risis.eu/alignment/plot/>"""
    count = 0
    writer.write("PREFIX ll: <{}>\n".format(Ns.alivocab))
    writer.write("PREFIX rdf: <{}>\n".format(Ns.rdf))
    writer.write("PREFIX link: <http://risis.eu/alignment/link/>\n")
    writer.write("PREFIX plot: <http://risis.eu/alignment/plot/>\n")
    writer.write("PREFIX mechanism: <{}>\n".format(Ns.mechanism))

    # DROPPING GRAPH IT IT ALREADY EXISTS
    writer.write(
        "\nDROP SILENT GRAPH plot:{}_{} ;\n".format(
            Ut.get_uri_local_name(datasets[0]), Ut.get_uri_local_name(datasets[1])))

    # INSERT NEW DATA
    writer.write("INSERT DATA\n{")
    writer.write("\n\tGRAPH plot:{}_{}\n".format(Ut.get_uri_local_name(datasets[0]), Ut.get_uri_local_name(datasets[1])))
    writer.write("\t{")
    for subject, predicate, obj in g.triples((None, None, None)):

        count += 1

        # print "> ", subject, predicate, obj
        if subject not in source:
            src_count += 1
            source[subject] = src_count

        if obj not in target:
            trg_count += 1
            target[obj] = trg_count

        pre_code = "{}_{}".format(source[subject], target[obj])
        if pre_code not in attribute:
            prd_count += 1
            attribute[pre_code] = prd_count

        # print "> ", subject
        # print "> ", predicate
        # print "> ", obj
        # pred = "{}_{}".format(source[subject], target[obj])
        # print ">>> ", source[subject], attribute[pred], target[obj]

        writer.write("\n\t\t### [ {} ]\n".format(count))
        writer.write("\t\t{}\n".format(predicate).replace(Ns.alivocab, "ll:"))
        writer.write("\t\t\tlink:source     {} ;\n".format(source[subject]))
        writer.write("\t\t\tlink:target     {} ;\n".format(target[obj]))
        writer.write("\t\t\tlink:source_uri <{}> ;\n".format(subject))
        writer.write("\t\t\tlink:target_uri <{}> ;\n".format(obj))
        for value in singletons[predicate]:
            writer.write("\t\t\tlink:mechanism  {} ;\n".format(value).replace(Ns.mechanism, "mechanism:"))
        writer.write("\t\t\trdf:type        link:Link .\n")
        writer.write("")
    writer.write("\t}\n}")

    Qry.virtuoso_request(writer.getvalue())
    # print count, triples
    # file.close()

    return {'result': writer.getvalue(), 'message': "Constructed"}


# ENRICHING DATASETS WITH GADM BOUNDARIES: THE QUERY
def enrich_query(limit=0, offset=0, is_count=True):

    if is_count is True:
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
            BIND( xsd:double(replace(str(?long), ",", ".")) as ?longitude)
            BIND( xsd:double(replace(str(?lat), ",", ".")) as ?latitude)
            FILTER(contains(str(?longitude), ".") && contains(str(?latitude), "."))
       }}
       GRAPH <http://geo.risis.eu/gadm>
       {{
            ?gadm geo:geometry ?geo .
            ?gadm gadm:level   ?level .
            FILTER(?level = 2)
       }}
       FILTER(bif:st_intersects (?geo, bif:st_point (?longitude, ?latitude)))
    }}
    {2}LIMIT {7}
    {2}OFFSET {8}
    """.format(Ns.alivocab, count_comment, get_comment, specs[St.entity_datatype], specs[St.graph],
               specs['long_predicate'], specs['lat_predicate'], limit, offset)
    return virtuoso


# ENRICHING DATASETS WITH GADM BOUNDARIES: THE MAIN FUNCTION
def enrich(spec):

    # specs[St.graph] = "http://grid.ac/20170712"
    print "GRAP:", spec[St.graph]
    print "ENTITY TYPE:", spec[St.entity_datatype]
    print "LAT PREDICATE", spec[St.long_predicate]
    print "LONG PREDICATE", spec[St.lat_predicate]
    # return {St.message:"OK", St.result: "ok"}

    total = 0
    limit = 20000
    # enriched_graph = None
    f_path = "C:\Users\Al\PycharmProjects\AlignmentUI\src\UploadedFiles\enriched_graph.ttl"
    b_path = "C:\Users\Al\PycharmProjects\AlignmentUI\src\UploadedFiles\enriched_graph{}".format(Ut.batch_extension())

    print "0. GETTING THE TOTAL NUMBER OF TRIPLES."
    count = enrich_query(limit=0, offset=0, is_count=True)
    print count
    count_res = Qry.virtuoso_request(count)
    result = count_res['result']

    # GET THE TOTAL NUMBER OF TRIPLES
    if result is None:
        print "NO RESULT FOR THIS ENRICHMENT."
        return count_res

    g = rdflib.Graph()
    g.parse(data=result, format="turtle")
    attribute = rdflib.URIRef("http://www.w3.org/2005/sparql-results#value")
    for subject, predicate, obj in g.triples((None, attribute, None)):
        total = int(obj)

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
        virtuoso = enrich_query(limit=limit, offset=offset, is_count=False)
        print virtuoso
        # exit(0)
        # print Qry.virtuoso(virtuoso)["result"]

        print "2. RUNNING THE QUERY + WRITE THE RESULT TO FILE"
        writer.write(Qry.virtuoso_request(virtuoso)["result"])

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


def export_flat_alignment2(alignment):

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
    print query

    # FIRE THE CONSTRUCT AGAINST THE TRIPLE STORE
    alignment_construct = Qry.endpointconstruct(query)
    print alignment_construct

    # REMOVE EMPTY LINES
    triples = 0
    # triples = len(re.findall('ll:mySameAs', alignment_construct))
    # alignment_construct = "\n".join([line for line in  alignment_construct.splitlines() if line.strip()])
    result = "### TRIPLE COUNT: {}\n### LINKSET: {}\n".format(triples, alignment) + alignment_construct
    message = "You have just downloaded the graph [{}] which contains [{}] correspondences. ".format(
        row_alignment, triples)

    return {'result': result, 'message': message}


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
    alignment_construct = "\n".join([line for line in alignment_construct.splitlines() if line.strip()])
    result = "### TRIPLE COUNT: {}\n### LINKSET: {}\n".format(triples, alignment) + alignment_construct
    message = "You have just downloaded the graph [{}] which contains [{}] correspondences. ".format(
        row_alignment, triples)
    return {'result': result, 'message': message}


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
    print query

    # construct = Qry.sparql_xml_to_matrix(query)
    # Qry.display_result(query, is_activated=True)

    # print construct


def import_gadm_query(limit=0, offset=0, is_count=False):

    if is_count is True:
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
    {1}    ?gadm a <{4}Boundary> .
    {1}    #?gadm gadm:level   ?level .
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
    """.format(count_comment, get_comment, limit, offset, Ns.riclass)
    # print query
    return query


def import_gadm():

    total = 0
    limit = 2000
    f_path = "C:\Users\Al\PycharmProjects\AlignmentUI\src\UploadedFiles\gadm.ttl"
    b_path = "C:\Users\Al\PycharmProjects\AlignmentUI\src\UploadedFiles\gadm{}".format(Ut.batch_extension())

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
    count_query = import_gadm_query(is_count=True)
    # print count_query
    count_res = Qry.virtuoso_request(count_query)
    result = count_res['result']
    if result is None:
        print "NO RESULT FOR THIS ENRICHMENT."
        return count_res

    print "2. PROCESSING THE COUNT RESULT"
    g = rdflib.Graph()
    g.parse(data=result, format="turtle")
    attribute = rdflib.URIRef("http://www.w3.org/2005/sparql-results#value")
    for subject, predicate, obj in g.triples((None, attribute, None)):
        total = int(obj)
    iterations = total / limit if total % limit == 0 else total / limit + 1
    print "\tTOTAL TRIPLES TO RETREIVE  : {} \n\tTOTAL NUMBER OF ITERATIONS : {}\n".format(total, iterations)

    # RUN THE ITERATIONS
    try:
        for i in range(0, iterations):

            offset = i * limit + 1
            print "ROUND: {} OFFSET: {}".format(i, offset)

            print "\tRUNNING THE QUERY"
            import_query = import_gadm_query(limit=limit, offset=offset, is_count=False)
            response = Qry.virtuoso_request(import_query)

            print "RESPONSE SIZE: ".format(response["result"])

            print "\tWRITING THE RESULT TO FILE"
            writer.write(response["result"])

            break

    except Exception as err:
        print str(err.message)

    # CLOSE THE IMPORT WRITER
    writer.close()
    print "4. RUNNING THE BATCH FILE"
    print "THE DATA IS BEING LOADED OVER HTTP POST." if Svr.settings[St.split_sys] is True \
        else "THE DATA IS BEING LOADED AT THE STARDOG LOCAL HOST FROM BATCH."
    print "PATH:", b_path
    os.system(b_path)
    print "JOB DONE!!!"


def get_bom_type(file_path):

    # path = "C:\Users\Al\Google Drive\RISIS-Project-VU\WP 7 - " \
    #        "datasets\OrgReg\OrgReg 2017 (new)\ORGREG_20170718__Entities.txt"
    # path2 = "E:\Linking2GRID\Data\OrgReg 20170718\ORGREG_20170718__Entities.txt"
    reader = open(file_path, "rb")
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




uri_4 = "http://risis.eu/linkset/" \
        "orgreg_20170718_grid_20170712_exactStrSim_University_Entity_current_name_English_P1888721829"

# print visualise([uri_4])

specs = {
    St.graph: "http://grid.ac/20170712",
    St.entity_datatype: "http://xmlns.com/foaf/0.1/Organization",
    St.long_predicate: "<http://www.grid.ac/ontology/hasAddress>/<http://www.w3.org/2003/01/geo/wgs84_pos#long>",
    St.lat_predicate: "<http://www.grid.ac/ontology/hasAddress>/<http://www.w3.org/2003/01/geo/wgs84_pos#lat>"}


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


path = "http://risis.eu/linkset/eter_2014_grid_20170712_exactStrSim_University_English_Institution_Name_P1141790218"
# exp = export_flat_alignment_and_metadata(path)
# print exp[St.result]
# print Qry.virtuoso(virtuoso)["result"]

# import_gadm()

# line = reader.readline()
# line = reader.readline()
# print line.startswith(to_bytes(codecs.BOM_UTF8))
# print reader.readline()
# print reader.readline()
# print reader.readline()

# result = """
# ### TRIPLE COUNT: 0
# ### LINKSET: <http://risis.eu/linkset/
# eter_2014_grid_20170712_exactStrSim_University_English_Institution_Name_P1141790218>
# @prefix ll: <http://risis.eu/alignment/predicate/> .
# <http://risis.eu/eter_2014/resource/BE0056>
# ll:exactStrSim2_66a70877-4af9-4567-8618-5686439a0a3b <http://www.grid.ac/institutes/grid.5596.f> .
# <http://risis.eu/eter_2014/resource/BG0015>
# ll:exactStrSim2_39bca57f-ba77-4dc7-a469-717c333e80f6 <http://www.grid.ac/institutes/grid.465937.a> .
# <http://risis.eu/eter_2014/resource/CZ0058>
# ll:exactStrSim2_e8f594d4-acf8-4636-bdcc-dd2618cb0610 <http://www.grid.ac/institutes/grid.471548.b> .
# <http://risis.eu/eter_2014/resource/CZ0060>
# ll:exactStrSim2_ef65515b-2d92-4143-a58a-6d703e125dff <http://www.grid.ac/institutes/grid.453492.d> .
# <http://risis.eu/eter_2014/resource/CZ0060>
# ll:exactStrSim2_ef65515b-2d92-4143-a58a-6d703e125dff <http://www.grid.ac/institutes/grid.5596.f> .
# """

print uuid()