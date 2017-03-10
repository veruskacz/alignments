from flask import render_template, g, request, jsonify, make_response
from SPARQLWrapper import SPARQLWrapper
import logging
import requests
import json
from app import app
import uuid
import pprint

ENDPOINT_URL = 'http://localhost:5820/risis/query'
UPDATE_URL = 'http://localhost:5820/risis/update'

REASONING_TYPE = 'SL'

log = app.logger
log.setLevel(logging.DEBUG)

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

@app.route('/print')
def prints():
    print "Hello"
    return "Hello"


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

    query = PREFIXES + """
    select distinct ?sub ?pred ?obj
    {
        GRAPH <""" + graph_uri + """>
        { ?sub ?pred ?obj }
        GRAPH ?g
        { ?pred ?p ?o }

    } limit 80
    """
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

    query = PREFIXES + """
    Select distinct ?pred ?obj
    {
      GRAPH ?graph
  	   {
        <""" + singleton_uri + """> ?pred ?obj
       }
    }
    """
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
                print k, v
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
