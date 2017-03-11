from flask import render_template, g, request, jsonify, make_response
from SPARQLWrapper import SPARQLWrapper
import logging
import requests
import json
from app import app
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)
handler = logging.StreamHandler()
logger.addHandler(handler)
import xmltodict
import collections
from kitchen.text.converters import to_bytes
import urllib2
import urllib
import uuid
import pprint
# local
import Queries as Qry


ENDPOINT_URL = 'http://localhost:5820/risis/query'
UPDATE_URL = 'http://localhost:5820/risis/update'
database = "risis"
host = "localhost:5820"

REASONING_TYPE = 'SL'

# log = app.logger
# log.setLevel(logging.DEBUG)

### This is old style, but leaving for backwards compatibility with earlier versions of Stardog
QUERY_HEADERS = {
                    'Accept': 'application/sparql-results+json',
                    'SD-Connection-String': 'reasoning={}'.format(REASONING_TYPE)
                }

UPDATE_HEADERS = {
                    'Content-Type': 'application/sparql-update',
                    'SD-Connection-String': 'reasoning={}'.format(REASONING_TYPE)
                 }

PREFIXES =  """

    PREFIX bdb: <http://vocabularies.bridgedb.org/ops#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX linkset: <http://risis.eu/linkset/>
    PREFIX void: <http://rdfs.org/ns/void#>
    PREFIX alivocab: <http://risis.eu/alignment/predicate/>
    PREFIX tmpgraph: <http://risis.eu/alignment/temp-match/> """

@app.route('/print', methods=['GET'])
def prints():
    msg = request.args.get('msg', '')
    print "\n\n\n"
    print msg
    return msg


@app.route("/")
def index():
    return render_template('base.html')


@app.route('/getgraphs')
def graphs():
    """
    This function is called due to request /getgraphs
    It queries the dataset for both linksets and lenses
    The results, two lists of uris and labels,
        are passed as parameters to the template graphs_list.html
    """

    query = PREFIXES + """
    SELECT DISTINCT ?g ?g_label ?subjectTargetURI ?subjectTarget
                    ?objectTargetURI ?objectTarget ?triples
                    ?alignsSubjects ?alignsObjects ?alignsMechanism
    WHERE
    {
		?g
		    rdf:type	 void:Linkset ;
            <http://rdfs.org/ns/void#subjectsTarget> ?subjectTargetURI;
            <http://rdfs.org/ns/void#objectsTarget> ?objectTargetURI;
            <http://rdfs.org/ns/void#triples> ?triples;
            <http://risis.eu/alignment/predicate/alignsSubjects> ?alignsSubjects;
            <http://risis.eu/alignment/predicate/alignsObjects> ?alignsObjects;
            <http://risis.eu/alignment/predicate/alignsMechanism> ?alignsMechanism.

        FILTER regex(str(?g), 'linkset', 'i')
        BIND(strafter(str(?g),'linkset/') AS ?g_label)
        BIND(UCASE(strafter(str(?subjectTargetURI),'dataset/')) AS ?subjectTarget)
        BIND(UCASE(strafter(str(?objectTargetURI),'dataset/')) AS ?objectTarget)
    }
    """
    linksets = sparql(query, strip=True)

    query2 = PREFIXES + """
        SELECT DISTINCT ?g ?g_label ?triples ?operator
        WHERE
        {
            ?g
                rdf:type	        bdb:Lens ;
                alivocab:operator   ?operator ;
                void:triples        ?triples .

            BIND(strafter(str(?g),'lens/') AS ?g_label)
        }
        """

    lenses = sparql(query2, strip=True)

    return render_template('graphs_list.html',linksets = linksets, lenses = lenses)


@app.route('/getcorrespondences', methods=['GET'])
def correspondences():
    """
    This function is called due to request /getcorrespondences
    It queries the dataset for both all the correspondences in a certain graph URI
    Expected Input: uri, label (for the graph)
    The results, ...,
        are passed as parameters to the template correspondences_list.html
    """
    graph_menu = request.args.get('graph_menu', '')
    graph_uri = request.args.get('uri', '')
    graph_label = request.args.get('label','')
    graph_triples = request.args.get('graph_triples','')
    alignsMechanism = request.args.get('alignsMechanism', '')
    operator = request.args.get('operator', '')

    query = Qry.get_correspondences(graph_uri)
    correspondences = sparql(query, strip=True)

    return render_template('correspondences_list.html',
                            operator = operator,
                            graph_menu = graph_menu,
                            correspondences = correspondences,
                            graph_label = graph_label,
                            graph_triples = graph_triples,
                            alignsMechanism = alignsMechanism)


### CHANGE THE NAME TO -DETAILS-
@app.route('/getdetails', methods=['GET'])
def details():
    """
    This function is called due to request /getdetails
    It queries the dataset for both all the correspondences in a certain graph URI
    Expected Input: uri, label (for the graph)
    The results, ...,
        are passed as parameters to the template correspondences_list.html
    """

    # singleton_uri = request.args.get('uri', '')

    sub_uri = request.args.get('sub_uri', '')
    obj_uri = request.args.get('obj_uri', '')
    subjectTarget = request.args.get('subjectTarget', '')
    objectTarget = request.args.get('objectTarget', '')
    alignsSubjects = request.args.get('alignsSubjects', '')
    alignsObjects = request.args.get('alignsObjects', '')

    query = PREFIXES + """
    select distinct *
    {
        graph ?gsource
        { <""" + sub_uri + """> <""" + alignsSubjects + """> ?srcPredValue }

        graph ?gtarget
        { <""" + obj_uri + """> <""" + alignsObjects + """> ?trgPredValue }
    }
    """
    details = sparql(query, strip=True)

    return render_template('details_list.html',
                            details = details,
                            # pred_uri = singleton_uri,
                            sub_uri = sub_uri,
                            obj_uri = obj_uri,
                            subjectTarget = subjectTarget,
                            objectTarget = objectTarget,
                            alignsSubjects = alignsSubjects,
                            alignsObjects = alignsObjects)


### CHANGE THE NAME TO -DETAILS-
@app.route('/getLensDetail', methods=['GET'])
def detailsLens():
    """
    This function is called due to request /getdetails
    It queries the dataset for both all the correspondences in a certain graph URI
    Expected Input: uri, label (for the graph)
    The results, ...,
        are passed as parameters to the template correspondences_list.html
    """

    singleton_uri = request.args.get('uri', '')
    sub_uri = request.args.get('sub_uri', '')
    obj_uri = request.args.get('obj_uri', '')
    subjectTarget = request.args.get('subjectTarget', '')
    objectTarget = request.args.get('objectTarget', '')
    alignsSubjects = request.args.get('alignsSubjects', '')
    alignsObjects = request.args.get('alignsObjects', '')

    evi_query = Qry.get_evidences(singleton_uri, "tmpgraph:wasDerivedFrom")
    evi_matrix = sparql_xml_to_matrix(evi_query)
    det_query = Qry.get_target_datasets(evi_matrix)
    # print det_query
    details = sparql(det_query, strip=True)
    # print details

    return render_template('lensDetails_list.html',
                           detailHeadings = details,
                            # pred_uri = singleton_uri,
                            sub_uri = sub_uri,
                            obj_uri = obj_uri,
                            subjectTarget = subjectTarget,
                            objectTarget = objectTarget,
                            alignsSubjects = alignsSubjects,
                            alignsObjects = alignsObjects)


### CHANGE THE NAME TO -DETAILS-
@app.route('/getdatadetails', methods=['GET'])
def dataDetails():
    """
    This function is called due to request /getdatadetails
    It queries the dataset for both all the correspondences in a certain graph URI
    Expected Input: uri, label (for the graph)
    The results, ...,
        are passed as parameters to the template correspondences_list.html
    """

    resource_uri = request.args.get('resource_uri', '')
    dataset_uri = request.args.get('dataset_uri', '')

    query = PREFIXES + """
    select distinct *
    {
        graph <""" + dataset_uri + """>
        { <""" + resource_uri + """> ?pred ?obj }
    }
    """
    dataDetails = sparql(query, strip=True)


    return render_template('datadetails_list.html',
                            dataDetails = dataDetails)


@app.route('/getevidence', methods=['GET'])
def evidence():
    """
    This function is called due to request /getevidence
    It queries the dataset for ...
    The results, ...,
        are passed as parameters to the template evidence_list.html
    """

    singleton_uri = request.args.get('singleton_uri', '')
    # print singleton_uri
    # evi_query = Qry.get_evidences(singleton_uri, "tmpgraph:wasDerivedFrom")
    # evi_matrix = sparql_xml_to_matrix(evi_query)
    # det_query = Qry.get_target_datasets(evi_matrix)
    # print det_query
    # detail_mat = sparql(det_query, strip=True)
    # print detail_mat
    #
    query = Qry.get_evidences(singleton_uri, predicate=None)
    evidences = sparql(query, strip=True)


    query = PREFIXES + """
    Select distinct ?nGood ?nBad ?nStrength
    {
    	{
         Select (count(?accepted) AS ?nGood)
         {
          GRAPH ?graph
      	   { <""" + singleton_uri + """> <http://example.com/predicate/good> ?accepted
           }
         }
        }

    	{
         Select (count(?rejected) AS ?nBad)
         {
          GRAPH ?graph
      	   { <""" + singleton_uri + """> <http://example.com/predicate/bad> ?rejected
           }
         }
        }

        {
         Select (count(?derivedFrom) AS ?nStrength)
         {
          GRAPH ?graph
      	   { <""" + singleton_uri + """> tmpgraph:wasDerivedFrom ?derivedFrom
           }
         }
        }
    }
    """
    validation_counts = sparql(query, strip=True)


    return render_template('evidence_list.html',
                            singleton_uri = singleton_uri,
                            evidences = evidences,
                            validation_counts = validation_counts)


@app.route('/updateevidence', methods=['GET'])
def updateEvidence():
    """
    This function is called due to request /updateevidence
    It updates a singleton property resource with the validation info.
    The results, ...,
    """

    singleton_uri = request.args.get('singleton_uri', '')
    predicate = request.args.get('predicate', '')
    validation_text = request.args.get('validation_text', '')

    query = PREFIXES + """
    INSERT
    {	GRAPH ?g
    	{<""" + singleton_uri + """> <""" + predicate + """> \"\"\"""" + validation_text + """\"\"\"}
    }
    WHERE
    {
      GRAPH ?g
      {<""" + singleton_uri + """> ?p ?o}
    }
    """
    print query

    result = sparql_update(query)
    print result
    return result
    #render_template('evidence_list.html',
    #                        singleton_uri = singleton_uri,
    #                        evidences = evidences)


def sparql_update(query, endpoint_url = UPDATE_URL):

    # log.debug(query)

    result = requests.post(endpoint_url,
        params={'reasoning': REASONING_TYPE}, data=query, headers=UPDATE_HEADERS)

    return result.content


def sparql(query, strip=False, endpoint_url = ENDPOINT_URL):
    """This method replaces the SPARQLWrapper SPARQL interface, since SPARQLWrapper
    cannot handle the Stardog-style query headers needed for inferencing"""

    result = requests.get(endpoint_url,
        params={'query': query, 'reasoning': REASONING_TYPE}, headers=QUERY_HEADERS)
    try :
        result_dict = json.loads(result.content)
    except Exception as e:
        return result.content

    if strip:
        new_results = []
        for r in result_dict['results']['bindings']:
            new_result = {}
            for k, v in r.items():
                # print k, v
                if v['type'] == 'uri' and not k+'_label' in r.keys():
                    new_result[k+'_label'] = {}
                    new_result[k+'_label']['type'] = 'literal'
                    new_result[k+'_label']['value'] = v['value'][v['value'].rfind('/')+1:]

                elif not k+'_label' in r.keys():
                    new_result[k+'_label'] = {}
                    new_result[k+'_label']['type'] = 'literal'
                    new_result[k+'_label']['value'] = v['value']

                new_result[k+'_stripped'] = {}
                new_result[k+'_stripped']['type'] = 'literal'
                new_result[k+'_stripped']['value'] = v['value'][v['value'].rfind('/')+1:]

                new_result[k] = v

            new_results.append(new_result)

        # log.debug(new_results)
        return new_results
    else :
        return result_dict['results']['bindings']


def sparql_xml_to_matrix(query):

    name_index = dict()

    if type(query) is not str:
        logger.warning("THE QUERY NEEDS TO BE OF TYPE STRING.")
        # logger.warning(query)
        return

    if (query is None) or (query == ""):
        logger.info("Empty query")
        return None

    # start_time = time.time()
    matrix = None
    logger.info("XML RESULT TO TABLE")
    # print query

    if query.lower().__contains__("optional") is True:
        return None

    response = endpoint(query)
    logger.info("1. RESPONSE OBTAINED")
    # print response

    # DISPLAYING THE RESULT

    if response is not None:

        logger.info("2. RESPONSE IS NOT ''NONE''")

        try:
            xml_doc = xmltodict.parse(response)
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
                "NO RESULT FOR THE QUERY:"
                # print query

            # SINGLE RESULT
            if type(results) is collections.OrderedDict:

                # Creates a list containing h lists, each of w items, all set to 0
                # INITIALIZING THE MATRIX
                w, h = variables_size, 2
                # print "Creating matrix with size {} by {}".format(w, h)
                # x*y*0 to avoid weak error say x and y where not used
                matrix = [[x*y*0 for x in range(w)] for y in range(h)]
                # print matrix
                col = -1

                if variables_size == 1:
                    for name, variable in variables_list.items():
                        col += 1
                        # print variable
                        matrix[0][col] = variable
                    # print matrix

                    # RECORDS
                    for key, value in results.items():
                        matrix[1][0] = value.items()[1][1]

                else:
                    # print "Variable greater than 1"
                    # HEADER
                    for variable in variables_list:
                        for key, value in variable.items():
                            col += 1
                            matrix[0][col] = value
                            name_index[to_bytes(value)] = col
                            # print "{} was inserted".format(value)
                            # print matrix

                    # RECORDS
                    # print results.items()
                    for key, value in results.items():
                        # COLUMNS
                        # print "Key: ", key
                        # print "Value: ", value
                        for i in range(variables_size):
                            # print "value Items: ", value.items()[i][1]
                            # print "Length:", len(value.items())
                            if type(value) is list:
                                # print value
                                data = value[i]
                                index = name_index[data['@name']]
                                item = value[index].items()[1][1]
                                # print data['@name'], name_index[data['@name']]
                            elif type(value) is collections.OrderedDict:
                                item = value.items()[i][1]

                            if type(item) is collections.OrderedDict:
                                # print "Data is a collection"
                                # print "{} was inserted".format(data.items()[1][1])
                                matrix[1][i] = item.items()[1][1]
                            else:
                                # print "data is regular"
                                # print "{} was inserted".format(data)
                                matrix[1][i] = item
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
                matrix = [[x*y*0 for x in range(w)] for y in range(h)]

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
                                item = value.items()[1][1]
                                matrix[row][0] = item
                    else:
                        for key, value in result.items():
                            # COLUMNS
                            # print type(value)
                            row += 1
                            # value is a list
                            for c in range(variables_size):
                                # print row, c
                                # print value[c].items()[1][1]
                                data = value[c]
                                # print data['@name'], name_index[data['@name']]
                                index = name_index[data['@name']]
                                item = data.items()[1][1]

                                if type(item) is collections.OrderedDict:
                                    matrix[row][index] = to_bytes(item.items()[1][1])
                                    # print "r{} c{} v{}".format(row, c, data.items()[1][1])
                                else:
                                    matrix[row][index] = to_bytes(item)
                                    # print "r:{} c:{} {}={}".format(row, c, matrix[0][c], to_bytes(item))
            # print "DONE"
            # print "out with: {}".format(matrix)
            return matrix

        except Exception as err:
            logger.warning("\nUNACCEPTED ERROR IN THE RESPONSE.")
            logger.warning(err)
            return None

    else:
        logger.warning("NO RESPONSE")
        return None

def endpoint(query):

    """
        param query         : The query that is to be run against the SPARQL endpoint
        param database_name : The name of the database () in with the named-graph resides
        param host          : the host (server) name
        return              : returns the result of the query in the default format of the endpoint.
                            In the case of STARDOG, the sever returns an XML result.
    """

    q = to_bytes(query)
    # print q
    # Content-Type: application/json
    # b"Accept": b"text/json"
    # 'output': 'application/sparql-results+json'
    # url = b"http://{}:{}/annex/{}/sparql/query?".format("localhost", "5820", "linkset")
    # headers = {b"Content-Type": b"application/x-www-form-urlencoded",
    #            b"Authorization": b"Basic YWRtaW46YWRtaW5UMzE0YQ=="}

    url = b"http://{}/annex/{}/sparql/query?".format(host, database)
    # print url
    params = urllib.urlencode(
        {b'query': q, b'format': b'application/sparql-results+json',
         b'timeout': b'0', b'debug': b'on', b'should-sponge': b''})
    headers = {b"Content-Type": b"application/x-www-form-urlencoded"}

    """
        Authentication
    """
    user = "admin"
    password = "admin"
    # password = "admin"
    passman = urllib2.HTTPPasswordMgrWithDefaultRealm()
    passman.add_password(None, url, user, password)
    urllib2.install_opener(urllib2.build_opener(urllib2.HTTPBasicAuthHandler(passman)))

    request = urllib2.Request(url, data=params, headers=headers)

    try:
        response = urllib2.urlopen(request)
        result = response.read()
        # print result
        return result

    except Exception as err:
        if str(err).__contains__("No connection") is True:
            logger.warning(err)
            return "No connection"

        logger.warning(err)
        print "\nTHERE IS AN ERROR IN THIS QUERY"
        print query
        return None
