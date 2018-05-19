# encoding=utf-8

import re
import time
import urllib
import urllib2
import logging
# import requests
import xmltodict
import collections
import Alignments.Settings as St
import Alignments.NameSpace as Ns
import Alignments.ErrorCodes as Ec
import Alignments.Server_Settings as Svr
from cStringIO import StringIO
from kitchen.text.converters import to_bytes  # to_unicode
import cStringIO as Buffer

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)
handler = logging.StreamHandler()
logger.addHandler(handler)


DATABASE = Svr.settings[St.database]
HOST = Svr.settings[St.stardog_host_name]
ERROR = "No connection could be made because the target machine actively refused it"
ERROR_2 = 'The query was successfully executed but no feedback was returned'


def from_alignment2singleton(alignment):

    if str(alignment).__contains__(Ns.linkset):
        return str(alignment).replace(Ns.linkset, Ns.singletons)
    elif str(alignment).__contains__(Ns.lens):
        return str(alignment).replace(Ns.lens, Ns.singletons)
    else:
        return alignment


def linkset_evidence(linkset, display=False):

    query = """
    ### GETTING LINKSET EVIDENCES
    prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    prefix owl: <http://www.w3.org/2002/07/owl#>
    prefix xsd: <http://www.w3.org/2001/XMLSchema#>
    prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX void: <http://rdfs.org/ns/void#>

    SELECT DISTINCT ?sing_evidence ?src_evidence ?trg_evidence
    {{
      # LINKSET METADATA
      <{0}>
                alivocab:singletonGraph		?singletonGraph  ;
                alivocab:alignsSubjects		?alignsSubjects ;
                alivocab:alignsObjects     	?alignsObjects ;
                void:subjectsTarget			?subjectsTarget ;
                void:objectsTarget			?objectsTarget .

      # LINKSET CORRESPONDENCE
      GRAPH <{0}>
      {{
         ?cor_subject ?cor_predicate ?cor_object .
      }}

      # LINKSET SINGLETON METADATA (EVIDENCE)
      GRAPH ?singletonGraph
      {{
         ?cor_predicate alivocab:hasEvidence ?sing_evidence .
      }}

      # SOURCE DATASET
      GRAPH ?subjectsTarget
      {{
         ?cor_subject ?alignsSubjects ?src_evidence .
      }}

      # TARGET DATASET
      GRAPH ?objectsTarget
      {{
         ?cor_object ?alignsObjects ?trg_evidence .
      }}
    }}
    """.format(linkset)

    if display is True:
        print query

    return query


def transitive_evidence(graph, database_name, host, activated=False):

    if activated is False:
        return

    type_linkset = 'http://rdfs.org/ns/void#Linkset'
    type_lens = 'http://vocabularies.bridgedb.org/ops#Lens'
    operator_union = "http://risis.eu/lens/operator/union"
    query = q_lens_transitive_metadata(graph)
    # print query

    get_metadata = sparql_xml_to_matrix(query)

    if get_metadata is None:
        message = """
    WE COULD NOT EXTRACT THE METADATA OF THIS GRAPH:
    "{}".
    PLEASE CHECK AGAIN WHETHER THE GRAPH IS A LINKSET OR A LENS""".format(graph)
        logger.warning(message)
        return None
    # print get_metadata

    print "\nABOUT THE LENS"

    lens_source = get_metadata[1][1]
    print "\tLens source: {}".format(lens_source)

    lens_target = get_metadata[1][2]
    print "\tLens target: {}".format(lens_target)

    is_transitive_by = [get_metadata[1][3]]
    print "\tTransitive by: {}".format(is_transitive_by[0])

    lens_sing_graph = get_metadata[1][0]
    print "\tLens singleton graph: {}".format(lens_sing_graph)

    lens_source_type = sparql_xml_to_matrix(graph_type(lens_source))[1][0]
    print "\tLens source type: {}".format(lens_source_type)

    lens_target_type = sparql_xml_to_matrix(graph_type(lens_target))[1][0]
    print "\tLens target type: {}".format(lens_target_type)

    # #######################################################################
    """ HELPER FUNCTIONS                                                  """
    # #######################################################################

    def lens(graph_uri, graph_datatype):

        if str(graph_datatype) == type_linkset:

            dataset_aligns = []
            # #######################################################################
            """ SOURCE                                                            """
            # #######################################################################
            print "\nABOUT THE Lens' COMPONENT 1"

            src_linkset_meta = sparql_xml_to_matrix(q_linkset_metadata(graph_uri))
            # print "\tSource linkset metadata:", src_ls_meta

            datasets = [src_linkset_meta[1][3], src_linkset_meta[1][4]]
            aligns = src_linkset_meta[1][1]
            intersection = list(set(datasets).difference(unicode(is_transitive_by)))

            graph_uri = get_metadata[1][1]
            print "\tOrigin: {}".format(graph_uri)
            # print '\tDatasets: ', datasets
            # print "\tAligns: {}".format(aligns)
            print "\tintersect:", intersection
            if len(intersection) == 1:
                dataset_aligns = intersection[0], aligns

            print "\tSource dataset: {}".format(dataset_aligns)
            return dataset_aligns

        elif str(graph_datatype) == type_lens:

            dataset_aligns = None
            # #######################################################################
            """ TARGET                                                            """
            # #######################################################################
            print "\nABOUT THE Lens' COMPONENT 2"
            print "\tOrigin: {}".format(graph_uri)
            operator = get_lens_operator(lens_target)
            print "\toperator: {}".format(operator)

            if operator == operator_union:
                datasets = get_lens_union_datasets(graph_uri)
                print "\tDatasets: {}".format(datasets)
                iterate = -1
                dataset_aligns = [None] * len(datasets)
                for dataset in list(datasets):
                    iterate += 1
                    meta = get_linkset_datatypes(dataset)
                    if meta is not None:
                        target_dataset = meta[1][4]
                        # print "\n\t\tDataset: {}".format(target_dataset)

                        aligns = meta[1][2]
                        # print "\t\t\tAligns: {}".format(aligns)

                        dataset_aligns[iterate] = target_dataset, aligns, operator
                        print "\t\t\tTarget dataset {}: {}".format(iterate + 1, dataset_aligns)

                return dataset_aligns

            return dataset_aligns

    def evidence_query(graph_uri, lens_singleton_graph, source_graph, target_graph):
        e_query = """
        SELECT DISTINCT ?cor_subject  ?cor_object ?src_evidence ?trg_evidence
        {{
          # LINKSET CORRESPONDENCE
          GRAPH <{}>
          {{
             ?cor_subject ?cor_predicate ?cor_object .
          }}

          # LINKSET SINGLETON METADATA (EVIDENCE)
          GRAPH <{}>
          {{
             ?cor_predicate alivocab:hasEvidence ?sing_evidence .
          }}

          # SOURCE DATASET
          GRAPH <{}>
          {{
             ?cor_subject <{}> ?src_evidence .
          }}

          # TARGET DATASET
          GRAPH <{}>
          {{
             ?cor_object <{}> ?trg_evidence .
          }}

        }}
        """.format(graph_uri, lens_singleton_graph, source_graph[0],
                   source_graph[1], target_graph[0], target_graph[1])

        return e_query

    # #######################################################################
    """ HELPER FUNCTIONS' RESULTS                                         """
    # #######################################################################
    sub_source = lens(lens_source, lens_source_type)
    sub_target = lens(lens_target, lens_target_type)
    print "\nWHAT TO USE?"
    print "\tSource: {}".format(sub_source)
    print "\tTarget: {}".format(sub_target)

    # #######################################################################
    """ QUERY RESULT                                         """
    # #######################################################################
    if (lens_source_type == type_linkset) and (lens_target_type == type_linkset):
        print "NOT YET DEVELOPED"

    if (lens_source_type == type_lens) and (lens_target_type == type_lens):
        print "NOT YET DEVELOPED"

    elif (lens_source_type == type_linkset) and (lens_target_type == type_lens):
        # print sub_target
        if sub_target[0][2] == operator_union:
            # print len(sub_target)
            for i in range(len(sub_target)):
                print "\nWAIT FOR THE QUERY RESULT"
                # print sub_target[i]
                query2 = evidence_query(graph, lens_sing_graph, sub_source, sub_target[i])
                print query2
                # display_result(query2, database_name, host, is_activated=True)

    elif(lens_source_type == type_lens) and (lens_target_type == type_linkset):

        if sub_source[0][2] == operator_union:
            # print len(sub_target)
            for i in range(len(sub_source)):
                print "\nWAIT FOR THE QUERY RESULT"
                # print sub_target[i]
                query2 = evidence_query(graph, lens_sing_graph, sub_target[i], sub_source)
                display_result(query2, database_name, host, is_activated=True)
                # print query2

    return graph_type(lens_source)


#################################################################
"""
    ABOUT QUERYING ENDPOINTS
"""
#################################################################


def endpoint(query):

    """
        param query         : The query that is to be run against the SPARQL endpoint
        param database_name : The name of the database () in with the named-graph resides
        param host          : the host (server) name
        return              : returns the result of the query in the default format of the endpoint.
                            In the case of STARDOG, the sever returns an XML result.
    """

    q = to_bytes(query)
    # print query
    # Content-Type: application/json
    # b"Accept": b"text/json"
    # 'output': 'application/sparql-results+json'
    # url = b"http://{}:{}/annex/{}/sparql/query?".format("localhost", "5820", "linkset")
    # headers = {b"Content-Type": b"application/x-www-form-urlencoded",
    #            b"Authorization": b"Basic YWRtaW46YWRtaW5UMzE0YQ=="}

    # THIS SHOULD WORK:
    # The Stardog SPARQL endpoint is http://<server>:<port>/{db}/query.
    # http://145.100.59.152:5820/risis_test#!/query/
    url = b"http://{}/annex/{}/sparql/query?".format(HOST, DATABASE)
    # url = b"http://{}/{}#!/query/".format(HOST, DATABASE)
    # print url
    params = urllib.urlencode(
        {b'query': q, b'format': b'application/sparql-results+json',
         b'timeout': b'0', b'debug': b'on', b'should-sponge': b''})
    headers = {b"Content-Type": b"application/x-www-form-urlencoded"}

    """
        Authentication
    """
    user = Svr.settings[St.stardog_user]
    password = Svr.settings[St.stardog_pass]
    passman = urllib2.HTTPPasswordMgrWithDefaultRealm()
    passman.add_password(None, url, user, password)
    urllib2.install_opener(urllib2.build_opener(urllib2.HTTPBasicAuthHandler(passman)))
    request = urllib2.Request(url, data=params, headers=headers)

    # print "THE REQUEST'S FULL URI: " + request.get_full_url()
    # print "THE REQUEST'S DATA: {}".format(request.data)

    request.get_method = lambda: "POST"
    try:
        response = urllib2.urlopen(request)
        result = response.read()
        # print result
        # print "NONE", result is None
        # print "EMPTY", len(result)
        return {St.message: "OK", St.result: result}

    except urllib2.HTTPError, err:
        message = err.read()
        if len(message) == 0:
            message = err

        if str(message).__contains__("Service Unavailable") or str(message).__contains__("Error 503"):
            print "THE SERVER IS NOT ON"
        else:
            print "USING THIS QUERY {}\nERROR CODE {}: {}".format(query, err.code, message)
        return {St.message: message, St.result: None}

    except Exception as err:

        if str(err).__contains__("No connection") is True:
            # logger.warning(err)
            # print ERROR
            return {St.message: ERROR, St.result: None}

        elif str(err.message).__contains__("timeout") is True:
            print "Query execution cancelled: Execution time exceeded query timeout"
            return {St.message: "Query execution cancelled: Execution time exceeded query timeout.",
                    St.result: None}

        logger.warning(err)
        message = "\nOR MAYBE THERE IS AN ERROR IN THIS QUERY"
        print message + "\n" + query
        return {St.message: err, St.result: None}


def boolean_endpoint_response(query, display=False):

    # if query.lower().__contains__('ask') is False:
    #     print "THE QUERY IS NOT OF TYPE [ASK]"
    #     return None

    # print query
    drop_start = time.time()
    response = endpoint(query)
    drop_end = time.time()
    result = None
    # print response
    if response[St.result] is not None:
        if len(response[St.result]) == 0:
            return ERROR_2
        drops_doc = xmltodict.parse(response[St.result])
        result = drops_doc['sparql']['boolean']
        # print "BOOLEAN QUERY RESULT: {}".format(result)
        if display is True:
            print ">>> Query executed : {:<14}".format(result)
            print ">>> Executed in    : {:<14} minute(s)".format(str((drop_end - drop_start) / 60))
            print ">>> Query details  : {}\n".format(query)
            print ""
    else:
        print query

    return result


def endpointconstruct(query, clean=True, insert=False):

    q = to_bytes(query)
    # print q
    # Content-Type: application/json
    # b"Accept": b"text/json"
    # 'output': 'application/sparql-results+json'
    # url = b"http://{}:{}/annex/{}/sparql/query?".format("localhost", "5820", "linkset")
    url = b"http://{}/annex/{}/sparql/query?".format(HOST, DATABASE)
    headers = {b"Content-Type": b"application/x-www-form-urlencoded", b'Accept': b'application/trig'}

    """
        Authentication
    """
    user = Svr.settings[St.stardog_user]
    password = Svr.settings[St.stardog_pass]
    passman = urllib2.HTTPPasswordMgrWithDefaultRealm()
    passman.add_password(None, url, user, password)
    urllib2.install_opener(urllib2.build_opener(urllib2.HTTPBasicAuthHandler(passman)))
    # print  query
    params = urllib.urlencode({b'query': q})
    request = urllib2.Request(url, data=params, headers=headers)
    request.get_method = lambda: "POST"

    try:
        response = urllib2.urlopen(request)
        # print "RESPONSE", response
        result = response.read()
        # print "RESPONSE RESULT:", result
        # result = str(result).replace("<<", "<").replace(">>", ">").replace("\

        if clean is True:

            pattern_1 = "<(<.*>\/<.*>)>"
            pattern_2 = "<(<[^<>]*\\\\*>)>"

            # REGULAR EXPRESSION FOR FIRST EXTRACTION OF STARDOG MESS
            # <<http://dbpedia.org/ontology/author\>/<http://dbpedia.org/property/name\>>
            regex_result = re.findall(pattern_1, result)
            regex_result += re.findall(pattern_2, result)

            # if len(regex_result) > 0:
            #
            #     # CLEANING UP THE  MESS
            #     bind = "\t### BINDING THIS BECAUSE STARDOG MESSES UP THE RESULT WHEN USING PROPERTY PATH\n"
            #     for i in range(len(regex_result)):
            #         # SOLVING THE PROBLEM BY INSERTING SOME VARIABLE BINDINGS
            #         result = result.replace("<{}>".format(regex_result[i]), "?LINK_{}".format(i))
            #         bind += "\tBIND( IRI(\"{}\") AS ?LINK_{} )\n".format(regex_result[i].replace("\>", ">"), i)
            #
            #     # FINAL CLEANING
            #     if insert is False:
            #         result = result.replace("{", "{{\n{}".format(bind))
            #         # print "RESPONSE RESULT ALTERED:", result
            #     else:
            #         inserting = Buffer.StringIO()
            #         inserting.write("INSERT\n")
            #         inserting.write(result)
            #         inserting.write("WHERE {{\n{}}}".format(bind))
            #         return inserting.getvalue()

            if len(regex_result) > 0:

                # remove duplicates
                regex_result = list(set(regex_result))

                # CLEANING UP THE  MESS
                bind = "\t### BINDING THIS BECAUSE STARDOG MESSES UP THE RESULT WHEN USING PROPERTY PATH\n"
                for i in range(len(regex_result)):
                    # SOLVING THE PROBLEM BY INSERTING SOME VARIABLE BINDINGS
                    result = result.replace("<{}>".format(regex_result[i]), "?LINK_{}".format(i))
                    bind += "\tBIND( IRI(\"{}\") AS ?LINK_{} )\n".format(regex_result[i].replace("\>", ">"), i)

                # FINAL CLEANING
                if insert is False:
                    result = result.replace("{", "{{\n{}".format(bind))
                    # print "RESPONSE RESULT ALTERED:", result
                else:
                    inserting = Buffer.StringIO()
                    inserting.write("INSERT\n")
                    inserting.write(result)
                    inserting.write("WHERE {{\n{}}}".format(bind))
                    return inserting.getvalue()

            elif insert is True:
                result = "INSERT DATA {}".format(result)

        return result

    except Exception as err:
        print err


def sparql_xml_to_matrix(query):

    name_index = dict()

    if type(query) is not str and type(query) is not unicode:
        message = "THE QUERY NEEDS TO BE OF TYPE STRING. {} WAS GIVEN".format(type(query))
        print message
        return {St.message: message, St.result: None}

    if (query is None) or (query == ""):
        message = "Empty query"
        print message
        return {St.message: message, St.result: None}

    # start_time = time.time()
    matrix = None
    logger.info("XML RESULT TO TABLE")
    # print query

    # if query.lower().__contains__("optional") is True:
    #     message = "MATRIX DOES NOT YET DEAL WITH OPTIONAL"
    #     return {St.message: message, St.result: None}

    response = endpoint(query)
    logger.info("1. RESPONSE OBTAINED")
    # print response[St.result]

    # DISPLAYING THE RESULT

    if response[St.message] == "OK":

        # print "response:", response[St.result]
        # print "response length:", len(response[St.result])

        if len(response[St.result]) == 0:
            message = "NO RESULT FOR THE QUERY"
            return {St.message: message, St.result: None}

        logger.info("2. RESPONSE IS NOT ''NONE''")

        if True:
            xml_doc = xmltodict.parse(response[St.result])
            # print "3. FROM XML TO DOC IN {}".format(str(time.time() - start_time))

            # VARIABLES
            # print "4. GETTING VARIABLE'S LIST FROM XML_DOC"
            variables_list = xml_doc['sparql']['head']['variable']
            # print "Variable List", variables_list
            # print "5. EXTRACTED IN {} SECONDS".format(str(time.time() - start_time))

            variables_size = len(variables_list)
            # print "6. VARIABLE SIZE:", variables_size

            # RESULTS
            # print "7. GETTING RESULT'S LIST FROM XML_DOC"
            results = xml_doc['sparql']['results']
            # print "8. IN {}".format(str(time.time() - start_time))

            if results is not None:
                # print "9. RESULT LIST IS NOT NONE"
                results = results['result']
                # print results
                # print type(results)
            else:
                message = "NO RESULT FOR THE QUERY"
                return {St.message: message, St.result: None}
                # print query

            """ >>> SINGLE RESULT """
            if type(results) is collections.OrderedDict:
                # print "SINGLE RESULT"
                # Creates a list containing h lists, each of w items, all set to 0
                # INITIALIZING THE MATRIX
                w, h = variables_size, 2
                # print "Creating matrix with size {} by {}".format(w, h)
                # x*y*0 to avoid weak error say x and y where not used
                matrix = [[str(x*y*0).replace("0", "") for x in range(w)] for y in range(h)]
                # print matrix
                col = -1

                if variables_size == 1:
                    for name, variable in variables_list.items():
                        # HEADER
                        col += 1
                        # print variable
                        matrix[0][col] = variable
                        # print matrix

                    # RECORDS
                    for key, value in results.items():
                        # print type(value)
                        if type(value) is collections.OrderedDict:
                            item_value = value.items()[1][1]
                            if "#text" in item_value:
                                # print to_bytes(item_value["#text"])
                                matrix[1][0] = to_bytes(item_value["#text"])
                            else:
                                matrix[1][0] = to_bytes(item_value)
                        else:
                            matrix[1][0] = to_bytes(value.items()[1][1])

                else:
                    # print "Variable greater than 1"
                    # HEADER
                    for variable in variables_list:
                        for key, value in variable.items():
                            col += 1
                            matrix[0][col] = to_bytes(value)
                            name_index[to_bytes(value)] = col
                            # print "{} was inserted".format(value)
                            # print matrix

                    # RECORDS
                    # print results.items()
                    for key, value in results.items():
                        # COLUMNS
                        # print "Key: ", key
                        # print "Value: ", value
                        for data in value:
                            # print "value Items: ", value.items()[i][1]
                            # print "Length:", len(value.items())
                            if type(value) is list:
                                # print "value:", value
                                # data = value[i]

                                # get_property = data['@name']
                                # print "get_property:", get_property
                                # index = name_index[get_property]
                                # print "index", index

                                index = name_index[data['@name']]
                                item = data.items()[1][1]
                                # print data['@name'], name_index[data['@name']]
                                matrix[1][index] = to_bytes(item)

                            elif type(value) is collections.OrderedDict:
                                index = name_index[value['@name']]
                                if value.items()[1][0] != '@name':
                                    item = value.items()[1][1]
                                    matrix[1][index] = to_bytes(item)
                                    # print "Collection:", value.items()[i][0]
                                else:
                                    item = ""

                            if type(item) is collections.OrderedDict:
                                # print "Data is a collection"
                                # print "{} was inserted".format(data.items()[1][1])
                                matrix[1][index] = to_bytes(item.items()[1][1])
                            else:
                                # print "data is regular"
                                # print "{} was inserted".format(data)
                                matrix[1][index] = to_bytes(item)
                                # print matrix

                    # print "The matrix is: {}".format(matrix)

            # >>> MORE THAN ONE RESULT
            if type(results) is list:
                # print "THE LIST CONTAINS MORE THAN ONE RESULTS"
                row = 0
                columns = -1
                row_size = len(results)

                # Creates a list containing h lists, each of w items, all set to 0
                w, h = variables_size, row_size + 1

                # print "INITIALIZING THE MATRIX FOR: [{}][{}]".format(h, w)
                matrix = [[str(x*y*0).replace("0", "") for x in range(w)] for y in range(h)]

                # HEADER
                # print "UPDATING MATRIX'S HEADER"
                for variable in variables_list:

                    if type(variable) is collections.OrderedDict:
                        for key, value in variable.items():
                            columns += 1
                            # print "COLUMN: ", columns, value
                            # print value
                            matrix[0][columns] = to_bytes(value)
                            name_index[to_bytes(value)] = columns
                    else:
                        # print "TYPE", type(variables_list)
                        # print "value:", variables_list.items()[0][1]
                        columns += 1
                        # print "COLUMN: ", columns
                        matrix[0][columns] = to_bytes(variables_list.items()[0][1])

                # RECORDS
                # print "UPDATING MATRIX WITH VARIABLES' VALUES"
                for result in results:

                    # ROWS
                    if variables_size == 1:
                        for key, value in result.items():
                            row += 1
                            for c in range(variables_size):
                                # print value.items()[1][1]

                                # if type(c) is collections.OrderedDict:
                                data = value.items()[1][1]
                                if type(data) is collections.OrderedDict:
                                    item = data.items()[1][1]
                                    matrix[row][0] = item

                                else:
                                    matrix[row][0] = to_bytes(data)
                    else:
                        for key, value in result.items():
                            # COLUMNS
                            # print type(value)
                            row += 1
                            # value is a list
                            # for c in range(variables_size):
                            for data in value:

                                if type(data) is collections.OrderedDict:

                                    # print row
                                    # print value[c].items()[1][1]
                                    # data = value[c]
                                    # print data['@name'], name_index[data['@name']]
                                    get_index = data['@name']
                                    index = name_index[get_index]
                                    # print "index:", index, "TYPE:", type(data)
                                    item = data.items()[1][1]
                                    # print index, item
                                    if type(item) is collections.OrderedDict:
                                        item_value = item.items()[1][1]
                                        matrix[row][index] = to_bytes(item_value)
                                        # print to_bytes(item_value)
                                        # print item.items()
                                        # print "r{} c{} v{}".format(row, c, data.items()[1][1])
                                    else:
                                        matrix[row][index] = to_bytes(item)
                                        # print to_bytes(item)
                                        # print "r:{} c:{} {}={}".format(row, c, matrix[0][c], to_bytes(item))
                                else:
                                    index = name_index[value['@name']]
                                    if data != '@name':
                                        matrix[row][index] = to_bytes(value[data])
                                        # print "data:", data, value[data], name_index[value['@name']]

            # print "DONE"
            # print "out with: {}".format(matrix)
            return {St.message: "OK", St.result: matrix}

        # except Exception as err:
        #     message = "\nUNACCEPTED ERROR IN THE RESPONSE."
        #     print message
        #     return {St.message: err, St.result: None}

    else:
        # logger.warning("NO RESPONSE")
        # print response[St.message]
        return {St.message: "NO RESPONSE", St.result: response[St.result], "justification": response[St.message]}


def sparql_xml_to_csv(query="SELECT * {?subject ?predicate ?object } LIMIT 2"):

    name_index = dict()
    csv_builder = StringIO()

    if type(query) is not str and type(query) is not unicode:
        message = "THE QUERY NEEDS TO BE OF TYPE STRING. {} WAS GIVEN".format(type(query))
        print message
        return {St.message: message, St.result: None}

    if (query is None) or (query == ""):
        message = "Empty query"
        print message
        return {St.message: message, St.result: None}

    # start_time = time.time()
    # matrix = None
    logger.info("XML RESULT TO TABLE")
    # print query

    response = endpoint(query)
    logger.info("1. RESPONSE OBTAINED")
    # print response[St.result]

    # DISPLAYING THE RESULT

    if response[St.message] == "OK":

        # print "response:", response[St.result]
        # print "response length:", len(response[St.result])

        if len(response[St.result]) == 0:
            message = "NO RESULT FOR THE QUERY"
            return {St.message: message, St.result: None}

        logger.info("2. RESPONSE IS NOT ''NONE''")

        if True:
            xml_doc = xmltodict.parse(response[St.result])
            # print "3. FROM XML TO DOC IN {}".format(str(time.time() - start_time))

            # VARIABLES
            # print "4. GETTING VARIABLE'S LIST FROM XML_DOC"
            variables_list = xml_doc['sparql']['head']['variable']
            # print "Variable List", variables_list
            # print "5. EXTRACTED IN {} SECONDS".format(str(time.time() - start_time))

            variables_size = len(variables_list)
            # print "6. VARIABLE SIZE:", variables_size

            # RESULTS
            # print "7. GETTING RESULT'S LIST FROM XML_DOC"
            results = xml_doc['sparql']['results']
            # print "8. IN {}".format(str(time.time() - start_time))

            if results is not None:
                # print "9. RESULT LIST IS NOT NONE"
                results = results['result']
                # print results
                # print type(results)
            else:
                message = "NO RESULT FOR THE QUERY"
                return {St.message: message, St.result: None}
                # print query

            """ >>> SINGLE RESULT """
            if type(results) is collections.OrderedDict:

                print "SINGLE RESULT"
                # Creates a list containing h lists, each of w items, all set to 0
                # INITIALIZING THE MATRIX
                w, h = variables_size, 2
                # print "Creating matrix with size {} by {}".format(w, h)
                # x*y*0 to avoid weak error say x and y where not used

                matrix = [[str(x*y*0).replace("0", "") for x in range(w)] for y in range(h)]
                "{}".format(matrix)
                # print matrix
                col = -1

                # SINGLE RESULT
                if variables_size == 1:

                    print "\tSINGLE VARIABLE"

                    for name, variable in variables_list.items():
                        # HEADER
                        col += 1
                        # print variable
                        # matrix[0][col] = variable
                        # print matrix

                        if col == 0:
                            csv_builder.write("\"{}\"".format(variable))
                        else:
                            csv_builder.write("\"{}\",".format(variable))

                    # END OF THE HEADER
                    csv_builder.write("\r\n")

                    # RECORDS
                    for key, value in results.items():
                        # print type(value)
                        if type(value) is collections.OrderedDict:
                            item_value = value.items()[1][1]

                            if "#text" in item_value:
                                # print to_bytes(item_value["#text"])
                                # matrix[1][0] = to_bytes(item_value["#text"])
                                csv_builder.write("\"{}\"\r\n".format(to_bytes(item_value["#text"])))
                            else:
                                # matrix[1][0] = to_bytes(item_value)
                                csv_builder.write("\"{}\"\r\n".format(to_bytes(item_value)))
                        else:
                            # matrix[1][0] = value.items()[1][1]
                            csv_builder.write("\"{}\"\r\n".format(to_bytes(value.items()[1][1])))

                # SINGLE RESULT WITH MORE THAN ONE VARIABLES
                else:
                    print "\tSINGLE RESULT WITH MORE THAN ONE VARIABLES"
                    # HEADER
                    for variable in variables_list:
                        for key, value in variable.items():
                            col += 1
                            # matrix[0][col] = value
                            if col == 0:
                                csv_builder.write("\"{}\"".format(to_bytes(value)))
                            else:
                                csv_builder.write(",\"{}\"".format(to_bytes(value)))
                            name_index[to_bytes(value)] = col
                            # print "{} was inserted".format(value)
                            # print matrix
                    # END OF THE HEADER
                    csv_builder.write("\r\n")
                    # RECORDS
                    # print results.items()
                    for key, value in results.items():
                        # COLUMNS
                        # print "Key: ", key
                        # print "Value: ", value
                        count = -1
                        for data in value:
                            count += 1
                            # print "value Items: ", value.items()[i][1]
                            # print "Length:", len(value.items())
                            if type(value) is list:
                                # print "value:", value
                                # data = value[i]

                                # ??? get_property = data['@name']
                                # print "get_property:", get_property
                                # index = name_index[get_property]
                                # print "index", index

                                # ??? index = name_index[data['@name']]
                                item = data.items()[1][1]
                                # print data['@name'], name_index[data['@name']]
                                # matrix[1][index] = item

                            elif type(value) is collections.OrderedDict:
                                # ??? index = name_index[value['@name']]
                                if value.items()[1][0] != '@name':
                                    item = value.items()[1][1]
                                    # print "Collection:", value.items()[i][0]
                                else:
                                    item = ""

                            if type(item) is collections.OrderedDict:
                                # print "Data is a collection"
                                # print "{} was inserted".format(data.items()[1][1])
                                # matrix[1][index] = item.items()[1][1]
                                item = item.items()[1][1]
                            # else:
                                # print "data is regular"
                                # print "{} was inserted".format(data)
                                # matrix[1][index] = item
                                # print matrix

                            if count == 0:
                                csv_builder.write("\"{}\"".format(to_bytes(item)))
                            elif count == len(value):
                                csv_builder.write(",\"{}\"\r\n".format(to_bytes(item)))
                            else:
                                csv_builder.write(",\"{}\"".format(to_bytes(item)))

                    # print "The matrix is: {}".format(matrix)

            # >>> MORE THAN ONE RESULT
            if type(results) is list:
                print "THE LIST CONTAINS MORE THAN ONE RESULTS"
                row = 0
                columns = -1
                row_size = len(results)

                # Creates a list containing h lists, each of w items, all set to 0
                w, h = variables_size, row_size + 1

                # print "INITIALIZING THE MATRIX FOR: [{}][{}]".format(h, w)
                matrix = [[str(x*y*0).replace("0", "") for x in range(w)] for y in range(h)]
                "{}".format(matrix)

                # HEADER
                # print "UPDATING MATRIX'S HEADER"
                for variable in variables_list:

                    if type(variable) is collections.OrderedDict:
                        for key, value in variable.items():
                            columns += 1
                            # print "COLUMN: ", columns, value
                            # print value
                            # matrix[0][columns] = to_bytes(value)

                            cell = to_bytes(value)
                            if cell is None:
                                cell = ""

                            if columns == 0:
                                csv_builder.write("\"{}\"".format(cell))
                            else:
                                csv_builder.write(",\"{}\"".format(cell))

                            name_index[to_bytes(value)] = columns
                    else:
                        # ONE VARIABLE AND SEVERAL ROWS
                        # print "TYPE", type(variables_list)
                        # print "value:", variables_list.items()[0][1]
                        columns += 1
                        # print "COLUMN: ", columns
                        # matrix[0][columns] = to_bytes(variables_list.items()[0][1])
                        cell = to_bytes(variables_list.items()[0][1])
                        if cell is None:
                            cell = ""
                        if columns == 0:
                            csv_builder.write("\"{}\"".format(cell))
                        else:
                            csv_builder.write(",\"{}\"".format(cell))

                # END OF THE HEADER
                csv_builder.write("\r\n")

                # RECORDS
                # print "UPDATING MATRIX WITH VARIABLES' VALUES"
                for result in results:
                    # ROWS
                    row_array = [str(x*0).replace("0", "") for x in range(w)]
                    if variables_size == 1:
                        for key, value in result.items():
                            row += 1
                            for c in range(variables_size):
                                # print value.items()[1][1]
                                cell = to_bytes(value.items()[1][1])
                                if cell is None:
                                    cell = ""
                                # matrix[row][0] = item
                                csv_builder.write("\"{}\"\n".format(cell))
                    else:
                        for key, value in result.items():
                            # COLUMNS
                            # print type(value)
                            row += 1
                            # value is a list
                            # for c in range(variables_size):
                            for data in value:

                                if type(data) is collections.OrderedDict:

                                    # print row
                                    # print value[c].items()[1][1]
                                    # data = value[c]
                                    # print data['@name'], name_index[data['@name']]
                                    get_index = data['@name']
                                    index = name_index[get_index]
                                    # print "index:", index, "TYPE:", type(data)
                                    item = data.items()[1][1]
                                    # print index, item
                                    if type(item) is collections.OrderedDict:
                                        cell = to_bytes(item.items()[1][1])
                                        if cell is None:
                                            cell = ""
                                        # matrix[row][index] = to_bytes(item_value)
                                        row_array[index] = cell
                                        # if index == 0:
                                        #     csv_builder.write("\"{}\"".format(cell))
                                        # else:
                                        #     csv_builder.write(",\"{}\"".format(cell))
                                        # print to_bytes(item_value)
                                        # print item.items()
                                        # print "r{} c{} v{}".format(row, c, data.items()[1][1])
                                    else:
                                        # matrix[row][index] = to_bytes(item)

                                        cell = to_bytes(item)
                                        if cell is None:
                                            cell = ""
                                        row_array[index] = cell
                                        # if index == 0:
                                        #     csv_builder.write("\"{}\"".format(cell))
                                        # else:
                                        #     csv_builder.write(",\"{}\"".format(cell))
                                        # print to_bytes(item)
                                        # print "r:{} c:{} {}={}".format(row, c, matrix[0][c], to_bytes(item))
                                else:
                                    index = name_index[value['@name']]
                                    if data != '@name':
                                        cell = to_bytes(value[data])
                                        if cell is None:
                                            cell = ""
                                        row_array[index] = cell
                                        # matrix[row][index] = to_bytes(value[data])

                                        # print "data:", data, value[data], name_index[value['@name']]

                            # END OF THE ROW
                            for i in range(len(row_array)):
                                if i == 0:
                                    csv_builder.write("\"{}\"".format(row_array[i]))
                                else:
                                    csv_builder.write(",\"{}\"".format(row_array[i]))
                            csv_builder.write("\r\n")

            # print "DONE"
            # print "out with: {}".format(matrix)
            # print "\nCSV BUILDER:\n", csv_builder.getvalue()
            return {St.message: "OK", St.result: csv_builder}

        # except Exception as err:
        #     message = "\nUNACCEPTED ERROR IN THE RESPONSE."
        #     print message
        #     return {St.message: err, St.result: None}

    else:
        # logger.warning("NO RESPONSE")
        # print response[St.message]
        return {St.message: "NO RESPONSE", St.result: response}


def display_result(query, info=None, spacing=50, limit=100, is_activated=False):

    if is_activated is False:
        print "The function [display_result] is not activated!"

    limit = limit
    if info is not None:
        info = "[Filtering by {}]".format(info)
    else:
        info = ""

    if is_activated is True:

        line = ""
        for space in range(50):
            line += "#"

        logger.info(display_result)
        my_format = "{{:.<{}}}".format(spacing)
        my_format2 = "{{:<{}}}".format(spacing)
        res_matrix = sparql_xml_to_matrix(query)[St.result]

        if res_matrix is None or type(res_matrix) is dict:
            logger.warning("\nTHE MATRIX IS EMPTY\n")
            return None

        static_check = limit and limit > 0

        message = """
        ####################################################################################
        TABLE OF {} Row(S) AND {} Columns {}
        LIMIT IS SET TO {} BUT COULD BE CHANGED WITH THE LIMIT PARAMETER.
        ####################################################################################
         """.format(len(res_matrix) - 1, len(res_matrix[0]), info, limit) if static_check is True else """
        ####################################################################################
        TABLE OF {} Row(S) AND {} Columns {}
        NO LIMIT IS SET BUT COULD BE CHANGED WITH THE LIMIT PARAMETER.
        ####################################################################################
         """.format(len(res_matrix) - 1, len(res_matrix[0]), info)

        print message

        count = 0


        for r in range(len(res_matrix)):

            count += 1

            row = ""

            if r == 0:
                for c in range(len(res_matrix[0])):
                    formatted = my_format2.format(to_bytes(res_matrix[r][c]))
                    row = row + formatted + " "

            if r == 1:
                for c in range(len(res_matrix[0])):
                    formatted = my_format2.format(line)
                    row = row + formatted + " "
                row += "\n"

            if r >= 1:
                for c in range(len(res_matrix[0])):
                    formatted = my_format.format(to_bytes(res_matrix[r][c]))
                    row = row + formatted + " "

            print row

            if static_check and count == limit + 1:
                break


def display_matrix(matrix, spacing=50, limit=100, output=False, line_feed='.', is_activated=False):

    limit = limit
    table = Buffer.StringIO()
    message = """
    ####################################################################################
    TABLE OF {} Row(S) AND {} Columns LIMIT={}
    ####################################################################################
         """.format(0, 0, limit)

    if is_activated is True:

        line = ""
        for space in range(spacing):
            line += "#"

        # logger.info(display_result)
        my_format = "{{:{}<{}}}".format(line_feed, spacing)
        my_format2 = "{{:<{}}}".format(spacing)

        if matrix[St.message] == "NO RESPONSE":
            print Ec.ERROR_CODE_1
            return message

        if matrix[St.result] is None:
            # logger.warning("\nTHE MATRIX IS EMPTY\n")
            print message
            return message

        message = """
    ####################################################################################
    TABLE OF {} Row(S) AND {} Columns LIMIT={}
    ####################################################################################
         """.format(len(matrix[St.result]) - 1, len(matrix[St.result][0]), limit)

        table.write(message)

        count = 0
        for r in range(len(matrix[St.result])):

            count += 1

            row = ""

            # SUBJECT
            if r == 0:
                for c in range(len(matrix[St.result][0])):
                    formatted = my_format2.format(to_bytes(matrix[St.result][r][c]))
                    row = "{}{} ".format(row, formatted)

            # SUBJECT LINE
            elif r == 1:
                for c in range(len(matrix[St.result][0])):
                    formatted = my_format2.format(line)
                    row = "{}{} ".format(row, formatted)
                row += "\n\t"

            if r >= 1:
                for c in range(len(matrix[St.result][0])):
                    formatted = my_format.format(to_bytes(matrix[St.result][r][c]))
                    row = "{}{} ".format(row, formatted)

            table.write("\n\t{}".format(row))

            if count == limit + 1:
                # if output is False:
                #     print table.getvalue()
                # else:
                #     return table.getvalue()
                break

    if output is False:
        print table.getvalue()
    else:
        return table.getvalue()


#######################################################################################
# GET QUERY AND EXECUTION FOR CLUSTERING
#######################################################################################


def get_cluster_rsc_strengths(resources, alignments):

    query = cluster_rsc_strengths_query(resources, alignments)
    # print query
    # THE RESULT OF THE QUERY ABOUT THE LINKED RESOURCES
    response = sparql_xml_to_matrix(query)
    result = response[St.result]

    # DICTIONARY KEY: (SUBJECT, OBJECT) VALUE: LIST OF STRENGTHS
    response_dic = dict()
    if result:
        for i in range(1, len(result)):
            # print result[i]
            key = (result[i][0], result[i][1]) if result[i][0] < result[i][1] else (result[i][1], result[i][0])
            if key not in response_dic:
                response_dic[key] = [result[i][2]]
            else:
                response_dic[key] += [result[i][2]]

    # display_matrix(response, is_activated=True)
    return response_dic


def cluster_rsc_strengths_query(resources, alignments):

    check = resources is None or len(resources) == 0
    comment = "#" if check is True else ""
    query = """
    PREFIX prov: <{3}>
    PREFIX ll: <{4}>
    SELECT DISTINCT ?lookup ?object ?Strength {5}?Evidence
    {{
        {5}VALUES ?lookup{{ {0} }}

        # FETCH CORRESPONDENCE IN BOTH DIRECTIONS
        {{
            GRAPH <{1}>
            {{ ?lookup ?predicate ?object .}}
        }}
        UNION
        {{
            GRAPH <{1}>
            {{?object ?predicate ?lookup . }}
        }}

        # FETCH CORRESPONDENCE STRENGTH
        {{
            GRAPH <{2}>
            {{
                ?predicate  prov:wasDerivedFrom*  ?DerivedFrom  .
                OPTIONAL {{ ?DerivedFrom  ll:hasStrength  ?Strength . }}
                OPTIONAL {{ ?DerivedFrom  ll:hasEvidence  ?Evidence . }}
            }}
            GRAPH ?g
            {{
                ?DerivedFrom  prov:wasDerivedFrom*/ll:hasStrength  ?Strength ;
                              prov:wasDerivedFrom*/ll:hasEvidence  ?Evidence .
            }}

        }} UNION
        {{
        GRAPH <{2}>
            {{
                ?predicate  ll:hasStrength  ?Strength .
            }}
        }} # CONSTRAINTS IF ANY
    }}""".format(resources, alignments, from_alignment2singleton(alignments), Ns.prov, Ns.alivocab, comment)
    # print query
    return query


#######################################################################################
# GET QUERY AND EXECUTION
#######################################################################################


def get_properties(graph):
    query = """
    SELECT DISTINCT ?pred
    {{
      graph <{}>
      {{
        ?sub ?pred ?obj .
      }}
    }}""".format(graph)
    # print query
    return sparql_xml_to_matrix(query)


def contains_duplicates(graph):

    query = """
    ask
    {{
          graph <{}>
          {{
            ?a ?p1 ?c .
            ?c ?p2 ?a .
          }}
    }}""".format(graph)
    response = boolean_endpoint_response(query)
    response = True if response == "true" else False
    return response


# ??? def remove_duplicates(graph, graph_name):
def remove_duplicates(graph):

    query = """
    PREFIX specific:    <{1}>

    INSERT
    {{
          graph  <{0}>
          {{
            ?s  ?p1         ?o .
          }}

          graph  specific:{1}
          {{
            ?p1 ?predicate  ?object .
          }}
    }}

    WHERE
    {{
        graph  <{0}>
        {{
            ?s ?p1 ?o .
            ?o ?p2 ?s .
        }}

        OPTIONAl
        {{
            graph  specific:{1}
            {{
                ?p2 ?predicate ?object .
            }}
        }}
        FILTER (str(?s) > str(?o) )
    }} ;


    DELETE
     {{
          graph  <{0}>
          {{
            ?o  ?p2         ?s .
          }}

          graph  specific:{1}
          {{
            ?p2 ?predicate  ?object .
          }}
    }}

    WHERE
    {{
        graph  <{0}>
        {{
            ?s ?p1 ?o .
            ?o ?p2 ?s .
        }}

        OPTIONAl
        {{
            graph  specific:{1}
            {{
                ?p2 ?predicate ?object .
            }}
        }}

        FILTER (str(?s) > str(?o) )
    }}""".format(graph, Ns.singletons)
    # print query
    response = boolean_endpoint_response(query)
    response = True if response == "true" else False
    return response


def graph_exists(graph):

    query = "\nASK {{ GRAPH <{}> {{ ?s ?p ?o . }} }}".format(graph)
    # print query
    ask = boolean_endpoint_response(query)
    ask = True if ask == "true" else False
    return ask


def get_type_mechanism(graph):

    query = """
    PREFIX alivocab:    <{}>
    SELECT ?type ?mechanism
    {{
      <{}>
         a                          ?type ;
         alivocab:alignsMechanism   ?mechanism ;
    }}""".format(Ns.alivocab, graph)
    # print query
    return sparql_xml_to_matrix(query)


def get_same_as_count(curr_mechanism):

    c_code = None

    if True:
        if str(curr_mechanism).__contains__("http://"):
            curr_mechanism = "<{}>".format(curr_mechanism)
        else:
            curr_mechanism = "mechanism:{}".format(curr_mechanism)

        context_code_query = """
    PREFIX void:        <{}>
    PREFIX alivocab:    <{}>
    PREFIX mechanism:   <{}>
    SELECT ?sameAsCount
    {{
      ?subject
        #a                          void:Linkset ;
         alivocab:alignsMechanism   {} ;
         alivocab:sameAsCount       ?sameAsCount .
    }}
    ORDER BY DESC(?sameAsCount)
    LIMIT 1""".format(Ns.void, Ns.alivocab, Ns.mechanism, curr_mechanism)
        # print context_code_query

        # print "GETTING sameAsCount"
        matrix = sparql_xml_to_matrix(context_code_query)
        # print "RESULT:", matrix

        if matrix:
            if matrix[St.message] != "NO RESPONSE":
                # print matrix[St.result]
                if matrix[St.result]:
                    current_code = matrix[St.result][1][0]
                    c_code = int(current_code) + 1
                    # c_code = code
                    # print "Next is: {}".format(c_code)
                else:
                    # print "CHECKING THE CONNECTION"
                    c_code = None if matrix[St.message] == ERROR else 1
                    # print c_code
            else:
                # print Ec.ERROR_CODE_1
                return c_code
        else:
            print "NULL"
            return c_code

        return c_code

    # except Exception as err:
    #     print "PROBLEM ACCESSING THE SAME-AS-COUNT"
    #     print "ERROR: ", err.message
    #     return c_code


def get_graph_type(graph):

    query = """
    ### GET TYPE
    SELECT DISTINCT ?type
    {{
      # GRAPH TYPE
      <{}>
                a    ?type .
    }}""".format(graph)
    # print query
    return sparql_xml_to_matrix(query)


def get_lens_operator(graph):
    query = """
    PREFIX alivocab: <{}>
    ### GATHERING TRANSITIVE LENS METADATA
    SELECT DISTINCT ?operator
    {{
      # LINKSET METADATA
      <{}>
                alivocab:operator		?operator  .
    }}""".format(Ns.alivocab, graph)
    # print query

    result = sparql_xml_to_matrix(query)
    # print result

    if result[St.result] is not None:
        return result[St.result][1][0]

    return None


def get_graph_targets(graph):

    query = """
    PREFIX void: <{}>
    SELECT DISTINCT ?targets
    {{
      # GRAPH TYPE
      <{}>
                void:target   ?targets .
    }}""".format(Ns.void, graph)
    # print query
    # return query
    return sparql_xml_to_matrix(query)


def get_graph_source_target(graph):

    query = """
    PREFIX void: <{}>
    SELECT DISTINCT ?subjectsTarget ?objectsTarget
    {{
      <{}>
                 void:subjectsTarget   ?subjectsTarget ;
                 void:objectsTarget    ?objectsTarget .
    }}""".format(Ns.void, graph)
    # print query
    # return query
    return sparql_xml_to_matrix(query)


def get_linkset_datatypes(linkset):

    query = """
    #################################################################
    ### LINKSET INFO                                              ###
    #################################################################
    PREFIX void:        <{}>
    PREFIX bdb:         <{}>
    PREFIX alivocab:    <{}>

    select DISTINCT ?subjectsDatatype ?objectsDatatype
    ?alignsSubjects ?alignsObjects ?subjectsTarget ?objectsTarget
    {{
      <{}>
            a                           void:Linkset ;
            bdb:subjectsDatatype        ?subjectsDatatype ;
            bdb:objectsDatatype         ?objectsDatatype ;
            alivocab:alignsSubjects     ?alignsSubjects ;
            alivocab:alignsObjects      ?alignsObjects ;
            void:subjectsTarget         ?subjectsTarget ;
            void:objectsTarget          ?objectsTarget .
    }}
    #################################################################
    """.format(Ns.void, Ns.bdb, Ns.alivocab, linkset)
    # print query
    return sparql_xml_to_matrix(query)


def get_lens_union_datasets(graph):

    #
    query = """
    PREFIX void: <{}>
    ### GATHERING TRANSITIVE LENS METADATA
    SELECT DISTINCT ?target
    {{
      # LINKSET METADATA
      <{}>
                void:target		?target  .
    }}""".format(Ns.void, graph)
    # print query

    response = sparql_xml_to_matrix(query)
    # print result

    if response is None:
        return None

    if response[St.result] is not None:
        datasets = [None]*(len(response[St.result])-1)
        for i in range(1, len(response[St.result])):
            datasets[i-1] = response[St.result][i][0]
        return datasets

    return None


def get_singleton(linkset):

    singleton_graph_query = """
    PREFIX void: <{}>
    PREFIX link: <{}>
    SELECT DISTINCT ?singletonGraph
    {{
      <{}>
        link:singletonGraph     ?singletonGraph .
    }}
    """.format(Ns.void, Ns.alivocab, linkset)
    # print singleton_graph_query

    singletons = sparql_xml_to_matrix(singleton_graph_query)

    if len(singletons) > 1:
        return singletons[1][0]

    return None


def get_triples(linkset):

    query = """
    ### GET THE TOTAL NUMBER OF CORRESPONDENCE TRIPLES INSERTED
    PREFIX void: <{}>
    SELECT DISTINCT ?triples
    {{
      <{}>
        void:triples     ?triples .
    }}
    """.format(Ns.void, linkset)
    # print query

    triples = sparql_xml_to_matrix(query)
    # print "TRIPLE COUNT:", triples

    if triples[St.result] is None:
        return None

    if len(triples[St.result]) > 1:
        # print "FOUND SOME RESULTS", triples[St.result]
        return triples[St.result][1][0]

    return None


def get_triples_count(graph):

    query = """
    ### COUNT THE NUMBER OF TRIPLES
    SELECT (COUNT(?sub) as ?triples)
    {{
      GRAPH <{}>
      {{
        ?sub ?pre ?obj .
      }}
    }}
    """.format(graph)
    # print query

    triples = sparql_xml_to_matrix(query)

    if triples is None:
        return None

    if len(triples[St.result]) > 1:
        # print triples
        # final_result = triples[St.result][1][0]
        # print  final_result
        return triples[St.result][1][0]

    return None


def get_union_triples(lens):

    query = """
    ### COUNT THE NUMBER OF TRIPLES IN THIS UNION
    SELECT (count(DISTINCT ?pre) as ?triples)
    {{
      GRAPH <{}>
      {{
        ?sub    ?pre       ?obj .
        ?pre    ?derived   ?from .
      }}
    }}
    """.format(lens)
    # print query

    triples = sparql_xml_to_matrix(query)
    # print triples

    if triples[St.result] is None:
        return

    if len(triples[St.result]) > 1:
        return triples[St.result][1][0]

    return None


def get_linkset_info():

    query = """
    ########################################
    ### LINKSET METADATA                 ###
    ########################################
    PREFIX void: <http://rdfs.org/ns/void#>
    PREFIX alivocab: <http://risis.eu/linkset/predicate/>
    select distinct * where
    {
        ?linkset a void:Linkset .
        #OPTIONAL { ?linkset alivocab:singletonGraph  ?singletonMetadata }
        ?linkset
           void:triples			    ?triples ;
           void:subjectsTarget	    ?dataSubject ;
           void:objectsTarget	    ?dataObject ;
           void:linkPredicate	    ?link ;

    }"""
    print query
    query_start = time.time()
    response = endpoint(query)
    query_end = time.time()
    # print response

    if response[St.result] is not None:

        xml_doc = xmltodict.parse(response[St.result])
        variables = xml_doc['sparql']['head']['variable']
        results = xml_doc['sparql']['results']

        print "\n###### About Linkset"
        print "=============================================="
        print "{:60} {:10} {:50} {:50} {:50}".format(
            variables[0]['@name'], variables[1]['@name'], variables[2]['@name'],
            variables[3]['@name'], variables[4]['@name'])

        if results is not None:
            get_results = results['result']
            # print (results)

            # print type(results)
            if get_results is not None and (type(get_results) is collections.OrderedDict):
                for value, key in get_results.items():
                    print "{:60} {:10} {:50} {:50} {:50}".format(
                        key[0]['uri'], key[1]['literal']['#text'], key[2]['uri'], key[3]['uri'], key[4]['uri'])

            # print type(get_results)
            elif get_results is not None and (type(get_results) is list):
                for value in get_results:
                    print "{:60} {:10} {:50} {:50} {:50}".format(
                        value['binding'][0]['uri'], value['binding'][1]['literal']['#text'],
                        value['binding'][2]['uri'], value['binding'][3]['uri'], value['binding'][4]['uri'])

    print "\nGRAPHS INFO EXTRACTED IN {} seconds\n". \
        format(str((query_end - query_start)))


def get_namedgraph_size(linkset_uri, isdistinct=False):

    distinct = ""

    if isdistinct is True:
        distinct = "DISTINCT "

    check_query = "\n{}\n{}\n{}\n{}\n{}\n{}\n{}".format(
        # "PREFIX linkset: <http://risis.eu/linkset/>",
        # "PREFIX lsMetadata: <http://risis.eu/linkset/metadata/>",
        # "PREFIX predicate: <http://risis.eu/linkset/predicate/>",
        # "PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>",
        "    ##### GETTING THE LINKSET SIZE",
        "    select(count({}?source) as ?triples)".format(distinct),
        "    WHERE ",
        "    {",
        "       GRAPH <{}>".format(linkset_uri),
        "       { ?source ?predicate ?target }",
        "    }"
    )

    # print check_query

    result = endpoint(check_query)

    # print result

    if result[St.result] is not None:
        # """
        # EXAMPLE OF THE RESULT
        # <?xml version='1.0' encoding='UTF-8'?>
        # <sparql xmlns='http://www.w3.org/2005/sparql-results#'>
        #     <head>
        #         <variable name='triples'/>
        #     </head>
        #     <results>
        #         <result>
        #             <binding name='triples'>
        #                 <literal datatype='http://www.w3.org/2001/XMLSchema#integer'>13164</literal>
        #             </binding>
        #         </result>
        #     </results>
        # </sparql>
        # """
        dropload_doc = xmltodict.parse(result[St.result])
        return dropload_doc['sparql']['results']['result']['binding']['literal']['#text']
    else:
        return None


def insert_size(linkset_uri, isdistinct=False):

    query = """
    PREFIX void: <{1}>

    DELETE {{ <{0}> void:triples ?count }}
    INSERT {{ <{0}>  void:triples ?triples . }}
    WHERE
      {{
          <{0}>  void:triples ?count .
          {{
                SELECT (count(?source) as ?triples)
                {{
                    GRAPH <{0}>
                    {{
                        ?source ?predicate ?target
                    }}
                }}
          }}
      }}
    """.format(linkset_uri, Ns.void)
    inserted = boolean_endpoint_response(query)
    # print query

    distinct = ""

    if isdistinct is True:
        distinct = "DISTINCT "

    check_query = "\n{}\n{}\n{}\n{}\n{}\n{}\n{}".format(
        # "PREFIX linkset: <http://risis.eu/linkset/>",
        # "PREFIX lsMetadata: <http://risis.eu/linkset/metadata/>",
        # "PREFIX predicate: <http://risis.eu/linkset/predicate/>",
        # "PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>",
        "    ##### GETTING THE LINKSET SIZE",
        "    select(count({}?source) as ?triples)".format(distinct),
        "    WHERE ",
        "    {",
        "       GRAPH <{}>".format(linkset_uri),
        "       { ?source ?predicate ?target }",
        "    }"
    )

    # print check_query

    result = endpoint(check_query)

    # print result

    if result[St.result] is not None:
        # """
        # EXAMPLE OF THE RESULT
        # <?xml version='1.0' encoding='UTF-8'?>
        # <sparql xmlns='http://www.w3.org/2005/sparql-results#'>
        #     <head>
        #         <variable name='triples'/>
        #     </head>
        #     <results>
        #         <result>
        #             <binding name='triples'>
        #                 <literal datatype='http://www.w3.org/2001/XMLSchema#integer'>13164</literal>
        #             </binding>
        #         </result>
        #     </results>
        # </sparql>
        # """
        dropload_doc = xmltodict.parse(result[St.result])
        return [inserted,
                dropload_doc['sparql']['results']['result']['binding']['literal']['#text'],
                "correspondences inserted"]
    else:
        return None


def entity_types(re_filter=None):

    regex = ""
    if re_filter is not None:
        regex = "Filter regex(str(?Graph), '{}', 'i')".format(re_filter)
    query = """
    #################################################################
    ### Count the number of entities per entity-type and per graph ###
    #################################################################
    select distinct ?Graph ?EntityType (count(distinct ?x) as ?EntityCount)
    {{
      GRAPH ?Graph
      {{
         ?x a ?EntityType .
      }}
    }} GROUP by ?Graph ?EntityType ORDER BY ?Graph
    """.format(regex)

    # print query
    query_start = time.time()
    response = endpoint(query)
    # print response
    query_end = time.time()
    print "\nNAMED GRAPHS - ENTITY-TYPES & INSTANCES COUNT in {} seconds\n". \
        format(str((query_end - query_start)))

    # toPrint = ""

    # DISPLAYING THE RESULT
    if response[St.result] is not None:

        xml_doc = xmltodict.parse(response[St.result])
        # PRINT VARIABLES
        print "\t{:50}{:70}{:30}".format(
            xml_doc['sparql']['head']['variable'][0]['@name'],
            xml_doc['sparql']['head']['variable'][1]['@name'],
            xml_doc['sparql']['head']['variable'][2]['@name'])
        to_print = xml_doc['sparql']['results']['result']

        # PRINT VARIABLES' VALUES
        for value in to_print:
            print "\t{:50}{:70}{:30}".\
                format(value['binding'][0]['uri'], value['binding'][1]['uri'], value['binding'][2]['literal']['#text'])


def namedgraphs(re_filter=None, isdistinct=False, display=False):

    distinct = ""

    if isdistinct is True:
        distinct = "DISTINCT "

    regex = ""
    if re_filter is not None:
        regex = "Filter regex(str(?graph), '{}', 'i')".format(re_filter)
    query = """
    ####################################################################################
    ### NAMED GRAPHS                                                                 ###
    ####################################################################################
    select distinct ?graph (count({}?s) as ?EntityCount)
    where
    {{
        GRAPH ?graph {{  ?s ?p ?o  }}
        {}
    }}
    GROUP by ?graph order by ?graph
    ####################################################################################
    """.format(distinct, regex)

    header = "\n####################################################################################################" \
             "\n### {} NAMED GRAPHS                                                                                 " \
             "\n####################################################################################################". \
        format(str(re_filter)).upper()

    graph_count = 0
    if display is True:
        print query
    print header
    query_start = time.time()
    response = endpoint(query)
    # print response
    query_end = time.time()

    # toPrint = ""
    if response is not None:
        xml_doc = xmltodict.parse(response)
        if xml_doc is not None:
            to_print = xml_doc['sparql']['results']

            print "{:90} {}".format(
                xml_doc['sparql']['head']['variable'][0]['@name'],
                xml_doc['sparql']['head']['variable'][1]['@name'])

            if to_print is not None:
                results = to_print['result']
                graph_count = len(results)
                for value in results:
                    if value is not None and (type(value) is collections.OrderedDict):
                        binding = value['binding']
                        if binding is not None:
                            print "{:90} {}".format(binding[0]['uri'], binding[1]['literal']['#text'])

    print "\nEXTRACTED {} graphs(s) IN {} seconds\n". \
        format(graph_count, str((query_end - query_start)))


def countlinksettriples(src_dataset_name, trg_dataset_name, context_code, linkset_name, see_who_uses_it):

    print see_who_uses_it
    check_query = "\n{}\n{}\n{}\n\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n". \
        format("PREFIX linkset: <{}>".format(Ns.linkset),
               "PREFIX predicate: <{}>".format(Ns.alivocab),
               "PREFIX rdfs: <{}>".format(Ns.rdfs),
               "CONSTRUCT {{linkset:{} predicate:triple ?triples}}".format(linkset_name),
               "WHERE",
               "{",
               "  {",
               "    select(count(?source) as ?triples)",
               "    WHERE ",
               "    {",
               "       GRAPH linkset:{}_{}_C{}_ExactName".format(src_dataset_name, trg_dataset_name,
                                                                 context_code),
               "       { ?source ?predicate ?target }",
               "    }",
               "  }",
               "}")

    # print check_query
    print "{}{}{}".format(
        "====================================================================================\n",
        "Checking the number of triples in linkset:{}_{}_ExactName\n".format(src_dataset_name,
                                                                             trg_dataset_name),
        "====================================================================================\n")

    construct = endpointconstruct(check_query)
    # print construct

    return construct


#######################################################################################
# DROP QUERY AND EXECUTION
#######################################################################################


def drop_graph(graph, display=False, activated=True):

    queries = """
    #################################################################
    ### DELETE LINKSET NAMED GRAPHS AND METADATA                  ###
    #################################################################

    ### 1. DELETING GRAPHS's METADATA
    PREFIX void:    <{0}>
    PREFIX bdb:     <{1}>
    PREFIX link:    <{2}>

    DELETE {{ ?linktype ?x ?y }}
    where
    {{
      <{3}>
        void:linkPredicate  ?linktype .
      ?linktype
        ?x                  ?y
    }} ;

    ### 2. DELETING ASSERTION METADATA
    DELETE {{ ?assertionMethod ?x ?y }}
    where
    {{
      <{3}>
        bdb:assertionMethod     ?assertionMethod .
      ?assertionMethod
        ?x                      ?y
    }} ;

    ### 3. DELETING JUSTIFICATION METADATA
    DELETE {{ ?linksetJustification ?x ?y }}
    where
    {{
      <{3}>
        bdb:linksetJustification    ?linksetJustification .
      ?linksetJustification
        ?x                          ?y
    }} ;

    ### 4. DELETING THE SINGLETON GRAPH
    DELETE {{ GRAPH ?singletonGraph {{ ?x ?y ?z }} }}
    where
    {{
      <{3}>
        link:singletonGraph 		?singletonGraph .
        GRAPH ?singletonGraph       {{ ?x ?y ?z }} .
    }} ;

    ### 5. DELETING THE META DATA
    DELETE {{ <{3}> ?x ?y . }}
    where
    {{
      <{3}>
               ?x   ?y
    }} ;

    #################################################################
    ### DELETE LINKSET NAMED GRAPHS                              ###
    #################################################################
    DROP SILENT  GRAPH <{3}>

    """.format(Ns.void, Ns.bdb, Ns.alivocab, graph)

    if activated is False and display is True:
        print queries

    # print endpoint(queries, database_name, host)

    if activated is True:
        print "{}{}{}".format(
            "======================================================="
            "=======================================================\n",
            "DROPPING THE GRAPH <{}>... \nPLEASE WAIT FOR FEEDBACK.".format(graph),
            "\n======================================================="
            "======================================================="
        )
        drop_start = time.time()
        drops_response = endpoint(queries)
        drop_end = time.time()

        if drops_response[St.result] is not None:
            drops_doc = xmltodict.parse(drops_response[St.result])
            print "\t>>> Query executed : {:<14}".format(drops_doc['sparql']['boolean'])
            print "\t>>> Executed in    : {:<14} minute(s)".format(str((drop_end - drop_start) / 60))
            if display is True:
                print ">>> Query details  : {}\n".format(queries)
        print ""


def drop_linkset(display=False, activated=True):

    queries = """
    #################################################################
    ### DELETE LINKSET NAMED GRAPHS AND METADATA                  ###
    #################################################################

    ### 1. DELETING LINKTYPE METADATA
    PREFIX void:    <{}>
    PREFIX bdb:     <{}>
    PREFIX link:    <{}>

    DELETE {{ ?linktype ?x ?y }}
    where
    {{
      ?linkset
        a                   void:Linkset ;
        void:linkPredicate  ?linktype .
      ?linktype
        ?x ?y
    }} ;

    ### 2. DELETING ASSERTION METADATA
    DELETE {{ ?assertionMethod ?x ?y }}
    where
    {{
      ?linkset
        a                       void:Linkset ;
        bdb:assertionMethod     ?assertionMethod .
      ?assertionMethod
        ?x ?y
    }} ;

    ### 3. DELETING JUSTIFICATION METADATA
    DELETE {{ ?linksetJustification ?x ?y }}
    where
    {{
      ?linkset
        a                           void:Linkset ;
        bdb:linksetJustification    ?linksetJustification .
      ?linksetJustification
        ?x ?y
    }} ;

    ### 4. DELETING THE SINGLETON GRAPH
    DELETE {{ GRAPH ?singletonGraph {{ ?x ?y ?z }} }}
    where
    {{
      ?linkset
        a 							void:Linkset ;
        link:singletonGraph 		?singletonGraph .
        GRAPH ?singletonGraph       {{ ?x ?y ?z }} .
    }} ;

    ### 5. DELETING LINKSET GRAPHS
    DELETE {{ ?linkset ?x ?y . }}
    where
    {{
      ?linkset a    void:Linkset ;
               ?x   ?y
    }} ;

    #################################################################
    ### DELETE LINKSET NAMED GRAPHS                              ###
    #################################################################
    DELETE {{ GRAPH ?graph {{  ?s ?p ?o  }} }}
    where
    {{
        GRAPH ?graph {{  ?s ?p ?o  }}
        Filter regex(str(?graph), 'linkset', 'i')
    }}
    """.format(Ns.void, Ns.bdb, Ns.alivocab)

    # print endpoint(queries, database_name, host)

    if activated is True:
        print "{}{}{}".format(
            "======================================================="
            "=======================================================\n",
            "DROPPING LINKSET...\nPLEASE WAIT FOR FEEDBACK.",
            "\n======================================================="
            "======================================================="
        )
        drop_start = time.time()
        drops_response = endpoint(queries)
        drop_end = time.time()

        if drops_response[St.result] is not None:
            drops_doc = xmltodict.parse(drops_response[St.result])
            print "\t>>> Query executed : {:<14}".format(drops_doc['sparql']['boolean'])
            print "\t>>> Executed in    : {:<14} minute(s)".format(str((drop_end - drop_start) / 60))
            if display is True:
                print ">>> Query details  : {}\n".format(queries)
        print ""


def drop_subset(display=False, activated=True):

    queries = """
    #################################################################
    ### DELETE LINKSET NAMED GRAPHS AND METADATA                  ###
    #################################################################

    ### 1. DELETING LINKTYPE METADATA
    PREFIX void:    <{}>
    PREFIX bdb:     <{}>
    PREFIX link:    <{}>
    DELETE {{ ?linktype ?x ?y }}
    where
    {{
      ?linkset
        a                   void:Linkset ;
        void:subset         ?subset ;
        void:linkPredicate  ?linktype .
      ?linktype
        ?x                  ?y
    }} ;

    ### 2. DELETING ASSERTION METADATA
    DELETE {{ ?assertionMethod ?x ?y }}
    where
    {{
      ?linkset
        a                   void:Linkset ;
        void:subset         ?subset ;
        bdb:assertionMethod ?assertionMethod .
      ?assertionMethod
        ?x                  ?y
    }} ;

    ### 3. DELETING JUSTIFICATION METADATA
    DELETE {{?linksetJustification ?x ?y}}
    where
    {{
      ?linkset
        a                           void:Linkset ;
        void:subset                 ?subset ;
        bdb:linksetJustification    ?linksetJustification .
      ?linksetJustification
        ?x                          ?y
    }} ;

    ### 4. DELETING THE SINGLETON GRAPH
    DELETE {{ GRAPH ?singletonGraph {{ ?x ?y ?z }} }}
    where
    {{
      ?linkset
        a 							void:Linkset ;
        void:subset                 ?subset ;
        link:singletonGraph 		?singletonGraph .
        GRAPH ?singletonGraph       {{ ?x ?y ?z }} .
    }} ;

    ### 5. DELETING LINKSET GRAPHS
    DELETE {{ ?linkset ?x ?y . }}
    where
    {{
      ?linkset
        a void:Linkset ;
        void:subset ?subset ;
        ?x ?y
    }};

    #################################################################
    ### DELETE LINKSET NAMED GRAPHS                              ###
    #################################################################
    DELETE {{ GRAPH ?graph {{  ?s ?p ?o  }} }}
    where
    {{
        GRAPH ?graph {{  ?s ?p ?o  }}
        Filter regex(str(?graph), 'subset', 'i')
    }}
    """.format(Ns.void, Ns.bdb, Ns.alivocab)

    if display is True:
        print queries

    # print endpoint(queries, database_name, host)

    if activated is True:
        print "{}{}{}".format(
            "======================================================="
            "=======================================================\n",
            "DROPPING SUBSETS...\nPLEASE WAIT FOR FEEDBACK.",
            "\n======================================================="
            "=======================================================")
        drop_start = time.time()
        drops_response = endpoint(queries)
        drop_end = time.time()

        if drops_response[St.result] is not None:
            drops_doc = xmltodict.parse(drops_response[St.result])
            print "\t>>> Query executed : {:<14}".format(drops_doc['sparql']['boolean'])
            print "\t>>> Executed in    : {:<14} minute(s)".format(str((drop_end - drop_start) / 60))
            if display is True:
                print ">>> Query details  : {}\n".format(queries)
        print ""


def drop_lens(display=False, activated=False):

    queries = """
    PREFIX void:    <{}>
    PREFIX bdb:     <{}>
    PREFIX link:    <{}>

    ### 1. DELETING ASSERTION METHOD
    DELETE {{ ?assertionMethod ?x ?y }}
    where
    {{
      ?linkset
        a 							bdb:Lense ;
        bdb:assertionMethod 		?assertionMethod .
      ?assertionMethod ?x ?y .
    }} ;

    ### 2. DELETING JUSTIFICATION
    DELETE {{ ?linksetJustification ?x ?y }}
    where
    {{
      ?linkset
        a 							bdb:Lense ;
        bdb:linksetJustification 	?linksetJustification ;.
      ?linksetJustification ?x ?y .
    }} ;

    ### 3. DELETING LINK-TYPE
    DELETE {{ ?linkPredicate ?x ?y }}
    where
    {{
      ?linkset
        a 							bdb:Lens ;
        void:linkPredicate 			?linkPredicate .
      ?linkPredicate ?x ?y .
    }} ;

    ### 4. DELETING THE SINGLETON GRAPH
    DELETE {{ GRAPH ?singletonGraph {{ ?x ?y ?z }} }}
    where
    {{
      ?linkset
        a 							bdb:Lens ;
        link:singletonGraph 		?singletonGraph .
        GRAPH ?singletonGraph       {{ ?x ?y ?z }} .
    }} ;

    ### 5. DELETING THE METADATA
    DELETE {{ ?linkset ?x ?y }}
    where
    {{
      ?linkset
        a 							bdb:Lens ;
        ?x                          ?y.
    }} ;

    #################################################################
    ### DELETE LINKSET NAMED GRAPHS                              ###
    #################################################################
    DELETE {{ GRAPH ?graph {{  ?s ?p ?o  }} }}
    where
    {{
        GRAPH ?graph {{  ?s ?p ?o  }}
        Filter regex(str(?graph), 'lens', 'i')
    }}
    """.format(Ns.void, Ns.bdb, Ns.alivocab)

    if activated is True:
        print "{}{}{}".format(
            "======================================================="
            "=======================================================\n",
            "DROPPING LENS...\nPLEASE WAIT FOR FEEDBACK.",
            "\n======================================================="
            "=======================================================")
        drop_start = time.time()
        drops_response = endpoint(queries)
        drop_end = time.time()

        if drops_response[St.result] is not None:
            drops_doc = xmltodict.parse(drops_response[St.result])
            print "\t>>> Query executed : {:<14}".format(drops_doc['sparql']['boolean'])
            print "\t>>> Executed in    : {:<14} minute(s)".format(str((drop_end - drop_start) / 60))
            if display is True:
                print ">>> Query details  : {}\n".format(queries)
        print ""


def drop_all():
    print "{}{}{}".format(
        "\n====================================================================================\n",
        "List of graphs dropped\n",
        "===================================================================================="
    )

    drops = """
    #################################################################
    ### DELETE NAMED GRAPHS                                       ###
    #################################################################
    DELETE {{ GRAPH ?graph {{  ?s ?p ?o  }} }}
    where
    {{
        GRAPH ?graph {{  ?s ?p ?o  }}
    }}
    """
    print drops

    print "{}{}{}".format(
        "\n=====================================================================\n",
        "DROPPING ALL...\nPLEASE WAIT FOR FEEDBACK.\n",
        "=====================================================================")
    print endpoint(drops)


def drop_union(display=False, activated=False):

    queries = """
    PREFIX void:        <{}>
    PREFIX bdb:         <{}>
    PREFIX alivocab:    <{}>
    PREFIX lensOp:      <{}>

    ### DELETING THE METHOD RESOURCE
    DELETE {{ ?method ?x ?y }}
    WHERE
    {{
        ?lens
            a                           bdb:Lens ;
            alivocab:operator           lensOp:union ;
            bdb:assertionMethod         ?method .
        ?method
            ?x                          ?y .
    }} ;

    ### DELETING THE METADATA
    DELETE {{ ?lens ?x ?y }}
    WHERE
    {{
        ?lens
            a                           bdb:Lens ;
            alivocab:operator           lensOp:union ;
            ?x                          ?y .
    }} ;

    #################################################################
    ### DELETE LINKSET NAMED GRAPHS                              ###
    #################################################################
    DELETE {{ GRAPH ?graph {{  ?s ?p ?o  }} }}
    where
    {{
        GRAPH ?graph {{  ?s ?p ?o  }}
        Filter regex(str(?graph), 'union_', 'i')
    }}
    """.format(Ns.void, Ns.bdb, Ns.alivocab, Ns.lensOp)

    if activated is True:
        print "{}{}{}".format(
            "======================================================="
            "=======================================================\n",
            "DROPPING UNION...\nPLEASE WAIT FOR FEEDBACK",
            "\n======================================================="
            "=======================================================",)
        drop_start = time.time()
        drops_response = endpoint(queries)
        drop_end = time.time()

        if drops_response[St.result] is not None:
            drops_doc = xmltodict.parse(drops_response[St.result])
            print "\t>>> Query executed : {:<14}".format(drops_doc['sparql']['boolean'])
            print "\t>>> Executed in    : {:<14} minute(s)".format(str((drop_end - drop_start) / 60))
            if display is True:
                print ">>> Query details  : {}\n".format(queries)
        print ""


#######################################################################################
# QUERY
#######################################################################################


def get_constructed_graph(graph):

    construct_query = "\n{}\n{}\n{}\n".format(
        "PREFIX alivocab: <{}>".format(Ns.alivocab),
        "construct { ?x ?y ?z }",
        "where     {{ graph <{}> {{ ?x ?y ?z }} }}".format(graph),
    )

    return endpointconstruct(construct_query)


def get_singleton_graph(linkset):

    singleton_graph_query = """
    PREFIX void: <{}>
    PREFIX link: <{}>
    SELECT DISTINCT ?singletonGraph
    {{
      <{}>
        link:singletonGraph     ?singletonGraph .
    }}
    """.format(Ns.void, Ns.alivocab, linkset)
    # print singleton_graph_query
    return singleton_graph_query


def get_intersection(graph, nbr_linkset):
    query = """
    SELECT ?sCorr ?oCorr
    {{
        GRAPH <{}>
        {{
            ?sCorr		?singPre 		?oCorr .
            ?singPre    ?p              ?O .
        }}
    }}
    GROUP BY ?p ?sCorr ?oCorr
    HAVING (count (?p) = {})
    ORDER BY ?sCorr
    """.format(graph, nbr_linkset)
    matrix = sparql_xml_to_matrix(query)
    return matrix


def q_lens_transitive_metadata(graph):
    query = """
    prefix alivocab:    <{}>
    PREFIX void:        <{}>

    ### GATHERING TRANSITIVE LENS METADATA
    SELECT DISTINCT ?singletonGraph	?subjectsTarget ?objectsTarget ?isTransitiveBy
    {{
      # LINKSET METADATA
      <{}>
                alivocab:singletonGraph		?singletonGraph  ;
                void:subjectsTarget			?subjectsTarget ;
                void:objectsTarget			?objectsTarget ;
                alivocab:isTransitiveBy     ?isTransitiveBy .
    }}""".format(Ns.alivocab, Ns.void, graph)
    return query


def q_linkset_metadata(graph):

    query = """
    ### GETTING LINKSET EVIDENCES
    prefix alivocab:    <{0}>
    PREFIX void:        <{1}>

    SELECT DISTINCT ?singletonGraph ?alignsSubjects ?alignsObjects ?subjectsTarget ?objectsTarget
    {{
      # LINKSET METADATA
      <{2}>
                alivocab:singletonGraph		?singletonGraph  ;
                alivocab:alignsSubjects		?alignsSubjects ;
                alivocab:alignsObjects     	?alignsObjects ;
                void:subjectsTarget			?subjectsTarget ;
                void:objectsTarget			?objectsTarget .
    }}
    """.format(Ns.alivocab, Ns.void, graph)
    return query


def linkset_singleton_graph(linkset):
    query = """
        ###### LINKSET SINGLETON GRAPH
        PREFIX link: <{}>
        PREFIX void: <{}>
        select DISTINCT ?singletonGraph
        {{
          <{}>
            a                       void:Linkset ;
            link:singletonGraph     ?singletonGraph .
        }}
        """.format(Ns.alivocab, Ns.void, linkset)
    # print query
    return sparql_xml_to_matrix(query)


def count_entity_type(re_filter=None, display=False, isdistinct=True):

    logger.info('count_entity_type')
    distinct = ""

    if isdistinct is True:
        distinct = "DISTINCT "

    regex = ""
    if re_filter is not None:
        regex = "Filter regex(str(?Graph), '{}', 'i')".format(re_filter)
    query = """
    ####################################################################################
    ### Count the number of entities per entity-type and per graph
    ####################################################################################
    SELECT DISTINCT ?Graph ?EntityType (count({}?x) as ?EntityCount)
    {{
      GRAPH ?Graph
      {{
         ?x a ?EntityType .
      }} {}
    }}
    GROUP BY ?Graph ?EntityType
    ORDER BY ?Graph
    ####################################################################################
    """.format(distinct, regex)

    if display is True:
        print query

    logger.info(query)
    return query


def graphs(re_filter=None, isdistinct=False, display=False):

    distinct = ""

    if isdistinct is True:
        distinct = "DISTINCT "

    regex = ""
    if re_filter is not None:
        regex = "Filter regex(str(?graph), '{}', 'i')".format(re_filter)
    query = """
    ####################################################################################
    ### NAMED GRAPHS                                                                ###
    ####################################################################################
    SELECT DISTINCT ?graph (count({}?s) as ?EntityCount)
    where
    {{
        GRAPH ?graph {{  ?s ?p ?o  }}
        {}
    }}
    GROUP BY ?graph
    ORDER BY ?graph
    ####################################################################################
    """.format(distinct, regex)

    if display is True:
        print query
    return query


def about_entity(entity, display=False):

    query = """
    ####################################################################################
    ### ABOUT THE ENTITY                                                             ###
    ####################################################################################
    SELECT *
    {{
      <{}> ?property ?object .
    }}
    """.format(entity)
    if display is True:
        print query
    return query


def construct_namedgraph(namedgraph):
    query = "\n{}\n{}\n".format(
        "construct { ?x ?y ?z }",
        "where     {{ graph <{}> {{ ?x ?y ?z }} }}".format(namedgraph),
    )
    return query


def linkset_aligns_prop(linkset_uri, cross_check=False):

    if cross_check is True:
        # read the property for cross checking instead of aligns
        prop_aligns = """
              {?linkset ll:crossCheckSubject ?s_prop ;
                       ll:crossCheckObject ?o_prop .
                       bind ('True' as ?crossCheck)
              }
              """
    else:
        # TODO: make the code dynamic for any amount of properties (for now works only for two, latitude and longitude)
        prop_aligns = """
              ?linkset ll:alignsSubjects ?SRC_onj ;
                       ll:alignsObjects ?trg_onj .
              {
              ?SRC_onj  rdf:first ?s_prop .
              ?trg_onj  rdf:first ?o_prop .
              }
              union {
              ?SRC_onj  rdf:rest/rdf:first ?s_prop .
              ?trg_onj  rdf:rest/rdf:first ?o_prop .
              }
              bind ('False' as ?crossCheck)
              """

    query = """
        ################################################################
        PREFIX ll:    <{}>
        PREFIX prov:  <{}>
        PREFIX void:  <{}>

        ### LINKSET ALIGNED PROPERTIES

        SELECT DISTINCT ?s_prop ?o_prop (GROUP_CONCAT(DISTINCT ?mechanism; SEPARATOR=" | ") as ?mec)
        ?s_dataset ?o_dataset ?crossCheck

        {{
            ### RETRIEVING LINKSET METADATA
            <{}>
                (prov:wasDerivedFrom/void:target)*/prov:wasDerivedFrom*        ?linkset .

            ?linkset
                #ll:alignsSubjects     ?s_prop ;
                #ll:alignsObjects      ?o_prop ;
                ll:alignsMechanism    ?mechanism ;
                void:subjectsTarget   ?s_dataset ;
                void:objectsTarget    ?o_dataset .

            {{
                ?linkset ll:alignsSubjects ?s_prop ;
                        ll:alignsObjects ?o_prop .
                #?graph   ll:alignsSubjects ?s_property.
                filter not exists {{?linkset ll:alignsSubjects/rdf:rest ?r}}
                filter not exists {{?linkset ll:alignsObjects/rdf:rest ?r}}
                bind ('False' as ?crossCheck)
            }}
            union
            {{
              # choices for aligns or crossCheck
              {}
            }}

          filter (isBlank(?o_prop) = "FALSE"^^xsd:boolean).
          filter (isBlank(?s_prop) = "FALSE"^^xsd:boolean).

        }}
        group by ?s_prop ?o_prop ?s_dataset ?o_dataset ?crossCheck
    """.format(Ns.alivocab, Ns.prov, Ns.void, linkset_uri, prop_aligns)
    print query
    return query


def linkset_cluster_aligns_prop(linkset_uri, prop_aligns):

    query = """
    ################################################################
    PREFIX ll:    <{}>
    PREFIX prov:  <{}>
    PREFIX void:  <{}>
    ### LINKSET ALIGNED PROPERTIES

    SELECT DISTINCT ?dataset ?datatype (GROUP_CONCAT(DISTINCT ?property; SEPARATOR=" | ") as ?properties)
    {{
        ### RETRIEVING LINKSET METADATA
        <{}>
            (prov:wasDerivedFrom/void:target)*/prov:wasDerivedFrom*        ?linkset .

        ?linkset	ll:hasAlignmentTarget  ?target .
        ?target
            ll:hasTarget  		?dataset ;
            ll:hasDatatype   	?datatype ;
            ll:aligns		    ?property .
    }}
    group by ?dataset ?datatype
    """.format(Ns.alivocab, Ns.prov, Ns.void, linkset_uri, prop_aligns)
    print query
    return query


def linkset_aligns_prop_old(linkset_uri):
    query = """
        ################################################################
        PREFIX ll:    <{}>
        PREFIX prov:  <{}>
        PREFIX void:  <{}>

        ### LINKSET ALIGNED PROPERTIES

        SELECT DISTINCT ?s_prop ?o_prop (GROUP_CONCAT(DISTINCT ?mechanism; SEPARATOR=" | ") as ?mec)
        ?s_dataset ?o_dataset

        {{
            ### RETRIEVING LINKSET METADATA
            <{}>
                (prov:wasDerivedFrom/void:target)*/prov:wasDerivedFrom*        ?linkset .

            ?linkset
                ll:alignsSubjects     ?s_prop ;
                ll:alignsObjects      ?o_prop ;
                ll:alignsMechanism    ?mechanism ;
                void:subjectsTarget   ?s_dataset ;
                void:objectsTarget    ?o_dataset .
        }}
        group by ?s_prop ?o_prop ?s_dataset ?o_dataset
    """.format(Ns.alivocab, Ns.prov, Ns.void, linkset_uri)
    print query
    return query


def properties(named_graph_uri, display=False):

    query = """
    ####################################################################################
    ### NAMED GRAPHS PROPERTIES                                                      ###
    ####################################################################################
    prefix rdf: <{}>
    SELECT DISTINCT ?properties
    {{
        GRAPH <{}>
        {{
            ?subject        ?properties     ?object .
        }}
    }}
    ####################################################################################
    """.format(Ns.rdf, named_graph_uri)
    if display is True:
        print query
    return query


def q_copy_graph(insert_linkset, insert_singleton_graph, where_linkset):

    # LINKSET METADATA
    insert_linkset_query = """
    ###### MOVE THIS LINKSET TO A NEW UNION LINKSET GRAPH
    INSERT
    {{
        GRAPH <{}>
        {{
            ?subject ?predicate	?object .
        }}
    }}
    WHERE
    {{
        GRAPH <{}>
        {{
            ?subject ?predicate	?object .
        }}
    }}""".format(insert_linkset, where_linkset)

    # SINGLETON METADATA
    singleton_graph = linkset_singleton_graph(where_linkset)
    if (singleton_graph[St.result] is None) or (len(singleton_graph[St.result]) == 0):
        return insert_linkset_query

    else:
        # exit(0)
        insert_singleton_query = """
    ###### MOVE THE SINGLETON METADATA GRAPH TO A NEW UNION SINGLETON GRAPH
    PREFIX ll:<{2}>
    INSERT
    {{
        GRAPH <{0}>
        {{
            ?subject        ?predicate	                ?object .
            ?validation     ?vPred                      ?vObj .
            ?rQuestion      ll:created                  ?validation .
        }}
    }}
    WHERE
    {{
        GRAPH <{1}>
        {{
            ?subject ?predicate	?object .
            OPTIONAL
            {{
               ?subject		    ll:hasValidation 			?validation .
               ?validation      ?vPred                      ?vObj .
               ?rQuestion       ll:created                  ?validation .
            }}
        }}
    }}""".format(insert_singleton_graph, singleton_graph[St.result][1][0], Ns.alivocab)

        result = "{} ; \n{}".format(insert_linkset_query, insert_singleton_query)
        return result


def fromdatabasea_insertindatabaseb(predicate, datagraph, linkset_graph):

    query = """
    CONSTRUCT
    {{
        ?subject   <{}>  ?object .
    }}
    WHERE
    {{
        GRAPH <{}>
        {{
            ?subject <{}>  ?object .
        }}
    }} limit 10
    """.format(predicate, datagraph, predicate)

    print query

    data = endpointconstruct(query)

    insert = """
    INSERT DATA
    {{
        GRAPH <{}>
        {}
    }}
    """.format(linkset_graph, data)

    print insert


def graph_type(graph):
    query = """
    ### GET TYPE
    SELECT DISTINCT ?type
    {{
      # GRAPH TYPE
      <{}>
                a    ?type .
    }}""".format(graph)
    # print query
    return query


#######################################################################################
# ENRICH QUERY
#######################################################################################


def q_admin_level_enrich(level, graph_to_align_with, enriched_graph, d_type):
    query = """
        ######################################################################
        # Enriched dataset WITH GADM - adminLevel - OrgCount per adminLevel
        ######################################################################
        prefix etevocab: <http://risis.eu/eter/ontology/predicate/>
        prefix grivocab: <http://risis.eu/grid/ontology/predicate/>
        prefix gadvocab: <http://risis.eu/gadm/ontology/predicate/>
        prefix tmpgraph: <{0}>
        prefix tmpvocab: <{1}>
        prefix alivocab: <{2}>
        prefix dataset:  <{3}>

        ### DROP datasets in case there already exist
        DROP SILENT GRAPH tmpgraph:load ;
        DROP SILENT GRAPH <{6}>;

        ###########################################################
        ### TEMPORARILY LOAD
        ###########################################################
        ### INSERT in tmpgraph:load the number of organisations per administrative level in GRID
        INSERT
        {{
            ### TEMPORARILY, SAVE THE THE NUMBER OF ORGANISATIONS IN A BOUNDARY
            ### INFORMATION EXTRACTED FROM THE ENRICHED GRID DATASET BASED ON GADM
            GRAPH tmpgraph:load
            {{
                ?adminLevel
                    tmpvocab:code 	?level ;
                    tmpvocab:count 	?nbrOrg .
            }}
        }}
        WHERE
        {{
          {{
            ### COUNT THE NUMBER OF ORGANISATIONS IN A BOUNDARY
            select  ?level  (count(distinct ?grid) as ?nbrOrg)
            {{
                graph dataset:gridGADMEnriched
                {{
                    ?grid
                        gadvocab:level_{4}	?level
                }}
            }} GROUP BY ?level
          }}
          BIND( UUID() as ?adminLevel)
        }} ;

        ###########################################################
        ### CREATE THE ACTUAL ENRICHED DATASET
        ###########################################################
        ### INSERT in dataset:eter_orgCountPerAdminLevelInGrid an enrichment of ETER with
        ### GADM admin levels and the number of organisation in the same region according to GRID
        INSERT
        {{
            ### CREATE A NEW DATASET, THAT IS AN ENRICHED SUBSET OF ETER. IN THIS SUBSET, WE HAVE
            ### DATA DESCRIBING ENTITIES WITHIN ETER THAT ARE IN A CERTAIN BOUNDARY AND THE NUMBER OF
            ### WORLD WIDE ORGANISATIONS IN THAT BOUNDARY ACCORDING TO GRID
            ### E.G: dataset:eter_orgCountPerAdminLevelInGrid
            GRAPH <{6}>
            {{
                ?eter
                    a                       <{7}> ;
                    tmpvocab:isIn 			?adminLevel .

                ?adminLevel
                    tmpvocab:hasCode 		?level ;
                    tmpvocab:hasOrgCount 	?nbrOrg .
            }}
        }}
        ### ALIGN WITH ADMIN LEVEL
        where
        {{
            ### LOAD DATASET ENRICHED WITH ADMIN LEVEL. E.G: dataset:EterGADMEnriched
            GRAPH <{5}>
            {{
                ?eter
                    gadvocab:level_{4}		?level .
            }}

            ### LOAD COUNT EXTRACTED FROM dataset:gridGADMEnriched
            GRAPH tmpgraph:load
            {{
                ?adminLevel
                    tmpvocab:code			?level ;
                    tmpvocab:count 			?nbrOrg .
            }}
        }} ;

        ### DROP the tmpgraph:load graph
        DROP SILENT GRAPH tmpgraph:load""".format(Ns.tmpgraph, Ns.tmpvocab, Ns.alivocab, Ns.dataset,
                                                  level, graph_to_align_with, enriched_graph, d_type)
    return query


def enrich_with_admin_level(graph_to_align_with, enriched_graph, d_type, level=2, display=False, activated=False):

    if str(graph_to_align_with).__contains__('<') or (str(graph_to_align_with) is None):
        logger.warning("ORIGIN: {}".format(graph_to_align_with))
        logger.warning("THE GRAPH NAME SHOULD NOT BE NULL, OR SHOULD CONTAIN NEITHER OF THE CHARACTERS '<' AND '>.")
        logger.warning("AS A DOMINO EFFECT, WE COULD NOT EXECUTE THE ACTION.")
        return

    if str(enriched_graph).__contains__('<') or (str(enriched_graph) is None):
        logger.warning("ORIGIN: {}".format(enriched_graph))
        logger.warning("THE GRAPH NAME SHOULD NOT BE NULL, OR SHOULD CONTAIN NEITHER OF THE CHARACTERS '<' AND '>.")
        logger.warning("AS A DOMINO EFFECT, WE COULD NOT EXECUTE THE ACTION.")
        return

    query = q_admin_level_enrich(level, graph_to_align_with, enriched_graph, d_type)

    if display is True:
        print query

    if activated is True:
        boolean_endpoint_response(query)


def countries_geodata(level=2, display=False, activated=False):

    """
    :return:
    """
    prefix = """
    PREFIX geoEntity: <http://risis.eu/CountriesGeoData/ontology/class/>
    PREFIX gadmEntity: <http://risis.eu/gadm/ontology/class/>
    PREFIX osmEntity: <http://risis.eu/osm/ontology/class/>
    PREFIX geovocab: <http://risis.eu/CountriesGeoData/ontology/predicate/>
    PREFIX gadmvocab: <http://risis.eu/gadm/ontology/predicate/>
    PREFIX osmvocab: <http://risis.eu/osm/ontology/predicate/>
    PREFIX datasetGraph: <{}>
    PREFIX tempGraph: <{}>
    PREFIX gadm: <http://geo.risis.eu/vocabulary/gadm/>
    PREFIX osm: <http://geo.risis.eu/vocabulary/osm/>
    PREFIX pre: <{}>
    PREFIX resource: <http://risis.eu/CountriesGeoData/resource/>""".format(Ns.dataset, Ns.tmpgraph, Ns.tmpvocab)

    drop = """
    DROP SILENT GRAPH datasetGraph:CountriesGeoData ;
    DROP SILENT GRAPH tempGraph:gadm ;
    DROP SILENT GRAPH tempGraph:osm"""

    gadm_temp = """
    ##########################################################
    ### 1. Temporarily GADM in tempGraph:gadm
    ### Extracting properties of interest from GADM
    ### GADM has both ISO2 & ISO2
    # #########################################################
    INSERT
    {
        GRAPH tempGraph:gadm
        {
            ?gadm
                pre:1                   ?uri ;
                gadmvocab:gadmID        ?gadmID ;
                gadmvocab:iso3          ?iso3 ;
                gadmvocab:iso2          ?iso2 ;
                gadmvocab:ison          ?ison ;
                gadmvocab:developing    ?dvpmt ;
                gadmvocab:fips          ?fips ;
                gadmvocab:localName     ?localName ;
                gadmvocab:sqkm          ?sqkm ;
                gadmvocab:pop2000       ?pop2000 ;
                gadmvocab:popskm        ?popsqkm .
        }
    }
    WHERE
    {
        SERVICE <http://sparql.sms.risis.eu/>
        {
            GRAPH <http://geo.risis.eu/gadm>
            {
                ?gadm
                    a               ?type ;
                    gadm:ID_0       ?gadmID ;
                    gadm:ISO        ?iso3 ;
                    gadm:ISO2       ?iso2 ;
                    gadm:ISON       ?ison .
                OPTIONAL { ?gadm    gadm:DEVELOPING  ?dvpmt .}
                OPTIONAL { ?gadm    gadm:FIPS        ?fips .}
                OPTIONAL { ?gadm    gadm:NAME_LOCAL  ?localName .}
                OPTIONAL { ?gadm    gadm:SQKM        ?sqkm .}
                OPTIONAL { ?gadm    gadm:POP2000     ?pop2000 .}
                OPTIONAL { ?gadm    gadm:POPSQKM     ?popsqkm .}
                BIND (concat("http://risis.eu/CountriesGeoData/resource/", ?iso2) as ?uri)
            }
        }
    }"""

    osm_temp_1 = """
    ##########################################################
    ### 2. Temporarily OSM in tempGraph:osm
    ### Extracting properties of interest from OSM .
    ### Also, we specially take admin levels from OSM .
    ### OSM is described with only ISO3
    ##########################################################
    INSERT
    {{
        GRAPH tempGraph:osm
        {{
            ?osm
                osmvocab:level      {0} ;
                osmvocab:iso3       ?iso3 ;
                osmvocab:osmID      ?osmID ;
                osmvocab:dbpedia    ?dbpedia ;
                osmvocab:wikidata   ?wikidata ;
                osmvocab:oldName    ?oldName .
        }}
    }}
    WHERE
    {{
        SERVICE <http://sparql.sms.risis.eu/>
        {{
            GRAPH <http://geo.risis.eu/osm>
            {{
                ?osm
                    osm:level       {0} ;
                    osm:ISO         ?iso3 .
                OPTIONAL {{ ?osm     osm:dbpedia     ?dbpedia . }}
                OPTIONAL {{ ?osm     osm:wikidata    ?wikidata . }}
                OPTIONAL {{ ?osm     osm:oldName     ?oldName . }}
                BIND( strafter(str(?osm), "_") as ?osmID )
            }}
        }}
    }}""".format(level)

    osm_temp_2 = """
    ##########################################################
    ### 3. Aligning OSM & GADM BY ISO3 in tempGraph:osm
    ### The trick here is to INTEGRATE GADM & OSM using ISO3
    ### and enrich OSM with ISO2 data from GADM
    ### insert Insert data from
    ### <http://sparql.sms.risis.eu/>.<http://geo.risis.eu/gadm> into OSM-graph
    ##########################################################
    INSERT
    {
        GRAPH tempGraph:osm
        {
            ?gadm
                pre:1           ?uri ;
                gadmvocab:iso3  ?iso3;
                gadmvocab:iso2  ?iso2 .
        }
    }
    WHERE
    {
        SERVICE <http://sparql.sms.risis.eu/>
        {
            GRAPH <http://geo.risis.eu/gadm>
            {
                ?gadm
                    a           ?type ;
                    gadm:ISO    ?iso3 ;
                    gadm:ISO2   ?iso2 .
                BIND ( concat("http://risis.eu/CountriesGeoData/resource/", ?iso2) as ?uri )
            }
        }
    }"""

    align = """
    ############################################################
    ### 4. Align GADM in permanently in dataset:CountriesGeoData
    ### Reconstruct GADM using the ISO2 country code, e.g.,
    ### http://risis.eu/CountriesGeoData/resource/AD
    ############################################################
    INSERT
    {{
        GRAPH datasetGraph:CountriesGeoData
        {{
            ?iso2_iri
                a                       gadmEntity:Country ;
                gadmvocab:gadmID        ?gadmID ;
                gadmvocab:iso3          ?iso3 ;
                gadmvocab:iso2          ?iso2 ;
                gadmvocab:ison          ?ison ;
                gadmvocab:developing    ?dvpmt ;
                gadmvocab:fips          ?fips ;
                gadmvocab:localName     ?localName ;
                gadmvocab:sqkm          ?sqkm ;
                gadmvocab:pop2000       ?pop2000 ;
                gadmvocab:popskm        ?popsqkm .
        }}
    }}
    where
    {{
        graph tempGraph:gadm
        {{
            ?gadm
                pre:1                ?iso2_uri ;
                gadmvocab:gadmID     ?gadmID ;
                gadmvocab:iso3       ?iso3;
                gadmvocab:iso2       ?iso2;
                gadmvocab:ison       ?ison .
            OPTIONAL{{ ?gadm         gadmvocab:developing        ?dvpmt .}}
            OPTIONAL{{ ?gadm         gadmvocab:fips              ?fips. }}
            OPTIONAL{{ ?gadm         gadmvocab:localName         ?localName .}}
            OPTIONAL{{ ?gadm         gadmvocab:sqkm              ?sqkm .}}
            OPTIONAL{{ ?gadm         gadmvocab:pop2000           ?pop2000 .}}
            OPTIONAL{{ ?gadm         gadmvocab:popskm            ?popsqkm .}}
            bind( IRI(?iso2_uri) as ?iso2_iri )
        }}
    }} ;

    ### Drop tempGraph:gadm
    DROP GRAPH tempGraph:gadm ;

    ### Reconstruct OSM on the basis that they share the same ISO3
    ### country code but create the resource using ISO2 country code
    ### e.g., http://risis.eu/CountriesGeoData/resource/AE
    INSERT
    {{
        GRAPH datasetGraph:CountriesGeoData
        {{
            ?iso2_iri
                a                   osmEntity:Country;
                osmvocab:level      {};
                osmvocab:iso3       ?iso3;
                osmvocab:osmID      ?osmID;
                osmvocab:dbpedia    ?dbpedia;
                osmvocab:wikidata   ?wikidata;
                osmvocab:oldName    ?oldName .
        }}
    }}

    WHERE
    {{
        GRAPH tempGraph:osm
        {{
            ?gadm
                pre:1               ?iso2_uri;
                gadmvocab:iso3      ?iso3;
                gadmvocab:iso2      ?iso2 .

            ?osm
                osmvocab:iso3   ?iso3 .

            OPTIONAL {{ ?osm         osmvocab:dbpedia    ?dbpedia . }}
            OPTIONAL {{ ?osm         osmvocab:wikidata   ?wikidata . }}
            OPTIONAL {{ ?osm         osmvocab:oldName    ?oldName . }}
            BIND( strafter(str(?osm), "_") as ?osmID )
            BIND( IRI(?iso2_uri) as ?iso2_iri )

        }}
    }} ;

    ### Drop tempGraph:osm
    DROP GRAPH tempGraph:osm
    """ .format(level)

    query = "{}\n{} ;\n{} ;\n{} ;\n{} ;\n{}".\
        format(prefix, drop, gadm_temp, osm_temp_1, osm_temp_2, align)

    if display is True:
        print query

    if activated is True:
        endpoint(query)


# enrich_with_admin_level(graph_to_align_with="http://risis.eu/dataset/EterGADMEnriched",
#                         enriched_graph="http://risis.eu/dataset/eter_orgCountPerAdminLevelInGrid",
#                         d_type="http://risis.eu/eter/ontology/class/University",
#                         database_name="risis", host="localhost:5820", level=2, display=True, activated=False)


def virtuoso_request(query):

    """
        param query         : The query that is to be run against the SPARQL endpoint
        param database_name : The name of the database () in with the named-graph resides
        param host          : the host (server) name
        return              : returns the result of the query in the default format of the endpoint.
                            In the case of STARDOG, the sever returns an XML result.
    """

    q = to_bytes(query)
    # print query
    # Content-Type: application/json
    # b"Accept": b"text/json"
    # 'output': 'application/sparql-results+json'
    # url = b"http://{}:{}/annex/{}/sparql/query?".format("localhost", "5820", "linkset")
    # headers = {b"Content-Type": b"application/x-www-form-urlencoded",
    #            b"Authorization": b"Basic YWRtaW46YWRtaW5UMzE0YQ=="}

    url = b"http://sparql.sms.risis.eu/?"
    # print url
    params = urllib.urlencode(
        {b'query': q, b'default-graph-uri': '', b'format': b'text/turtle',
         b'timeout': b'0', b'debug': b'on', b'should-sponge': b''})
    headers = {b"Content-Type": b"application/x-www-form-urlencoded"}

    """
        Authentication
    """
    user = Svr.settings[St.stardog_user]
    password = Svr.settings[St.stardog_pass]
    # password = "admin"
    passman = urllib2.HTTPPasswordMgrWithDefaultRealm()
    passman.add_password(None, url, user, password)
    urllib2.install_opener(urllib2.build_opener(urllib2.HTTPBasicAuthHandler(passman)))
    request = urllib2.Request(url, data=params, headers=headers)
    request.get_method = lambda: "POST"

    try:
        response = urllib2.urlopen(request)
        # print "RESPONSE CODE:", response.code
        result = response.read()
        # print result
        # print "NONE", result is None
        # print "EMPTY", len(result)
        return {St.message: "OK", St.result: result, "response_code": response.code}

    except urllib2.HTTPError, err:
        message = err.read()
        if len(message) == 0:
            message = str(err)
        print "\nERROR CODE {}: {}\nUSING THIS QUERY BELOW\n{}".format(err.code, message, query)
        return {St.message: message, St.result: None}

    except Exception as err:

        if str(err).__contains__("No connection") is True:
            # logger.warning(err)
            # print ERROR
            return {St.message: ERROR, St.result: None}

        elif str(err.message).__contains__("timeout") is True:
            print "Query execution cancelled: Execution time exceeded query timeout"
            return {St.message: "Query execution cancelled: Execution time exceeded query timeout.",
                    St.result: None}

        logger.warning(err)
        message = "\nOR MAYBE THERE IS AN ERROR IN THIS QUERY"
        print message + "\n" + query
        return {St.message: err, St.result: None}


def remote_endpoint_request(query, endpoint_url):

    """
        param query         : The query that is to be run against the SPARQL endpoint
        param database_name : The name of the database () in with the named-graph resides
        param host          : the host (server) name
        return              : returns the result of the query in the default format of the endpoint.
                            In the case of STARDOG, the sever returns an XML result.
    """

    q = to_bytes(query)
    url = endpoint_url
    params = urllib.urlencode(
        {b'query': q, b'default-graph-uri': '', b'format': b'text/turtle',
         b'timeout': b'0', b'debug': b'on', b'should-sponge': b''})
    headers = {b"Content-Type": b"application/x-www-form-urlencoded"}

    """
        Authentication
    """
    user = Svr.settings[St.stardog_user]
    password = Svr.settings[St.stardog_pass]
    passman = urllib2.HTTPPasswordMgrWithDefaultRealm()
    passman.add_password(None, url, user, password)
    urllib2.install_opener(urllib2.build_opener(urllib2.HTTPBasicAuthHandler(passman)))
    request = urllib2.Request(url, data=params, headers=headers)
    request.get_method = lambda: "POST"

    try:
        response = urllib2.urlopen(request)
        result = response.read()
        return {St.message: "OK", St.result: result, "response_code": response.code}

    except urllib2.HTTPError, err:
        message = err.read()
        if len(message) == 0:
            message = str(err)
        print "\nERROR CODE {}: {}\nUSING THIS QUERY BELOW\n{}".format(err.code, message, query)
        return {St.message: message, St.result: None}

    except Exception as err:

        if str(err).__contains__("No connection") is True:
            return {St.message: ERROR, St.result: None}

        elif str(err.message).__contains__("timeout") is True:
            print "Query execution cancelled: Execution time exceeded query timeout"
            return {St.message: "Query execution cancelled: Execution time exceeded query timeout.",
                    St.result: None}

        logger.warning(err)
        message = "\nOR MAYBE THERE IS AN ERROR IN THIS QUERY"
        print message + "\n" + query
        return {St.message: err, St.result: None}


def remote_stardog(query, endpoints, user, password):

    """
        param query         : The query that is to be run against the SPARQL endpoint
        param database_name : The name of the database () in with the named-graph resides
        param host          : the host (server) name
        return              : returns the result of the query in the default format of the endpoint.
                            In the case of STARDOG, the sever returns an XML result.
    """
    url = endpoints
    params = urllib.urlencode(
        {b'query':  to_bytes(query), b'format': b'application/sparql-results+json',
         b'timeout': b'0', b'debug': b'on', b'should-sponge': b''})
    headers = {b"Content-Type": b"application/x-www-form-urlencoded"}

    """
        Authentication
    """
    passman = urllib2.HTTPPasswordMgrWithDefaultRealm()
    passman.add_password(None, url, user, password)
    urllib2.install_opener(urllib2.build_opener(urllib2.HTTPBasicAuthHandler(passman)))
    request = urllib2.Request(url, data=params, headers=headers)
    request.get_method = lambda: "POST"
    try:
        response = urllib2.urlopen(request)
        result = response.read()
        return {St.message: "OK", St.result: result}

    except urllib2.HTTPError, err:
        message = err.read()
        if len(message) == 0:
            message = err
        print "USING THIS QUERY {}\nERROR CODE {}: {}".format(query, err.code, message)
        return {St.message: message, St.result: None}

    except Exception as err:

        if str(err).__contains__("No connection") is True:
            return {St.message: ERROR, St.result: None}

        elif str(err.message).__contains__("timeout") is True:
            print "Query execution cancelled: Execution time exceeded query timeout"
            return {St.message: "Query execution cancelled: Execution time exceeded query timeout.",
                    St.result: None}

        logger.warning(err)
        message = "\nOR MAYBE THERE IS AN ERROR IN THIS QUERY"
        print message + "\n" + query
        return {St.message: err, St.result: None}

