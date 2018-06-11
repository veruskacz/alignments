from os import path
import subprocess
import Alignments.Query as Qry
import Alignments.Utility as Ut
import Alignments.Settings as St
import Alignments.NameSpace as Ns
import Alignments.Server_Settings as Svr


stardog_cmds = {

    "server_status": "\"{}stardog-admin\" server status",

    # 0. STARDOG BIN
    "query_list": "\"{}stardog-admin\" query list",

    # 0. STARDOG BIN    1. QUERY ID
    "query_kill": "\"{}stardog-admin\" query kill {}",

    # 0. STARDOG BIN    1. QUERY ID
    "query_status": "\"{}stardog-admin\" query status {}",

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

stardog_bin = Svr.settings[St.stardog_path]
stardog_db = Svr.settings[St.database]



# ********************************************************************************
""" STARDOG FROM COMMAND LINE """
# ********************************************************************************


def main_alignment(alignment):

    # LOCAL NAME OF THE GRAPH
    name = Ut.get_uri_local_name_plus(alignment)
    print "{:12} : {}".format("LOCAL NAME", name)
    query = std_queries["graphs_search"].format(name)
    response = Qry.sparql_xml_to_matrix(query)
    results = response["result"]
    if results is not None:
        for i in range(1, len(results)):
            if results[i][0].__contains__("singletons") is False:
                return results[i][0]

    if str(alignment).__contains__(Ns.singletons):
        return str(alignment).replace(Ns.singletons, Ns.linkset)

    else:
        return alignment


def stardog_query_list():

    """""""""""""""""""""""""""""""""""""""""""""""""""""""""
    #   QUERRYING STARDOG FOR THE CURRENT LIST OF QUERIES
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""

    try:
        cmd = stardog_cmds["query_list"].format(stardog_bin)
        remove = "{}".format(stardog_bin)
        print "{:12} : {}".format("STARDOG COMMAND", cmd.replace("\"", "").replace(remove, ""))
        return subprocess.check_output(cmd, shell=True)
    except Exception as err:
        return err


def stardog_status():

    """""""""""""""""""""""""""""""""""""""""""""""""""""""""
    #   QUERRYING STARDOG FOR THE CURRENT LIST OF QUERIES
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""

    try:
        cmd = stardog_cmds["server_status"].format(stardog_bin)
        remove = "{}".format(stardog_bin)
        print "{:12} : {}".format("STARDOG COMMAND", cmd.replace("\"", "").replace(remove, ""))
        return subprocess.check_output(cmd, shell=True)
    except Exception as err:
        return err


def stardog_query_kill(query_id):

    """""""""""""""""""""""""""""""""""""""""""""""""""""""""
    #       TERMINATING A SPECIFIC QUERY BASED ON ID
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""

    try:
        cmd = stardog_cmds["query_kill"].format(stardog_bin, query_id)
        remove = "{}".format(stardog_bin)
        print "{:12} : {}".format("STARDOG COMMAND", cmd.replace("\"", "").replace(remove, ""))
        return subprocess.check_output(cmd, shell=True)
    except Exception as err:
        return err


def stardog_query_status(query_id):

    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    #   ASSESSING THE STATUS OF A SPECIFIC CURRENTLY RUNNING QUERIES
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

    try:
        cmd = stardog_cmds["query_status"].format(stardog_bin, query_id)
        remove = "{}".format(stardog_bin)
        print "{:12} : {}".format("STARDOG COMMAND", cmd.replace("\"", "").replace(remove, ""))
        return subprocess.check_output(cmd, shell=True)
    except Exception as err:
        return err


def stardog_export_db(file_path, database=None):

    """""""""""""""""""""""""""""""""""""""""""""
    #   EXPORTING AN ENTIRE STARDOG DATABASE
    """""""""""""""""""""""""""""""""""""""""""""

    if database is None:
        database = stardog_db

    try:
        cmd = stardog_cmds["export_db"].format(stardog_bin, database, file_path)
        remove = "{}".format(stardog_bin)
        print "{:12} : {}".format("STARDOG COMMAND", cmd.replace("\"", "").replace(remove, ""))
        return subprocess.check_output(cmd, shell=True)
    except Exception as err:
        return err


def stardog_export_graph(file_path, graph, database=None):

    """""""""""""""""""""""""""""""""""""""""""""
    #   EXPORTING AN ENTIRE STARDOG DATABASE
    """""""""""""""""""""""""""""""""""""""""""""

    if database is None:
        database = stardog_db

    try:
        cmd = stardog_cmds["export_graph"].format(stardog_bin, graph, database, file_path)
        remove = "{}".format(stardog_bin)
        print "{:12} : {}".format("STARDOG COMMAND", cmd.replace("\"", "").replace(remove, ""))
        return subprocess.check_output(cmd, shell=True)
    except Exception as err:
        return err


def stardog_data_add_folder(folder_path, named_graph=None, database=None, add=True, fies_format="trig", activated=False):


    if activated is False:
        message = "THE FUNCTION [stardog_data_add_folder] IS NOT ACTIVATED"
        print message
        return message

    if fies_format.strip() == "ttl" and named_graph is None:
        return "The named graph is required for loading your data."

    """""""""""""""""""""""""""""""""""""""""""""
    #   EXPORTING AN ENTIRE STARDOG DATABASE
    """""""""""""""""""""""""""""""""""""""""""""

    if database is None:
        database = stardog_db

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
        return err


def stardog_data_add_file(file_path, graph=None, database=None, add=True, activated=False):

    if activated is False:
        message = "THE FUNCTION [stardog_data_add_folder] IS NOT ACTIVATED"
        print message
        return message

    """""""""""""""""""""""""""""""""""""""""""""
    #   EXPORTING AN ENTIRE STARDOG DATABASE
    """""""""""""""""""""""""""""""""""""""""""""

    if database is None:
        database = stardog_db

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
        return err


# ##############################################################################
""" STARDOG QUERIES """
# ##############################################################################


def query(query):

    """""""""""""""""""""""""""""
    #   QUERYING STARDOG
    """""""""""""""""""""""""""""

    try:
        cmd = std_queries["query"].format(stardog_bin, stardog_db, query)
        remove = "\"{}stardog\" query {} \"".format(stardog_bin, stardog_db)
        print "{:12} : {}".format("QUERY", cmd[0:-1].replace(remove, ""))
        cmd = cmd.replace("\n", "")
        return subprocess.check_output(cmd, shell=True)
    except Exception as err:
        return err


def query_generic(graph, limit=100):

    """""""""""""""""""""""""""""
    #   QUERRYING STARDOG
    """""""""""""""""""""""""""""

    try:
        cmd = std_queries["query_generic"].format(stardog_bin, stardog_db, graph, limit)
        remove = "\"{}stardog\" query {} \"".format(stardog_bin, stardog_db)
        print "{:12} : {}".format("QUERY", cmd[0:-1].replace(remove, ""))
        return subprocess.check_output(cmd, shell=True)
    except Exception as err:
        return err


def query_graphs():
    qry = std_queries["graph_all"]
    return query(qry)


def query_graph_properties(graph):
    qry = std_queries["graph_properties"].format(graph)
    return query(qry)


def query_graph_search(search_exp):
    qry = std_queries["graphs_search"].format(search_exp)
    return query(qry)


def query_graph_metadata(graph):

    print "{:12} : {}".format("INPUT GRAPH ", graph)
    graph = main_alignment(graph)
    print "{:12} : {}".format("MAIN GRAPH", graph)
    qry = std_queries["metadata"].format(graph)
    result = query(qry)
    print result
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
#     folder_path="D:\Linking2GRID\Data\Leiden Ranking 2015 extended\converted\leidenRanking_2015.2017-08-03\University",
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