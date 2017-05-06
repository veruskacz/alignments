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

import ast
import re
import urllib2
import urllib
import Queries as Qry


ENDPOINT_URL = 'http://localhost:5820/risis/query'
UPDATE_URL = 'http://localhost:5820/risis/update'
DATABASE = "risis"
HOST = "localhost:5820"

REASONING_TYPE = 'SL'


CREATION_ACTIVE = True

if CREATION_ACTIVE:
    import src.Alignments.Linksets.SPA_Linkset as spa_linkset2
    import src.Alignments.Linksets.SPA_LinksetSubset as spa_subset
    from src.Alignments.Lenses.Lens_Union import union
    from src.app import app

    import src.Alignments.Settings as St
    import src.Alignments.UserActivities.UserRQ as Urq
    import src.Alignments.Linksets.SPA_LinksetRefine as refine
    import src.Alignments.UserActivities.View as mod_view
    from src.Alignments.SimilarityAlgo.ApproximateSim import prefixed_inverted_index
    import src.Alignments.UserActivities.User_Validation as UVld
    import src.Alignments.Manage.AdminGraphs as adm
else:
    from src.app import app

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
# <http://www.w3.org/ns/prov#>
PREFIXES =  """
    PREFIX bdb: <http://vocabularies.bridgedb.org/ops#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX linkset: <http://risis.eu/linkset/>
    PREFIX void: <http://rdfs.org/ns/void#>
    PREFIX prov: <http://www.w3.org/ns/prov#>
    PREFIX alivocab: <http://risis.eu/alignment/predicate/>
    PREFIX tmpgraph: <http://risis.eu/alignment/temp-match/> """

PRINT_RESULTS = False

# @app.route('/print', methods=['GET'])
# def prints():
#     msg = request.args.get('msg', '')
#     print "\n\n\n"
#     print msg
#     return msg


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

    # SEND BAK RESULTS
    return render_template('graphs_list.html',linksets = linksets, lenses = lenses)


@app.route('/getdatasets')
def datasets():
    """
    This function is called due to request /getdatasets
    It queries the datasets 
    The result is passed as parameter to the render the template 
    """
    # GET QUERY ABOUT DATASETS
    template = request.args.get('template', 'list_group.html')
    function = request.args.get('function', '')
    query = Qry.get_datasets()
    # RUN QUERIES AGAINST ENDPOINT
    datasets = sparql(query, strip=True)

    if PRINT_RESULTS:
        print "DATASETS:", datasets

    # SEND BAK RESULTS
    return render_template(template, list = datasets, btn_name = 'datasets', function = function)


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
    rq_uri = request.args.get('rq_uri', '')
    graph_uri = request.args.get('graph_uri', '')
    filter_uri = request.args.get('filter_uri', '')
    filter_term = request.args.get('filter_term', '')
    graph_label = request.args.get('label','')
    graph_triples = request.args.get('graph_triples','')
    alignsMechanism = request.args.get('alignsMechanism', '')
    operator = request.args.get('operator', '')

    corresp_query = Qry.get_correspondences(rq_uri, graph_uri, filter_uri, filter_term)
    correspondences = sparql(corresp_query, strip=True)

    if PRINT_RESULTS:
        print "\n\nCORRESPONDENCES:", correspondences

    return render_template('correspondences_list.html',
                            operator = operator,
                            graph_menu = graph_menu,
                            correspondences = correspondences,
                            graph_uri = graph_uri,
                            graph_label = get_URI_local_name(graph_label).replace("_"," "),
                            graph_triples = graph_triples,
                            alignsMechanism = get_URI_local_name(alignsMechanism))


@app.route('/setlinkesetfilter', methods=['GET'])
def setlinkesetfilter():
    rq_uri = request.args.get('rq_uri', '')
    linkset_uri = request.args.get('linkset_uri', '')
    property = request.args.get('property', '')
    json_item = request.args.get('value_1', '')
    value_1 = ast.literal_eval(json_item)
    json_item = request.args.get('value_2', '')
    value_2 = ast.literal_eval(json_item)

    # print ">>>>>>>", rq_uri, linkset_uri, property.lower(), value_1, value_2
    if property:
        result = UVld.register_correspondence_filter(
                        rq_uri, linkset_uri, property.lower(),
                        value_1 if value_1 != {} else None,
                        value_2 if value_2 != {} else None)

    # print result
    return ''


@app.route('/getlinkesetfilter', methods=['GET'])
def getlinkesetfilter():
    return ''

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
    query = Qry.get_linkset_corresp_sample_details(linkset, limit=10)
    details = sparql(query, strip=True)

    s_property_list = ''
    o_property_list = ''
    mechanism_list = ''
    D = None

    if details:
        d = details[0]
        list1 = d['s_property']['value'].split("|")
        list2 = d['o_property']['value'].split("|")
        list3 = d['mechanism']['value'].split("|")

        for i in range(len(list1)):
            s_property_list += get_URI_local_name(list1[i]) + ' | ' \
                if i < len(list1) - 1 else get_URI_local_name(list1[i])

            o_property_list += get_URI_local_name(list2[i]) + ' | ' \
                if i < len(list1) - 1 else get_URI_local_name(list2[i])

            mechanism_list += get_URI_local_name(list3[i]) + ' | ' \
                if i < len(list1) - 1 else get_URI_local_name(list3[i])


    query = Qry.get_linkset_corresp_details(linkset, limit=10)
    metadata = sparql(query, strip=True)

    if metadata:
        md = metadata[0]
    else:
        return 'NO RESULTS!'

    if PRINT_RESULTS:
        print "\n\nDETAILS:", details

    # RETURN THE RESULT
    if (template == 'none'):
        return json.dumps(md)
    else:
        return render_template(template,
            details = details,
            s_datatype = md['s_datatype_stripped']['value'],
            subTarget = md['subTarget_stripped']['value'],
            o_datatype = md['o_datatype_stripped']['value'],
            objTarget = md['objTarget_stripped']['value'],
            s_property = md['s_property_stripped']['value'],
            o_property= md['o_property_stripped']['value'],
            mechanism = md['mechanism_stripped']['value'],
            s_property_list= s_property_list,
            o_property_list= o_property_list,
            mechanism_list= mechanism_list
        )


@app.route('/getlensspecs', methods=['GET'])
def lenspecs():
    lens = request.args.get('lens', '')
    query = Qry.get_lens_specs(lens)

    details = sparql(query, strip=True)

    if PRINT_RESULTS:
        print "\n\nDETAILS:", details

    badge = "<span class='badge alert-primary'><strong>{}</strong></span>";
    if details:
        result = """
        <div class="panel panel-primary">
            <div class="panel-heading" id="inspect_lens_lens_details_col">
        """
        result += "This lens applies the " + badge.format(details[0]['operator_stripped']['value']) + " operator to "
        for i in range(len(details)):
            if i < len(details)-2:
                result += ", "
            elif i == (len(details)-1):
                result += " and "
            result += badge.format(details[i]['graph_stripped']['value'])
        result += " producing " + badge.format(details[0]['triples']['value']) + " triples."
        result += """
            </div>
            <div class="panel-body" style='display:none'></div>
        </div>
        """
    else:
        result = 'NO RESULTS!'

    # print result

    return result #json.dumps(details)


@app.route('/getlensdetails', methods=['GET'])
def lensdetails():
    """
    This function is called due to request /getlensdetails
    It queries the dataset for ...
    The results, ...,
        are passed as parameters to the template lensDetails_list.html
    """

    # RETRIEVE VARIABLES
    lens = request.args.get('lens', '')
    template = request.args.get('template', 'lensDetails_list.html')
    query = Qry.get_lens_corresp_details(lens, limit=10)

    details = sparql(query, strip=True)

    if details:
        d = details[0]
    else:
        return 'NO RESULTS!'

    if PRINT_RESULTS:
        print "\n\nDETAILS:", details

    # RETURN THE RESULT
    if (template == 'none'):
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
                            operator = d['operator_stripped']['value']
                            )


### TODO: REPLACE
@app.route('/getLensDetail1', methods=['GET'])
def detailsLens():
    """
    This function is called due to request /getLensDetail
    It queries the dataset for all the correspondences in a certain graph URI
    The results, ...,
        are passed as parameters to the template lensDetails_list.html
    """

    singleton_uri = request.args.get('uri', '')
    graph_uri = request.args.get('graph_uri', '')
    sub_uri = request.args.get('sub_uri', '')
    obj_uri = request.args.get('obj_uri', '')
    subjectTarget = request.args.get('subjectTarget', '')
    objectTarget = request.args.get('objectTarget', '')
    alignsSubjects = request.args.get('alignsSubjects', '')
    alignsObjects = request.args.get('alignsObjects', '')

    evi_query = Qry.get_evidences(graph_uri, singleton_uri, "prov:wasDerivedFrom")
    # print "QUERY:", evi_query
    evi_matrix = sparql_xml_to_matrix(evi_query)
    # print "MATRIX:", evi_matrix
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

    return render_template('lensDetails_list1.html',
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
        are passed as parameters to the template datadetails_list.html
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
    graph_uri = request.args.get('graph_uri', '').replace('linkset','singletons')

    query = Qry.get_evidences(graph_uri, singleton_uri, predicate=None)
    evidences = sparql(query, strip=True)
    if PRINT_RESULTS:
        print "\n\nEVIDENCES:", evidences

    query = Qry.get_evidences_counters(singleton_uri)
    validation_counts = sparql(query, strip=True)

    if PRINT_RESULTS:
        print "\n\nVALIDATION COUNTS:", validation_counts

    return render_template('evidence_list.html',
                            singleton_uri = singleton_uri,
                            evidences = evidences,
                            validation_counts = validation_counts)


@app.route('/updateevidence', methods=['GET'])
def updEvidence():
    """
    This function is called due to request /updateevidence
    It updates a singleton property resource with the validation info.
    The results, ...,
    """

    singleton_uri = request.args.get('singleton_uri', '')
    type = request.args.get('type', '')
    validation_text = request.args.get('validation_text', '')
    research_uri = request.args.get('research_uri', '')

    result = UVld.update_evidence(singleton_uri, validation_text, research_uri, accepted=(type=='accept'))
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
        results_x = response[1:]
        results = []
        f = lambda x: x.decode('utf-8') if str(x) else x
        for r in results_x:
          results += [map(f, r)]

    # print '\n\n', results

    return render_template('viewsDetails_list.html',
                            header = header,
                            results = results)

#######################################################################
## VIEW MODE
#######################################################################


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
    # print "TEST"
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



@app.route('/getpredicateslist')
def predicatesList():
    """
    This function is called due to request /getpredicates
    It queries the dataset for all the distinct predicates in a graph,
    togehter with a sample value
    The result list is passed as parameters to the template list_dropdown.html
    """
    graph_uri = request.args.get('graph_uri', '')
    function = request.args.get('function', '')
    template = request.args.get('template', 'list_dropdown.html')
    # GET QUERY
    query = Qry.get_predicates_list(graph_uri, exclude_rdf_type=True)

    # RUN QUERY AGAINST ENDPOINT
    list = sparql(query, strip=True)
    if PRINT_RESULTS:
        print "\n\nPREDICATES:", list

    # SEND BAK RESULTS
    return render_template(template,
                           list = list,
                           btn_name='Other Types',
                           function = function)


@app.route('/getdatasetpredicatevalues')
def datasetpredicatevalues():
    """
    This function is called due to request /getpredicates
    It queries the dataset for all the distinct predicates in a graph,
    togehter with a sample value
    The result list is passed as parameters to the template list_dropdown.html
    """
    graph_uri = request.args.get('graph_uri', '')
    predicate_uri = request.args.get('predicate_uri', '')
    function = request.args.get('function', '')
    template = request.args.get('template', 'list_dropdown.html')
    # GET QUERY
    query = Qry.get_dataset_predicate_values(graph_uri, predicate_uri)

    # RUN QUERY AGAINST ENDPOINT
    list = sparql(query, strip=True)
    if PRINT_RESULTS:
        print "\n\nPREDICATE Values:", predicate_uri, list

    # SEND BAK RESULTS
    return render_template(template,
                           list = list,
                           btn_name='Type Values',
                           function = function)


@app.route('/createLinkset')
def spa_linkset():

    rq_uri = request.args.get('rq_uri', '')
    specs = {
        'researchQ_URI': rq_uri,

        'source': {
            'graph': request.args.get('src_graph', ''),
            St.link_old: request.args.get('src_aligns', ''),
            'aligns': request.args.get('src_aligns', ''),
            'entity_datatype': request.args.get('src_entity_datatye', '')
        },

        'target': {
            'graph': request.args.get('trg_graph', ''),
            'aligns': request.args.get('trg_aligns', ''),
            'entity_datatype': request.args.get('trg_entity_datatye', '')
        },

        'mechanism': request.args.get('mechanism', '')
    }


    # print "\n\n\nSPECS: ", specs
    if CREATION_ACTIVE:
        if specs['mechanism'] == 'exactStrSim':
            linkset_result = spa_linkset2.specs_2_linkset(specs, display=False, activated=True)

        elif specs['mechanism'] == 'embededAlignment':
            del specs['target']['aligns']
            linkset_result = spa_subset.specification_2_linkset_subset(specs, activated=True)

        elif specs['mechanism'] == 'identity':
            linkset_result = spa_linkset2.specs_2_linkset_id(specs, display=False, activated=True)

        elif specs['mechanism'] == 'approxStrSim':
            linkset_result = prefixed_inverted_index(specs, 0.8)

        elif specs['mechanism'] == 'geoSim':
            linkset_result = None

        else:
            linkset_result = None
    else:
        linkset_result = {'message': 'Linkset creation is inactive!',
                           'error_code': -1,
                           St.result: None}

    # print "\n\nERRO CODE: ", linkset_result['error_code'], type(linkset_result['error_code'])


    # print "\n\n\n{}".format(linkset_result['message'])
    return json.dumps(linkset_result)


@app.route('/refineLinkset')
def refineLinkset():

    specs = {

        St.researchQ_URI: request.args.get('rq_uri', ''),

        'mechanism': request.args.get('mechanism', ''),

        St.linkset: request.args.get('linkset_uri', ''),

        St.intermediate_graph: request.args.get('intermediate_graph', ''),

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
    }

    if CREATION_ACTIVE:
        if specs['mechanism'] == 'exactStrSim':
            linkset_result = refine.refine(specs, exact=True)

        elif specs['mechanism'] == 'identity':
            linkset_result = spa_linkset2.specs_2_linkset_id(specs, display=False, activated=True)

        elif specs['mechanism'] == 'approxStrSim':
            linkset_result = None

        elif specs['mechanism'] == 'geoSim':
            linkset_result = None

        elif specs[St.mechanism] == "intermediate":
            linkset_result = refine.refine(specs, exact_intermediate=True)
            #linkset_result = result['refined']

        else:
            linkset_result = None
    else:
        linkset_result = {'message': 'Linkset refinement is inactive!',
                           'error_code': -1,
                           'linkset': ''}

    # print "\n\nERRO CODE: ", linkset_result['error_code'], type(linkset_result['error_code'])
    if linkset_result:
        refined = linkset_result[St.refined]
        if refined:
            if refined[St.error_code] == 0:
                return json.dumps(refined)

    # print "\n\n\n{}".format(linkset_result['message'])
    return json.dumps(linkset_result)


@app.route('/importLinkset')
def importLinkset():
    rq_uri = request.args.get('rq_uri')
    graphs = request.args.getlist('graphs[]')

    # print "RESEARCH QUESTION:", rq_uri
    # print "LINKSET", graphs

    if CREATION_ACTIVE:
        response = Urq.import_linkset(rq_uri, graphs)
    else:
        response =  'Linkset import is inactive!'
    return response


@app.route('/createLens')
def spa_lens():
    rq_uri = request.args.get('rq_uri')
    graphs = request.args.getlist('graphs[]')
    operator = request.args.get('operator', '')

    specs = {
        St.researchQ_URI: rq_uri,
        'datasets': graphs,
        'lens_operation': operator
    };

    # print "\n\n\nSPECS: ", specs

    if CREATION_ACTIVE:
        if operator == "union":
            lens_result = union(specs, activated=True)
        else:
            lens_result = {'message': 'Operation no implemented!',
                           'error_code': -1,
                           St.result: None}
    else:
        lens_result = {'message': 'Lens creation is inactive!',
                       'error_code': -1,
                       St.result: None}

    return json.dumps(lens_result)


@app.route('/importLens')
def importLens():
    rq_uri = request.args.get('rq_uri')
    graphs = request.args.getlist('graphs[]')

    # print "RESEARCH QUESTION:", rq_uri
    # print "LINKSET", graphs

    if CREATION_ACTIVE:
        response = Urq.import_lens(rq_uri, graphs)

    else:
        response =  'Lens import is inactive!'

    return response


@app.route('/createView')
def createView():
    rq_uri = request.args.get('rq_uri');
    mode = request.args.get('mode', 'save');
    view_lens = request.args.getlist('view_lens[]');
    view_filter_js = request.args.getlist('view_filter[]');

    view_specs = {
        St.researchQ_URI: rq_uri,
        'datasets': view_lens,
        'lens_operation': 'http://risis.eu/lens/operator/intersection'}

    view_filter = []
    for json_item in view_filter_js:
        f = ast.literal_eval(json_item)
        exist = False
        for d in view_filter:
            if d['graph'] == f['ds'] :
                d['properties'].append(f['att'])
                exist = True
                break
        if not exist:
            dict = {'graph': f['ds'],
                    'properties': [f['att']]}
            view_filter.append(dict)

    # print "\n\nVIEW SPECS:", view_specs
    # print "\n\nVIEW DESIGN:", view_filter

    # metadata: {"select": view_select, "where": view_where}
    # view_query = {"select": view_select, "where": view_where}
    # final result: {"metadata": view_metadata, "query": view_query, "table": table}

    if CREATION_ACTIVE:
        save = (mode == 'save')
        result = mod_view.view(view_specs, view_filter, save=save, limit=10)
        # print result
    else:
        metadata = {'message': 'View creation is not active!'}
        result = {"metadata": metadata, "query": '', "table": []}


    return json.dumps(result)


@app.route('/getviewdetails')
def viewdetails():
    rq_uri = request.args.get('rq_uri');
    view_uri = request.args.get('view_uri');

    view = mod_view.retrieve_view(rq_uri, view_uri)
    badge = "<span class='badge alert-primary'><strong>{}</strong></span>";
    details = """
    <div class="panel panel-primary">
        <div class="panel-heading" id="inspect_lens_lens_details_col">
    """
    details += "<div class='row'><div class='col-md-6'>"

    details += '<h4>View Lens</h4>'
    details += "</div><div class ='col-md-6'>"
    details += '<h4>View Filter </h4>'
    details += "</div></div> </div>"

    details += """<div class="panel-body">"""
    details += "<div class='row'><div class='col-md-6'>"
    for g in view['view_lens']:
        details += '- ' + get_URI_local_name(g).replace('_', ' ') +'<br/>'
    datasets_bag = map(lambda x: x[0], view['view_filter_matrix'][1:])
    datasets = list(set(datasets_bag))
    details += "</div><div class ='col-md-6'>"
    for d in set(datasets):
        details += '<strong>' + get_URI_local_name(d) + '</strong><br/>'
        details += '- '
        for f in view['view_filter_matrix'][1:]:
            if f[0] == d:
                details += get_URI_local_name(f[1]) + ', '
        details += '<br/>'
    details += "</div></div></div></div>"

    for i in range(1,len(view['view_filter_matrix'])):
        filter = view['view_filter_matrix'][i]
        # print get_URI_local_name(filter[0]), get_URI_local_name(filter[1])
        view['view_filter_matrix'][i] += [get_URI_local_name(filter[0]), get_URI_local_name(filter[1])]

    view['details'] = details

    return json.dumps(view)


@app.route('/getgraphsentitytypes')
def graphsEntityTypes():
    """
    This function is called due to request /getgraphsentitytypes
    It queries ...
    The result list is passed as parameters to the template graph_type_list.html
    """
    # GET QUERY
    function = request.args.get('function', '')
    rq_uri = request.args.get('rq_uri', '')
    mode = request.args.get('mode', 'toAdd')
    query = Qry.get_types_per_graph(rq_uri, mode)

    if (mode == 'added'):
        style = 'background-color:lightblue'
    else:
        style = ''

    # RUN QUERY AGAINST ENDPOINT
    data = sparql(query, strip=True)
    if PRINT_RESULTS:
        print "\n\nDATASET | TYPE | COUNT:", data
    # SEND BAK RESULTS

    if data and 'EntityCount' in data[0]:
        if data[0]['EntityCount']['value'] == '0':
            return ''

    return render_template('graph_type_list.html',
                            function = function,
                            style = style,
                            data = data)


@app.route('/getfilters')
def getfilters():
    """
    This function is called due to request /getfilters
    It queries ...
    The result list is passed as parameters to the template list_group_description.html
    """
    # GET QUERY
    function = request.args.get('function', '')
    rq_uri = request.args.get('rq_uri', '')
    graph_uri = request.args.get('graph_uri', '')
    mode = request.args.get('mode', '')
    query = Qry.get_filter(rq_uri, graph_uri)

    if (mode == 'added'):
        style = 'background-color:lightblue'
    else:
        style = ''

    # RUN QUERY AGAINST ENDPOINT
    data = sparql(query, strip=False)
    # print data

    return render_template('list_group_description.html',
                            function = function,
                            style = style,
                            list = data)

# TODO: REMOVE
@app.route('/insertrq', methods=['GET'])
def insertrq():
    """
    This function is called due to request /insertrq
    It inserts ...
    The results, ...,
    """

    question = request.args.get('question', '')

    if CREATION_ACTIVE:
        response = Urq.register_research_question(question)
    else:
        response = {'message': 'RQ creation is not active!', 'result': None}

    # if PRINT_RESULTS:
    # print "\n\nRESPONSE:", dict

    return json.dumps(response)

# TODO: REMOVE
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

    # print "\n\nMAP:", mapping

    if CREATION_ACTIVE:
        response = Urq.register_dataset_mapping(rq_uri, mapping)
    else:
        response = {'message': 'RQ dataset mapping is not active!', 'result': None}


    return response['message']


@app.route('/getrquestions')
def rquestions():
    """
    This function is called due to request /getrquestions
    It queries ...
    The result list is passed as parameters to the template list_dropdown.html
    """
    query = Qry.get_rqs();
    result = sparql(query, strip=False)
    # print result

    template = request.args.get('template', 'list_dropdown.html')
    function = request.args.get('function', '')

    if PRINT_RESULTS:
        print "\n\nRQs:", result

    # SEND BAK RESULTS
    return render_template(template,
                            list = result,
                            btn_name = 'Research Question',
                            function = function)


@app.route('/getoverviewrq')
def overviewrq():
    """
    This function is called due to request /getrquestions
    It queries ...
    The result list is passed as parameters to the template list_dropdown.html
    """
    rq_uri = request.args.get('rq_uri', '')
    result = mod_view.activity_overview(rq_uri, get_text=False)

    # if PRINT_RESULTS:
    # print "\n\nOverview:", result['idea']

    # SEND BAK RESULTS
    return json.dumps(result)


@app.route('/adminDel')
def adminDel():
    """
    This function is called due to request /getrquestions
    It queries ...
    The result list is passed as parameters to the template list_dropdown.html
    """
    typeDel = request.args.get('typeDel', '')

    if typeDel == 'idea':
        adm.drop_all_research_questions(display=True, activated=True)
    elif typeDel == 'linkset':
        adm.drop_linksets(display=True, activated=True)
    elif typeDel == 'lens':
        adm.drop_lenses(display=True, activated=True)
    # elif typeDel == 'view':
    #     result = ''

    # SEND BAK RESULTS
    return 'done'


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

    if type(query) is not str and type(query) is not unicode:
        message = "THE QUERY NEEDS TO BE OF TYPE STRING. {} WAS GIVEN".format(type(query))
        print message
        return None

    if (query is None) or (query == ""):
        message = "Empty query"
        print message
        return None

    # start_time = time.time()
    matrix = None
    logger.info("XML RESULT TO TABLE")
    # print query

    if query.lower().__contains__("optional") is True:
        message = "MATRIX DOES NOT YET DEAL WITH OPTIONAL"
        print message
        return None

    response = endpoint(query)
    logger.info("1. RESPONSE OBTAINED")

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
                message = "NO RESULT FOR THE QUERY:"
                return None
                # print query

            # SINGLE RESULT
            if type(results) is collections.OrderedDict:

                # Creates a list containing h lists, each of w items, all set to 0
                # INITIALIZING THE MATRIX
                w, h = variables_size, 2
                # print "Creating matrix with size {} by {}".format(w, h)
                # x*y*0 to avoid weak error say x and y where not used
                matrix = [[x * y * 0 for x in range(w)] for y in range(h)]
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
                matrix = [[x * y * 0 for x in range(w)] for y in range(h)]

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
                                    item_value = item.items()[1][1]
                                    matrix[row][index] = to_bytes(item_value)
                                    # print to_bytes(item_value)
                                    # print item.items()
                                    # print "r{} c{} v{}".format(row, c, data.items()[1][1])
                                else:
                                    matrix[row][index] = to_bytes(item)
                                    # print to_bytes(item)
                                    # print "r:{} c:{} {}={}".format(row, c, matrix[0][c], to_bytes(item))
            # print "DONE"
            # print "out with: {}".format(matrix)
            return  matrix

        except Exception as err:
            message = "\nUNACCEPTED ERROR IN THE RESPONSE."
            print message
            return None

    else:
        # logger.warning("NO RESPONSE")
        # print response[St.message]
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
