import Alignments.Query as Qry
import Alignments.Settings as St
import Alignments.NameSpace as Ns
import Alignments.Utility as Ut
from Alignments.Utility import get_uri_local_name, write_to_file, update_specification

PREFIX = """
    PREFIX bdb:         <http://vocabularies.bridgedb.org/ops#>
    PREFIX rdf:         <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX linkset:     <http://risis.eu/linkset/>
    PREFIX void:        <http://rdfs.org/ns/void#>
    PREFIX alivocab:    <http://risis.eu/alignment/predicate/>
    PREFIX tmpgraph:    <http://risis.eu/alignment/temp-match/>
    PREFIX prov:        <http://www.w3.org/ns/prov#>
"""

def diff_lens_name(specs):
    specs[St.lens_operation] = Ns.lensOpd
    src_name = get_uri_local_name(specs[St.subjectsTarget])
    trg_name = get_uri_local_name(specs[St.objectsTarget])
    specs[St.lens] = "{}diff_{}_{}".format(Ns.lens, src_name, trg_name)
    update_specification(specs)


def lens_targets_unique(unique_list, graph):

    def get_targets(graph_uri):
        target_query = PREFIX + """
        ### GET LINKSET METADATA
        SELECT DISTINCT ?g
        WHERE
        {
                { <""" + graph_uri + """> <http://rdfs.org/ns/void#subjectsTarget>                ?g }
                UNION
                { <""" + graph_uri + """> <http://rdfs.org/ns/void#objectsTarget>                 ?g }
                UNION
                { <""" + graph_uri + """> void:target                                             ?g }
        }
        """

        return target_query

    def get_lens_union_targets(lens):
        u_query = PREFIX + """
        select *
        {{
            <{}> void:target ?target .
        }}
        """.format(lens)

        return u_query

    # THIS FUNCTION TAKES AS INPUT A LENS AND FILS IN THE  THE DICTIONARY
    # ARGUMENT WITH UNIQUE DATASETS INVOLVED IN THE LENS

    # GET THE TYPE OF THE GRAPH: e.g.: http://rdfs.org/ns/void#Linkset
    type_matrix = Qry.get_graph_type(graph)
    # print type_matrix

    if type_matrix[St.message] != "NO RESPONSE":

        if type_matrix[St.result]:

            # THIS IS THE BASE OF THE RECURSION
            if type_matrix[St.result][1][0] == "http://rdfs.org/ns/void#Linkset":

                # QUERY FOR THE GRAPHS/DATASETS
                query = get_targets(graph)
                result = Qry.sparql_xml_to_matrix(query)
                # print query
                # print "\n\nRESULT:", result

                # SAVE THE GRAPH AND MAKE SURE THEY ARE UNIQUE
                for i in range(1, len(result[St.result])):
                    if result[St.result][i][0] not in unique_list:
                        unique_list.append(result[St.result][i][0])
                        # print result[i]
                return

            if type_matrix[St.result][1][0] == "http://vocabularies.bridgedb.org/ops#Lens":
                # print "I am Keanu Reeves"
                # GET THE OPERATOR
                # alivocab:operator	 http://risis.eu/lens/operator/union
                operator = Qry.get_lens_operator(graph)
                print "\nOPERATOR:", operator

                if operator == "http://risis.eu/lens/operator/union":
                    # GET THE LIST OF TARGETS
                    target_matrix = Qry.sparql_xml_to_matrix(get_lens_union_targets(graph))
                    if target_matrix[St.result]:
                        for i in range(1, len(target_matrix[St.result])):
                            lens_targets_unique(unique_list, target_matrix[St.result][i][0])


def ask_union(datasets):
    # USING THE GRAPHS COMPOSING THIS LINKSET, CHECK WHETHER THERE EXISTS A GRAPH
    # THAT WAS ALREADY GENERATED USING THE SAME COMPOSITION OF  GRAPHS.
    # THE SELECTED PROPERTY IS USED AS THE RETURNED EXISTING LENS
    triples = ""
    for i in range(0, len(datasets)):
        connect = "\t\t" if i == 0 else ";\n\t\t\t"
        triples += "{}void:target\t\t<{}> ".format(connect, datasets[i])
    return """
    PREFIX void:<{}>
    SELECT *
    {{
        ?subject
    {}.
    }}
    """.format(Ns.void, triples)


def unique_targets(datasets):

    # RETURN A LIST OF UNIQUE DATASETS FROM THE DATASET LIST
    unique_list = list()
    for dataset in datasets:
        lens_targets_unique(unique_list, dataset)

    return unique_list


def generate_lens_name(datasets):

    datasets.sort()
    ds_concat = ""
    for dataset in datasets:
        ds_concat += dataset

    # RETURN THE LIST OF DATASET UNIQUE NAMES
    unique_list = list()

    # THE QUERY FOR CHECKING WHETHER THE LENS EXIST
    query = ask_union(datasets)

    for dataset in datasets:
        lens_targets_unique(unique_list, dataset)

    # print unique_list
    name = ""
    for i in range(0, len(unique_list)):
        local_name = Ut.get_uri_local_name(unique_list[i])
        link = "" if i == 0 else "_"
        # print (local_name[0]).upper()
        name += link + (local_name[0]).upper() + local_name[1:]

    hash_value = hash(name + ds_concat)

    hash_value = str(hash_value).replace("-", "N") if str(hash_value).__contains__("-") else "P{}".format(hash_value)

    name = "union_{}_{}".format(name, hash_value)

    # print name
    # print query
    # print hash(name)
    return {"name": name, "query": query}

