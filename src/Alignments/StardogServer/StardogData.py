from os import path
import traceback
import subprocess
import Alignments.Query as Qry
import Alignments.Utility as Ut
import Alignments.Settings as St
import Alignments.NameSpace as Ns
import Alignments.Server_Settings as Svr
from Alignments.Utility import headings
import os

# database = Svr.settings[St.database]
stardog_bin = Svr.settings[St.stardog_path]
stardog_db = Svr.settings[St.database]
stardog_uri = Svr.settings[St.stardog_uri]
stardog_address = Svr.settings[St.stardog_uri].replace("/{}".format(stardog_db), "")


namespaces = """
    {0}stardog namespace add {1} --prefix owl --uri http://www.w3.org/2002/07/owl#
    {0}stardog namespace add {1} --prefix void --uri http://rdfs.org/ns/void#
    {0}stardog namespace add {1} --prefix bdb --uri http://vocabularies.bridgedb.org/ops#
    {0}stardog namespace add {1} --prefix prov --uri http://www.w3.org/ns/prov#
    {0}stardog namespace add {1} --prefix skos --uri http://www.w3.org/2004/02/skos/core#
    {0}stardog namespace add {1} --prefix lens --uri http://risis.eu/lens/
    {0}stardog namespace add {1} --prefix risis --uri http://risis.eu/
    {0}stardog namespace add {1} --prefix riclass --uri http://risis.eu/class/
    {0}stardog namespace add {1} --prefix schema --uri http://risis.eu/ontology/
    {0}stardog namespace add {1} --prefix dataset --uri http://risis.eu/dataset/
    {0}stardog namespace add {1} --prefix idea --uri http://risis.eu/activity/
    {0}stardog namespace add {1} --prefix linkset --uri http://risis.eu/linkset/
    {0}stardog namespace add {1} --prefix method --uri http://risis.eu/method/
    {0}stardog namespace add {1} --prefix ll --uri http://risis.eu/alignment/predicate/
    {0}stardog namespace add {1} --prefix tmpgraph --uri http://risis.eu/alignment/temp-match/
    {0}stardog namespace add {1} --prefix tempG --uri http://risis.eu/alignment/temp-match/
    {0}stardog namespace add {1} --prefix tmpvocab --uri http://risis.eu//temp-match/temp-match/predicate/
    {0}stardog namespace add {1} --prefix mechanism --uri http://risis.eu/mechanism/
    {0}stardog namespace add {1} --prefix singletons --uri http://risis.eu/singletons/
    {0}stardog namespace add {1} --prefix justification --uri http://risis.eu/justification/
    {0}stardog namespace add {1} --prefix lensOp --uri http://risis.eu/lens/operator/
    {0}stardog namespace add {1} --prefix lensOpu --uri http://risis.eu/lens/operator/union
    {0}stardog namespace add {1} --prefix lensOpi --uri http://risis.eu/lens/operator/intersection
    {0}stardog namespace add {1} --prefix lensOpt --uri http://risis.eu/lens/operator/transitive
    {0}stardog namespace add {1} --prefix lensOpd --uri http://risis.eu/lens/operator/difference
    {0}stardog namespace add {1} --prefix singletons --uri http://risis.eu/singletons/
    {0}stardog namespace add {1} --prefix dataset --uri http://risis.eu/dataset/
    {0}stardog namespace add {1} --prefix gadm --uri http://geo.risis.eu/vocabulary/gadm/
"""


stardog_cmds = {

    "server_status": "\"{}stardog-admin\" --server {} server status",

    # 0. STARDOG BIN
    "query_list": "\"{}stardog-admin\" --server {} query list",

    # 0. STARDOG BIN    1. QUERY ID
    "query_kill": "\"{}stardog-admin\" --server {} query kill {}",

    # 0. STARDOG BIN    1. QUERY ID
    "query_status": "\"{}stardog-admin\" --server {} query status {}",

    # 0. STARDOG BIN    1.DATASET     2.OURPUT FILE PATH
    "export_db": "\"{}stardog\" data export --named-graph ALL --format TRIG {} {}",

    # 0. STARDOG BIN    1.GRAPH       2.DATASET     3.OUTPUT FILE PATH
    "export_graph": "\"{}stardog\" data export --named-graph {} --format TRIG {} {}",

    # 0. STARDOG BIN    1. ADD/REMOVE   2.DATABASE       3.named graph  4.FOLDER PATH      5.FILE FORMAT(ttl or trig)
    "data_add_folder": "\"{}stardog\" data {} {} {} \"{}\"*.{}",

    # 0. STARDOG BIN    1. ADD/REMOVE   2.DATABASE       3.GRAPH     4.FILE PATH
    "data_add_file": "\"{}stardog\" data {} {} {} {}",

    # 0. STARDOG BIN    1. PREFIX       2.URI       3.DATABASE
    "data_add_prefix": "\"{}stardog\" namespace add --prefix {} --uri {}  {}"
}

std_queries = {

    # 0. STARDOG BIN    1. DATABASE     2. QUERY
    "query": "\"{}stardog\" query {} \"{}\"",

    # 0. STARDOG BIN    1. DATABASE     2. QUERY
    "query_generic": "\"{}stardog\" query {} \"SELECT * {{ GRAPH <{}> {{ ?sub ?pred ?obj }} }} LIMIT {}\"",

    # 0. SEARCH EXPRESSION
    "graphs_search": "SELECT DISTINCT ?g where {{ graph ?g {{ ?s ?p ?o }} filter regex(str(?g), '{}', 'i') }}",

    # 0. GRAPH
    "graph_properties": "SELECT DISTINCT ?p where {{  graph <{}> {{  ?s ?p ?o  }} }}",

    # NO PARAMETER
    "graph_all": "SELECT DISTINCT ?g where {  graph ?g {  ?s ?p ?o  } }",

    # NO PARAMETER
    "default": "SELECT * {?sub ?pred ?obj} LIMIT 10",

    # GRAPH/ALIGNMENT/LINKSET/LENS/SINGLETONS
    "metadata": "SELECT * {{ <{}> ?predicate ?object .}} "}


def reset_ll_port(port):
    env = os.environ

    if "LL_PORT" in os.environ:
        os.environ["LL_PORT"] = str(port)
        return "DONE!"

    for (key, val) in env.items():
        if str(key).__contains__('PORT'):
            os.environ[key] = "5077"
            print "\t", key, os.environ[key]


# ********************************************************************************
""" STARDOG FROM COMMAND LINE """
# ********************************************************************************


def add_namespace(namespace, uri):

    print headings("ADDING A NAMESPACE")
    print "NAMESPACE LABEL:".format(namespace)
    print "NAMESPACE URIS :".format(uri)
    # PLATFORM DEPENDENT CMD
    try:
        cmd = "stardog namespace add {} --prefix {} --uri {}".format(Svr.settings[St.stardog_uri], namespace, uri)
        return subprocess.check_output(cmd, shell=True)
    except ValueError:
        traceback.print_exc()


def load_default_namespaces(directory):

    print headings("LOADING DEFAULT NAMESPACES TO STARDOG [{}]".format(stardog_db))

    if path.isdir(directory) is False:
        return "\n>>> [{}] IS NOT A DIRECTORY ".format(directory)

    f_path = path.join(directory, "namespace.bat" if Ut.is_windows() else "namespace.sh")

    # PLATFORM DEPENDENT CMD
    if Ut.is_windows():
        cmd = namespaces.format("call ", Svr.settings[St.stardog_uri])
    else:
        cmd = namespaces.format(stardog_bin, Svr.settings[St.stardog_uri],)

    # EXECUTE THE CMD
    result = Ut.run_cdm(cmd, f_path, delete_after=True, output=False)

    # DISPLAY THE FINAL RETURN
    print "Finished with: {}".format(result)


def main_alignment(alignment):

    # ****************************************************************************
    # GIVEN AN ALIGNMENT, RETURN THE MAIN ONE
    # ****************************************************************************

    try:
        # LOCAL NAME OF THE GRAPH
        name = Ut.get_uri_local_name_plus(alignment)
        print "{:12} : {}".format("LOCAL NAME", name)
        query_search = std_queries["graphs_search"].format(name)
        response = Qry.sparql_xml_to_matrix(query_search)
        results = response["result"]
        if results is not None:
            for i in range(1, len(results)):
                if results[i][0].__contains__("singletons") is False:
                    return results[i][0]

        if str(alignment).__contains__(Ns.singletons):
            return str(alignment).replace(Ns.singletons, Ns.linkset)

        else:
            return alignment

    except ValueError:
        traceback.print_exc()
        return alignment


def stardog_query_list():

    """""""""""""""""""""""""""""""""""""""""""""""""""""""""
    #   QUERYING STARDOG FOR THE CURRENT LIST OF QUERIES
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""
    print headings("QUERYING STARDOG FOR THE CURRENT LIST OF QUERIES")

    try:
        cmd = stardog_cmds["query_list"].format(stardog_bin, stardog_address)
        remove = "{}".format(stardog_bin)
        print "{:12} : {}".format("STARDOG COMMAND", cmd.replace("\"", "").replace(remove, ""))
        return subprocess.check_output(cmd, shell=True)
    except Exception as err:
        return err


def stardog_status():

    """""""""""""""""""""""""""""""""""""""""""""""""""""""""
    #   QUERRYING STARDOG FOR THE CURRENT LIST OF QUERIES
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""
    print headings("QUERYING STARDOG FOR THE CURRENT LIST OF QUERIES")

    try:
        cmd = stardog_cmds["server_status"].format(stardog_bin, stardog_address)
        remove = "{}".format(stardog_bin)
        print "{:12} : {}".format("STARDOG COMMAND", cmd.replace("\"", "").replace(remove, ""))
        return subprocess.check_output(cmd, shell=True)
    except Exception as err:
        return err


def stardog_query_kill(query_id):

    """""""""""""""""""""""""""""""""""""""""""""""""""""""""
    #       TERMINATING A SPECIFIC QUERY BASED ON ID
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""
    print headings("TERMINATING A SPECIFIC QUERY BASED ON ID")

    try:
        cmd = stardog_cmds["query_kill"].format(stardog_bin, stardog_address, query_id)
        remove = "{}".format(stardog_bin)
        print "{:12} : {}".format("STARDOG COMMAND", cmd.replace("\"", "").replace(remove, ""))
        return subprocess.check_output(cmd, shell=True)
    except Exception as err:
        return err


def stardog_query_status(query_id):

    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    #   ASSESSING THE STATUS OF A SPECIFIC CURRENTLY RUNNING QUERY
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    print headings("ASSESSING THE STATUS OF A SPECIFIC CURRENTLY RUNNING QUERY")

    try:
        cmd = stardog_cmds["query_status"].format(stardog_bin, stardog_address, query_id)
        remove = "{}".format(stardog_bin)
        print "{:12} : {}".format("STARDOG COMMAND", cmd.replace("\"", "").replace(remove, ""))
        return subprocess.check_output(cmd, shell=True)

    except Exception as err:
        return err


def stardog_export_db(file_path, database=None):

    """""""""""""""""""""""""""""""""""""""""""""
    #   EXPORTING AN ENTIRE STARDOG DATABASE
    """""""""""""""""""""""""""""""""""""""""""""
    print headings("EXPORTING AN ENTIRE STARDOG DATABASE")

    if database is None:
        database = stardog_uri

    try:
        cmd = stardog_cmds["export_db"].format(stardog_bin, database, file_path)
        remove = "{}".format(stardog_bin)
        print "{:12} : {}".format("STARDOG COMMAND", cmd.replace("\"", "").replace(remove, ""))
        return subprocess.check_output(cmd, shell=True)
    except Exception as err:
        return err


def stardog_export_graph(file_path, graph, database=None):

    """""""""""""""""""""""""""""""""""""""""""""
    #   EXPORTING AN ENTIRE STARDOG GRAPH
    """""""""""""""""""""""""""""""""""""""""""""
    print headings("EXPORTING AN ENTIRE STARDOG GRAPH")

    if database is None:
        database = stardog_uri

    try:
        cmd = stardog_cmds["export_graph"].format(stardog_bin, graph, database, file_path)
        remove = "{}".format(stardog_bin)
        print "{:12} : {}".format("STARDOG COMMAND", cmd.replace("\"", "").replace(remove, ""))
        return subprocess.check_output(cmd, shell=True)
    except Exception as err:
        return err


def stardog_data_add_folder(
        folder_path, named_graph=None, database=None, add=True, fies_format="trig", activated=False):

    if activated is False:
        message = "THE FUNCTION [stardog_data_add_folder] IS NOT ACTIVATED"
        print message
        return message

    if fies_format.strip() == "ttl" and named_graph is None:
        return "The named graph is required for loading your data."

    """""""""""""""""""""""""""""""""""""""""""""
    #   ADDING DATA TO STARDOG
    """""""""""""""""""""""""""""""""""""""""""""
    print headings("ADDING DATA TO STARDOG FROM A FOLDER")

    if database is None:
        database = stardog_uri

    if named_graph is not None:
        graph = "-g {}".format(named_graph.strip())
    else:
        graph = ""

    if folder_path.strip().endswith(path.sep) is False:
        folder_path = "{}{}".format(folder_path, path.sep)

    add_remove = "add" if add is True else "remove"

    try:
        cmd = stardog_cmds["data_add_folder"].format(stardog_bin, add_remove, database, graph, folder_path, fies_format)
        cmd = cmd.replace("\\", "/")
        remove = "{}".format(stardog_bin)
        print "{:12} : {}".format("STARDOG COMMAND", cmd.replace("\"", "").replace(remove, ""))
        result = subprocess.check_output(cmd, shell=True)
        print result
        return result

    except Exception as err:
        traceback.print_exc()
        return err


def stardog_data_add_file(file_path, graph=None, database=None, add=True, activated=False):

    if activated is False:
        message = "THE FUNCTION [stardog_data_add_folder] IS NOT ACTIVATED"
        print message
        return message

    """""""""""""""""""""""""""""""""""""""""""""
    #   EXPORTING AN ENTIRE STARDOG DATABASE
    """""""""""""""""""""""""""""""""""""""""""""
    print headings("ADDING DATA TO STARDOG FROM A FILE")

    if database is None:
        database = stardog_uri

    if graph is not None:
        graph = "-g {}".format(graph.strip())

    add_remove = "add" if add is True else "remove"

    try:
        cmd = stardog_cmds["data_add_file"].format(stardog_bin, add_remove, database, graph, file_path)
        cmd = cmd.replace("\\", "/")
        remove = "{}".format(stardog_bin)
        print "{:12} : {}".format("STARDOG COMMAND", cmd.replace("\"", "").replace(remove, ""))
        result = subprocess.check_output(cmd, shell=True)
        print result
        return result

    except Exception as err:
        traceback.print_exc()
        return err


# ##############################################################################
""" STARDOG QUERIES """
# ##############################################################################


def query(query_search):

    """""""""""""""""""""""""""""
    #   QUERYING STARDOG
    """""""""""""""""""""""""""""
    print headings("QUERYING STARDOG")

    try:
        cmd = std_queries["query"].format(stardog_bin, stardog_uri, query_search)
        remove = "\"{}stardog\" query {} \"".format(stardog_bin, stardog_uri)
        print "{:12} : {}".format("QUERY", cmd[0:-1].replace(remove, ""))
        cmd = cmd.replace("\n", "")
        return subprocess.check_output(cmd, shell=True)

    except Exception as err:
        traceback.print_exc()
        return err


def query_generic(graph, limit=100):

    """""""""""""""""""""""""""""
    #   QUERRYING STARDOG
    """""""""""""""""""""""""""""
    print headings("GENERIC QUERY FOR STARDOG")

    try:
        cmd = std_queries["query_generic"].format(stardog_bin, stardog_uri, graph, limit)
        remove = "\"{}stardog\" query {} \"".format(stardog_bin, stardog_uri)
        print "{:12} : {}".format("QUERY", cmd[0:-1].replace(remove, ""))
        return subprocess.check_output(cmd, shell=True)

    except Exception as err:
        traceback.print_exc()
        return err


def query_graphs():

    print headings("QUERYING STARDOG'S NAMED GRAPHS")
    qry = std_queries["graph_all"]
    return query(qry)


def query_graph_properties(graph):

    print headings("QUERYING STARDOG'S GRAPH PROPERTIES")
    qry = std_queries["graph_properties"].format(graph)
    return query(qry)


def query_graph_search(search_exp):

    print headings("QUERYING STARDOG FOR A SPECIFIC GRAPH")
    qry = std_queries["graphs_search"].format(search_exp)
    return query(qry)


def query_graph_metadata(graph):

    print headings("QUERYING STARDOG FOR THE GENERIC METADATA OF A GRAPH")
    print "{:12} : {}".format("INPUT GRAPH ", graph)
    graph = main_alignment(graph)
    print "{:12} : {}".format("MAIN GRAPH", graph)
    qry = std_queries["metadata"].format(graph)
    result = query(qry)
    # print result
    return result


# INSERT STARDOG DATA FROM A FOLDER
eter = "D:\Linking2GRID\Data\ETER 2017\converted\eter_2014.2017-08-03\University\\"
leiden = "D:\Linking2GRID\Data\Leiden Ranking 2015 extended\converted\leidenRanking_2015.2017-08-03\University"
# print stardog_data_folder(leiden)

# print query_graphs()
#
# print query_generic("http://risis.eu/dataset/grid_20170712_enriched")

# print stardog_data_file(graph="http://risis.eu/dataset/grid_20180501", database=None, add=True,
#                         file_path="D:\Linking2GRID\Grid\grid20180501\grid.ttl")

# print stardog_query_list()
# print stardog_query_status(94)
# print stardog_status()
# print query_graph_search("dataset")

# # GRID
# stardog_data_add_file(
#     file_path="D:\Linking2GRID\Grid\grid20180501\grid.ttl",
#     graph="http://risis.eu/dataset/grid_20180501", database="risis", add=True, activated=False)
#
# # ETER
# stardog_data_add_folder(
#     folder_path="D:\Linking2GRID\Data\ETER 2017\converted\eter_2014.2017-08-03\University",
#     database="risis", fies_format="trig", add=True, activated=False)
#
# # LEIDEN
# stardog_data_add_folder(
#     folder_path=
# "D:\Linking2GRID\Data\Leiden Ranking 2015 extended\converted\leidenRanking_2015.2017-08-03\University",
#     database="risis", fies_format="trig", add=True, activated=False)

query_str = """
#### Query for enriching GRID with organisation counts at GADM level-2
PREFIX dataset:		<http://risis.eu/dataset/>
prefix foaf: 		<http://xmlns.com/foaf/0.1/>
prefix grivocab: 	<http://www.grid.ac/ontology/>
prefix ll: 			<http://risis.eu/alignment/predicate/>
PREFIX gadm: 		<http://geo.risis.eu/vocabulary/gadm/>
PREFIX coord:		<http://www.w3.org/2003/01/geo/wgs84_pos#>

select (count(distinct ?grid) as ?total)
{
    GRAPH dataset:grid_20180501_enriched
    {
        ?grid ll:intersects ?gadm .
    }

    service <http://sparql.sms.risis.eu/>
    {
        GRAPH <http://geo.risis.eu/gadm>
        {
            ?gadm gadm:level ?level .
        }
    }
}
"""

# print query(query_str)
# stardog_export_graph("C:\Git\RISIS-2018-course\datasets\grid_20180501_NL.trig",
# "http://risis.eu/dataset/grid_20180501_NL", database=None)
# stardog_export_graph("C:\Git\RISIS-2018-course\datasets\eter_2014_enriched.trig",
# "http://risis.eu/dataset/eter_2014_enriched", database=None)
# stardog_export_graph("C:\Git\RISIS-2018-course\datasets\grid_20180501_enriched.trig",
# "http://risis.eu/dataset/grid_20180501_enriched", database=None)
