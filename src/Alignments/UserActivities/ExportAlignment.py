import re
import Alignments.Query as Qry
import Alignments.Utility as Ut
import Alignments.NameSpace as Ns

def export_flat_alignment(alignment):

    alignment = str(alignment).strip()
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
    return "### TRIPLE COUNT: {}\n### LINKSET: {}\n".format(triples, alignment) + alignment_construct

# text = export_flat_alignment("http://risis.eu/linkset/orgreg_2017_grid_20171712_approxStrSim_Organisation_Char_legal_name_P147291413")
# text = export_flat_alignment("http://risis.eu/lens/union_Orgreg_2017_Grid_20171712_N1952841170")
# print text


def federate():
    # http://linkedgeodata.org/OSM
    query = """
    ### 1. LOADING SOURCE AND TARGET TO A TEMPORARY GRAPH
    SELECT DISTINCT *
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
     Filter(bif:st_intersects (?geo, bif:st_point (117.379737854, 40.226871490479), 0.1))
            }
       }
    } limit 1000
    """

    # construct = Qry.sparql_xml_to_matrix(query)
    Qry.display_result(query, is_activated=True)

    # print construct

"""
select distinct ?subject ?level where
{
   GRAPH <http://geo.risis.eu/gadm>
   {
     ?subject <http://www.w3.org/2003/01/geo/wgs84_pos#geometry> ?geo ;
        <http://geo.risis.eu/vocabulary/gadm/level> ?level .
     Filter(bif:st_intersects (?geo, bif:st_point (117.379737854, 40.226871490479), 0.1))
   }
}
"""


federate()