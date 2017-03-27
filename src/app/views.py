# encoding=utf-8
import json
import logging

import requests
from flask import render_template, request # , jsonify, make_response, g

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
# import uuid
# import pprint
# from SPARQLWrapper import SPARQLWrapper
# import logging
# local
import Queries as Qry
import ast

ENDPOINT_URL = 'http://localhost:5820/risis/query'
UPDATE_URL = 'http://localhost:5820/risis/update'
DATABASE = "risis"
HOST = "localhost:5820"

REASONING_TYPE = 'SL'

CREATION_ACTIVE = False

if CREATION_ACTIVE:
    import src.Alignments.Linksets.SPA_Linkset as spa_linkset2
    from src.Alignments.Lenses.Lens_Union import union
    from src.Alignments.Query import boolean_endpoint_response as boolean_response
    from src.app import app
else:
    from app import app

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

PRINT_RESULTS = False

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

    if PRINT_RESULTS:
        print "\n\nLINKSETS:", linksets
        print "LENSES:", lenses

    # TEST
    LINKSET = "http://risis.eu/linkset/grid_orgref_C001_exactStrSim"
    LENS = "http://risis.eu/lens/union_grid_orgref_C001"
    result = list()
    result2 = dict()
    # lens_targets_unique(result, LENS)
    lens_targets_details(result2, LENS)
    # print "\n\nResult2:", result2

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

    if PRINT_RESULTS:
        print "\n\nCORRESPONDENCES:", correspondences

    return render_template('correspondences_list.html',
                            operator = operator,
                            graph_menu = graph_menu,
                            correspondences = correspondences,
                            graph_label = graph_label,
                            graph_triples = graph_triples,
                            alignsMechanism = alignsMechanism)


@app.route('/getdetails', methods=['GET'])
def details():
    """
    This function is called due to request /getdetails
    It queries the dataset for both all the correspondences in a certain graph URI
    Expected Input: uri, label (for the graph)
    The results, ...,
        are passed as parameters to the template details_list.html
    """

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

    if PRINT_RESULTS:
        print "\n\nDETAILS:", details

    # RETURN THE RESULT
    return render_template('details_list.html',
                            details = details,
                            sub_uri = sub_uri,
                            obj_uri = obj_uri,
                            subjectTarget = subjectTarget,
                            objectTarget = objectTarget,
                            alignsSubjects = get_URI_local_name(alignsSubjects),
                            alignsObjects = get_URI_local_name(alignsObjects))


@app.route('/getlinksetdetails', methods=['GET'])
def linksetdetails():
    """
    This function is called due to request /getdetails
    It queries the dataset for both all the correspondences in a certain graph URI
    Expected Input: uri, label (for the graph)
    The results, ...,
        are passed as parameters to the template linksetDetails_list.html
    """

    # RETRIEVE VARIABLES
    linkset = request.args.get('linkset', '')
    template = request.args.get('template', 'linksetDetails_list.html')
    query = Qry.get_linkset_corresp_details(linkset, limit=10)
    details = sparql(query, strip=True)

    d = details[0]

    # if PRINT_RESULTS:
    print "\n\nDETAILS:", details

    # RETURN THE RESULT
    if (template == 'none'):
        print d
        return json.dumps(d)
    else:
        return render_template(template,
                            details = details,
                            s_datatype = d['s_datatype_stripped']['value'],
                            subTarget = d['subTarget_stripped']['value'],
                            o_datatype = d['o_datatype_stripped']['value'],
                            objTarget = d['objTarget_stripped']['value'],
                            s_property = d['s_property_stripped']['value'],
                            o_property= d['o_property_stripped']['value'],
                            mechanism = d['mechanism_stripped']['value']
                            )


### CHANGE THE NAME TO -DETAILS-
@app.route('/getLensDetail', methods=['GET'])
def detailsLens():
    """
    This function is called due to request /getLensDetail
    It queries the dataset for all the correspondences in a certain graph URI
    The results, ...,
        are passed as parameters to the template lensDetails_list.html
    """

    singleton_uri = request.args.get('uri', '')
    sub_uri = request.args.get('sub_uri', '')
    obj_uri = request.args.get('obj_uri', '')
    subjectTarget = request.args.get('subjectTarget', '')
    objectTarget = request.args.get('objectTarget', '')
    alignsSubjects = request.args.get('alignsSubjects', '')
    alignsObjects = request.args.get('alignsObjects', '')

    evi_query = Qry.get_evidences(singleton_uri, "prov:wasDerivedFrom")
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
        # print "align_list", align_list
        if s in align_list:
            align_list.remove(s)
        # print "align_list", align_list
        val_query = Qry.get_resource_description(dataset, res, align_list)

        values_matrix = sparql_xml_to_matrix(val_query)

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

    return render_template('lensDetails_list.html',
                            detailHeadings = details,
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

    query = Qry.get_resource_description(dataset_uri, resource_uri, predicate=None)
    # print "\n\nQUERY:", query
    dataDetails = sparql(query, strip=True)
    if PRINT_RESULTS:
        print "\n\nDATA DETAILS:", dataDetails


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
    if PRINT_RESULTS:
        print "\n\nEVIDENCES:", evidences

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
    if PRINT_RESULTS:
        print "\n\nVALIDATION COUNTS:", validation_counts

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

    result = sparql_update(query)
    if PRINT_RESULTS:
        print "\n\nUPDATE RESPOSNSE:", result

    return result


@app.route('/sparql', methods=['GET'])
def sparqlDirect():
    query = str(request.args.get('query', None))

    results = []
    header = []
    response = sparql_xml_to_matrix(query)
    if (response):
        header = response[0]
        results = response[1:]

    return render_template('viewsDetails_list.html',
                            header = header,
                            results = results)

#######################################################################
## VIEW MODE
#######################################################################

# @app.route('/getgraphspertype')
# def graphspertype():
#     """
#     This function is called due to request /getgraphspertype
#     It queries the dataset for of all the graphs of a certain type
#     The result listis passed as parameters to the informed template
#     (default list_dropdown.html)
#     """
#     # GET QUERY
#     type = request.args.get('type', 'dataset')
#     btn_name = request.args.get('btn_name', type)
#     template = request.args.get('template', 'list_dropdown.html')
#     graphs_query = Qry.get_graphs_per_type(type)
#     # RUN QUERY AGAINST ENDPOINT
#     graphs = sparql(graphs_query, strip=True)
#     if PRINT_RESULTS:
#         print "\n\nGRAPHS:", graphs
#     # SEND BAK RESULTS
#     return render_template(template, list = graphs, btn_name = btn_name)

@app.route('/getgraphsperrqtype')
def graphsperrqtype():
    """
    This function is called due to request /getgraphsperrqtype
    It queries the dataset for of all the graphs of a certain type
    The result listis passed as parameters to the informed template
    (default list_dropdown.html)
    """
    # GET QUERY
    rq_uri = request.args.get('rq_uri', '')
    type = request.args.get('type', 'dataset')
    mode = request.args.get('mode', 'inspect')
    btn_name = request.args.get('btn_name', type)
    template = request.args.get('template', 'list_dropdown.html')
    if (mode == 'import'):
        graphs_query = Qry.get_graphs_related_to_rq_type(rq_uri,type)
    else:
        graphs_query = Qry.get_graphs_per_rq_type(rq_uri,type)
    # RUN QUERY AGAINST ENDPOINT
    graphs = sparql(graphs_query, strip=True)
    if PRINT_RESULTS:
        print "\n\nGRAPHS:", graphs
    # SEND BAK RESULTS
    return render_template(template, list = graphs, btn_name = btn_name, function = '')


@app.route('/getdatasetsperrq')
def datasetsperrq():
    """
    This function is called due to request /getgraphspertype
    It queries the dataset for of all the graphs of a certain type
    The result listis passed as parameters to the informed template
    (default list_dropdown.html)
    """
    # GET QUERY
    print "TEST"
    rq_uri = request.args.get('rq_uri', '')
    btn_name = request.args.get('btn_name', 'dataset')
    template = request.args.get('template', 'list_dropdown.html')
    function = request.args.get('function', '')
    print rq_uri, btn_name, template, function
    source_query = Qry.get_source_per_rq(rq_uri)
    # RUN QUERY AGAINST ENDPOINT
    sources = sparql(source_query, strip=True)
    if PRINT_RESULTS:
        print "\n\nGRAPHS:", sources
    # SEND BAK RESULTS
    return render_template(template,
                            list = sources,
                            btn_name = btn_name,
                            function = function)


# @app.route('/getentitytype')
# def entitytype():
#     """
#     This function is called due to request /getentitytype
#     It queries the dataset for of all the graphs of a certain type
#     The result listis passed as parameters to the informed template
#     (default list_dropdown.html)
#     """
#     # GET QUERY
#     print '\n\nGET ENTITY TYPE'
#     graph_uri = request.args.get('graph_uri', '')
#     template = request.args.get('template', 'list_dropdown.html')
#     query = Qry.get_entity_type(graph_uri)
#     # RUN QUERY AGAINST ENDPOINT
#     types = sparql(query, strip=True)
#     if PRINT_RESULTS:
#         print "\n\nENTITY TYPES:", types
#     # SEND BAK RESULTS
#     return render_template(template, list = types, btn_name = 'Entity Type')


@app.route('/getentitytyperq')
def entitytyperq():
    """
    This function is called due to request /getentitytype
    It queries the dataset for of all the graphs of a certain type
    The result listis passed as parameters to the informed template
    (default list_dropdown.html)
    """
    # GET QUERY
    # print '\n\nGET ENTITY TYPE'
    graph_uri = request.args.get('graph_uri', '')
    rq_uri = request.args.get('rq_uri', '')
    template = request.args.get('template', 'list_dropdown.html')
    function = request.args.get('function', '')
    query = Qry.get_entity_type_rq(rq_uri,graph_uri)
    # RUN QUERY AGAINST ENDPOINT
    types = sparql(query, strip=True)
    if PRINT_RESULTS:
        print "\n\nENTITY TYPES:", types
    # SEND BAK RESULTS
    return render_template(template, list = types,
                            btn_name = 'Entity Type',
                            function = function)


@app.route('/getpredicates')
def predicates():
    """
    This function is called due to request /getpredicates
    It queries the dataset for all the distinct predicates in a graph,
    togehter with a sample value
    The result list is passed as parameters to the template datadetails_list.html
    """
    dataset_uri = request.args.get('dataset_uri', '')
    function = request.args.get('function', '')
    # GET QUERY
    query = Qry.get_predicates(dataset_uri)

    # RUN QUERY AGAINST ENDPOINT
    dataDetails = sparql(query, strip=True)
    if PRINT_RESULTS:
        print "\n\nPREDICATES:", dataDetails
    # SEND BAK RESULTS
    return render_template('datadetails_list.html',
                            dataDetails = dataDetails,
                            function = function)


def lens_targets_details(detail_dict, graph):
    # GET THE TYPE OF THE GRAPH
    graph_type_matrix = sparql_xml_to_matrix(
        Qry.get_graph_type(graph))

    if graph_type_matrix:
        # THIS IS THE BASE OF THE RECURSION
        if graph_type_matrix[1][0] == "http://rdfs.org/ns/void#Linkset":
            # print "I am Neo"
            metadata_matrix = sparql_xml_to_matrix(Qry.get_linkset_metadata(graph))
            # print "\nSUBJECT TARGET:", metadata_matrix[1][0]
            # print "OBJECT TARGET:",metadata_matrix[1][1]
            # THIS CONNECTS THE GRAPH TO IT SUBJECT AND TARGET DATASETS
            if graph not in detail_dict:
                detail_dict[graph] = metadata_matrix
            return

        if graph_type_matrix[1][0] == "http://vocabularies.bridgedb.org/ops#Lens":
            # print "I am Keanu Reeves"
            # GET THE OPERATOR
            # alivocab:operator	 http://risis.eu/lens/operator/union
            lens_operator_matrix = sparql_xml_to_matrix(Qry.get_lens_operator(graph))
            # print "\nOPERATOR:", lens_operator_matrix
            if lens_operator_matrix:
                if lens_operator_matrix[1][0] == "http://risis.eu/lens/operator/union":
                    # GET THE LIST OF TARGETS
                    target_matrix = sparql_xml_to_matrix(Qry.get_lens_union_targets(graph))
                    if target_matrix:
                        for i in range(1, len(target_matrix)):
                            lens_targets_details(detail_dict, target_matrix[i][0])


# @app.route('/gettargetdatasets')
# def targetdatasets():
#     """
#     This function is called due to request /gettargetdatasets
#     It queries all the (dataset) tagerts given a graph
#     The result list is passed as parameters to the template graphs_listgroup.html
#     """
#     graph_uri = request.args.get('graph_uri', '')
#
#     ## existing target datasets are reasembled as original strip_dict
#     ## and passed as parameter to avoid repeated results
#     # targetdatasets = request.args.getlist('targetdatasets[]')
#     # ldict = []
#     # for t in targetdatasets:
#     #     dict1 = {u'g': {u'type': u'uri', u'value': t}}
#     #     ldict.append(dict1)
#     # result_dict = {u'results': {u'bindings': ldict}}
#     # graphs = strip_dict(result_dict)
#
#     selectedLenses = request.args.getlist('selectedLenses[]')
#     # print '\n\nSELECTED LENSES', selectedLenses
#     graphs = []
#     for lens in selectedLenses:
#         lens_targets_unique(graphs, lens)
#
#     if PRINT_RESULTS:
#         print "\n\nTARGETS:", graphs
#
#     # SEND BAK RESULTS
#     return render_template('graphs_listgroup.html',
#                             graphs = graphs)


def lens_targets_unique(unique_list, graph):

    # GET THE TYPE OF THE GRAPH
    graph_type_matrix = sparql_xml_to_matrix(
        Qry.get_graph_type(graph))

    if graph_type_matrix:
        # THIS IS THE BASE OF THE RECURSION
        if graph_type_matrix[1][0] == "http://rdfs.org/ns/void#Linkset":
            query = Qry.get_targets(graph)
            result = sparql(query, strip=True)
            for r in result:
                if not(r in unique_list):
                    unique_list.append(r)
            return

        if graph_type_matrix[1][0] == "http://vocabularies.bridgedb.org/ops#Lens":
            # print "I am Keanu Reeves"
            # GET THE OPERATOR
            # alivocab:operator	 http://risis.eu/lens/operator/union
            lens_operator_matrix = sparql_xml_to_matrix(Qry.get_lens_operator(graph))
            # print "\nOPERATOR:", lens_operator_matrix
            if lens_operator_matrix:
                if lens_operator_matrix[1][0] == "http://risis.eu/lens/operator/union":
                    # GET THE LIST OF TARGETS
                    target_matrix = sparql_xml_to_matrix(Qry.get_lens_union_targets(graph))
                    if target_matrix:
                        for i in range(1, len(target_matrix)):
                            lens_targets_unique(unique_list, target_matrix[i][0])


@app.route('/createLinkset')
def spa_linkset():

    rq_uri = request.args.get('rq_uri', '')
    specs = {

        'source': {
            'graph': request.args.get('src_graph', ''),
            'aligns': request.args.get('src_aligns', ''),
            'entity_datatype': request.args.get('src_entity_datatye', '')
        },

        'target': {
            'graph': request.args.get('trg_graph', ''),
            'aligns': request.args.get('trg_aligns', ''),
            'entity_datatype': request.args.get('trg_entity_datatye', '')
        },

        'mechanism': request.args.get('mechanism', '')

        # ,'context_code': request.args.get('context_code', '')
    }

    # specs = {'source': {'aligns': u'http://risis.eu/grid/ontology/predicate/name',
    #                     'graph': u'http://risis.eu/dataset/grid',
    #                     'entity_datatype': u'http://risis.eu/grid/ontology/class/Institution'},
    #          'target': {'aligns': u'http://risis.eu/orgref/ontology/predicate/Name',
    #                     'graph': u'http://risis.eu/dataset/orgref',
    #                     'entity_datatype': u'http://risis.eu/orgref/ontology/class/Organisation'},
    #          'mechanism': u'exactStrSim',
    #          'context_code': u'666'}

    # print "\n\n\nSPECS: ", specs
    if CREATION_ACTIVE:
        if specs['mechanism'] == 'exactStrSim':
            linkset_result = spa_linkset2.specs_2_linkset(specs, DATABASE, HOST, display=False, activated=True)
        elif specs['mechanism'] == 'identity':
            linkset_result = spa_linkset2.specs_2_linkset_id(specs, DATABASE, HOST, display=False, activated=True)
        elif specs['mechanism'] == 'approxStrSim':
            linkset_result = None
        elif specs['mechanism'] == 'geoSim':
            linkset_result = None
        else:
            linkset_result = None
    else:
        linkset_result = {'message': 'Linkset creation is inactive!',
                           'error_code': -1,
                           'linkset': ''}

    # print "\n\nERRO CODE: ", linkset_result['error_code'], type(linkset_result['error_code'])
    if linkset_result:
        if linkset_result['error_code'] == 0:
            query = Qry.associate_linkset_lens_to_rq(rq_uri, linkset_result['linkset'])
            print boolean_response(query, DATABASE, HOST)

    # print "\n\n\n{}".format(linkset_result['message'])
    return json.dumps(linkset_result)


@app.route('/createLens')
def spa_lens():
    rq_uri = request.args.get('rq_uri');
    graphs = request.args.getlist('graphs[]');
    operator = request.args.get('operator', '');
    # context_code = request.args.get('context_code', '');

    # TODO: add proper function to create unique name
    List_graph_names = map((lambda x: x[x.rfind('/')+1:]), graphs)
    Concat_Names = reduce( (lambda x,y:x+y), List_graph_names)
    lens_uri = "http://risis.eu/lens/union_" + Concat_Names + operator

    specs = {'datasets': graphs,
             'lens_operation': operator,
             'lens': lens_uri};

    # print "\n\n\nSPECS: ", specs

    if CREATION_ACTIVE:
        if operator == "union":
            lens_result = union(specs, DATABASE, HOST, activated=True)
        else:
            lens_result = {'message': 'Operation no implemented!',
                           'error_code': -1,
                           'lens': ''}
    else:
        lens_result = {'message': 'Lens creation is inactive!',
                       'error_code': -1,
                       'lens': lens_uri}

    if lens_result:
        if lens_result['error_code'] == 0:
            query = Qry.associate_linkset_lens_to_rq(rq_uri, lens_result['lens'])
            boolean_response(query, DATABASE, HOST)

    return json.dumps(lens_result)


@app.route('/createView')
def createView():
    rq_uri = request.args.get('rq_uri');
    view_lens = request.args.getlist('view_lens[]');
    view_filter = request.args.getlist('view_filter[]');

    view_specs = {'datasets': view_lens,
                  'lens_operation': 'http://risis.eu/lens/operator/intersection' }

    design_view = []
    for json_item in view_filter:
        f = ast.literal_eval(json_item)
        exist = False
        for d in design_view:
            if d['graph'] == f['ds'] :
                d['properties'].append(f['att'])
                exist = True
                break
        if not exist:
            dict = {'graph': f['ds'],
                    'properties': [f['att']]}
            design_view.append(dict)

    # print "\n\nVIEW SPECS:", view_specs
    # print "\n\nVIEW DESIGN:", design_view

    if CREATION_ACTIVE:
        view_result = view(design_view, view_specs, DATABASE, HOST, limit=75)
    else:
        view_result = {'message': 'View creation is inactive!',
                       'error_code': -1,
                       'view': ''}

    if view_result:
        if view_result['error_code'] == 0:
            query = Qry.associate_linkset_lens_to_rq(rq_uri, view_result['view'])
            boolean_response(query, DATABASE, HOST)

    return json.dumps(view_result)


@app.route('/getgraphsentitytypes')
def graphsEntityTypes():
    """
    This function is called due to request /getgraphsentitytypes
    It queries ...
    The result list is passed as parameters to the template graph_type_list.html
    """
    # GET QUERY
    query = Qry.get_types_per_graph()

    # RUN QUERY AGAINST ENDPOINT
    data = sparql(query, strip=True)
    if PRINT_RESULTS:
        print "\n\nDATASET | TYPE | COUNT:", dataDetails
    # SEND BAK RESULTS
    return render_template('graph_type_list.html',
                            data = data)


@app.route('/insertrq', methods=['GET'])
def insertrq():
    """
    This function is called due to request /insertrq
    It inserts ...
    The results, ...,
    """

    question = request.args.get('question', '')
    query = Qry.check_RQ_existance(question)
    if CREATION_ACTIVE:
        check = boolean_response(query, DATABASE, HOST)
    else:
        check = 'false'
    # print "\n\nCHECK: ",check
    msg = ""
    if check == 'true':
        msg = 'This research question already exists!.<br/> URI = {}'
    else:
        query = Qry.insert_RQ(question)
        result = sparql_update(query)
        if result == 'true':
            msg = 'Your research question is created.<br/> URI = {}'

    rq_query = Qry.find_rq(question)
    rq = sparql_xml_to_matrix(rq_query)
    # print "RQ: ", rq

    dict = {
        'rq': rq[1][0],
        'msg': msg.format(rq[1][0])
    }

    # if PRINT_RESULTS:
    # print "\n\nRESPONSE:", dict

    return json.dumps(dict)


@app.route('/updaterq', methods=['GET'])
def updaterq():
    """
    This function is called due to request /updaterq
    It updates ...
    The results, ...,
    """
    list = request.args.getlist('list[]')
    rq_uri = request.args.get('rq_uri', '')

    mapping = dict()
    for item in list:
        py_obj = ast.literal_eval(item)

        if py_obj['graph'] not in mapping:
            mapping[py_obj['graph']] = [py_obj['type']]
        else:
            mapping[py_obj['graph']] += [py_obj['type']]

    query = Qry.insert_ds_mapping(rq_uri, mapping)
    if CREATION_ACTIVE:
        result = boolean_response(query, DATABASE, HOST)
    else:
        sparql_update(query)
        result = 'true'

    # result = 'false'
    if (result == 'true'):
        msg = "Your mapping was inserted: ({}). <br/>URI = {}".format(result, rq_uri)
    else:
        msg = "Your mapping could NOT be inserted: ({}) <br/>URI = {}".format(result, rq_uri)
    # question = request.args.get('question', '')
    # query = Qry.check_RQ_exsitance(question)
    # check = boolean_response(query, DATABASE, HOST)
    # # print "\n\nCHECK: ",check
    #
    # if check == 'true':
    #     result = 'This research question already exists!'
    # else:
    #     query = Qry.insert_RQ(question)
    #     result = sparql_update(query)
    #     if result == 'true':
    #         result = 'Research question created'
    #
    # if PRINT_RESULTS:
    #     print "\n\nRESPONSE:", result

    return msg #""#result


@app.route('/getrquestions')
def rquestions():
    """
    This function is called due to request /getrquestions
    It queries ...
    The result list is passed as parameters to the template list_dropdown.html
    """
    query = Qry.get_rqs();
    result = sparql(query, strip=False)

    template = request.args.get('template', 'list_dropdown.html')
    function = request.args.get('function', '')

    if PRINT_RESULTS:
        print "\n\nRQs:", result

    # SEND BAK RESULTS
    return render_template(template,
                            list = result,
                            btn_name = 'Research Question',
                            function = function)

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
        new_results = strip_dict(result_dict)
        # log.debug(new_results)
        return new_results
    else :
        # print result_dict
        return result_dict['results']['bindings']


def strip_dict(result_dict):
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
            if k == 'uri':  ## specially for removing _ when var name is uri
                new_result[k+'_stripped']['value'] = temp.replace('_',' ')
            else:
                new_result[k+'_stripped']['value'] = temp

            new_result[k] = v

        new_results.append(new_result)
    return new_results

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
