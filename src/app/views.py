# encoding=utf-8

import os
import re
import ast
import json
import urllib
import urllib2
import logging
import requests
import xmltodict
import collections
import Queries as Qry
from kitchen.text.converters import to_bytes, to_unicode
from flask import render_template, request, redirect,   jsonify  # url_for, make_response, g

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)
handler = logging.StreamHandler()
logger.addHandler(handler)

# import cgi
# from os import listdir
# from os.path import isfile, isdir, join


CREATION_ACTIVE = True
FUNCTION_ACTIVATED = True
if CREATION_ACTIVE:
    from app import app
    import Alignments.Utility as Ut
    import Alignments.Settings as St
    import Alignments.ToRDF.CSV as CSV
    import Alignments.ErrorCodes as Ec
    import Alignments.Linksets.Linkset as Ls
    import Alignments.Manage.AdminGraphs as adm
    from Alignments.Lenses.Lens_Union import union
    from Alignments.Lenses.Lens_Difference import difference as diff
    from Alignments.Lenses.Lens_transitive import lens_transitive as trans
    import Alignments.UserActivities.UserRQ as Urq
    import Alignments.UserActivities.View as mod_view
    import Alignments.Linksets.SPA_Linkset as spa_linkset2
    import Alignments.Linksets.SPA_LinksetRefine as refine
    import Alignments.UserActivities.User_Validation as UVld
    from Alignments.UserActivities import Import_Data as Ipt
    import Alignments.Linksets.SPA_LinksetSubset as spa_subset
    from Alignments.SimilarityAlgo.ApproximateSim import prefixed_inverted_index
    from Alignments.Manage.DatasetStats import stats_optimised as stats
    from Alignments.Query import sparql_xml_to_matrix as sparql2matrix
    from Alignments.Query import sparql_xml_to_csv as sparql2csv
    import Alignments.UserActivities.ExportAlignment as Ex

    import Alignments.Server_Settings as Svr

else:
    from app import app

DATABASE = Svr.DATABASE
HOST = Svr.settings[St.stardog_host_name]
ENDPOINT_URL = 'http://{}/{}/query'.format(HOST, DATABASE)
UPDATE_URL = 'http://{}/{}/update'.format(HOST, DATABASE)
PATH_DS_FILES= '/Users/veruskacz/PyWebApp/alignments/src/data/'
REASONING_TYPE = 'SL'
if os.getcwd().endswith("src"):
    UPLOAD_FOLDER = "{0}{1}{1}UploadedFiles".format(os.getcwd(),os.path.sep)
    UPLOAD_ARCHIVE = "{0}{1}{1}UploadedArchive".format(os.getcwd(), os.path.sep)
else:
    UPLOAD_FOLDER = "{0}{1}{1}src{1}{1}UploadedFiles".format(os.getcwd(), os.path.sep)
    UPLOAD_ARCHIVE = "{0}{1}{1}src{1}{1}UploadedArchive".format(os.getcwd(), os.path.sep)

ALLOWED_EXTENSIONS = ['csv', 'txt','ttl','trig']


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

# UPLOAD_FOLDER = '/AlignmentUI/UploadedFiles/'
# "C:\Users\Al\PycharmProjects\AlignmentUI\UploadedFiles"
# ALLOWED_EXTENSIONS2 = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

# app = Flask(__name__)



@app.route('/default_dir_files')
def default_dir_files():

    list = Ut.dir_files(UPLOAD_FOLDER , [".csv", ".txt", ".tsv", ".ttl", '.trig'])
    selected_list = ""
    for i in range(len(list)):
        selected_list += "<option>{}</option>".format(list[i])

    # print list, selected_list
    return jsonify({"success": True, 'selected_list': selected_list})


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    # if request.method == 'POST':
        # file = request.files['file']
        # if file and allowed_file(file.filename):
        #     now = datetime.now()
        #     filename = os.path.join(UPLOAD_FOLDER, "%s.%s" % (now.strftime("%Y-%m-%d-%H-%M-%S-%f"), file.filename.rsplit('.', 1)[1]))
        #     file.save(filename)
    file = request.files['file']
    if file and allowed_file(file.filename):

        dir = "{0}{1}{1}".format(UPLOAD_FOLDER, os.path.sep)
        print "\nWe will upload: {}".format(file.filename)
        print "Directory: {}".format(dir)
        print "Path: {}".format(os.path.join(UPLOAD_FOLDER, file.filename))
        # file.save(os.path.join(UPLOAD_FOLDER, file.filename))

        # SAVE ORIGINAL FILE
        original = Ipt.save_original_file(file, UPLOAD_FOLDER)
        # print "{}\nWas uploaded to the server".format(file.filename)

        return jsonify({"success": True, 'original': original})

    else:
        print "\nFile not allowed"
        return jsonify({"success": False, 'list': []})


    # return jsonify({"success":True})


@app.route('/getupload')
def getupload():

    upload_type = request.args.get('type', 'linkset')
    original = request.args.get('original', '')
    print "upload_type", upload_type

    # upload_type = request.args.get('type', 'linkset')
    if upload_type == 'dataset':

        list = Ut.dir_files(UPLOAD_FOLDER, [".csv", ".txt", ".tsv"])

        select_list = ""
        for i in range(len(list)):
            select_list += "<option>{}</option>".format(list[i])
        # print list, selectlist
        return jsonify({"success": True, 'selectlist': select_list, 'original': original})

    elif upload_type == 'linkset':

        # RETURN A LIST OF PREDICATES IN THE ORIGINAL FILE
        list = Ipt.extract_predicates(original)
        # print "List", list

        # DISPLAY THE LIST OF PREDICATES
        select_list = ""
        for i in range(len(list)):
            select_list += "<option>{}</option>".format(str(list[i]).replace("<", "").replace(">", ""))

        # list = Ut.dir_files(dir, [".trig", ".ttl"])
        # print list
        return jsonify({"success": True, 'selectlist': select_list, 'original': original})

    return ""


@app.route('/userLinksetImport')
def userLinksetImport():
    original = request.args.get('original', '')
    index = request.args.get('index', '')
    result = Ipt.import_graph(file_path=original, upload_folder=UPLOAD_FOLDER, upload_archive=UPLOAD_ARCHIVE,
                              parent_predicate_index=int(index)-1, detail=False)
    return result["message"]


@app.route("/", methods=['GET'])
def index():

    if request.method == 'POST':

        # check if the post request has the file part
        if 'file' not in request.files:
            # flash('No file part')
            print "Nothing to upload"
            return redirect(request.url)

        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            # flash('No selected file')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            # filename = secure_filename(file.filename)
            dir = "{}\\UploadedFiles".format(UPLOAD_FOLDER)
            print "\nWe will upload: {}".format(file.filename)
            print "Directory: {}".format(dir)
            print "Path: {}".format(os.path.join(UPLOAD_FOLDER, file.filename))
            file.save(os.path.join(UPLOAD_FOLDER, file.filename))
            print "{}\nWas uploaded to the server".format(file.filename)
            # return jsonify({"success": True})
            # return render_template('base.html')
            # return redirect(url_for('uploaded_file', filename=file.filename))
    else:
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



@app.route('/getcorrespheader', methods=['GET'])
def correspondencesHeader():

    rq_uri = request.args.get('rq_uri', '')
    graph_uri = request.args.get('graph_uri', '')
    filter_uri = request.args.get('filter_uri', '')
    filter_term = request.args.get('filter_term', '').replace('\"','').replace('\'','')

    query = Qry.get_correspondHeader(rq_uri, graph_uri, filter_uri, filter_term)
    data = sparql(query, strip=True)

    header_template = """<h3><strong>Correspondences</strong></h3>
                          <span class="badge alert-primary"> {{ graph_label }} </span> contains
                          <span id='triples_span' class="badge alert-success">{{ graph_triples }}</span> triples
                            {% if alignsMechanism != ''%}
                          , aligned using the <span class="badge alert-info"> {{ alignsMechanism|upper }}</span> mechanism.
                            {%endif%}
                            {% if operator != ''%}
                           generated using the <span class="badge alert-info"> {{ operator|upper }}</span> operator.
                            {%endif%}"""

    return render_template(header_template, data)


@app.route('/getcorrespondences', methods=['GET'])
def correspondences():
    """
    This function is called due to request /getcorrespondences
    It queries the dataset for both all the correspondences in a certain graph URI
    Expected Input: uri, label (for the graph)
    The results, ...,
        are passed as parameters to the template correspondences_list.html
    """
    rq_uri = request.args.get('rq_uri', '')
    graph_uri = request.args.get('graph_uri', '')
    filter_uri = request.args.get('filter_uri', '')
    filter_term = request.args.get('filter_term', '')

    # Try first to query using stardog approximate search.
    # If this does not work, then try exact string match
    try:
        query = Qry.get_correspondences(rq_uri, graph_uri, filter_uri, filter_term)
        correspondences = sparql(query, strip=True)
        # print ">>>> Results corr", correspondences, type(correspondences)
        if (str(correspondences).find('com.complexible.stardog.plan.eval.ExecutionException') >= 0):
            print ">>>>", correspondences
            raise Exception(correspondences)
    except:
        try:
            query = Qry.get_correspondences(rq_uri, graph_uri, filter_uri, filter_term, useStardogApprox=False)
            correspondences = sparql(query, strip=True)
        except:
            correspondences = []

    if PRINT_RESULTS:
        print "\n\nCORRESPONDENCES:", correspondences

    return render_template('correspondences_list.html',
                            graph_uri = graph_uri,
                            correspondences = correspondences)


@app.route('/getcorrespondences2', methods=['GET'])
def correspondences2():
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

    # Try first to query using stardog approximate search.
    # If this does not work, then try exact string match
    try:
        query = Qry.get_correspondences(rq_uri, graph_uri, filter_uri, filter_term)
        correspondences = sparql(query, strip=True)
        print ">>>> Results corr", correspondences, type(correspondences)
        if correspondences == [{}]:
            correspondences = []
        elif (str(correspondences).find('com.complexible.stardog.plan.eval.ExecutionException') >= 0):
            # print 'TEST'
            raise Exception(correspondences)
    except:
        try:
            query = Qry.get_correspondences(rq_uri, graph_uri, filter_uri, filter_term, useStardogApprox=False)
            correspondences = sparql(query, strip=True)
        except:
            correspondences = []

    if PRINT_RESULTS:
        print "\n\nCORRESPONDENCES:", correspondences

    return render_template('correspondences_list2.html',
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
    return json.dumps(result)


@app.route('/setfilter', methods=['GET'])
def setFilter():
    rq_uri = request.args.get('rq_uri', '')
    graph_uri = request.args.get('graph_uri', '')
    property = request.args.get('property', '')
    json_item = request.args.get('value_1', '')
    value_1 = ast.literal_eval(json_item)
    json_item = request.args.get('value_2', '')
    value_2 = ast.literal_eval(json_item)

    # print ">>>>>>>", rq_uri, graph_uri, property.lower(), value_1, value_2
    if property:
        result = UVld.register_correspondence_filter(
                        rq_uri, graph_uri, property.lower(),
                        value_1 if value_1 != {} else None,
                        value_2 if value_2 != {} else None)

    # print result
    return json.dumps(result)


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
    rq_uri = request.args.get('rq_uri', '')
    filter_uri = request.args.get('filter_uri', '')

    query = Qry.get_linkset_corresp_details(linkset, limit=10, rq_uri = rq_uri, filter_uri = filter_uri )
    metadata = sparql(query, strip=True)

    if metadata:
        md = metadata[0]
    else:
        return 'NO RESULTS!'

    # RETURN THE RESULT
    if (template == 'none'):
        return json.dumps(md)
    else:
        query = Qry.get_linkset_corresp_sample_details(linkset, limit=10)
        details = sparql(query, strip=True)

        # print "LINKSET DETAIL QUERY:", query
        # print "LINKSET DETAIL RESULT:", details

        s_property_list = ''
        o_property_list = ''
        mechanism_list = ''
        D = None
        # print "RESULT!!!!!!!!", details
        if details:
            d = details[0]
            # print "!!!!!!!! D", d
            s_property_list = d['s_property_stripped']['value']
            o_property_list = d['o_property_stripped']['value']
            mechanism_list = d['mechanism_stripped']['value']

        if PRINT_RESULTS:
            print "\n\nDETAILS:", details

        data = render_template(template,
            details = details,
            s_datatype = md['s_datatype_stripped']['value'],
            subTarget = md['subTarget_stripped']['value'],
            o_datatype = md['o_datatype_stripped']['value'],
            objTarget = md['objTarget_stripped']['value'],
            s_property = md['s_property_stripped']['value'],
            o_property = md['o_property_stripped']['value'],
            mechanism = md['mechanism_stripped']['value'],
            s_property_list = s_property_list,
            o_property_list = o_property_list,
            mechanism_list = mechanism_list
        )

        return json.dumps({'metadata': md, 'data': data})


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

    #evi_query = Qry.get_evidences(graph_uri, singleton_uri, "prov:wasDerivedFrom")
    # print "QUERY:", evi_query
    #evi_matrix = sparql_xml_to_matrix(evi_query)
    # print "MATRIX:", evi_matrix
    # evi_matrix = ''
    # det_query = Qry.get_target_datasets(evi_matrix, graph_uri)
    det_query = Qry.get_target_datasets(graph_uri)
    # print det_query
    # print "\n\n\n\n\n"
    details = sparql(det_query, strip=True)


    datasets_dict = dict()
    for i in range(len(details)):

        # DATASETS
        src_dataset = details[i]['subjectsTarget']['value']
        trg_dataset = details[i]['objectsTarget']['value']

        # ALIGNED PREDICATES
        try:
            src_aligns = details[i]['alignsSubjects']['value']
        except:
            src_aligns = ''

        try:
            trg_aligns = details[i]['alignsObjects']['value']
        except:
            trg_aligns = ''

        try:
            src_resource = details[i]['sub']['value']
        except:
            src_resource = sub_uri

        try:
            trg_resource = details[i]['obj']['value']
        except:
            trg_resource = obj_uri

        # LOAD THE DICTIONARY WITH UNIQUE DATASETS AS KEY
        # AND LIST OF UNIQUE ALIGNED PREDICATES AS VALUE
        if src_aligns:
            if src_dataset not in datasets_dict:
                datasets_dict[src_dataset] = (src_resource, [src_aligns], [])
            else:
                (res, align_list, pred_values) = datasets_dict[src_dataset]
                if src_aligns not in align_list:
                    # datasets_dict[src_dataset] = (res, align_list+[src_aligns])
                    align_list += [src_aligns]
        # print datasets_dict

        if trg_aligns:
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

        # print 'BEFORE: ',pred_values
        for d in pred_values:
            # d['value'] = d['value'].decode('utf-8') if str(d['value']) else d['value']
            d['value'] = to_unicode(d['value'])# if str(d['value']) else d['value']
        # print 'AFTER: ',pred_values


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
    # print 'ROWS: ',rows

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
    # print "evidences!!!!!!!!!!!!!!!!", evidences
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

    header = []
    query = str(request.args.get('query', None))

    print "RUNNING SPARQL QUERY:{}".format(query)
    dic_response = sparql2matrix(query)
    # print dic_response
    # print St.message in dic_response

    print "PROCESSING THE RESULT..."
    if dic_response[St.message] == "OK":

        # response = sparql_xml_to_matrix(query)
        response = dic_response[St.result]
        results = []
        if (response):
            header = response[0]
            results_x = response[1:]

            # results = []
            f = lambda x: x.decode('utf-8') if str(x) else x
            for r in results_x:
              results += [map(f, r)]

        # print '\n\n', results
        if len(response) > 1:
            message = "Have a look at the result in the table below"
        else:
            message = "The query was successfully run with no result to show. " \
                      "<br/>Probably the selected properties need some revising."

        return json.dumps({'message': message, 'result':
            render_template('viewsDetails_list.html', header = header, results = results)})

    elif dic_response[St.message] == "NO RESPONSE":
        print "NO RESULT FOR THIS QUERY..."
        return json.dumps({'message': "NO RESPONSE", 'result': None})

    else:
        message = dic_response[St.message]
        return json.dumps({'message': message, 'result': None})


@app.route('/sparqlToCSV', methods=['GET'])
def sparqlToCSV():

    query = str(request.args.get('query', None)).replace("LIMIT", "### LIMIT")

    print "RUNNING SPARQL QUERY:{}".format(query)
    dic_response = sparql2csv(query)

    print "PROCESSING THE RESULT..."
    if dic_response[St.message] == "OK":

        if (dic_response[St.result]):
            result = dic_response[St.result].getvalue()
        else:
            result = ''
        if len(result) > 1:
            message = "OK"
        else:
            message = "The query was successfully run with no result to show. " \
                      "<br/>Probably the selected properties need some revising."

        return json.dumps({'message': message, 'result':result})

    else:
        if dic_response[St.message] == "NO RESPONSE":
            print "NO RESULT FOR THIS QUERY..."
        return json.dumps({'message': dic_response[St.message], 'result': None})

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
    function = request.args.get('function', '')
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
    return render_template(template, list = graphs, btn_name = btn_name, function = function)


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
    type = request.args.get('type', '')
    total = request.args.get('total', None)
    propPath = request.args.get('propPath', None)
    function = request.args.get('function', '')
    # GET QUERY
    query = Qry.get_predicates(dataset_uri, type, total, propPath)

    # RUN QUERY AGAINST ENDPOINT
    try:
        dataDetails = sparql(query, strip=True)
        if PRINT_RESULTS:
            print "\n\nPREDICATES:", dataDetails
        # SEND BAK RESULTS

        # print "RESULTS: ", len(dataDetails), len(dataDetails[0])
        if (len(dataDetails) > 0) and (len(dataDetails[0]) > 0):
            return json.dumps({'message': 'OK', 'result': render_template('datadetails_list.html',
                                dataDetails = dataDetails,
                                function = function)})
        else:
            return json.dumps({'message': 'Empty', 'result': None})
    except Exception as error:
        return json.dumps({'message': str(error.message), 'result': None})


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
            'entity_datatype': request.args.get('src_entity_datatype', '')
        },

        'target': {
            'graph': request.args.get('trg_graph', ''),
            'aligns': request.args.get('trg_aligns', ''),
            'entity_datatype': request.args.get('trg_entity_datatype', '')
        },

        'mechanism': request.args.get('mechanism', ''),

        St.intermediate_graph: request.args.get('intermediate_graph', '')
    }
    if len(request.args.get('src_reducer', '')) > 0:
        specs[St.source][St.reducer] = request.args.get('src_reducer', '')
    if len(request.args.get('trg_reducer', '')) > 0:
        specs[St.target][St.reducer] = request.args.get('trg_reducer', '')


    check_type = "linkset"
    id = False
    try:

        threshold = request.args.get('threshold', '0.8')
        threshold = float(threshold.strip())
        print threshold
        stop_words = request.args.get('stop_words', '')
        stop_symbols = request.args.get('stop_symbols', '')

        if CREATION_ACTIVE:

            # print "\n\n\nSPECS: ", specs

            if specs['mechanism'] == 'exactStrSim':
                linkset_result = spa_linkset2.specs_2_linkset(specs=specs, display=False, activated=FUNCTION_ACTIVATED)

            elif specs['mechanism'] == 'embededAlignment':
                del specs['target']['aligns']
                check_type = "subset"
                linkset_result = spa_subset.specification_2_linkset_subset(specs, activated=FUNCTION_ACTIVATED)

            elif specs['mechanism'] == 'identity':
                id = True
                linkset_result = spa_linkset2.specs_2_linkset_id(specs, display=False, activated=FUNCTION_ACTIVATED)

            elif specs['mechanism'] == 'approxStrSim':
                linkset_result = prefixed_inverted_index(specs, threshold, stop_words_string=stop_words, stop_symbols_string=stop_symbols)

            elif specs[St.mechanism] == "intermediate":
                linkset_result = spa_linkset2.specs_2_linkset_intermediate(specs, display=False, activated=FUNCTION_ACTIVATED)

            elif specs['mechanism'] == 'geoSim':
                linkset_result = None

            else:
                linkset_result = None
        else:
            linkset_result = {'message': 'Linkset creation is inactive!', 'error_code': -1, St.result: None}

        # print "\n\nERRO CODE: ", linkset_result['error_code'], type(linkset_result['error_code'])


        # print "\n\n\n{}".format(linkset_result['message'])
        return json.dumps(linkset_result)

    except Exception as err:

        print "SECOND CHECK AFTER SERVER ERROR"

        if id == True:
            check = Ls.run_checks_id(specs)
        else:
            check = Ls.run_checks(specs, check_type=check_type)

        if check[St.result] != "GOOD TO GO":
            # THE LINKSET WAS CREATED
            linkset_result = {'message': Ec.ERROR_CODE_22.replace('#', check[St.result]),
                              'error_code': 0, St.result: check[St.result]}
        else:
            linkset_result = {'message': str(err.message), 'error_code': -1, St.result: None}

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
            linkset_result = refine.refine(specs, exact=True, activated=True)

        elif specs['mechanism'] == 'identity':
            linkset_result = spa_linkset2.specs_2_linkset_id(specs, display=False, activated=True)

        elif specs['mechanism'] == 'approxStrSim':
            linkset_result = None

        elif specs['mechanism'] == 'geoSim':
            linkset_result = None

        elif specs[St.mechanism] == "intermediate":
            linkset_result = refine.refine(specs, exact_intermediate=True, activated=True)
            # print linkset_result
            #linkset_result = result['refined']

        else:
            linkset_result = None
    else:
        linkset_result = {'message': 'Linkset refinement is inactive!',
                           'error_code': -1,
                           'linkset': ''}

    # print "\n\nERRO CODE: ", linkset_result['error_code'], type(linkset_result['error_code'])
    if linkset_result:
        if St.refined in linkset_result:
            refined = linkset_result[St.refined]
            if refined:
                if refined[St.error_code] == 0:
                    return json.dumps(refined)
        else:
            linkset_result = {'message': linkset_result[St.message],
                              'error_code': -1,
                              'linkset': ''}
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
    operator = request.args.get('operator', '')

    # print "\n\n\nSPECS: ", specs

    if CREATION_ACTIVE:

        print "#####", request.args.get('subjects_target'), request.args.get('objects_target')

        if str(operator).lower()  == "union":
            graphs = request.args.getlist('graphs[]')
            specs = {
                St.researchQ_URI: rq_uri,
                St.datasets: graphs,
                St.lens_operation: operator }
            lens_result = union(specs, activated=True)

        elif str(operator).lower() == "difference":
            specs = {
                St.researchQ_URI: rq_uri,
                St.subjectsTarget: request.args.get('subjects_target'),
                St.objectsTarget: request.args.get('objects_target'),
                St.lens_operation: operator }
            lens_result = diff(specs, activated=True)

        elif str(operator).lower() == "transitive":
            specs = {
                St.researchQ_URI: rq_uri,
                St.subjectsTarget: request.args.get('subjects_target'),
                St.objectsTarget: request.args.get('objects_target'),
                St.lens_operation: operator }
            lens_result = trans(specs, activated=True)

        else:
            lens_result = {'message': 'Operation not implemented!',
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

    dict_stats = {}

    view_filter = []
    for json_item in view_filter_js:
        filter_row = ast.literal_eval(json_item)
        # exists_dataset = False
        dict_graph = None
        exists_dataset_entityType = False
        # print "KEYS", filter_row.keys()

        for elem in view_filter:
            # check if the dataset has been already registered
            if (elem['graph'] == filter_row['ds']):
                # only assigns value to dict_graph if the desired dataset was found
                dict_graph = elem
                data_list = elem['data']
                for data in data_list:
                    # check if the entityType has been already registered for that graph
                    if (data['entity_datatype'] == filter_row['type']):

                        # if a valid entity type is provided
                        if (filter_row['type'] != 'no_type'):
                            uri = filter_row['att'].replace("<", "").replace(">", "")
                            print "\nURI", uri
                            print "TYPE:", filter_row['type']
                            print "OPTIONAL CODE:", dict_stats[filter_row['ds']][filter_row['type']]
                            print "STATS:", dict_stats

                            optional = dict_stats[filter_row['ds']][filter_row['type']][uri]
                            tuple_data = (filter_row['att'], optional)
                            data['properties'].append(tuple_data)
                            # if desired dictionary is found, the loop can be broken
                            exists_dataset_entityType = True
                            break
                        else:
                            data['properties'].append(filter_row['att'])
                            exists_dataset_entityType = True
                            break

        # if the above loop finished wihtout finding the desired dictionary, then it will be registerd
        if not exists_dataset_entityType:

            # this means the entry for the dataset does not exists
            if (dict_graph is None):
                # create an entry for this dataset
                dict_graph = {'graph': filter_row['ds'], 'data':[]}
                view_filter.append(dict_graph)
                # check if there is already an entry for the dataset in dict_stats
                if filter_row['ds'] not in dict_stats:
                    # calculate the stats per dataset, if it hasn't been done yet
                    dict_stats[filter_row['ds']] =  stats(filter_row['ds'], display_table=False, display_text=False)
                    print "DATASET:", filter_row['ds']
                    print "STATS:", dict_stats

            if (filter_row['type'] != 'no_type'):
                uri = filter_row['att'].replace("<", "").replace(">", "")
                # print "URI:", uri
                # print "\n\nPRINTING:", filter_row['ds'], filter_row['att']
                # print "DICTIONARY 0:", dict_stats
                # print "DICTIONARY 1:", dict_stats[filter_row['ds']]
                # print "DICTIONARY 2:", dict_stats[filter_row['ds']][filter_row['type']]
                # print "OPTIONAL:", dict_stats[filter_row['ds']][filter_row['type']][uri]

                optional = dict_stats[filter_row['ds']][filter_row['type']][uri]
                properties = [(filter_row['att'], optional)]
                # dict = {'graph': filter_row['ds'], 'entity_datatype': filter_row['type'], 'properties': [tuple_data]}
                # view_filter.append(dict)
            else:
                properties = [filter_row['att']]
                # dict = {'graph': filter_row['ds'], 'properties': [filter_row['att']]}
                # view_filter.append(dict)

            data = {'entity_datatype': filter_row['type'], 'properties': properties}

            print "data", data
            print "dict_graph", dict_graph

            dict_graph['data'].append(data)


    # print "\n\nVIEW SPECS:", view_specs
    # print "\n\nVIEW DESIGN:", view_filter

    # CREATION_ACTIVE = False
    print view_filter

    if CREATION_ACTIVE:
        save = (mode == 'save')
        print "FILTER:", view_filter
        result = mod_view.view(view_specs, view_filter, save=save, limit=100)
        # print result
    else:
        metadata = {'message': 'View creation is not active!'}
        result = {"metadata": metadata, "query": '', "table": []}


    return json.dumps(result)


@app.route('/getviewdetails')
def viewdetails():
    rq_uri = request.args.get('rq_uri')
    view_uri = request.args.get('view_uri')

    view = mod_view.retrieve_view(rq_uri, view_uri)
    # print "\nVIEW:", view
    # badge = "<span class='badge alert-primary'><strong>{}</strong></span>";
    details = """
    <div class="panel panel-primary">
        <div class="panel-heading" id="inspect_lens_lens_details_col">
    """
    details += "<div class='row'><div class='col-md-6'>"

    details += '<h4>Final Integration Lens</h4>'
    details += "</div><div class ='col-md-6'>"
    details += '<h4>Property Selection </h4>'
    details += "</div></div> </div>"

    details += """<div class="panel-body">"""
    details += "<div class='row'><div class='col-md-6'>"
    for g in view['view_lens']:
        details += '- ' + get_URI_local_name(g).replace('_', ' ') +'<br/>'

    # datasets_bag = map(lambda x: x[0], view['view_filter_matrix'][1:])
    # datasets = list(set(datasets_bag))

    details += "</div><div class ='col-md-6'>"
    # for d in set(datasets):
    #     details += '<strong>' + get_URI_local_name(d) + '</strong><br/>'
    #     details += '- '
    #     for f in view['view_filter_matrix'][1:]:
    #         if f[0] == d:
    #             details += get_URI_local_name(f[1]) + ', '
    #     details += '<br/>'
    list_pred = []

    # print view

    for row in view['view_filter_matrix'][1:]:
        dataset_uri = row[0]
        dataset = get_URI_local_name(dataset_uri)
        details += '<strong>' + dataset
        if str(row[1]) != '':
            entityType_uri = row[1]
            entityType = get_URI_local_name(entityType_uri)
            if entityType is None:
                entityType = ""
            details += ' | ' + entityType
        else:
            entityType_uri = ''
            entityType = ''

        predicatesList = str(row[2]).split(', ')
        predicatesNames = []
        if predicatesList != ['']:
            for pred_uri in predicatesList:
                pred = get_URI_local_name(pred_uri)
                list_pred += ['<li class="list-group-item" style="background-color:lightblue"' \
                             + 'pred_uri="' + pred_uri \
                             + '" graph_uri="' + dataset_uri \
                             + '" type_uri="' + entityType_uri \
                             + '"><span class="list-group-item-heading"><b>' \
                             + dataset + ' | ' + entityType + '</b>: ' + pred + '</span></li>']
                predicatesNames += [pred]
            # predicatesList = map(lambda x: get_URI_local_name(x), predicatesList)
            predicates = reduce(lambda x, y: x + ', ' + y ,predicatesNames)
            details += '</strong><br/> - ' + predicates + '<br/>'

        predicatesList = str(row[3]).split(', ')
        predicatesNames = []
        if predicatesList != ['']:
            for pred_uri in predicatesList:
                pred = get_URI_local_name(pred_uri)
                if pred is None:
                    pred = ""
                list_pred += ['<li class="list-group-item" style="background-color:lightblue"' \
                    + ' pred_uri="' + pred_uri \
                    + '" graph_uri="' + dataset_uri \
                    + '" type_uri="' + entityType_uri \
                    + '"><span class="list-group-item-heading"><b>' \
                    + dataset + ' | ' + entityType + '</b>: ' + pred + '</span></li>']
                predicatesNames += [pred]
            # predicatesNames = map(lambda x: get_URI_local_name(x), predicatesList)
            predicates = reduce(lambda x, y: x + ', ' + y ,predicatesNames)
            details += ' - Opt: ' + predicates + '<br/>'


    details += "</div></div></div></div>"

    for i in range(1,len(view['view_filter_matrix'])):
        filter = view['view_filter_matrix'][i]
        # print get_URI_local_name(filter[0]), get_URI_local_name(filter[1])
        view['view_filter_matrix'][i] += [get_URI_local_name(filter[0]), get_URI_local_name(filter[1])]

    view['details'] = details

    view['list_pred'] = list_pred
    # print list_pred

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

    if (mode == 'added'):
        style = 'background-color:lightblue'
    else:
        style = ''

    if (mode == 'view'):
        mode = 'added'

    query = Qry.get_types_per_graph(rq_uri, mode)

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
    try:
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
    except Exception as err:
        # print err.message[1]
        # (a,b) = err.message
        print type(err.message)
        return str(err.message[1])


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
    uri = request.args.get('uri', '')

    if typeDel == 'idea':
        if len(str(uri).strip()) > 0:
            adm.drop_a_research_question(uri, display=True, activated=True)
        else:
            print 'I am deleting...'
            adm.drop_all_research_questions(display=True, activated=True)
    elif typeDel == 'linkset':
        adm.drop_linksets(display=True, activated=True)
    elif typeDel == 'lens':
        adm.drop_lenses(display=True, activated=True)
    # elif typeDel == 'view':
    #     result = ''

    # SEND BAK RESULTS
    return 'done'


@app.route('/exportAlignment')
def exportAlignment():
    graph_uri = request.args.get('graph_uri', '')
    try:
        print "\n before:", graph_uri
        result = Ex.export_flat_alignment(graph_uri)
        print "\n after:", result

    except Exception as error:
        print "AN ERROR OCCURRED: ", error
        result = json.dumps({'message':str(error.message), 'result':None})

    return json.dumps(result)


@app.route('/deleteLinkset')
def deleteLinkset():
    rq_uri = request.args.get('rq_uri', '')
    linkset_uri = request.args.get('linkset_uri', '')
    mode = request.args.get('mode', '')

    try:
        if mode == 'check':

            query = Qry.check_graph_dependencies_rq(rq_uri, linkset_uri)
            result = sparql(query, strip=True)
            print ">>>> CHECKED: ", result, len(result) #, len(result[0])
            if (len(result) > 0) and (len(result[0]) > 0): #result is not empty [{}]
                dependencies = 'The following dependencies need to be deleted first:</br>'
                for r in result:
                    dependencies += r['type_label']['value'] + ': ' + r['uri_stripped']['value'] + '</br>'
                print dependencies
                return json.dumps({'message': 'Check Dependencies', 'result': dependencies})
            else:
                return json.dumps({'message':'OK', 'result':None})
            # return json.dumps({'message':'OK', 'result':None})

        elif mode == 'delete':
            print ">>>> TO DELETE:"
            query = adm.delete_linkset_rq(rq_uri, linkset_uri)
            print "CONDITIONAL DELETE QUERY:", query
            if Svr.settings[St.stardog_version] == "COMPATIBLE":
                result = sparql(query, strip=False)
            else:
                result = sparql(query, strip=False, endpoint_url=UPDATE_URL)
            # result = sparql(query)
            print ">>>> DELETION RESULT:", result
            return json.dumps({'message': 'Linkset successfully deleted', 'result': 'OK'})

        else:
            return json.dumps({'message':'Invalid mode.', 'result':None})

    except Exception as error:
        print "AN ERROR OCCURRED: ", error
        return json.dumps({'message':str(error.message), 'result':None})


@app.route('/deleteLens')
def deleteLens():
    rq_uri = request.args.get('rq_uri', '')
    lens_uri = request.args.get('lens_uri', '')
    mode = request.args.get('mode', '')

    try:
        if mode == 'check':
            query = Qry.check_graph_dependencies_rq(rq_uri, lens_uri)
            result = sparql(query, strip=True)
            print ">>>> CHECKED: ", result, len(result) #, len(result[0])
            if (len(result) > 0) and (len(result[0]) > 0): #result is not empty [{}]
                dependencies = 'The following dependencies need to be deleted first:</br>'
                for r in result:
                    dependencies += r['type_label']['value'] + ': ' + r['uri_stripped']['value'] + '</br>'
                print dependencies
                return json.dumps({'message': 'Check Dependencies', 'result': dependencies})
            else:
                return json.dumps({'message':'OK', 'result':None})
            # return json.dumps({'message':'OK', 'result':None})

        elif mode == 'delete':
            print ">>>> TO DELETE:"
            query = adm.delete_lens_rq(rq_uri, lens_uri)
            print "CONDITIONAL DELETE QUERY:", query
            if Svr.settings[St.stardog_version] == "COMPATIBLE":
                result = sparql(query, strip=False)
            else:
                result = sparql(query, strip=False, endpoint_url=UPDATE_URL)
            print ">>>> DELETION RESULT:", result
            return json.dumps({'message': 'Lens successfully deleted', 'result': 'OK'})

        else:
            return json.dumps({'message':'Invalid mode.', 'result':None})

    except Exception as error:
        print "AN ERROR OCCURRED: ", error
        return json.dumps({'message':str(error.message), 'result':None})



@app.route('/deleteFilter')
def deleteFilter():
    rq_uri = request.args.get('rq_uri', '')
    filter_uri = request.args.get('filter_uri', '')
    try:
        query = Qry.get_delete_filter(rq_uri, filter_uri)

        if Svr.settings[St.stardog_version] == "COMPATIBLE":
            result = sparql(query, strip=False)
        else:
            result = sparql(query, strip=False, endpoint_url=UPDATE_URL)

        print ">>>> DELETION RESULT:", result
        return json.dumps({'message': 'Filter successfully deleted', 'result': 'OK'})

    except Exception as error:
        print "AN ERROR OCCURRED: ", error
        return json.dumps({'message':str(error.message), 'result':None})


@app.route('/deleteValidation')
def deleteValidation():
    rq_uri = request.args.get('rq_uri', '')
    graph_uri = request.args.get('graph_uri', '')
    singleton_uri = request.args.get('singleton_uri', '')

    try:
        query = Qry.get_delete_validation(rq_uri, graph_uri, singleton_uri)

        if Svr.settings[St.stardog_version] == "COMPATIBLE":
            result = sparql(query, strip=False)
        else:
            result = sparql(query, strip=False, endpoint_url=UPDATE_URL)

        print ">>>> DELETION RESULT:", result
        return json.dumps({'message': 'Validation successfully deleted', 'result': 'OK'})

    except Exception as error:
        print "AN ERROR OCCURRED: ", error
        return json.dumps({'message':str(error.message), 'result':None})




@app.route('/deleteView')
def deleteView():
    rq_uri = request.args.get('rq_uri', '')
    view_uri = request.args.get('view_uri', '')
    mode = request.args.get('mode', '')

    try:
        if mode == 'delete':
            print ">>>> TO DELETE:"
            query = Qry.delete_view_rq(rq_uri, view_uri)
            print query

            # endpoint_url=UPDATE_URL works for stardog 5
            result = sparql(query, strip=False, endpoint_url=UPDATE_URL)
            # for stardog 4it works without endpoint_url=UPDATE_URL
            if (result != None) or (str(result) == ''):
                result = sparql(query, strip=False)

            print ">>>> DELETION RESULT:", result
            return json.dumps({'message': 'View successfully deleted', 'result': 'OK'})

        else:
            return json.dumps({'message':'Invalid mode.', 'result':None})

    except Exception as error:
        print "AN ERROR OCCURRED: ", error
        return json.dumps({'message':str(error.message), 'result':None})


@app.route('/updateViewLabel')
def updateViewLabel():
    rq_uri = request.args.get('rq_uri', '')
    view_uri = request.args.get('view_uri', '')
    view_label = request.args.get('view_label', '')

    try:
        query = Qry.update_view_label_rq(rq_uri, view_uri, view_label)
        print query
        result = sparql(query, strip=False)
        print ">>>> RESULT:", result
        return json.dumps({'message': 'View successfully updated', 'result': 'OK'})

    except Exception as error:
        print "AN ERROR OCCURRED: ", error
        return json.dumps({'message':str(error.message), 'result':None})


@app.route('/updateLabel')
def updateLabel():
    rq_uri = request.args.get('rq_uri', '')
    graph_uri = request.args.get('graph_uri', '')
    label = request.args.get('label', '')

    try:
        query = Qry.update_label_rq(rq_uri, graph_uri, label)
        print query
        result = sparql(query, strip=False)
        print ">>>> RESULT:", result
        return json.dumps({'message': 'Label successfully updated', 'result': 'OK'})

    except Exception as error:
        print "AN ERROR OCCURRED: ", error
        return json.dumps({'message':str(error.message), 'result':None})


@app.route('/convertCSVToRDF')
def convertCSVToRDF():
    filePath = request.args.get('file', '')
    separator = request.args.get('separator', '')
    database = request.args.get('database', '')
    entity_type = request.args.get('entity_type', '')
    rdftype = map(int, request.args.getlist('rdftype[]'))
    subject_id = request.args.get('subject_id', None)
    print subject_id

    # print subject_id, rdftype

    converter = CSV.CSV(database=database, is_trig=True, file_to_convert=filePath,
            separator=separator, entity_type=entity_type,
            rdftype=rdftype if rdftype != [] else None,
            subject_id = int(subject_id) if subject_id != '' else None,
            field_metadata=None)

    return jsonify({'batch': converter.bat_file, 'data': converter.outputPath, 'schema': converter.outputMetaPath})


# @app.route('/readFileSample')
# def readFileSample():
#     filePath = request.args.get('file', '')
#     # result = readAndReturnSample(filePath)
#     result = ""
#     return json.dumps(result)


@app.route('/importConvertedDataset')
def importConvertedDataset():
    filePath = request.args.get('file', '')
    # result = import(filePath)
    result = ""
    return json.dumps(result)


@app.route('/viewSampleFile')
def viewSampleFile():
    print "VIEW SAMPLE FILE"
    filePath = request.args.get('file', '')
    size = request.args.get('size', '10')
    return json.dumps(CSV.CSV.view_file(filePath, int(size)))


@app.route('/viewSampleRDFFile')
def viewSampleRDFFile():
    print "VIEW RDF SAMPLE FILE"
    filePath = request.args.get('file', '')
    return json.dumps(CSV.CSV.view_data(filePath))


@app.route('/headerExtractor', methods=['POST'])
def headerExtractor():
    print "HEADER EXTRACTOR"
    header_line = request.form['header_line']
    separator = request.form['separator']
    # print "HEADER:[{}]\nSEPARATOR: [{}]".format(header_line, separator)
    header_list = CSV.CSV.extractor(header_line, separator)
    header = ""
    for i in range(len(header_list)):
        header += "<option>{}</option>".format(header_list[i])
    # print header
    return header


@app.route('/loadGraph')
def loadGraph():
    batch_file = request.args.get('batch_file', '')
    return json.dumps(Ut.batch_load(batch_file))


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


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
    # print "ENDPOINT_URL", ENDPOINT_URL

    result = requests.post(endpoint_url, data={'query': query, 'reasoning': REASONING_TYPE}, headers=QUERY_HEADERS,
                           timeout=None)
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
        if "results" in result_dict:
            return result_dict['results']['bindings']
        elif "boolean" in result_dict:
            return result_dict['boolean']
        else:
            print "NO RESPONSE FROM THE SERVER"
            return "true"


def strip_dict(result_dict):
    new_results = []
    for r in result_dict['results']['bindings']:
        new_result = {}
        for k, v in r.items():
            # print k, v
            if v['type'] == 'uri' and not k+'_label' in r.keys():
                new_result[k+'_label'] = {}
                new_result[k+'_label']['type'] = 'literal'
                # temp = v['value']
                # temp = temp[temp.rfind('/')+1:]
                # temp = temp[temp.rfind('#')+1:]
                # new_result[k+'_label']['value'] = temp
                new_result[k + '_label']['value'] = Ut.get_uri_local_name(v['value'], sep=" / ")


            elif not k+'_label' in r.keys():
                new_result[k+'_label'] = {}
                new_result[k+'_label']['type'] = 'literal'
                # print "!!!!!!!!!!!!", v['type'], k, v
                # if 'datatype' in v:
                if ('datatype' in v) and (v['datatype'] == "http://www.w3.org/2001/XMLSchema#decimal"):
                    new_result[k + '_label']['value'] =v['value']
                else:
                    new_result[k+'_label']['value'] =  Ut.pipe_split(v['value'], sep=" / ")


            # print new_result[k + '_label']['value']
            new_result[k+'_stripped'] = {}
            new_result[k+'_stripped']['type'] = 'literal'
            # temp = v['value']
            # temp = temp[temp.rfind('/')+1:]
            # temp = temp[temp.rfind('#')+1:]
            if k == 'uri':  ## specially for removing _ when var name is uri
                new_result[k+'_stripped']['value'] = new_result[k + '_label']['value'].replace('_',' ')
            else:
                new_result[k+'_stripped']['value'] = new_result[k + '_label']['value']

            new_result[k] = v

        new_results.append(new_result)
    return new_results


# TODO Deprecated because its been updated with optional functionality
def sparql_xml_to_matrix2(query):

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

    # if query.lower().__contains__("optional") is True:
    #     message = "MATRIX DOES NOT YET DEAL WITH OPTIONAL"
    #     print message
    #     return None

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

    # if query.lower().__contains__("optional") is True:
    #     message = "MATRIX DOES NOT YET DEAL WITH OPTIONAL"
    #     return {St.message: message, St.result: None}

    response = endpoint(query)
    logger.info("1. RESPONSE OBTAINED")
    # print response[St.result]

    # DISPLAYING THE RESULT
    # print "RESPONSE:", response

    if response is not None:

        if len(response) == 0:
            message = "NO RESULT FOR THE QUERY:"
            return None

        logger.info("2. RESPONSE IS NOT ''NONE''")

        if True:
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

            # >>> SINGLE RESULT
            if type(results) is collections.OrderedDict:

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
                                # print "value:", value
                                data = value[i]
                                index = name_index[data['@name']]
                                item = value[index].items()[1][1]
                                # print data['@name'], name_index[data['@name']]

                            elif type(value) is collections.OrderedDict:
                                index = name_index[value['@name']]
                                if value.items()[i][0] != '@name':
                                    item = value.items()[i][1]
                                    # print "Collection:", value.items()[i][0]
                                else:
                                    item = ""

                            if type(item) is collections.OrderedDict:
                                print "Data is a collection"
                                # print "{} was inserted".format(data.items()[1][1])
                                matrix[1][index] = item.items()[1][1]
                            else:
                                # print "data is regular"
                                # print "{} was inserted".format(data)
                                matrix[1][index] = item
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
                                item = value.items()[1][1]
                                matrix[row][0] = item
                    else:
                        for key, value in result.items():
                            # COLUMNS
                            # print type(value)
                            row += 1
                            # value is a list
                            # for c in range(variables_size):
                            for data in value:
                                if type(data) is collections.OrderedDict:

                                    # print row, c
                                    # print value[c].items()[1][1]
                                    # data = value[c]
                                    # print data['@name'], name_index[data['@name']]
                                    get_index = data['@name']
                                    index = name_index[get_index]
                                    # print index, type(data)
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
            return matrix

        # except Exception as err:
        #     message = "\nUNACCEPTED ERROR IN THE RESPONSE."
        #     print message
        #     return {St.message: err, St.result: None}

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

        elif str(err).__contains__("timeout") is True:
            print "Query execution cancelled: Execution time exceeded query timeout"
            return "Timeout"

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
