import re
import os
import codecs
import rdflib
import Alignments.Query as Qry
import Alignments.Utility as Ut
import Alignments.Settings as St
import Alignments.NameSpace as Ns
import Alignments.Server_Settings as Svr
from kitchen.text.converters import to_unicode

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

# text = export_flat_alignment("http://risis.eu/linkset/orgreg_2017_grid_20171712_approxStrSim_Organisation_Char_legal_name_P147291413")
# text = export_flat_alignment("http://risis.eu/lens/union_Orgreg_2017_Grid_20171712_N1952841170")
# print text
# http://stardog.risis.d2s.labs.vu.nl/annex/risis/sparql/query


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

    total = 0
    limit = 20000
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

    # RUN THE ITERATIONS
    for i in range(0, iterations):

        offset = i * 20000 + 1
        print "ROUND: {} OFFSET: {}".format(i, offset)

        print "1. GENERATING THE ENRICHMENT QUERY"
        virtuoso = enrich_query(specs, limit=limit, offset=offset, isCount=False)
        print virtuoso
        exit(0)
        # print Qry.virtuoso(virtuoso)["result"]

        print "2. RUNNING THE QUERY + WRITE THE RESULT TO FILE"
        writer = codecs.open(f_path, "wb", "utf-8")
        batch_writer = codecs.open(b_path, "wb", "utf-8")
        writer.write(Qry.virtuoso(virtuoso)["result"])
        writer.close()

        print "3. GENERATING THE BATCH FILE TEXT"
        stardog_path = '' if Ut.OPE_SYS == "windows" else Svr.settings[St.stardog_path]
        load_text = """echo "Loading data"
        {}stardog data add risis -g http://risis.eu/dataset/{}_enriched "{}"
        """.format(stardog_path, "grid", f_path)
        batch_writer.write(to_unicode(load_text))
        batch_writer.close()

        print "4. RUNNING THE BATCH FILE"
        print "THE DATA IS BEING LOADED OVER HTTP POST." if Svr.settings[St.split_sys] is True \
            else "THE DATA IS BEING LOADED AT THE STARDOG LOCAL HOST FROM BATCH."
        os.system(b_path)

    print "JOB DONE...!!!!!!"

specs = {
    St.graph: "http://grid.ac/20170712",
    St.entity_datatype: "http://xmlns.com/foaf/0.1/Organization",
    St.long_predicate: "<http://www.grid.ac/ontology/hasAddress>/<http://www.w3.org/2003/01/geo/wgs84_pos#long>",
    St.lat_predicate: "<http://www.grid.ac/ontology/hasAddress>/<http://www.w3.org/2003/01/geo/wgs84_pos#lat>"
}
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

# export_flat_alignment_and_metadata("http://risis.eu/linkset/eter_2014_grid_20170712_exactStrSim_University_English_Institution_Name_N622708676")
# print Qry.virtuoso(virtuoso)["result"]