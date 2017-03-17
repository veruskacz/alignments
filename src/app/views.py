# encoding=utf-8
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
import re
import uuid
import pprint
# local
import Queries as Qry


ENDPOINT_URL = 'http://localhost:5820/risis/query'
UPDATE_URL = 'http://localhost:5820/risis/update'
DATABASE = "risis"
HOST = "localhost:5820"

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
    # GET QUERY ABOUT LINKSETS AND LENSES
    linkset_query = Qry.get_graph_linkset()
    lens_query = Qry.get_graph_lens()
    # RUN QUERIES AGAINST ENDPOINT
    linksets = sparql(linkset_query, strip=True)
    lenses = sparql(lens_query, strip=True)
    # SEND BAK RESULTS
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

    corresp_query = Qry.get_correspondences(graph_uri)
    correspondences = sparql(corresp_query, strip=True)

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
    # RETRIEVE VARIABLES
    sub_uri = request.args.get('sub_uri', '')
    obj_uri = request.args.get('obj_uri', '')
    subjectTarget = request.args.get('subjectTarget', '')
    objectTarget = request.args.get('objectTarget', '')
    alignsSubjects = request.args.get('alignsSubjects', '')
    alignsObjects = request.args.get('alignsObjects', '')
    # FOR EACH DATASET GET VALUES FOR THE ALIGNED PROPERTIES
    query = Qry.get_aligned_predicate_value(sub_uri, obj_uri, alignsSubjects, alignsObjects)
    details = sparql(query, strip=True)
    # RETURN THE RESULT
    return render_template('details_list.html',
                            details = details,
                            # pred_uri = singleton_uri,
                            sub_uri = sub_uri,
                            obj_uri = obj_uri,
                            subjectTarget = subjectTarget,
                            objectTarget = objectTarget,
                            alignsSubjects = get_URI_local_name(alignsSubjects),
                            alignsObjects = get_URI_local_name(alignsObjects))


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
    # print "\n\n\n\n\n"
    details = sparql(det_query, strip=True)


    datasets_dict = dict()
    for i in range(len(details)):

        # DATASETS
        src_dataset = details[i]['subjectsTarget']['value']
        trg_dataset = details[i]['objectsTarget']['value']

        # ALIGNED PREDICATES
        src_aligns = details[i]['alignsSubjects']['value']
        trg_aligns = details[i]['alignsObjects']['value']

        src_resource = details[i]['sub']['value']
        trg_resource = details[i]['obj']['value']

        # LOAD THE DICTIONARY WITH UNIQUE DATASETS AS KEY
        # AND LIST OF UNIQUE ALIGNED PREDICATES AS VALUE
        if src_dataset not in datasets_dict:
            datasets_dict[src_dataset] = (src_resource, [src_aligns], [])
        else:
            (res, align_list, pred_values) = datasets_dict[src_dataset]
            if src_aligns not in align_list:
                # datasets_dict[src_dataset] = (res, align_list+[src_aligns])
                align_list += [src_aligns]
        # print datasets_dict

        if trg_dataset not in datasets_dict:
            datasets_dict[trg_dataset] = (trg_resource, [trg_aligns], [])
        else:
            (res, align_list, pred_values) = datasets_dict[trg_dataset]
            if trg_aligns not in align_list:
                align_list += [trg_aligns]

    # FOR EACH ALIGNED PREDICATE, GET IT DESCRIPTION VALUE
    sub_datasets = []
    obj_datasets = []
    for dataset, (res, align_list, pred_values)  in datasets_dict.items():
        # print type(predicates)
        s = u'http://risis.eu/alignment/predicate/resourceIdentifier'
        print "align_list", align_list
        if s in align_list:
            align_list.remove(s)
        print "align_list", align_list
        val_query = Qry.get_resource_description(dataset, res, align_list)

        values_matrix = sparql_xml_to_matrix(val_query)


        # print "\n\n",align_list
        # print values_matrix[1]

        if res == sub_uri:
            sub_datasets += [dataset]
        else: ## == obj_uri
            obj_datasets += [dataset]

        for i in range(len(align_list)):
            # print "\n", align_list[i], "=", values_matrix[1][i]
            if values_matrix is None:
                pred_value = {'pred': get_URI_local_name(align_list[i]), 'value': ""}
            else:
                pred_value = {'pred': get_URI_local_name(align_list[i]), 'value':values_matrix[1][i]}
            pred_values += [pred_value]
            # datasets_dict[dataset] = (res, align_list, pred_values)


    # print datasets_dict
    # print "\n\n\n"
    # print "HERE:", sub_datasets, obj_datasets

    rows = []
    for i in range(max(len(sub_datasets),len(sub_datasets))):
        if i < len(sub_datasets):
            (res, align_list, pred_values) = datasets_dict[sub_datasets[i]]
            col1 = {'dataset': sub_datasets[i],
                    'dataset_stripped': get_URI_local_name(sub_datasets[i]),
                    'predicates': pred_values}
        else:
            col1 = ""
        if i < len(obj_datasets):
            (res, align_list, pred_values) = datasets_dict[obj_datasets[i]]
            col2 = {'dataset': obj_datasets[i],
                    'dataset_stripped': get_URI_local_name(obj_datasets[i]),
                    'predicates': pred_values}
        else:
            col2 = ""
        rows += [{'col1': col1, 'col2': col2}]

    # print rows

    return render_template('lensDetails_list.html',
                           detailHeadings = details,
                            # pred_uri = singleton_uri,
                           rows = rows,
                            sub_uri = sub_uri,
                            obj_uri = obj_uri,
                            sub_datasets = sub_datasets,
                            obj_datasets = obj_datasets,
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

    # query = PREFIXES + """
    # select distinct *
    # {
    #     graph <""" + dataset_uri + """>
    #     { <""" + resource_uri + """> ?pred ?obj }
    # }
    # """
    query = Qry.get_resource_description(dataset_uri, resource_uri, predicate=None)
    print "\n\nQEURY:", query
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

#######################################################################
## VIEW MODE
#######################################################################

@app.route('/getgraphs2')
def graphs2():
    """
    This function is called due to request /getgraphs2
    It queries the dataset for ...
    The results, ...,
        are passed as parameters to the template linksetsCreation.html
    """
    # GET QUERY
    graphs_query = Qry.get_graph_type()
    # RUN QUERY AGAINST ENDPOINT
    graphs = sparql(graphs_query, strip=True)
    # SEND BAK RESULTS
    return render_template('linksetsCreation.html',src_graphs = graphs, trg_graphs = graphs)

@app.route('/getpredicates')
def predicates():
    """
    This function is called due to request /getpredicates
    It queries the dataset for ...
    The results, ...,
        are passed as parameters to the template linksetsCreation.html
    """
    dataset_uri = request.args.get('dataset_uri', '')
    # GET QUERY
    query = Qry.get_predicates(dataset_uri)
    print query
    # RUN QUERY AGAINST ENDPOINT
    dataDetails = sparql(query, strip=True)
    # print dataDetails
    # SEND BAK RESULTS
    return render_template('datadetails_list.html',
                            dataDetails = dataDetails)


# ######################################################################
## ENDPOINT
# ######################################################################

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
                    temp = v['value']
                    temp = temp[temp.rfind('/')+1:]
                    temp = temp[temp.rfind('#')+1:]
                    new_result[k+'_label']['value'] = temp

                elif not k+'_label' in r.keys():
                    new_result[k+'_label'] = {}
                    new_result[k+'_label']['type'] = 'literal'
                    new_result[k+'_label']['value'] = v['value']

                new_result[k+'_stripped'] = {}
                new_result[k+'_stripped']['type'] = 'literal'
                temp = v['value']
                temp = temp[temp.rfind('/')+1:]
                temp = temp[temp.rfind('#')+1:]
                new_result[k+'_stripped']['value'] = temp

                new_result[k] = v

            new_results.append(new_result)

        # log.debug(new_results)
        return new_results
    else :
        return result_dict['results']['bindings']


@app.route('/sparql', methods=['GET'])
def sparqlDirect():
    query = str(request.args.get('query', None))

    results = []
    header = []
    response = sparql_xml_to_matrix(query)
    if (response):
        header = response[0]
        results = response[1:]
        # if (query_results):
        #     size = (len(query_results)-1)/2
        #     print "\n\n"
        #     print size
        #     if size > 0:
        #         header = query_results[:size-1]
        #         results = query_results[size:]
        #         print "\n\n"
        #         print header
        #         print results

    return render_template('viewsDetails_list.html',
                            header = header,
                            results = results)


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
                                item = to_bytes(value[index].items()[1][1])
                                # print data['@name'], name_index[data['@name']]
                            elif type(value) is collections.OrderedDict:
                                item = value.items()[i][1]

                            if type(item) is collections.OrderedDict:
                                # print "Data is a collection"
                                # print "{} was inserted".format(data.items()[1][1])
                                matrix[1][i] = to_bytes(item.items()[1][1])
                            else:
                                # print "data is regular"
                                # print "{} was inserted".format(data)
                                matrix[1][i] = to_bytes(item)
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
                                matrix[row][0] = to_bytes(item)
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
                                item = to_bytes(data.items()[1][1])

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

    url = b"http://{}/annex/{}/sparql/query?".format(HOST, DATABASE)
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


def get_URI_local_name(uri):
    # print "URI: {}".format(uri)

    if (uri is None) or (uri == ""):
        return None
    else:
        non_alphanumeric_str = re.sub('[ \w]', '', uri)
        if non_alphanumeric_str == "":
            return uri
        else:
            last_char = non_alphanumeric_str[-1]
            index = uri.rindex(last_char)
            name = uri[index + 1:]
            return name
