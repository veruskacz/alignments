from Alignments.Manage.AdminGraphs import drop_linkset
from Alignments.Query import display_result as display
from Alignments.Query import sparql_xml_to_matrix as sparql_matrix
import Alignments.NameSpace as Ns

""" EXECUTE LINKSET SPECIFICATIONS """
# to_delete = "http://risis.eu/linkset/grid_20170522_orgref10_exactStrSim_label_P1517853875"
# to_delete = "http://risis.eu/linkset/refined_en_nl_exactStrSim_label_P916744941_intermediate_author_name"
# to_delete = "http://risis.eu/linkset/en_nl_intermediate_author_name_N36817389"
# to_delete = "http://risis.eu/linkset/en_nl_exactStrSim_name_N467336337"
# drop_linkset(to_delete, display=False, activated=True)

"""
PREFIX linkset:     <http://risis.eu/linkset/>
PREFIX activity:    <http://risis.eu/activity/>
delete data
{
    GRAPH activity:idea_2e6b7c
    {
        activity:idea_algmt_222eea
            alivocab:created        linkset:en_nl_intermediate_author_label_P1605654795 .
    }
}
"""


def linkset_aligns_prop(linkset_uri):
    query = """
        ################################################################
        PREFIX ll:    <{}>
        PREFIX prov:  <{}>

        ### LINKSET ALIGNED PROPERTIES

        SELECT ?s_prop ?o_prop
        {{
            ### RETRIEVING LINKSET METADATA
            <{}>
                prov:wasDerivedFrom*        ?linkset .

            ?linkset
                ll:alignsSubjects     ?s_prop ;
                ll:alignsObjects      ?o_prop .
        }}
    """.format(Ns.alivocab, Ns.prov, linkset_uri)
    return query


def linkset_detail_query(linkset_uri):

    query = """
    ################################################################
    PREFIX bdb:         <http://vocabularies.bridgedb.org/ops#>
    PREFIX rdf:         <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX linkset:     <http://risis.eu/linkset/>
    PREFIX void:        <http://rdfs.org/ns/void#>
    PREFIX alivocab:    <http://risis.eu/alignment/predicate/>
    PREFIX tmpgraph:    <http://risis.eu/alignment/temp-match/>
    PREFIX prov:        <http://www.w3.org/ns/prov#>

    ### LINKSET DETAILS WITH SAMPLE OF ALIGNED PREDICATES

    SELECT DISTINCT
    ?subTarget ?objTarget ?s_datatype ?o_datatype ?operator
    (GROUP_CONCAT(?s_PredV; SEPARATOR=" | ") as ?s_PredValue)
    (GROUP_CONCAT(?o_PredV; SEPARATOR=" | ") as ?o_PredValue)
    (GROUP_CONCAT(?s_prop; SEPARATOR="|") as ?s_property)
    (GROUP_CONCAT(?o_prop; SEPARATOR="|") as ?o_property)
    (GROUP_CONCAT(?mec; SEPARATOR="|") as ?mechanism)
    (GROUP_CONCAT(?trip; SEPARATOR="|") as ?triples)

    WHERE
    {
        ### GETTING THE LINKSET AND DERIVED LINKSETS WHEN REFINED
        <http://risis.eu/linkset/refined_en_nl_exactStrSim_label_P916744941_intermediate_author_name>
            prov:wasDerivedFrom*        ?linkset .

        ### RETRIEVING LINKSET METADATA
        ?linkset
            alivocab:alignsMechanism    ?mec ;
            void:subjectsTarget         ?subTarget ;
            void:objectsTarget          ?objTarget ;
            bdb:subjectsDatatype        ?s_datatype ;
            bdb:objectsDatatype         ?o_datatype ;
            alivocab:alignsSubjects     ?s_prop;
            alivocab:alignsObjects      ?o_prop ;
            void:triples                ?trip .

        ### RETRIEVING CORRESPONDENCES
        GRAPH  <http://risis.eu/linkset/refined_en_nl_exactStrSim_label_P916744941_intermediate_author_name>
        {
            ?sub_uri    ?aligns        ?obj_uri
        }

        ### RETRIEVING SUBJECT DATASET INFO
        GRAPH ?subTarget
        {
            ###SOURCE SLOT
        }

        ### RETRIEVING OBJECT DATASET INFO WHEN EXISTS
        ### SOME ALIGNMENTS LIKE EMBEDDED SUBSET DO NOT USE OBJECT DATASET
        graph ?objTarget
        {
            ###TARGET SLOT
        }

        BIND (IF(bound(?o_PredVal), ?o_PredVal , "none") AS ?o_PredV)
        BIND ("" AS ?operator)
    }
    group by ?subTarget ?objTarget  ?sub_uri ?obj_uri  ?s_datatype ?o_datatype ?operator
    LIMIT 10
    """

    source = ""
    target = ""
    prop_query = linkset_aligns_prop(linkset_uri)
    prop_matrix = sparql_matrix(prop_query)["result"]
    for i in range(1, len(prop_matrix)):
        # print matrix[i]
        src = "<{}>".format(prop_matrix[i][0]) if prop_matrix[i][0].__contains__(">/<") is False else prop_matrix[i][0]
        trg = "<{}>".format(prop_matrix[i][1]) if prop_matrix[i][1].__contains__(">/<") is False else prop_matrix[i][1]
        if i == 1:
            source = "{{ ?sub_uri  {}  ?s_PredV . }}".format(src)
            target = "{{ ?obj_uri  {}  ?o_PredVal . }}".format(trg)
        else:
            source += "\n\t\t\t UNION \n\t\t\t{{ ?sub_uri  {}  ?s_PredV . }}".format(src)
            target += "\n\t\t\t UNION \n\t\t\t{{ ?obj_uri  {}  ?o_PredVal . }}".format(trg)

        query = str(query).replace("###SOURCE SLOT", source).replace("###TARGET SLOT", target)

        return query

# test = linkset_detail_query(
    # "http://risis.eu/linkset/refined_en_nl_exactStrSim_label_P916744941_intermediate_author_name")

# matrix = sparql_matrix(test)["result"]
# print test
# display(query=test, limit=10, is_activated=True, spacing=80)


drop_linkset("http://risis.eu/linkset/orgref_20170703_grid_20171712_approxStrSim_Org_Name_N440779016", activated=True)