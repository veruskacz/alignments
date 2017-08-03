import re
import os
import codecs
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

# text = export_flat_alignment("http://risis.eu/linkset/orgreg_2017_grid_20171712_approxStrSim_Organisation_Char_legal_name_P147291413")
# text = export_flat_alignment("http://risis.eu/lens/union_Orgreg_2017_Grid_20171712_N1952841170")
# print text


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

def enrich():

    f_path = "C:\Users\Al\PycharmProjects\AlignmentUI\src\UploadedFiles\enriched_graph.ttl"
    b_path = "C:\Users\Al\PycharmProjects\AlignmentUI\src\UploadedFiles\enriched_graph{}".format(Ut.batch_extension())

    print "1. GETTING THE TOTAL NUMBER "
    count = """
    PREFIX ll: <{}>
    PREFIX pos: <http://www.w3.org/2003/01/geo/wgs84_pos#>
    PREFIX gadm: <http://geo.risis.eu/vocabulary/gadm/>
    SELECT (count(?dataset) as ?TOTAL)
    WHERE
    {{
       GRAPH <http://grid.ac/20170712>
       {{
            ?dataset <http://www.grid.ac/ontology/hasAddress>/pos:long ?long .
            ?dataset <http://www.grid.ac/ontology/hasAddress>/pos:lat  ?lat .
            FILTER(contains(str(?long), ".") && contains(str(?lat), "."))
       }}
       GRAPH <http://geo.risis.eu/gadm>
       {{
            ?gadm geo:geometry ?geo .
            ?gadm gadm:level   ?level .
            FILTER(?level = 2)
       }}
       FILTER(bif:st_intersects (?geo, bif:st_point (?long, ?lat), 0.1))
    }}
    """.format(Ns.alivocab, "http://xmlns.com/foaf/0.1/Organization")
    print count
    # count_res = Qry.virtuoso(count)
    total = 363101
    limit = 20000
    iteration = total / limit if total % limit == 0 else total / limit + 1
    print "ITERATIONS:", iteration
    for i in range(1, iteration):
        print "ROUND: {}".format(i)
        offset = i * 20000 + 1

        # print "1. GENERATING THE ENRICHMENT QUERY"
        # virtuoso = """
        # PREFIX ll: <{}>
        # PREFIX pos: <http://www.w3.org/2003/01/geo/wgs84_pos#>
        # PREFIX gadm: <http://geo.risis.eu/vocabulary/gadm/>
        # CONSTRUCT
        # {{
        #     ?dataset  a <{}> .
        #     ?dataset  ll:intersects ?gadm .
        #     #?gadm     gadm:level    ?level .
        # }}
        # WHERE
        # {{
        #    GRAPH <http://grid.ac/20170712>
        #    {{
        #         ?dataset <http://www.grid.ac/ontology/hasAddress>/pos:long ?long .
        #         ?dataset <http://www.grid.ac/ontology/hasAddress>/pos:lat  ?lat .
        #         FILTER(contains(str(?long), ".") && contains(str(?lat), "."))
        #    }}
        #    GRAPH <http://geo.risis.eu/gadm>
        #    {{
        #         ?gadm geo:geometry ?geo .
        #         ?gadm gadm:level   ?level .
        #         FILTER(?level = 2)
        #    }}
        #    FILTER(bif:st_intersects (?geo, bif:st_point (?long, ?lat), 0.1))
        # }}
        # LIMIT {}
        # OFFSET {}
        # """.format(Ns.alivocab, "http://xmlns.com/foaf/0.1/Organization", limit, offset)
        # print virtuoso
        # exit(0)
        # # print Qry.virtuoso(virtuoso)["result"]
        #
        # print "2. RUNNING THE QUERY + WRITE THE RESULT TO FILE"
        # writer = codecs.open(f_path, "wb", "utf-8")
        # batch_writer = codecs.open(b_path, "wb", "utf-8")
        # writer.write(Qry.virtuoso(virtuoso)["result"])
        # writer.close()
        #
        # print "3. GENERATING THE BATCH FILE TEXT"
        # stardog_path = '' if Ut.OPE_SYS == "windows" else Svr.settings[St.stardog_path]
        # load_text = """echo "Loading data"
        # {}stardog data add risis -g http://risis.eu/dataset/{}_enriched "{}"
        # """.format(stardog_path, "grid", f_path)
        # batch_writer.write(to_unicode(load_text))
        # batch_writer.close()
        #
        # print "4. RUNNING THE BATCH FILE"
        # print "THE DATA IS BEING LOADED OVER HTTP POST." if Svr.settings[St.split_sys] is True \
        #     else "THE DATA IS BEING LOADED AT THE STARDOG LOCAL HOST FROM BATCH."
        # os.system(b_path)

    print "JOB DONE...!!!!!!"

enrich()
# federate()
# X = {'message': 'OK', 'result': '@prefix res: <http://www.w3.org/2005/sparql-results#> .\n@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .\n_:_ a res:ResultSet .\n_:_ res:resultVariable "TOTAL" .\n_:_ res:solution [\n      res:binding [ res:variable "TOTAL" ; res:value 363101 ] ] .\n'}
# print X['result']

# print Qry.virtuoso(virtuoso)["result"]