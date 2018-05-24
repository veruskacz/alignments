import subprocess
import Alignments.Query as Qry
import Alignments.Utility as Ut
import Alignments.Settings as St
import Alignments.NameSpace as Ns
import Alignments.Server_Settings as Svr


stardog_cmds = {

    # 0. STARDOG BIN    1. DATABASE     2. QUERY
    "query": "\"{}stardog\" query {} \"{}\"",

    # 0. STARDOG BIN
    "query_list": "\"{}stardog-admin\" query list",

    # 0. STARDOG BIN    1. QUERY ID
    "query_kill": "\"{}stardog-admin\" query kill {}",

    # 0. STARDOG BIN    1. QUERY ID
    "query_status": "\"{}stardog-admin\" query status {}",

    # 0. STARDOG BIN    1.DATASET     2.OURPUT FILE PATH
    "query_export_db": "\"{}stardog\" data export --named-graph ALL --format TRIG {} {}",

    # 0. STARDOG BIN    1.GRAPH       2.DATASET     3.OURPUT FILE PATH
    "query_export_graph": "\"{}stardog\" data export --named-graph {} --format TRIG {} {}"
}

std_queries = {

    # 0. SEARCH EXPRESSION
    "graphs_search": "SELECT DISTINCT ?g where {{ graph ?g {{ ?s ?p ?o }} filter regex(str(?g), '{}', 'i') }}",

    # 0. GRAPH
    "graph_properties": "SELECT DISTINCT ?p where {{  graph <{}> {{  ?s ?p ?o  }} }}",

    # NO PARAMETER
    "graph_all": "SELECT DISTINCT ?g where {  graph ?g {  ?s ?p ?o  } }",

    # NO PARAMETER
    "default": "SELECT * {?sub ?pred ?obj} LIMIT 10",

    # GRAPH/ALIGNMNET/LINKSET/LENS/SINGLETONS
    "metadata": "SELECT * {{ <{}> ?predicate ?object .}} "}

stardog_bin = Svr.settings[St.stardog_path]
stardog_db = Svr.settings[St.database]


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


def stardog_query(query):

    """""""""""""""""""""""""""""
    #   QUERRYING STARDOG
    """""""""""""""""""""""""""""

    try:
        cmd = stardog_cmds["query"].format(stardog_bin, stardog_db, query)
        remove = "\"{}stardog\" query {} \"".format(stardog_bin, stardog_db)
        print "{:12} : {}".format("QUERY", cmd[0:-1].replace(remove, ""))
        return subprocess.check_output(cmd, shell=True)
    except Exception as err:
        return err


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
        cmd = stardog_cmds["query_export_db"].format(stardog_bin, database, file_path)
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
        cmd = stardog_cmds["query_export_graph"].format(stardog_bin, graph, database, file_path)
        remove = "{}".format(stardog_bin)
        print "{:12} : {}".format("STARDOG COMMAND", cmd.replace("\"", "").replace(remove, ""))
        return subprocess.check_output(cmd, shell=True)
    except Exception as err:
        return err


def graphs():
    query = std_queries["graph_all"]
    return stardog_query(query)


def graph_properties(graph):
    query = std_queries["graph_properties"].format(graph)
    return stardog_query(query)


def graph_search(search_exp):
    query = std_queries["graphs_search"].format(search_exp)
    return stardog_query(query)


def graph_metadata(graph):

    print "{:12} : {}".format("INPUT GRAPH ", graph)
    graph = main_alignment(graph)
    print "{:12} : {}".format("MAIN GRAPH", graph)
    query = std_queries["metadata"].format(graph)
    print stardog_query(query)
