# -*- coding: utf-8 -*-
# coding=utf-8

import os
import codecs
import rdflib
import datetime
import re as regex
import cStringIO as Buffer
import Alignments.Query as Qry
import Alignments.Utility as Ut
import Alignments.Settings as St
import Alignments.NameSpace as Ns
import Alignments.Server_Settings as Svr
from kitchen.text.converters import to_unicode, to_bytes
from Alignments.UserActivities.Import_Data import download_stardog_data


# ALIGNMENT FOR VISUALISATION
# TODO: NEEDS TO BE UPDATED WITH OFSET IN CASE OF LARGE ALIGNMENTS.
# TODO: THE download_stardog_data FUNCTIION FROM import_data.py COULD BE THE WAY TO GO
def export_alignment_all(alignment, directory=None, limit=5000):

    directory = os.path.join(directory, "")
    print directory
    if os.path.isdir(os.path.dirname(directory)) is False or os.path.exists(directory) is False:
        print "CREATING THE DIRECTORY"
        os.mkdir(os.path.dirname(directory))

    # COMMENT THE LINKSET OIT IF IT IS EQUAL TO NONE

    # This function returns all the links + some metadata about the alignment.
    # METADATA: source dataset, target dataset and mechanism

    use = alignment
    alignment = str(alignment).strip()
    row_alignment = alignment
    alignment = alignment if Ut.is_nt_format(alignment) is True else "<{}>".format(alignment)

    # ****************************************************
    # 1. GET THE METADATA OF THE ALIGNMENT: THE QUERY
    # ****************************************************
    meta = """
    PREFIX ll: <{0}>
    CONSTRUCT {{ {1} ?y ?z. ?z ?p ?o . }}
    WHERE
    {{
        {1} ?y ?z .
        OPTIONAL{{ ?z ?p ?o . }}
        OPTIONAL{{ ?O ?Q ?R . }}
    }} order by ?y
    """.format(Ns.alivocab, alignment)
    # print meta

    # GET THE METADATA OF THE ALIGNMENT: RUN THE QUERY
    meta_construct = Qry.endpointconstruct(meta, clean=False)
    meta_construct = meta_construct.replace("{", "").replace("}", "")
    with open(os.path.join(directory, "metadata.ttl"), "wb") as metadata:
        metadata.write(meta_construct)
    # print meta_construct

    # ****************************************************
    # 2. GET THE CORRESPONDENCES OF THE LINKSET
    # ****************************************************
    # CONSTRUCT QUERY FOR EXTRACTING HE CORRESPONDENCES
    comment = "" if limit else "#"
    query = """
        PREFIX ll: <{}>
        CONSTRUCT {{ ?x ?y ?z }}
        WHERE
        {{
            GRAPH {}
            {{
                ?x ?y ?z
            }}
        }} order by ?x {}LIMIT {}
        """.format(Ns.alivocab, alignment, comment, limit)
    # print query

    # FIRE THE CONSTRUCT FOR CORRESPONDENCES AGAINST THE TRIPLE STORE
    alignment_construct = Qry.endpointconstruct(query, clean=False)
    if alignment_construct:
        alignment_construct = alignment_construct.replace("{", "{}\n{{".format(alignment))
    # print alignment_construct
    with open(os.path.join(directory, "linkset.trig"), "wb") as links:
        links.write(alignment_construct)

    # ****************************************************
    # 3. GET THE METADATA CORRESPONDENCES' PREDICATES
    # ****************************************************
    singleton_graph_uri = Ut.from_alignment2singleton(alignment)
    singleton_query = """
    PREFIX ll: <{0}>
    PREFIX singletons: <{1}>
    CONSTRUCT {{ ?predicate ?x  ?y }}
    WHERE
    {{
        {{
            SELECT ?predicate
            {{
                GRAPH {2}
                {{
                    ?subject ?predicate ?object
                }}
            }} order by ?x {3}LIMIT {4}
        }}
        GRAPH {5}
        {{
            ?predicate ?x  ?y
        }}
    }}
    """.format(Ns.alivocab, Ns.singletons, alignment, comment, limit, singleton_graph_uri)
    # print singleton_query

    # FIRE THE CONSTRUCT FOR SINGLETON AGAINST THE TRIPLE STORE
    singleton_construct = Qry.endpointconstruct(singleton_query, clean=False)
    if singleton_construct:
        singleton_construct = singleton_construct.replace("{", "{}\n{{".format(singleton_graph_uri))
    # print singleton_construct
    with open(os.path.join(directory, "singletons.trig"), "wb") as singletons:
        singletons.write(singleton_construct)

    # LOAD THE METADATA USING RDFLIB
    sg = rdflib.Graph()
    sg.parse(data=meta_construct, format="turtle")

    # EXTRACT FROM THE RESPONSE: THE SOURCE AND TARGET DATASETS AND THE ALIGNMENT
    sbj = rdflib.URIRef(use)
    triples_uri = rdflib.URIRef("http://rdfs.org/ns/void#triples")

    # EXTRACT THE ALIGNMENT TYPE
    triples = ""
    for item in sg.objects(sbj, triples_uri):
        triples = item
        print "TRIPLES: ", triples

    if alignment_construct is not None:
        links = "### TRIPLE COUNT: {}\n### LINKSET: {}\n".format(triples, alignment) + alignment_construct
        links = links.replace("{", "").replace("}", "")
    message = "You have just downloaded the graph [{}] which contains [{}] correspondences. ".format(
        row_alignment, triples)

    host = Svr.settings[St.stardog_host_name]
    endpoint = b"http://{}/annex/{}/sparql/query?".format(host, Svr.settings[St.database])

    local_name = Ut.get_uri_local_name_plus(alignment)
    file_at_parent_directory = os.path.join(os.path.abspath(
        os.path.join(directory, os.pardir)), "{}.zip".format(local_name))

    zipped_file = Ut.zip_folder(directory, output_file_path=file_at_parent_directory)
    print "\t>>> THE ZIPPED FILE IS LOCATED AT:\n\t\t- {}".format(zipped_file)

    # result = result
    # print result
    print "Done with graph: {}".format(alignment)

    # return {'result': {
    #     "generic_metadata": meta_construct,
    #     'specific_metadata': singleton_construct,
    #     'data': alignment_construct}, 'message': message}

    return {'result': zipped_file, 'message': message}


# FLAT ALIGNMENT
def export_flat_alignment(alignment):

    print "Export for: {}".format(alignment)
    alignment = str(alignment).strip()
    row_alignment = alignment
    alignment = alignment if Ut.is_nt_format(alignment) is True else "<{}>".format(alignment)

    # CONSTRUCT QUERY
    query = """
    PREFIX ll: <{}>
    CONSTRUCT {{ ?x ll:mySameAs ?z }}
    WHERE
    {{
        GRAPH {}
        {{
            ?x ?y ?z
        }}
    }} order by ?x
    """.format(Ns.alivocab, alignment)
    # print query
    # FIRE THE CONSTRUCT AGAINST THE TRIPLE STORE
    alignment_construct = Qry.endpointconstruct(query)

    # REMOVE EMPTY LINES
    # COMMA IS COUNTED WHENEVER THERE ARE MORE OBJECTS FOR THE SUBJECT
    triples = len(regex.findall('ll:mySameAs', alignment_construct)) + len(regex.findall(',', alignment_construct))
    alignment_construct = "\n".join([line for line in alignment_construct.splitlines() if line.strip()])
    alignment_construct = alignment_construct.replace("{", "{}\n{{".format(alignment))

    # RESULTS
    result = "### TRIPLE COUNT: {0}\n### LINKSET: {1}\n".format(triples, alignment) + alignment_construct
    message = "You have just downloaded the graph [{}] which contains [{}] correspondences. ".format(
        row_alignment, triples)

    return {'result': result, 'message': message, "triples": triples}


# EXPORT ALIGNMENT WITH GENERIC METADATA
def export_flat_alignment_and_metadata(alignment):

    flat = export_flat_alignment(alignment)

    alignment = str(alignment).strip()
    row_alignment = alignment
    alignment = alignment if Ut.is_nt_format(alignment) is True else "<{}>".format(alignment)
    # CONSTRUCT QUERY
    query = """
    PREFIX ll: <{0}>
    PREFIX linkset: <{1}>
    PREFIX lens: <{2}>
    PREFIX singletons: <{3}>
    CONSTRUCT
    {{
        ?alignment ?pred  ?obj .
        ?obj  ?predicate ?object .
    }}
    WHERE
    {{
        BIND ({4} AS ?alignment)
        # THE METADATA
        ?alignment  ?pred  ?obj .
        OPTIONAL {{ ?obj  ?predicate ?object . }}
    }} #LIMIT 10
    """.format(Ns.alivocab, Ns.linkset, Ns.lens, Ns.singletons, alignment)
    # print query

    # FIRE THE CONSTRUCT AGAINST THE TRIPLE STORE
    alignment_construct = Qry.endpointconstruct(query, clean=False)

    # REMOVE EMPTY LINES
    triples = flat["triples"]
    # triples = len(re.findall('ll:mySameAs', alignment_construct))
    alignment_construct = "\n".join([line for line in alignment_construct.splitlines() if line.strip()]) + "\n\n" + \
                          flat['result']

    result = "### GENERIC METADATA FOR \n### LINKSET: {}\n\n{}".format(alignment, alignment_construct)
    message = "You have just downloaded the graph [{}] which contains [{}] correspondences. ".format(
        row_alignment, triples)
    print result
    return {'result': result, 'message': message}


# ALIGNMENT FOR VISUALISATION
def export_alignment(alignment, limit=5000):

    # COMMENT THE LINKSET IF IT IS EQUAL TO NONE

    # This function returns all the links + some metadata about the alignment.
    # METADATA: source dataset, target dataset and mechanism

    use = alignment
    alignment = str(alignment).strip()
    row_alignment = alignment
    alignment = alignment if Ut.is_nt_format(alignment) is True else "<{}>".format(alignment)
    src_dataset = None
    trg_dataset = None
    lens_targets = []
    mec_dataset = None
    rdf_type = None

    # GET THE METADATA OF THE ALIGNMENT: THE QUERY
    meta = """
    PREFIX ll: <{0}>
    CONSTRUCT {{ {1} ?y ?z. ?z ?p ?o . }}
    WHERE
    {{
        {1} ?y ?z .
        #?z ?p ?o .
    }} order by ?y
    """.format(Ns.alivocab, alignment)
    # print meta

    # GET THE METADATA OF THE ALIGNMENT: RUN THE QUERY
    meta_construct = Qry.endpointconstruct(meta, clean=False)
    meta_construct = meta_construct.replace("{", "").replace("}", "")
    # print meta_construct

    # LOAD THE METADATA USING RDFLIB
    sg = rdflib.Graph()
    sg.parse(data=meta_construct, format="turtle")

    # EXTRACT FROM THE RESPONSE: THE SOURCE AND TARGET DATASETS AND THE ALIGNMENT
    sbj = rdflib.URIRef(use)
    source = rdflib.URIRef("http://rdfs.org/ns/void#subjectsTarget")
    target = rdflib.URIRef("http://rdfs.org/ns/void#objectsTarget")
    lens_uri_targets = rdflib.URIRef("http://rdfs.org/ns/void#target")
    rdf_uri_type = rdflib.URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type")
    mechanism = rdflib.URIRef("http://risis.eu/alignment/predicate/alignsMechanism")

    # EXTRACT THE ALIGNMENT TYPE
    for item in sg.objects(sbj, rdf_uri_type):
        rdf_type = item
        print "TYPE: ", rdf_type

    if str(rdf_type) == Ns.lens_type:

        # EXTRACT THE SOURCE DATASET
        for item in sg.objects(sbj, lens_uri_targets):
            lens_targets += [str(item)]
        print "{} TARGETS in {}".format(len(lens_targets), alignment)
        for trg_item in lens_targets:
            print "\t- {}".format(trg_item)

    else:

        # EXTRACT THE SOURCE DATASET
        for item in sg.objects(sbj, source):
            src_dataset = item

        # EXTRACT THE TARGET DATASET
        for item in sg.objects(sbj, target):
            trg_dataset = item

        # EXTRACT THE MECHANISM USED FOR THIS ALIGNMENT
        for item in sg.objects(sbj, mechanism):
            mec_dataset = item

    # CONSTRUCT QUERY FOR EXTRACTING HE CORRESPONDENCES
    comment = "" if limit else "#"
    query = """
    PREFIX ll: <{}>
    CONSTRUCT {{ ?x ?y ?z }}
    WHERE
    {{
        GRAPH {}
        {{
            ?x ?y ?z
        }}
    }} order by ?x {}LIMIT {}
    """.format(Ns.alivocab, alignment, comment, limit)
    # print query

    # FIRE THE CONSTRUCT FOR CORRESPONDENCES AGAINST THE TRIPLE STORE
    alignment_construct = Qry.endpointconstruct(query, clean=False)

    triples = 0
    links = None
    # RESULTS

    if alignment_construct is not None:
        links = "### TRIPLE COUNT: {}\n### LINKSET: {}\n".format(triples, alignment) + alignment_construct
        links = links.replace("{", "").replace("}", "")
    message = "You have just downloaded the graph [{}] which contains [{}] correspondences. ".format(
        row_alignment, triples)

    # result = result
    # print result
    print "Done with graph: {}".format(alignment)
    return {
        "type": rdf_type,
        'result': links,
        'message': message,
        'source': src_dataset,
        "target": trg_dataset,
        "lens_targets": lens_targets,
        'mechanism': mec_dataset}


# ALIGNMENT FOR VISUALISATION: THE MAIN FUNCTION
def visualise(graphs, directory, credential):

    # production_directory = "/scratch/risis/data/rdf-data/links"
    # directory = production_directory

    writer = Buffer.StringIO()
    g = rdflib.Graph()
    source = {}
    target = {}
    attribute = {}
    src_count = 0
    trg_count = 0
    prd_count = 0
    singletons = {}
    triples = 0
    datasets = [None, None]
    code = 0

    for graph in graphs:
        # print graph

        code += 1
        links = export_alignment(graph)

        # THE MECHANISM USED
        mechanism = links['mechanism']
        # print "mechanism", mechanism

        # THE SOURCE AND TARGET DATASETS
        if datasets == [None, None]:

            if str(links["type"]) == Ns.lens_type:
                datasets = links["lens_targets"]
            else:
                datasets = [links["source"], links['target']]

        # MAKE SURE THAT FOR ALL ALIGNMENT, THE SOURCE DATASET AND TARGET DATASETS ARE THE SAME
        elif datasets != [links["source"], links['target']]:
            print "No visualisation for different set of source-target"
            return None

        print "DATASETS: ", datasets

        # print links['result']
        if links['result'] is not None:

            # LOAD THE CORRESPONDENCES TO THE MAIN GRAPH
            g.parse(data=links['result'], format="turtle")

            # INDEX THE CORRESPONDENCES USING THE SINGLETON PROPERTY
            sg = rdflib.Graph()
            sg.parse(data=links['result'], format="turtle")
            triples += len(sg)
            for subject, predicate, obj in sg.triples((None, None, None)):
                mech = "{}_{}".format(mechanism, code)
                if predicate not in singletons:
                    singletons[predicate] = [mech]
                elif mech not in singletons[mech]:
                    singletons[mech] += [mech]

    # WRITING THE FILE
    count = 0
    writer.write("PREFIX ll: <{}>\n".format(Ns.alivocab))
    writer.write("PREFIX rdf: <{}>\n".format(Ns.rdf))
    writer.write("PREFIX link: <http://risis.eu/alignment/link/>\n")
    writer.write("PREFIX plot: <http://risis.eu/alignment/plot/>\n")
    writer.write("PREFIX mechanism: <{}>\n".format(Ns.mechanism))

    print "size: ", len(datasets)
    if len(datasets) > 2:
        name = hash("".join(datasets))
        name = "{}".format(str(name).replace("-", "P")) if str(name).__contains__("-") else "P{}".format(name)
    else:
        name = "{}_{}".format(Ut.get_uri_local_name(datasets[0]), Ut.get_uri_local_name(datasets[1]))
    print "NAME: ", name

    # DROPPING GRAPH IF IT ALREADY EXISTS
    writer.write(
        "\n#DROP SILENT GRAPH plot:{} ;\n".format(name))

    # INSERT NEW DATA
    writer.write("#INSERT DATA\n#{")
    writer.write("\n\tplot:{}\n".format(name))
    writer.write("\t{")

    # GOING THROUGH ALL CORRESPONDENCES OF HE MAIN GRAPH (MERGED)
    for subject, predicate, obj in g.triples((None, None, None)):

        count += 1

        # INDEX THE SOURCE CORRESPONDENCE
        if subject not in source:
            src_count += 1
            source[subject] = src_count

        # INDEX THE TARGET CORRESPONDENCE
        if obj not in target:
            trg_count += 1
            target[obj] = trg_count

        # INDEX THE PAIR
        pre_code = "{}_{}".format(source[subject], target[obj])
        if pre_code not in attribute:
            prd_count += 1
            attribute[pre_code] = prd_count

        # WRITE THE PLOT COORDINATE AND ITS METADATA
        writer.write("\n\t\t### [ {} ]\n".format(count))
        writer.write("\t\t{}\n".format(predicate).replace(Ns.alivocab, "ll:"))
        writer.write("\t\t\tlink:source     {} ;\n".format(source[subject]))
        writer.write("\t\t\tlink:target     {} ;\n".format(target[obj]))
        writer.write("\t\t\tlink:source_uri <{}> ;\n".format(subject))
        writer.write("\t\t\tlink:target_uri <{}> ;\n".format(obj))

        for value in singletons[predicate]:
            if str(value) != "None_1":
                writer.write("\t\t\tlink:mechanism  {} ;\n".format(value).replace(Ns.mechanism, "mechanism:"))
        writer.write("\t\t\trdf:type        link:Link .\n")
        writer.write("")
    writer.write("\t}\n#}")

    # THE PATH OF THE OUTPUT FILES

    date = datetime.date.isoformat(datetime.date.today()).replace('-', '')
    f_path = "{0}{1}{1}{2}_plots_{3}.trig".format(directory, os.path.sep, name, date)
    b_path = "{0}{1}{1}{2}_plots_{3}{4}".format(directory, os.path.sep, name, date, Ut.batch_extension())
    print "DIRECTORY:", directory

    # MAKE SURE THE FOLDER EXISTS
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
    except OSError as err:
        print "\n\t[utility_LOAD_TRIPLE_STORE:]", err
        return

    # CREATE THE FILES
    plot_writer = codecs.open(f_path, "wb", "utf-8")
    batch_writer = codecs.open(b_path, "wb", "utf-8")

    # print "3. GENERATING THE BATCH FILE TEXT"
    # enriched_graph = "{}{}_plots".format(Ns.plot, name)
    # stardog_path = '' if Ut.OPE_SYS == "windows" else Svr.settings[St.stardog_path]

    # load_text = """echo "Loading data"
    # {}stardog data add {} -g {} "{}"
    # """.format(stardog_path, Svr.DATABASE, enriched_graph, f_path)

    # GENERATE THE BATCH FILE FOR AUTOMATIC LOAD
    user = "..."
    password = "..."
    if credential is not None:
        if "user" in credential:
            user = credential["user"]
        if "password" in credential:
            password = credential["password"]

    load_text = "echo \"Loading data\"\n" \
                "/usr/local/virtuoso-opensource/bin/isql 1112 {} {} exec=\"DB.DBA.TTLP_MT (file_to_string_output" \
                "('/scratch/risis/data/rdf-data/links/Plots/{}_plots{}.trig'), '', 'http://risis.eu/converted', " \
                "256);\"".format(user, password, name, date)
    batch_writer.write(to_unicode(load_text))
    batch_writer.close()
    os.chmod(b_path, 0o777)

    # WRITE THE CORRESPONDENCES TO FILE
    plot_writer.write(writer.getvalue())
    plot_writer.close()

    print "PLOT: {}".format(f_path)
    print "BATCH: {}".format(b_path)
    print "Job Done!!!"
    # Qry.virtuoso_request(writer.getvalue())
    # print count, triples
    # file.close()

    return {'result': writer.getvalue(), 'message': "Constructed"}


# ENRICHING DATASETS WITH GADM BOUNDARIES: THE QUERY
def enrich_query(specs, limit=0, offset=0, is_count=True):

    if is_count is True:
        count_comment = ""
        get_comment = "#"
    else:
        count_comment = "#"
        get_comment = ""

    virtuoso = """
    PREFIX ll: <{0}>
    PREFIX gadm: <http://geo.risis.eu/vocabulary/gadm/>
    {1}SELECT (count(?dataset) as ?TOTAL)
    {2}CONSTRUCT
    {2}{{
    {2}    ?dataset  a <{3}> .
    {2}    ?dataset  ll:intersects ?gadm .
    {2}    #?gadm     gadm:level    ?level .
    {2}}}
    WHERE
    {{
       GRAPH <{4}>
       {{
            ?dataset {5} ?long .
            ?dataset {6} ?lat .
            BIND( xsd:double(replace(str(?long), ",", ".")) as ?longitude)
            BIND( xsd:double(replace(str(?lat), ",", ".")) as ?latitude)
            FILTER(contains(str(?longitude), ".") && contains(str(?latitude), "."))
       }}
       GRAPH <http://geo.risis.eu/gadm>
       {{
            ?gadm geo:geometry ?geo .
            ?gadm gadm:level   ?level .
            FILTER(?level = 2)
       }}
       FILTER(bif:st_intersects (?geo, bif:st_point (?longitude, ?latitude)))
    }}
    {2}LIMIT {7}
    {2}OFFSET {8}
    """.format(Ns.alivocab, count_comment, get_comment, specs[St.entity_datatype], specs[St.graph],
               specs['long_predicate'], specs['lat_predicate'], limit, offset)
    return virtuoso


# ENRICHING DATASETS WITH GADM BOUNDARIES: THE MAIN FUNCTION
def enrich(specs, directory, endpoint):

    # TODO RUN IT IF THERE IS NOT GRAPH ENRICHED WITH THE SAME NAME

    # specs[St.graph] = "http://grid.ac/20170712"
    print "ENRICHING DATA/GRAPH FROM EXPORT-ALIGNMENT"
    print "GRAPH:", specs[St.graph]
    print "ENTITY TYPE:", specs[St.entity_datatype]
    print "LAT PREDICATE:", specs[St.long_predicate]
    print "LONG PREDICATE:", specs[St.lat_predicate]
    print "FILE DIRECTORY:", directory
    name = Ut.get_uri_local_name(specs[St.graph])

    print endpoint
    data_1 = Qry.virtuoso_request("ask {{ GRAPH <{}> {{ ?x ?y ?z . }} }}".format(specs[St.graph]), endpoint)
    data_1 = regex.findall("rs:boolean[ ]*(.*)[ ]*\.", data_1["result"])
    if len(data_1) > 0:
        data_1 = data_1[0].strip() == "true"
        if data_1 is False:
            print "GRAPH: {} {}".format(specs[St.graph], "DOES NOT EXIST AT THE REMOTE VIRTUOSO SITE.")

    # CHECKING WHETHER BOTH DATASETS ARE AT THE VIRTUOSO TRIPLE STORE
    data_2 = Qry.virtuoso_request("ask {GRAPH <http://geo.risis.eu/gadm>{ ?x ?y ?z . }}", endpoint)
    data_2 = regex.findall("rs:boolean[ ]*(.*)[ ]*\.", data_2["result"])
    if len(data_2) > 0:
        data_2 = data_2[0].strip() == "true"
        if data_2 is False:
            print "GRAPH: {} {}".format(specs[St.graph], "DOES NOT EXIST AT THE REMOTE VIRTUOSO SITE.")

    if data_1 is False or data_2 is False:
        message = "BECAUSE BOTH DATASETS NEED TO BE PRESENT AT OUR TRIPLES STORE, WE ARE UNABLE TO EXECUTE THE REQUEST."
        return {St.message: message,
                St.result: 'The dataset {} '
                           'cannot be enriched with GADM boundary  at the moment.'.format(specs[St.graph])}

    total = 0
    limit = 20000
    date = datetime.date.isoformat(datetime.date.today()).replace('-', '')
    f_path = "{0}{1}{1}{2}_enriched_{3}.ttl".format(directory, os.path.sep, name, date)
    b_path = "{0}{1}{1}{2}_enriched_{3}{4}".format(directory, os.path.sep, name, date, Ut.batch_extension())

    # MAKE SURE THE FOLDER EXISTS
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
    except OSError as err:
        print "\n\t[utility_LOAD_TRIPLE_STORE:]", err
        return

    print "\n1. GETTING THE TOTAL NUMBER OF TRIPLES."
    count_query = enrich_query(specs, limit=0, offset=0, is_count=True)
    print count_query
    count_res = Qry.virtuoso_request(count_query, endpoint)
    result = count_res['result']

    # GET THE TOTAL NUMBER OF TRIPLES
    if result is None:
        print "NO RESULT FOR THIS ENRICHMENT."
        return count_res

    g = rdflib.Graph()
    g.parse(data=result, format="turtle")
    attribute = rdflib.URIRef("http://www.w3.org/2005/sparql-results#value")
    for subject, predicate, obj in g.triples((None, attribute, None)):
        total = int(obj)

    # NUMBER OF REQUEST NEEDED
    iterations = total / limit if total % limit == 0 else total / limit + 1
    print "\n2. TOTAL TRIPLES TO RETREIVE  : {} \n\tTOTAL NUMBER OF ITERATIONS : {}\n".format(total, iterations)

    writer = codecs.open(f_path, "wb", "utf-8")
    batch_writer = codecs.open(b_path, "wb", "utf-8")

    print "3. GENERATING THE BATCH FILE TEXT"
    enriched_graph = "{}_enriched".format(specs[St.graph])
    stardog_path = '' if Ut.OPE_SYS == "windows" else Svr.settings[St.stardog_path]

    load_text = """echo "Loading data"
            {}stardog data add {} -g {} "{}"
            """.format(stardog_path, Svr.settings[St.database], enriched_graph, f_path)

    batch_writer.write(to_unicode(load_text))
    batch_writer.close()

    # RUN THE ITERATIONS
    for i in range(0, iterations):

        offset = i * 20000 + 1
        print "\tROUND: {} OFFSET: {}".format(i + 1, offset)

        # print "\t\t1. GENERATING THE ENRICHMENT QUERY"
        virtuoso = enrich_query(specs, limit=limit, offset=offset, is_count=False)
        # print virtuoso
        # exit(0)
        # print Qry.virtuoso(virtuoso)["result"]

        # print "\t\t2. RUNNING THE QUERY + WRITE THE RESULT TO FILE"
        writer.write(Qry.virtuoso_request(virtuoso, endpoint)["result"])

    writer.close()
    print "\n4. RUNNING THE BATCH FILE"
    print "\tTHE DATA IS BEING LOADED OVER HTTP POST." if Svr.settings[St.split_sys] is True \
        else "\tTHE DATA IS BEING LOADED AT THE STARDOG LOCAL HOST FROM BATCH."
    # os.system(b_path)

    # RUN THE BATCH FILE
    print "\tFILE: {}".format(f_path)
    print "\tBATCH: {}\n".format(b_path)
    os.chmod(b_path, 0o777)
    Ut.batch_load(b_path)
    if os.path.exists(b_path) is True:
        os.remove(b_path)

    # TODO 1. REGISTER THE DATASET TO BE ENRICHED IF NOT YET REGISTER
    # TODO 2. ADD THE ENRICHED DATASET TO THE RESEARCH QUESTION (REGISTER).
    # TODO 3. MAYBE, CREATE THE LINKSET BETWEEN THE SOURCE AND THE RESULTING

    size = Qry.get_namedgraph_size(enriched_graph)

    print "JOB DONE...!!!!!!"

    return {St.message: "The select dataset was enriched with the GADM boundary as {}. "
                        "{} triples were created.".format(enriched_graph, size), St.result: enriched_graph}


def export_flat_alignment2(alignment):

    alignment = str(alignment).strip()
    row_alignment = alignment
    alignment = alignment if Ut.is_nt_format(alignment) is True else "<{}>".format(alignment)
    # CONSTRUCT QUERY
    query = """
    PREFIX ll: <{0}>
    PREFIX linkset: <{1}>
    PREFIX lens: <{2}>
    PREFIX singletons: <{3}>
    CONSTRUCT
    {{
        ?srcCorr  ll:mySameAs ?trgCorr .
        ?trgCorr  ll:mySameAs ?srcCorr .
        ?alignment ?pred  ?obj .
        ?obj  ?predicate ?object .
    }}
    WHERE
    {{
        BIND( {4} as ?alignment )
        # THE ALIGNMENT GRAPH WITH EXPLICIT SYMMETRY
        GRAPH ?alignment
        {{
            ?srcCorr ?singleton ?trgCorr .
        }}

         # THE METADATA
        ?alignment  ?pred  ?obj .
        OPTIONAL {{ ?obj  ?predicate ?object . }}
    }}
    """.format(Ns.alivocab, Ns.linkset, Ns.lens, Ns.singletons, alignment, )
    print query

    # FIRE THE CONSTRUCT AGAINST THE TRIPLE STORE
    alignment_construct = Qry.endpointconstruct(query)
    print alignment_construct

    # REMOVE EMPTY LINES
    triples = 0
    # triples = len(re.findall('ll:mySameAs', alignment_construct))
    # alignment_construct = "\n".join([line for line in  alignment_construct.splitlines() if line.strip()])
    result = "### TRIPLE COUNT: {}\n### LINKSET: {}\n".format(triples, alignment) + alignment_construct
    message = "You have just downloaded the graph [{}] which contains [{}] correspondences. ".format(
        row_alignment, triples)

    return {'result': result, 'message': message}


def export_flat_alignment_service(alignment):

    alignment = str(alignment).strip()
    row_alignment = alignment
    alignment = alignment if Ut.is_nt_format(alignment) is True else "<{}>".format(alignment)
    # CONSTRUCT QUERY
    query = """
    PREFIX ll: <{0}>
    PREFIX linkset: <{1}>
    PREFIX lens: <{2}>
    PREFIX singletons: <{3}>
    CONSTRUCT
    {{
        ?srcCorr  ll:mySameAs ?trgCorr .
        ?trgCorr  ll:mySameAs ?srcCorr .
    }}
    WHERE
    {{
        BIND( {4} as ?alignment )
        # THE ALIGNMENT GRAPH WITH EXPLICIT SYMMETRY
        GRAPH ?alignment
        {{
            ?srcCorr ?singleton ?trgCorr .
        }}
    }} ;

    CONSTRUCT
    {{
        ?alignment ?pred  ?obj .
        ?obj  ?predicate ?object .
    }}
    WHERE
    {{
        # THE METADATA
        BIND( {4} as ?alignment )
        ?alignment  ?pred  ?obj .
        OPTIONAL {{ ?obj  ?predicate ?object . }}
    }}

    """.format(Ns.alivocab, Ns.linkset, Ns.lens, Ns.singletons, alignment, )
    print query
    exit(0)
    # FIRE THE CONSTRUCT AGAINST THE TRIPLE STORE
    alignment_construct = Qry.endpointconstruct(query)
    # REMOVE EMPTY LINES
    triples = len(regex.findall('ll:mySameAs', alignment_construct))
    alignment_construct = "\n".join([line for line in alignment_construct.splitlines() if line.strip()])
    result = "### TRIPLE COUNT: {}\n### LINKSET: {}\n".format(triples, alignment) + alignment_construct
    message = "You have just downloaded the graph [{}] which contains [{}] correspondences. ".format(
        row_alignment, triples)
    return {'result': result, 'message': message}


def federate():
    # http://linkedgeodata.org/OSM
    query = """
    ### 1. LOADING SOURCE AND TARGET TO A TEMPORARY GRAPH
    PREFIX geo: <http://www.opengis.net/def/function/geosparql/>
    PREFIX geof: <http://www.opengis.net/def/function/geosparql/>
    PREFIX bif: <http://www.openlinksw.com/schemas/bif#>
    SELECT DISTINCT ?subject ?level
    WHERE
    {
        ### SOURCE DATASET
        service <http://sparql.sms.risis.eu>
        {
            graph <http://geo.risis.eu/gadm>
            {
                # ?subj ?pred ?obj .
                ?subject <http://www.w3.org/2003/01/geo/wgs84_pos#geometry> ?geo ;
                    <http://geo.risis.eu/vocabulary/gadm/level> ?level .
                Filter(geof:nearby (?geo, "Point(-77.03653 38.897676 )"^^geo:wktLiteral, 0.1))
            }
       }
    } limit 1000
    """
    print query

    # construct = Qry.sparql_xml_to_matrix(query)
    # Qry.display_result(query, is_activated=True)

    # print construct


def import_gadm_query(limit=0, offset=0, is_count=False):

    if is_count is True:
        count_comment = ""
        get_comment = "#"
    else:
        count_comment = "#"
        get_comment = ""

    query = """
    PREFIX gadm: <http://geo.risis.eu/vocabulary/gadm/>
    {0}SELECT (COUNT (DISTINCT ?gadm ) AS ?TOTAL)
    {1}CONSTRUCT
    {1}{{
    {1}    ?gadm geo:geometry ?geo .
    {1}    ?gadm a <{4}Boundary> .
    {1}    #?gadm gadm:level   ?level .
    {1}}}
    WHERE
    {{
        GRAPH <http://geo.risis.eu/gadm>
        {{
            ?gadm geo:geometry ?geo .
            ?gadm gadm:level   ?level .
            #FILTER(?level = 2)
        }}
    }}
    {1}LIMIT {2} OFFSET {3}
    """.format(count_comment, get_comment, limit, offset, Ns.riclass)
    # print query
    return query


def import_gadm():

    total = 0
    limit = 2000
    f_path = "C:\Users\Al\PycharmProjects\AlignmentUI\src\UploadedFiles\gadm.ttl"
    b_path = "C:\Users\Al\PycharmProjects\AlignmentUI\src\UploadedFiles\gadm{}".format(Ut.batch_extension())

    # CREATE THE WRITERS
    writer = codecs.open(f_path, "wb", "utf-8")
    batch_writer = codecs.open(b_path, "wb", "utf-8")

    # GENERATING THE BATCH FILE TEXT
    graph = "{}gadm".format(Ns.dataset)
    stardog_path = '' if Ut.OPE_SYS == "windows" else Svr.settings[St.stardog_path]
    load_text = """echo "Loading data"
                {}stardog data add {} -g {} "{}"
                """.format(stardog_path, Svr.settings[St.database], graph, f_path)
    batch_writer.write(to_unicode(load_text))
    batch_writer.close()

    print "1. GET THE TOTAL NUMBER OF TRIPLES TO LOAD"
    count_query = import_gadm_query(is_count=True)
    # print count_query
    count_res = Qry.virtuoso_request(count_query)
    result = count_res['result']
    if result is None:
        print "NO RESULT FOR THIS ENRICHMENT."
        return count_res

    print "2. PROCESSING THE COUNT RESULT"
    g = rdflib.Graph()
    g.parse(data=result, format="turtle")
    attribute = rdflib.URIRef("http://www.w3.org/2005/sparql-results#value")
    for subject, predicate, obj in g.triples((None, attribute, None)):
        total = int(obj)
    iterations = total / limit if total % limit == 0 else total / limit + 1
    print "\tTOTAL TRIPLES TO RETREIVE  : {} \n\tTOTAL NUMBER OF ITERATIONS : {}\n".format(total, iterations)

    # RUN THE ITERATIONS
    try:
        for i in range(0, iterations):

            offset = i * limit + 1
            print "ROUND: {} OFFSET: {}".format(i, offset)

            print "\tRUNNING THE QUERY"
            import_query = import_gadm_query(limit=limit, offset=offset, is_count=False)
            response = Qry.virtuoso_request(import_query)

            print "RESPONSE SIZE: ".format(response["result"])

            print "\tWRITING THE RESULT TO FILE"
            writer.write(response["result"])

            break

    except Exception as err:
        print str(err.message)

    # CLOSE THE IMPORT WRITER
    writer.close()
    print "4. RUNNING THE BATCH FILE"
    print "THE DATA IS BEING LOADED OVER HTTP POST." if Svr.settings[St.split_sys] is True \
        else "THE DATA IS BEING LOADED AT THE STARDOG LOCAL HOST FROM BATCH."
    print "PATH:", b_path
    os.system(b_path)
    print "JOB DONE!!!"


def get_bom_type(file_path):

    # path = "C:\Users\Al\Google Drive\RISIS-Project-VU\WP 7 - " \
    #        "datasets\OrgReg\OrgReg 2017 (new)\ORGREG_20170718__Entities.txt"
    # path2 = "E:\Linking2GRID\Data\OrgReg 20170718\ORGREG_20170718__Entities.txt"
    reader = open(file_path, "rb")
    line = reader.readline()

    bom_type = None
    text = None

    if line.startswith(to_bytes(codecs.BOM_BE)):
        bom_type = to_bytes(codecs.BOM_BE)
        text = "BOM_BE"
    elif line.startswith(to_bytes(codecs.BOM32_BE)):
        bom_type = to_bytes(codecs.BOM32_LE)
        text = "BOM32_BE"
    elif line.startswith(to_bytes(codecs.BOM64_BE)):
        bom_type = to_bytes(codecs.BOM64_LE)
        text = "BOM64_BE"
    elif line.startswith(to_bytes(codecs.BOM_UTF16_BE)):
        bom_type = to_bytes(codecs.BOM_UTF16_BE)
        text = "BOM_UTF16_BE"
    elif line.startswith(to_bytes(codecs.BOM_UTF32_BE)):
        bom_type = to_bytes(codecs.BOM_UTF32_BE)
        text = "BOM_UTF32_BE"

    elif line.startswith(to_bytes(codecs.BOM_LE)):
        bom_type = to_bytes(codecs.BOM_LE)
        text = "BOM_LE"
    elif line.startswith(to_bytes(codecs.BOM32_LE)):
        bom_type = to_bytes(codecs.BOM32_LE)
        text = "BOM32_LE"
    elif line.startswith(to_bytes(codecs.BOM64_LE)):
        bom_type = to_bytes(codecs.BOM64_LE)
        text = "BOM64_LE"
    elif line.startswith(to_bytes(codecs.BOM_UTF16_LE)):
        bom_type = to_bytes(codecs.BOM_UTF16_LE)
        text = "BOM_UTF16_LE"
    elif line.startswith(to_bytes(codecs.BOM_UTF32_LE)):
        bom_type = to_bytes(codecs.BOM_UTF32_LE)
        text = "BOM_UTF32_LE"

    elif line.startswith(to_bytes(codecs.BOM_UTF8)):
        bom_type = to_bytes(codecs.BOM_UTF8)
        text = "BOM_UTF8"
    elif line.startswith(to_bytes(codecs.BOM_UTF16)):
        bom_type = to_bytes(codecs.BOM_UTF16)
        text = "BOM_UTF16"
    elif line.startswith(to_bytes(codecs.BOM_UTF32)):
        bom_type = to_bytes(codecs.BOM_UTF32)
        text = "BOM_UTF32"

    # bom = ""
    # for i in range(len(bom_type)):
    #     bom += line[i]
    # line = line.replace(bom, '')
    # line = line.decode("utf_8")

    # print len(bom_type)
    line = line[len(bom_type):]
    print "line: {}".format(line)

    if text is None:
        print "THE LINE IS ENCODED WITH NONE OF THE FOLLOWING FORMATS:\n" \
              "\tBOM_BE - BOM32_BE - BOM64_BE - BOM_UTF16_BE - BOM_UTF32_BE\n" \
              "\tBOM_LE - BOM32_LE - BOM64_LE - BOM_UTF16_LE - BOM_UTF32_LE\n" \
              "\tBOM_UTF8 - BOM_UTF16 - BOM_UTF32"
    else:
        print text

    return bom_type


uri_4 = "http://risis.eu/linkset/" \
        "orgreg_20170718_grid_20170712_exactStrSim_University_Entity_current_name_English_P1888721829"

"""?sub a foaf:Organization ; ?pred ?object """

# print visualise([uri_4])

# specs = {
#     St.graph: "http://grid.ac/20170712",
#     St.entity_datatype: "http://xmlns.com/foaf/0.1/Organization",
#     St.long_predicate: "<http://www.grid.ac/ontology/hasAddress>/<http://www.w3.org/2003/01/geo/wgs84_pos#long>",
#     St.lat_predicate: "<http://www.grid.ac/ontology/hasAddress>/<http://www.w3.org/2003/01/geo/wgs84_pos#lat>"}


"""
PREFIX bif: <http://www.openlinksw.com/schemas/bif#>
select distinct ?subject ?level where
{
   GRAPH <http://geo.risis.eu/gadm>
   {
     ?subject <http://www.w3.org/2003/01/geo/wgs84_pos#geometry> ?geo ;
        <http://geo.risis.eu/vocabulary/gadm/level> ?level .
     #    point(long, lat)
     Filter(bif:st_intersects (?geo, bif:st_point(117.379737854, 40.226871490479), 0.1))
   }
}
"""


path = "http://risis.eu/linkset/eter_2014_grid_20170712_exactStrSim_University_English_Institution_Name_P1141790218"
# exp = export_flat_alignment_and_metadata(path)
# print exp[St.result]
# print Qry.virtuoso(virtuoso)["result"]

# import_gadm()

# line = reader.readline()
# line = reader.readline()
# print line.startswith(to_bytes(codecs.BOM_UTF8))
# print reader.readline()
# print reader.readline()
# print reader.readline()

# result = """
# ### TRIPLE COUNT: 0
# ### LINKSET: <http://risis.eu/linkset/
# eter_2014_grid_20170712_exactStrSim_University_English_Institution_Name_P1141790218>
# @prefix ll: <http://risis.eu/alignment/predicate/> .
# <http://risis.eu/eter_2014/resource/BE0056>
# ll:exactStrSim2_66a70877-4af9-4567-8618-5686439a0a3b <http://www.grid.ac/institutes/grid.5596.f> .
# <http://risis.eu/eter_2014/resource/BG0015>
# ll:exactStrSim2_39bca57f-ba77-4dc7-a469-717c333e80f6 <http://www.grid.ac/institutes/grid.465937.a> .
# <http://risis.eu/eter_2014/resource/CZ0058>
# ll:exactStrSim2_e8f594d4-acf8-4636-bdcc-dd2618cb0610 <http://www.grid.ac/institutes/grid.471548.b> .
# <http://risis.eu/eter_2014/resource/CZ0060>
# ll:exactStrSim2_ef65515b-2d92-4143-a58a-6d703e125dff <http://www.grid.ac/institutes/grid.453492.d> .
# <http://risis.eu/eter_2014/resource/CZ0060>
# ll:exactStrSim2_ef65515b-2d92-4143-a58a-6d703e125dff <http://www.grid.ac/institutes/grid.5596.f> .
# """
