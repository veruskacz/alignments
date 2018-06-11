# encoding=utf-8

import re
import os
import codecs
import shutil
import rdflib
import cStringIO
import zipfile
import Alignments.Query as Qr
import Alignments.Query as Qry
import Alignments.Utility as Ut
import Alignments.Settings as St
import Alignments.NameSpace as Ns
import Alignments.Server_Settings as Ss
import Alignments.Server_Settings as Svr
from os import listdir, path
from os.path import join, isfile, isdir
from Alignments.Utility import normalise_path as nrm
from kitchen.text.converters import to_bytes, to_unicode
from Alignments.UserActivities.View import view_description

# THE PROCESS OF IMPORTING AN ALIGNMENT
#   1. SAVE THE TRIG FILE
#   2. SAVE THE COPY OF THE ALTERED FILE
#   3. LOAD THE ALTERED FILE ONTO STARDOG IN A TEMPORARY GRAPH
#   3. IMPORT THE WRITE TRIPLE THOUGHT AN INSERT OPERATION
#   4. DELETE THE TEMPORARY GRAPH

# 1. A LINKSET IS A NAMED GRAPH => (1) TRIG FILE AND (2) GRAPH NAME
#   IF THE PROVIDED INPUT IS NOT A TRIG FILE,
#   WARNING:
#       IN THIS FRAMEWORK, AN ALIGNMENT IS A NAMED GRAPH MEANING THE FOLLOWING ARE REQUIRED:
#       1. THE EXTENSION FILE       ".trig"
#       2. THE NAMED GRAPH          "<http://linkset/test_0>" OR "test:test_0"
#       3. OPENING CURLY BRACKET    "{"
#       4. CLOSING CURLY BRACKET    "{"
# 	AND, ALL ARGUMENTS SHOULD BE RETURNED TO THE JS
#   AND A URI NEEDS TO BE PROVIDED FOR THE GRAPH

# 2. A LINKSET SHOULD HAVE ONLY ONE PREDICATE
#    IF SEVERAL PREDICATES ARE FOUND, ALL ARGUMENTS SHOULD BE RETURNED TO THE JS UI
#    AND A SINGLE PREDICATE SHOULD BE SELECTED FROM THE LIST OF FOUND PREDICATES

current_dir = os.path.dirname(os.path.dirname(Ss.UPLOAD_FOLDER))
# UPLOAD_FOLDER = os.path.join(current_dir, "UploadedFiles")
# UPLOAD_ARCHIVE = os.path.join(current_dir, "UploadedArchive")


def extract_predicates(file_path):

    pred_list = []

    print """ EXTRACTING THE PREDICATE USED IN THIS ALIGNMENT USING THE ORIGINAL TRIG FILE """
    _file = open(file_path, 'rb')

    while True:

        current = to_bytes(_file.readline())

        if len(current.strip()) > 0:

            # THE RESULT OF THE FIND COMES AS A TUPLE
            found = re.findall('.*:[^ \t].*[ \t]+(.*:[^ \t].*)[ \t]+.*:[^ \t].* *[.;]|'
                               '([a-zA-Z0-9].*:[^ \t][^ \t]*)[ \t]+[^ \t]*:[^ \t].* *[.;]', current, re.M)

            for pred in found:

                pred_1 = pred[0].strip()
                pred_2 = pred[1].strip()

                if len(pred_1) > 0 and pred_1 not in pred_list:
                    pred_list += [pred_1]

                if len(pred_2) > 0 and pred_2 not in pred_list:
                    pred_list += [pred_2]

        elif not current:
            "The end..."
            break

    _file.close()

    # for key in pred_list:
    #     print "\t{}".format(key)

    return pred_list


def save_original_file(uploaded_file, upload_folder):
    # SAVE THE ORIGINAL FILE TO THE UPLOADED FOLDER
    new_path = os.path.join(upload_folder, uploaded_file.filename)
    uploaded_file.save(new_path)
    print "FILE SAVED AT: {}".format(new_path)
    return new_path


def load_copy_2_stardog(original_file, altered_file, upload_folder, upload_archive):

    try:
        # MOVE THE FILES TO THE ARCHIVE FOLDER AFTER LOADING IT TO STARDOG

        # MOVE ORIGINAL FILE TO ARCHIVE
        original = os.path.basename(original_file)
        original_archive = os.path.join(upload_archive, original)
        if os.path.exists(original_archive) is True:
            os.remove(original_archive)
        shutil.move(original_file, upload_archive)

        # GENERATE THE BATCH FILE
        file__name = os.path.basename(os.path.splitext(altered_file)[0])
        batch_path = Ut.win_bat(upload_folder, file__name)

        # LOAD THE TRIG FILE TO STARDOG USING THE BATCH FILE
        loaded = Ut.batch_load(batch_path)

        # if loaded["message"] == "OK":

        # MOVE ALTERED FILE TO archive
        altered = os.path.basename(altered_file)
        altered_archive = os.path.join(upload_archive, altered)
        if os.path.exists(altered_archive) is True:
            os.remove(altered_archive)
        shutil.move(altered_file, upload_archive)

        # MOVE THE CREATED BATCH FILE TO archive
        batch = os.path.basename(batch_path)
        batch_archive = os.path.join(upload_archive, batch)
        if os.path.exists(batch_archive) is True:
            os.remove(batch_archive)
        shutil.move(batch_path, batch_archive)
        # os.remove(batch_path)

        return loaded

    except Exception as err:
        return {"message": str(err.message)}


def get_graph_name_1(text_input):

    name = ""
    lines = re.findall('(.*)\n', text_input, re.M)
    for i in range(len(lines)):
        # print i, composition[i]
        if lines[i].__contains__('{'):
            # print composition[i], i
            for j in reversed(range(i)):
                if lines[j]:
                    # print j, composition[j]
                    # print text_input[j]
                    name = lines[j]
                    break
    if name.__contains__('prefix'):
        name = ""
    return name


def get_graph_name_2(file_path, file_copy_name, upload_folder):

    bom = ''
    name = ""
    found = False
    count_line = 1
    builder = []
    pred_list = []
    ns = cStringIO.StringIO()

    try:
        # Open the file to convert
        # _file = codecs.open(self.inputPath, 'rb', encoding="utf-8")
        _file = open(file_path, 'rb')

    except Exception as exception:
        return {"message": exception}

    """
    About BYTE ORDER MARK (BOM)
    """
    first_line = to_bytes(_file.readline())
    if first_line.startswith(to_bytes(codecs.BOM_UTF8)):
        for i in range(len(to_bytes(codecs.BOM_UTF8))):
            bom += first_line[i]
        first_line = first_line.replace(bom, '')
        print u"[" + os.path.basename(file_path) + u"]", u"contains BOM."

    """
    EXTRACTING THE NAME OF THE GRAPH AND THE NAMESPACES USED
    IT STOPS AT THE FIRST OCCURRENCE OF AN OPEN CURLY BRACKET
    """
    while True:
        # Next line
        if count_line == 1:
            current = first_line
        else:
            current = to_bytes(_file.readline())
        count_line += 1

        #  If next line is not empty
        # print "Line: ", current, len(current.strip())
        if current:
            prefixes = re.findall('^@(.*) *\.', current.strip(), re.M)
            if len(prefixes) > 0:
                for pref in prefixes:
                    # print "prefix =>", pref
                    if pref.__contains__("\n") is False and pref.__contains__("\r") is True:
                        pref = pref.replace("\r", "\n")
                    ns.write("\t{}\n".format(pref))
                # print "prefix", prefixes
            # Add it to the builder list
            builder += [current]
            # Check if we start a graph
            if current.__contains__('{'):
                # If yes, revert through the list
                for item in reversed(range(len(builder) - 1)):
                    # Stop at the very first non empty line
                    # print item, builder[item]
                    if len(builder[item].strip()) > 0:
                        name = builder[item].replace("\n", "").replace("\r", "")
                        found = True
                        # print "current", name
                        break
        else:
            "The end..."
            break

        if found is True:
            break

    # END OF NAME EXTRACTION
    if name.__contains__('prefix'):
        name = ""
    _file.close()

    """
    EXTRACTING THE PREDICATE USED IN THIS ALIGNMENT USING THE ORIGINAL TRIG FILE
    """
    _file = open(file_path, 'rb')
    copy = os.path.join(upload_folder, file_copy_name)

    # CREATE THE NEW FILE
    # print "PATH OF THE COPY:", copy
    to_dick = open(copy, 'wb')

    while True:
        # if is_found is True:
        #     break
        current = to_bytes(_file.readline())

        # WRITING THE COPY TO FILE BECAUSE WE NEED TO LOAD THE GRAPH
        # IN A TEMPORARY GRAPH BEFORE FINAL LINKSET EXTRACTION
        to_dick.write(current.replace(name, "<http://risis.eu/alignment/temp-match/load>"))

        if len(current.strip()) > 0:

            # THE RESULT OF THE FIND COMES AS A TUPLE
            found = re.findall('.*:[^ \t].*[ \t]+(.*:[^ \t].*)[ \t]+.*:[^ \t].* *[.;]|'
                               '([a-zA-Z0-9].*:[^ \t][^ \t]*)[ \t]+[^ \t]*:[^ \t].* *[.;]', current, re.M)
            # print found
            for pred in found:

                # print pred, current
                pred_1 = pred[0].strip()
                pred_2 = pred[1].strip()

                if len(pred_1) > 0 and pred_1 not in pred_list:
                    pred_list += [pred_1]
                    # is_found = True

                if len(pred_2) > 0 and pred_2 not in pred_list:
                    pred_list += [pred_2]
                    # is_found = True

        elif not current:
            "The end..."
            break
    # CLOSE THE ORIGINAL FILE
    _file.close()
    # CLOSE THE COPIED FILE
    to_dick.close()
    # _file = open(file_path, 'rb')
    # while True:
    #     current = to_bytes(_file.readline()).replace(name, "<http://risis.eu/alignment/temp-match/load>")
    #     if len(current.strip()) > 0:
    #         print current
    #     elif not current:
    #         "The end..."
    #         break

    # print ns.getvalue()
    # print "Name Space:\n{}".format(ns.getvalue())
    # print "Graph                : {}".format(name)
    # print "Meta Graph           : {}_Meta".format(name)
    # print "MPredicates found    : {}".format(len(pred_list))
    # for key in pred_list:
    #     print "\t{}".format(key)
    # if len(pred_list) > 0:
    #     print "Predicate            : {}".format(pred_list[0])
    # else:
    #     print "Predicate        : {}".format("")

    return {"message": "OK", "namespace": ns.getvalue(), "graph": name, "predicate": pred_list,
            "file_copy_path": copy}


def import_graph(file_path, upload_folder, upload_archive, parent_predicate_index=0, detail=False):

    # NEED TO HAVE:
    #   1. THE NAMESPACE
    #   2. THE NAMED GRAPH
    #   3. THE PARENT PREDICATE

    # print "UPLOAD_FOLDER", UPLOAD_FOLDER
    # print "UPLOAD_ARCHIVE", UPLOAD_ARCHIVE

    predicate = ""

    """ 0. FILE EXTENSION OF THE ORIGINAL TRIG FILE """
    file__name = os.path.basename(os.path.splitext(file_path)[0])
    file_extension = os.path.basename(os.path.splitext(file_path)[1])
    new_name = "{}-Altered_copy{}".format(file__name, file_extension)
    if file_extension.lower() != ".trig":
        print "THE INPUT FILE NEEDS TO BE OF '.TRIG' EXTENSION."
        return {"message": "THE INPUT FILE NEEDS TO BE OF .TRIG EXTENSION."}

    """ 1. GET THE SAME AS COUNT """
    same_as_count = 5

    """ 2. GET ALL ARGUMENTS USING THE ORIGINAL TRIG FILE """
    arguments = get_graph_name_2(file_path, new_name, upload_folder)
    if arguments["message"] != "OK":
        print arguments
        return {"message": "A PROBLEM OCCURRED WHILE EXTRACTING ALL PARAMETERS."}

    """ 3. GENERATE THE NAME OF THE META DATA GRAPH """
    # linkset_graph is supposed to be automatically extracted. This means that
    # it is either represented with a name-space or with '<' and '>"
    if str(arguments["graph"]).__contains__("<"):
        graph = re.findall('<(.*)>', str(arguments["graph"]), re.M)
        meta_graph = "<{}_meta>".format(graph[0])
    else:
        meta_graph = "{}_meta".format(arguments["graph"])

    """ 4. EXTRACT THE LOCAL NAME OF THE PARENT PREDICATE USING THE ORIGINAL TRIG FILE """
    if len(list(arguments["predicate"])) > parent_predicate_index:
        predicate = arguments["predicate"][parent_predicate_index].replace("<", "").replace(">", "")
        if predicate.__contains__("http"):
            predicate = Ut.get_uri_local_name(predicate)
        else:
            found = re.findall('.*:(.*)', predicate, re.M)
            predicate = str(found[0]).strip()
    else:
        print "PREDICATE WARNING..."

    """ 5. PRINT IF NEEDED """
    if detail:
        print "Graph                : {}".format(arguments["graph"])
        print "Meta Graph           : {}".format(meta_graph)
        print "First Predicate      : {}".format(arguments["predicate"][parent_predicate_index])
        print "MPredicates found    : {}".format(len(list(arguments["predicate"])))

        for key in arguments["predicate"]:
            print "\t{}".format(key)
        print "Name Space:\n{}".format(arguments["namespace"])

    """ 6. IMPORT QUERY """
    import_query = """
    ##########################################################################################
    ### IMPORTING: {0}\n{6}\t##########################################################################################

    INSERT
    {{
        ### Correspondence graph
        GRAPH {0}
        {{
            ### Correspondence triple with singleton predicate
            ?source ?singPre ?target .
        }}

        ### Metadata graph
        GRAPH {1}
        {{
            ### Metadata is attached to the singleton property
            ?singPre rdf:singletonPropertyOf {2} .
        }}
    }}
    WHERE
    {{
        ### Imported alignment loaded in a temporally graph
        GRAPH <{3}load>
        {{
            ### Alignment described with the parent property
            ?source {2}  ?target .

            ### Create A SINGLETON URI (in A, replace C with B)
            BIND
            (
                replace
                (
                    "{4}imported_{7}_{5}_#", "#",
                    STRAFTER(str(UUID()),"uuid:")
                )
                as ?pre
            )

            ### BIND THE SINGLETON AS A URI
            BIND(iri(?pre) as ?singPre)
        }}
    }}


""".format(
        # 0                 1           2
        arguments["graph"], meta_graph, arguments["predicate"][parent_predicate_index],
        # 3          4            5              6                       7
        Ns.tmpgraph, Ns.alivocab, same_as_count, arguments["namespace"], predicate
    )

    # LOAD THE ALTERED FILE TO STARDOG.
    # IF SUCCESSFUL, MOVE ORIGINAL AND ALTERED FILE TO ARCHIVE
    loaded = load_copy_2_stardog(file_path, arguments["file_copy_path"], upload_folder, upload_archive)

    if loaded["message"] == "OK":
        if detail is True:
            print import_query
        Qr.boolean_endpoint_response(import_query)
        Qr.boolean_endpoint_response("DROP SILENT GRAPH <{}load>".format(Ns.tmpgraph))
        print import_query
    else:
        print "NOT OKAY!"

    message = """
    Graph                : {}
    Meta Graph           : {}
    Parent Predicate     : {}
    """.format(arguments["graph"], meta_graph, arguments["predicate"][parent_predicate_index])
    print "Done!!!"
    return {"message": message}


def download_data(endpoint, entity_type, graph, directory,  limit, load=False,
                  start_at=0, main_query=None, count_query=None, activated=False):

    # ENTITY TYPE IS USED ONLY FOR THE FILE NAME
    # EXAMPLE
    # endpoint      = "http://145.100.59.37:8891/sparql"
    # graph         = "https://www.openaire.eu"
    # e_type        = "OrganizationEntity"
    # directory     = "D:\Linking2GRID\Data\OpenAire_20180219"
    #
    # main_query    = """CONSTRUCT {?organisation ?predicate ?object.}
    # WHERE
    # {
    #   GRAPH <https://www.openaire.eu>
    #   {
    #     ?organisation a <http://lod.openaire.eu/vocab/OrganizationEntity> .
    #     ?organisation ?predicate ?object.
    #   }
    # }"""
    #
    # count_query = """SELECT(COUNT(?organisation) AS ?Total)
    # WHERE
    # {
    #   GRAPH <https://www.openaire.eu>
    #   {
    #     ?organisation a <http://lod.openaire.eu/vocab/OrganizationEntity> .
    #     ?organisation ?predicate ?object.
    #   }
    # }"""

    if activated is False:
        print "\nTHE FUNCTION IS NOT ACTIVATED"
        return {St.message: "THE FUNCTION IS NOT ACTIVATED.", St.result: None}

    triples = 0

    print "\n\tENDPOINT  : {}\n\tDIRECTORY : {}".format(endpoint, directory)

    # MAKE SURE THE FOLDER EXISTS
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
    except OSError as err:
        print "\n\t[download_data:]", err
        return

    # COUNT TRIPLES
    count_res = Qry.remote_endpoint_request(count_query, endpoint_url=endpoint)
    result = count_res['result']
    Qry.remote_endpoint_request(count_query, endpoint_url=endpoint)

    # GET THE TOTAL NUMBER OF TRIPLES
    if result is None:
        print "NO RESULT FOR THIS ENRICHMENT."
        return count_res

    # LOAD THE RESULT AND EXTRACT THE COUNT
    g = rdflib.Graph()
    g.parse(data=result, format="turtle")
    attribute = rdflib.URIRef("http://www.w3.org/2005/sparql-results#value")
    for subject, predicate, obj in g.triples((None, attribute, None)):
        triples = int(obj)

    # NUMBER OF REQUEST NEEDED
    iterations = triples / limit if triples % limit == 0 else triples / limit + 1
    print "\n\tTOTAL TRIPLES TO RETREIVE  : {}\n\tTOTAL NUMBER OF ITERATIONS : {}\n".format(triples, iterations)

    # ITERATIONS
    for i in range(start_at, iterations):

        if i == 0:
            offset = 0
        else:
            offset = i * limit + 1

        print "\t\tROUND: {:9}/{:<9} OFFSET: {:<10}".format(i + 1, iterations, offset)
        current_q = "{} LIMIT {} OFFSET {}".format(main_query, limit, offset)
        # print current_q
        response = Qry.remote_endpoint_request(current_q, endpoint_url=endpoint)

        # GET THE TOTAL NUMBER OF TRIPLES
        if response[St.result] is None:
            print "NO RESULT FOR THIS ENRICHMENT."
            return count_res

        if response["response_code"] == 200:
            #  CREATE THE FILE
            f_path = "{}/{}_{}.ttl".format(directory, entity_type, str(i + 1))
            f_writer = open(f_path, "wb")
            f_writer.write(response[St.result])
            f_writer.close()

        # if i == 1:
        #     break

    print ""
    # GENERATE THE BATCH FILE AND LOAD THE DATA
    stardog_path = '' if Ut.OPE_SYS == "windows" else Svr.settings[St.stardog_path]
    b_file = "{}/{}{}".format(directory, entity_type, Ut.batch_extension())
    b_writer = open(b_file, "wb")
    load_text = """echo "Loading data"
    {}stardog data add {} -g {} "{}/"*.ttl
    """.format(stardog_path, Svr.settings[St.stardog_uri], graph, directory)
    b_writer.write(load_text)
    b_writer.close()
    os.chmod(b_file, 0o777)
    if load is True:
        Ut.batch_load(b_file)

        message = "You have just successfully downloaded [{}] triples." \
                  "\n\t{} files where created in the folder [{}] and loaded " \
                  "into the [{}] dataset. ".format(triples, iterations, directory, Svr.settings[St.database])
    else:
        message = "You have just successfully downloaded [{}] triples." \
                  "\n\t{} files where created in the folder [{}].".format(triples, iterations, directory)

    print "\n\t{}".format(message)

    print "\n\tJOB DONE!!!"

    return {St.message: message, St.result: True}


def download_stardog_data(endpoint, entity_type, graph, directory,  limit, count=1, load=False,
                          start_at=0, main_query=None, count_query=None, create_graph=True,
                          cleanup=True, insert=False, activated=False):

    # ENTITY TYPE IS USED ONLY FOR THE FILE NAME
    # EXAMPLE
    # endpoint      = "http://145.100.59.37:8891/sparql"
    # graph         = "https://www.openaire.eu"
    # e_type        = "OrganizationEntity"
    # directory     = "D:\Linking2GRID\Data\OpenAire_20180219"
    #
    # main_query    = """CONSTRUCT {?organisation ?predicate ?object.}
    # WHERE
    # {
    #   GRAPH <https://www.openaire.eu>
    #   {
    #     ?organisation a <http://lod.openaire.eu/vocab/OrganizationEntity> .
    #     ?organisation ?predicate ?object.
    #   }
    # }"""
    #
    # count_query = """SELECT(COUNT(?organisation) AS ?Total)
    # WHERE
    # {
    #   GRAPH <https://www.openaire.eu>
    #   {
    #     ?organisation a <http://lod.openaire.eu/vocab/OrganizationEntity> .
    #     ?organisation ?predicate ?object.
    #   }
    # }"""

    if activated is False:
        print "\nTHE FUNCTION IS NOT ACTIVATED"
        return {St.message: "THE FUNCTION IS NOT ACTIVATED.", St.result: None}

    # user = Svr.settings[St.stardog_user]
    # password = Svr.settings[St.stardog_pass]

    # MAKE SURE THE FOLDER EXISTS
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
    except OSError as err:
        print "\n\t[download_data:]", err
        return

    triples = 0
    print "\n\tENDPOINT    : {}\n\tDIRECTORY   : {}\n\tGRAPH  {:4} : {}".format(endpoint, directory, count, graph)

    # COUNT TRIPLES
    count_res = Qry.sparql_xml_to_matrix(count_query)
    result = count_res['result']

    # GET THE TOTAL NUMBER OF TRIPLES
    if result is None:
        print "NO RESULT FOR THIS ENRICHMENT."
        return count_res

    if len(result) > 1:
        triples = int(result[1][0])

    # NUMBER OF REQUEST NEEDED
    iterations = triples / limit if triples % limit == 0 else triples / limit + 1
    print "\tTOTAL TRIPLES TO RETREIVE  : {}\n\tTOTAL NUMBER OF ITERATIONS : {}".format(triples, iterations)

    # ITERATIONS
    for i in range(start_at, iterations):

        if i == 0:
            offset = 0
        else:
            offset = i * limit + 1

        print "\t\tROUND: {:10}/{:<10} OFFSET: {:<10}".format(i + 1, iterations, offset)
        current_q = "{} LIMIT {} OFFSET {}".format(main_query, limit, offset)
        # print current_q
        response = Qry.endpointconstruct(current_q, clean=cleanup, insert=insert)

        # GET THE TOTAL NUMBER OF TRIPLES
        if response is None:
            print "NO RESULT FOR THIS ENRICHMENT."
            return count_res

        if len(response) > 0 and str(response).__contains__("{"):
            #  CREATE THE FILE

            if insert is True:
                f_path = "{}/{}_{}.sparql".format(directory, entity_type, str(i + 1))

            elif create_graph is True:
                f_path = "{}/{}_{}.trig".format(directory, entity_type, str(i + 1))

            else:
                f_path = "{}/{}_{}.ttl".format(directory, entity_type, str(i + 1))

            f_writer = open(f_path, "wb")

            if create_graph is True and insert is False:
                f_writer.write("<{}>".format(graph))
                f_writer.write(response)

            elif create_graph is True and insert is True:

                if response.__contains__("INSERT DATA"):
                    response = response.replace("INSERT DATA", "INSERT DATA {{ GRAPH <{}> ".format(graph)) + "}"
                    f_writer.write(response)
                else:
                    response = response.replace("INSERT", "INSERT {{ GRAPH <{}>".format(graph))
                    response = response.replace("WHERE", "} WHERE")
                    f_writer.write(response)
            else:
                # response = (response.strip())[1:-1]
                # response = response.replace("<<", "<").replace(">>", ">")
                f_writer.write(response)

            f_writer.close()

        # if i == 1:
        #     break

    if load is True:
        # GENERATE THE BATCH FILE AND LOAD THE DATA
        stardog_path = '' if Ut.OPE_SYS == "windows" else Svr.settings[St.stardog_path]
        b_file = "{}/{}{}".format(directory, entity_type, Ut.batch_extension())
        b_writer = open(b_file, "wb")
        load_text = """echo "Loading data"
        {}stardog data add {} -g {} "{}/"*.ttl
        """.format(stardog_path, Svr.settings[St.stardog_uri], graph, directory)
        b_writer.write(load_text)
        b_writer.close()
        os.chmod(b_file, 0o777)

        Ut.batch_load(b_file)

        message = "You have just successfully downloaded [{}] triples." \
                  "\n\t{} file(s) created in the folder [{}] and loaded " \
                  "into the [{}] dataset. ".format(triples, iterations, directory, Svr.settings[St.database])
    else:
        message = "You have just successfully downloaded [{}] triples." \
                  "\n\t{} file(s) created in the folder [{}].".format(triples, iterations, directory)

    print "\t{}".format(message)

    print "\tDOWNLOAD DONE!!!"

    return {St.message: message, St.result: True}


def export_research_question(research_question, directory, activated=False):

    print "THE FILE COLD BE FOUND IN {}".format(directory)

    if activated is False:
        print "\nTHE FUNCTION [export_research_question] IS NOT ACTIVATED"
        return {St.message: "THE FUNCTION [export_research_question] IS NOT ACTIVATED.", St.result: None}

    host = Svr.settings[St.stardog_host_name]
    endpoint = b"http://{}/annex/{}/sparql/query?".format(host, Svr.settings[St.database])

    # **************************************************************
    # 1. DOWNLOAD ALL TRIPLES (metadata) IN THE IDEA GRAPH
    # **************************************************************

    idea_query = """
    CONSTRUCT {{ ?idea ?predicate ?objects. }} WHERE
    {{
        graph <{}>
        {{
            ?idea ?predicate ?objects
        }}
    }}
    """.format(research_question)

    idea_total = """
    SELECT (count(?idea) as ?total)
    {{
        graph <{}>
        {{
            ?idea ?predicate ?objects
        }}
    }}
    """.format(research_question)

    print "\n1. DOWNLOAD ALL TRIPLES (metadata) IN THE IDEA GRAPH"
    download_stardog_data(endpoint, entity_type="Research Question", graph=research_question,
                          directory=directory, limit=10000, load=False, start_at=0,
                          main_query=idea_query, count_query=idea_total, create_graph=True,
                          cleanup=True, insert=True, activated=True)

    # **************************************************************
    # 2. GET ALL LINKSETS CREATED FROM AN ALIGNMENT MAPPING
    # **************************************************************

    print "\n2. GET ALL LINKSETS CREATED FROM AN ALIGNMENT MAPPING"
    linksets_query = """
    PREFIX class: <http://risis.eu/class/>
    PREFIX ll: <http://risis.eu/alignment/predicate/>
    PREFIX prov: <http://www.w3.org/ns/prov#>
    SELECT DISTINCT ?linkset
    {{
        graph <{}>
        {{
            ?mappings  a class:AlignmentMapping .
            ?mappings  ll:created|prov:used ?linkset .
        }}
    }}
    """.format(research_question)
    linksets_response = Qr.sparql_xml_to_matrix(linksets_query)
    linksets = linksets_response[St.result]
    if linksets:
        print "\t There are {} linksets".format(len(linksets) - 1)

    # **************************************************************
    # 3. GET ALL LENSES CREATED FROM AN ALIGNMENT MAPPING
    # **************************************************************

    print "\n3. GET ALL LENSES CREATED FROM AN ALIGNMENT MAPPING"
    lenses_query = """
        PREFIX ll: <http://risis.eu/alignment/predicate/>
        PREFIX prov: <http://www.w3.org/ns/prov#>
        PREFIX bdb: <http://vocabularies.bridgedb.org/ops#>
        SELECT DISTINCT ?subject
        {{
            graph <{0}>
            {{
                ?subject  a bdb:Lens .
                <{0}> ll:created|prov:used ?subject .
            }}
        }}
        """.format(research_question)
    lenses_response = Qr.sparql_xml_to_matrix(lenses_query)
    lenses = lenses_response[St.result]
    if lenses:
        print "\t There are {} lenses".format(len(lenses) - 1)

    # **************************************************************
    # 4. DOWNLOAD ALL LINKSETS CREATED FROM AN ALIGNMENT MAPPING
    # **************************************************************

    graph_query = """
    CONSTRUCT {{ ?subject  ?predicate ?object. }}
    WHERE
    {{
        graph <{}>
        {{
            ?subject  ?predicate ?object.
        }}
    }}"""

    graph_count_query = """
    SELECT ( count(?subject) as ?total)
    {{
        graph <{}>
        {{
            ?subject  ?predicate ?object.
        }}
    }}"""

    sing_query = """
    CONSTRUCT {{ ?subject ?predicate  ?object . }}
    WHERE
    {{
        GRAPH <{}>
        {{
            ?subject ?predicate  ?object .
        }}
    }}"""

    sing_count = """
    SELECT ( COUNT(?subject) AS ?total )
    {{
        GRAPH <{}>
        {{
            ?subject ?predicate  ?object .
        }}
    }}"""

    linkset_gen_q = """
    CONSTRUCT
    {{
        <{0}>  ?pre_1 ?object_1 .
        ?object_1 ?pred_2 ?object_2 .
        ?object_2 ?pred_3 ?object_3 .
    }}
    WHERE
    {{
        <{0}>
            ?pre_1 ?object_1 .

        OPTIONAL
        {{
            ?object_1 ?pred_2 ?object_2 .
            OPTIONAL{{ ?object_2 ?pred_3 ?object_3 . }}
        }}
    }}
    """

    linkset_gen_c = """
    SELECT ( COUNT(?object_1) AS ?total)
    {{
        <{}>
            ?pre_1 ?object_1 .

        OPTIONAL
        {{
            ?object_1 ?pred_2 ?object_2
            OPTIONAL{{ ?object_2 ?pred_3 ?object_3 . }}
        }}
    }}
    """

    print "\n4. DOWNLOADING ALL LINKSETS"
    if linksets and len(linksets) > 1:
        for i in range(1, len(linksets)):

            linkset_graph = linksets[i][0]
            print "\n\tDOWNLOAD LINKSET {:6}/{:<6}: {}".format(i, len(linksets) - 1, linkset_graph)

            current_ls_query_count = graph_count_query.format(linkset_graph)
            current_ls_query = graph_query.format(linkset_graph)

            current_singleton_graph = Ut.from_alignment2singleton(linkset_graph)
            current_singleton_q = sing_query.format(current_singleton_graph)
            current_singleton_c = sing_count.format(current_singleton_graph)

            current_gen_q = linkset_gen_q.format(linkset_graph)
            current_gen_c = linkset_gen_c.format(linkset_graph)

            # DOWNLOAD THE GENERIC METADATA
            download_stardog_data(endpoint, entity_type="linkset_{}_general_meta".format(i), graph=linkset_graph,
                                  directory=directory, limit=10000, load=False, start_at=0,  count=i,
                                  main_query=current_gen_q, count_query=current_gen_c, create_graph=False,
                                  cleanup=True, insert=True, activated=True)

            # DOWNLOAD THE SINGLETON METADATA
            download_stardog_data(endpoint, entity_type="linkset_{}_singletons".format(i),
                                  graph=current_singleton_graph,
                                  directory=directory, limit=10000, load=False, start_at=0,  count=i,
                                  main_query=current_singleton_q, count_query=current_singleton_c, create_graph=True,
                                  cleanup=True, insert=True, activated=True)

            # DOWNLOAD THE LINKSET
            download_stardog_data(endpoint, entity_type="linkset_{}".format(i), graph=linkset_graph,
                                  directory=directory, limit=10000, load=False, start_at=0,  count=i,
                                  main_query=current_ls_query, count_query=current_ls_query_count, activated=True)

    # **************************************************************
    # 3. DOWNLOAD ALL LENSES IN THE IDEA GRAPH
    # **************************************************************

    lenses_gen_q = """
    CONSTRUCT
    {{
        <{0}>  ?pre_1 ?object_1 .
        ?object_1 ?pred_2 ?object_2 .
        ?object_2 ?pred_3 ?object_3 .
    }}
    WHERE
    {{
        <{0}>
            ?pre_1 ?object_1 .

        OPTIONAL
        {{
            ?object_1 ?pred_2 ?object_2 .
        }}
    }}
    """

    lenses_gen_c = """
    SELECT ( COUNT(?object_1) AS ?total)
    WHERE
    {{
        <{0}>
            ?pre_1 ?object_1 .

        OPTIONAL
        {{
            ?object_1 ?pred_2 ?object_2 .
            OPTIONAL{{ ?object_2 ?pred_3 ?object_3 . }}
        }}
    }}
    """

    print "\n5. DOWNLOADING ALL LENSES"
    if lenses and len(lenses) > 1:
        for i in range(1, len(lenses)):

            lens_graph = lenses[i][0]
            print "\n\tDOWNLOAD LENS    {:6}/{:<6}: {}".format(i, len(lenses) - 1, lens_graph)

            # GENERAL LENS METADATA
            current_lens_gen_q = lenses_gen_q.format(lens_graph)
            current_lens_gen_c = lenses_gen_c.format(lens_graph)

            # LENS SINGLETON METADATA
            current_lens_singleton_graph = Ut.from_alignment2singleton(lens_graph)
            current_singleton_q = sing_query.format(current_lens_singleton_graph)
            current_singleton_c = sing_count.format(current_lens_singleton_graph)

            # LENS DATA
            current_lens_query_count = graph_count_query.format(lens_graph)
            current_lens_query = graph_query.format(lens_graph)
            # print current_lens_query_count
            # print current_lens_query

            # DOWNLOAD THE GENERIC METADATA
            download_stardog_data(endpoint, entity_type="lens_{}_general_meta".format(i), graph=lens_graph,
                                  directory=directory, limit=10000, load=False, start_at=0,  count=i,
                                  main_query=current_lens_gen_q, count_query=current_lens_gen_c, create_graph=False,
                                  cleanup=True, insert=True, activated=True)

            # DOWNLOAD THE SINGLETON METADATA
            download_stardog_data(endpoint, entity_type="lens_{}_singletons".format(i),  count=i,
                                  graph=current_lens_singleton_graph, directory=directory, limit=10000, load=False,
                                  start_at=0, main_query=current_singleton_q, count_query=current_singleton_c,
                                  create_graph=True, cleanup=True, insert=True, activated=True)

            # DOWNLOAD THE LENS
            download_stardog_data(endpoint, entity_type="lens_{}".format(i), graph=lens_graph,
                                  directory=directory, limit=10000, load=False, start_at=0,  count=i,
                                  main_query=current_lens_query, count_query=current_lens_query_count, activated=True)

    read_me_path = os.path.join(directory, "read_me.txt")
    f_writer = open(read_me_path, "wb")
    f_writer.write(get_research_question_link_stats(research_question, indent=True, activated=activated))
    f_writer.close()

    local_name = Ut.get_uri_local_name_plus(research_question)
    file_at_parent_directory = os.path.join(os.path.abspath(
        os.path.join(directory, os.pardir)), "{}.zip".format(local_name))

    return Ut.zip_folder(directory, output_file_path=file_at_parent_directory)


def get_research_question_link_stats(research_question, indent=True, activated=False):

    """ OUTPUT EXAMPLE
    2. GET ALL LINKSETS CREATED FROM AN ALIGNMENT MAPPING
    PREFIX ls:<http://risis.eu/linkset/>
    There are 21 linksets
        LINKSET      1/21      497 triples in ls:h2020_leidenRanking_2015_approxStrSim_Organization_name_N247890402
        LINKSET      2/21      186 triples in ls:h2020_h2020_approxStrSim_Organization_name_N529851809
        LINKSET      3/21      718 triples in ls:h2020_eter_2014_approxStrSim_Organization_name_P1029719164
        LINKSET      4/21       61 triples in ls:eter_2014_eter_2014_approxStrSim_University_Institution_Name_P98241885
        ...
        LINKSET     20/21     2358 triples in ls:grid_20170712_h2020_approxStrSim_Organization_label_N1087999532

    3. GET ALL LENSES CREATED FROM AN ALIGNMENT MAPPING
    PREFIX lens:<http://risis.eu/linkset/>
     There are 1 lenses
        LENS         1/1    68145 triples : lens:union_E..._P1768695787

    """

    if activated is False:
        print "\nTHE FUNCTION [get_research_question_link_stats] IS NOT ACTIVATED"
        return {St.message: "THE FUNCTION [get_research_question_link_stats] IS NOT ACTIVATED.", St.result: None}

    read_me = cStringIO.StringIO()
    idt = "\t" if indent is True else ""
    # **************************************************************
    # 1. GET THE RESEARCH QUESTION DESCRIPTION
    # **************************************************************
    description_query = """
    select ?description
    {{
        graph <{}>
        {{ ?researchQuestion rdfs:label ?description . }}
    }}
    """.format(research_question)
    description_response = Qr.sparql_xml_to_matrix(description_query)
    description = description_response[St.result]
    read_me.write("{}1. RESEARCH QUESTION DESCRIPTION\n".format(idt))
    read_me.write("\t{}{:12}: {}\n".format(idt, "URI", research_question))
    if description is not None:
        read_me.write("{}\t{:12}: {}\n\n".format(idt, "DESCRIPTION", description[1][0]))

    graph_count_query = """
    SELECT ( count(?subject) as ?total)
    {{
        graph <{}>
        {{
            ?subject  ?predicate ?object.
        }}
    }}"""
    # DATABASE = Svr.DATABASE
    # HOST = Svr.settings[St.stardog_host_name]
    # endpoint = b"http://{}/annex/{}/sparql/query?".format(HOST, DATABASE)

    # **************************************************************
    # 2. DOCUMENTING THE VIEWS IN THIS RESEARCH QUESTION
    # **************************************************************
    read_me.write("{}2. VIEWS CREATED\n".format(idt))
    descroptiom = view_description(research_question)
    if description_response:
        read_me.write(view_description(research_question) + "\n")

    # **************************************************************
    # 2. GET ALL LINKSETS CREATED FROM AN ALIGNMENT MAPPING
    # **************************************************************
    idt = "\t" if indent is True else ""

    read_me.write("{}3. LINKSETS CREATED FROM AN ALIGNMENT MAPPING\n".format(idt))
    linksets_query = """
    PREFIX class: <http://risis.eu/class/>
    PREFIX ll: <http://risis.eu/alignment/predicate/>
    PREFIX prov: <http://www.w3.org/ns/prov#>
    SELECT DISTINCT ?linkset
    {{
        graph <{}>
        {{
            ?mappings  a class:AlignmentMapping .
            ?mappings  ll:created|prov:used ?linkset .
        }}
    }}
    """.format(research_question)
    linksets_response = Qr.sparql_xml_to_matrix(linksets_query)
    linksets = linksets_response[St.result]

    if linksets is not None:
        read_me.write("{}\tPREFIX ls:<{}> \n".format(idt, Ns.linkset))
        read_me.write("{}\tThere are {} linksets\n".format(idt, len(linksets) - 1))
        if len(linksets) > 1:
            for i in range(1, len(linksets)):
                linkset_graph = linksets[i][0]
                count_response = Qry.sparql_xml_to_matrix(graph_count_query.format(linkset_graph))
                count_result = count_response[St.result]
                if count_result is not None and len(count_result) > 1:
                    triples = count_result[1][0]
                    read_me.write("{}\t\tLINKSET {:6}/{:}{:>9} triples in {}\n".format(
                        idt, i, len(linksets) - 1, triples, linkset_graph.replace(Ns.linkset, "ls:")))

    # **************************************************************
    # 3. GET ALL LENSES CREATED FROM AN ALIGNMENT MAPPING
    # **************************************************************

    read_me.write("\n{}4. LENSES CREATED FROM AN ALIGNMENT MAPPING\n".format(idt))
    lenses_query = """
        PREFIX ll: <http://risis.eu/alignment/predicate/>
        PREFIX prov: <http://www.w3.org/ns/prov#>
        PREFIX bdb: <http://vocabularies.bridgedb.org/ops#>
        SELECT DISTINCT ?subject
        {{
            graph <{0}>
            {{
                ?subject  a bdb:Lens .
                <{0}> ll:created|prov:used ?subject .
            }}
        }}
        """.format(research_question)
    lenses_response = Qr.sparql_xml_to_matrix(lenses_query)
    lenses = lenses_response[St.result]

    if lenses is not None and len(lenses) > 1:
        read_me.write("{}\tPREFIX lens:<{}>\n".format(idt, Ns.linkset))
        read_me.write("{}\tThere are {} lenses\n".format(idt, len(lenses) - 1))
        for i in range(1, len(lenses)):
            lens_graph = lenses[i][0]
            count_response = Qry.sparql_xml_to_matrix(graph_count_query.format(lens_graph))
            count_result = count_response[St.result]
            if count_result is not None and len(count_result) > 1:
                triples = count_result[1][0]
                read_me.write("{}\t\tLENS    {:6}/{}{:>9} triples : {}\n".format(
                    idt, i, len(lenses) - 1, triples, lens_graph.replace(Ns.lens, "lens:")))

    return read_me.getvalue()


def import_research_question(zip_path, load=False, activated=False):

    if activated is False:
        print "\nTHE FUNCTION [import_research_question] IS NOT ACTIVATED"
        return {St.message: "THE FUNCTION [import_research_question] IS NOT ACTIVATED.", St.result: None}

    if isfile(zip_path) is False:
        print "THE FILE DOES NOT EXISTS"
        return

    bat_path = ""
    message = cStringIO.StringIO()
    message2 = cStringIO.StringIO()

    extension = os.path.splitext(zip_path)
    file_name = os.path.basename(zip_path)
    file_short_name = file_name.replace(extension[1], "")

    if len(extension) > 1 and str(extension[1]).lower() == ".zip":

        zip_folder = zip_path.replace(extension[1], "")
        data_folder = "{0}{1}{1}{2}{1}".format(zip_folder, os.path.sep, file_short_name)

        zip_ref = zipfile.ZipFile(zip_path, 'r')
        zip_ref.extractall(zip_folder)
        zip_ref.close()

        bat_path = "{0}{1}{1}{2}{3}".format(zip_folder, os.path.sep, "load_to_server", Ut.batch_extension())
        load_cmd = generate_win_bat_for_rq(data_folder)
        writer = codecs.open(bat_path, "wb", "utf-8")
        writer.write(to_unicode(load_cmd))
        writer.close()
        read_me = open("{0}{1}{1}{2}".format(data_folder, os.path.sep, "read_me.txt"))

        message.write("\n{}\n\n".format(">>> GENERAL INFO"))
        message.write("\t{:20}: {}\n".format("Zip Short File Name", file_short_name))
        message.write("\t{:20}: {}\n".format("Zip File Name", file_name))
        message.write("\t{:20}: {}\n".format("Zip Folder", zip_folder))
        message.write("\t{:20}: {}\n".format("Data Folder", os.path.abspath(data_folder)))
        message.write("\t{:20}: {}\n".format("Unzipping", zip_path))
        message.write("\t{:20}: {}\n\n".format("Bat File", bat_path))
        message.write("{}\n".format(">>> DESCRIPTION ON FILES TO LOAD TO THE SERVER\n"))
        read_me_text = read_me.read()
        message.write(read_me_text)

        message2.write("{}\n".format(">>> DESCRIPTION ON FILES TO LOAD TO THE SERVER\n"))
        message2.write(read_me_text)
        read_me.close()

        if Ut.OPE_SYS != "windows":
            os.chmod(bat_path, 0o777)
            print "MAC"

        if Ut.OPE_SYS == "windows":

            if load is True:
                message.write("\n{}\n".format(">>> PLEASE, WAIT OR THE FEEDBACK"))
                print "LOADING..."
                Ut.bat_load(bat_path)

        else:
            if load is True:
                message.write("\n{}\n".format(">>> PLEASE, WAIT OR THE FEEDBACK"))
                print "LOADING..."
                Ut.bat_load(bat_path)

    elif len(extension) > 1:
        message.write("THIS EXTENSION [{}] IS NOT SUPPORTED.\n".format(extension[1]))
        message2.write("THIS EXTENSION [{}] IS NOT SUPPORTED.\n".format(extension[1]))

    print message.getvalue()

    return {St.message: message2.getvalue(), "sh_bat": bat_path}


def generate_win_bat_for_rq(directory):

    batch = cStringIO.StringIO()
    if path.isdir(directory):

        files = [f for f in listdir(nrm(directory)) if isfile(join(nrm(directory), f))]

        if Ut.OPE_SYS == "windows":

            for i in range(0, len(files)):

                if files[i].endswith(".trig") or files[i].endswith(".sparql"):
                    batch.write("""echo Loading data {:6}: {}\n""".format(i, files[i]))

                if files[i].endswith(".trig"):
                    batch.write("""\tcall stardog data add {} "{}" \n\n""".format(
                        Svr.settings[St.stardog_uri], join(nrm(directory), files[i])))

                if files[i].endswith(".sparql"):
                    batch.write("""\tcall stardog query {} "{}" \n\n""".format(
                        Svr.settings[St.stardog_uri], join(nrm(directory), files[i])))

        else:

            stardog_path = Svr.settings[St.stardog_path]
            cmd = "\n\t{}stardog".format(stardog_path)

            for i in range(0, len(files)):

                if files[i].endswith(".trig") or files[i].endswith(".sparql"):
                    batch.write("""echo Loading data {:6}: {}""".format(i, files[i]))

                if files[i].endswith(".trig"):
                    batch.write("""\t{} data add {} "{}"; \n\n""".format(
                        cmd, Svr.settings[St.stardog_uri], join(nrm(directory), files[i])))

                if files[i].endswith(".sparql"):
                    batch.write("""\t{} query {} "{}"; \n\n""".format(
                        cmd, Svr.settings[St.stardog_uri], join(nrm(directory), files[i])))

    return batch.getvalue()


def load_rq_from_batch(batch_file, zip_path):

    # LOAD THE DATA TO THE TRIPLE STORE
    if isfile(batch_file) is True:
        print "ABOUT TO LOAD [{}]".format(batch_file)
        output = Ut.batch_load(batch_file)

        # CHECK THE ZIP FILE IF IT EXISTS
        if isfile(zip_path) is True:
            extension = os.path.splitext(zip_path)

            # REMOVE THE ZIP FILE
            os.remove(zip_path)
            zip_folder = zip_path.replace(extension[1], "")
            print "{:19}: {}".format("ZIP FILE DELETED", zip_path)

            # REMOVE THE UNZIP FOLDER
            if isdir(zip_folder):
                shutil.rmtree(zip_folder)
                print "{:19}: {}".format("ZIP FOLDER DELETED", zip_folder)

            # return {"message": "OK", "result": output}
            return output["result"]

        return "THE FILE DOES NOT EXIST"

    else:
        return "NO BATCH FILE"


# endpoint d2s http://risis.eu/activity/idea_a5791d

file_2 = "C:\Users\Al\PycharmProjects\AlignmentUI\src\Alignments\Data\Linkset\Exact\\" \
         "eter_eter_gadm_stat_identity_N307462801(Linksets)-20170526.trig"

file_1 = "C:\Users\Al\Dropbox\@VU\Ve\medical data\import_test_2.trig"

file_3 = "C:\Users\Al\Dropbox\@VU\Ve\medical data\LODmapping.ttl"

# import_graph(file_path=file_1, parent_predicate_index=0, detail=False)
# extract_predicates(file_1)
# DOWNLOADING OPENAIRE FORM
# endpoint = "http://145.100.59.37:8891/sparql"
# graph =  "https://www.openaire.eu"
# e_type = "OrganizationEntity"
# directory = "D:\Linking2GRID\Data\OpenAire_20180219"
# main_query = """CONSTRUCT {?organisation ?predicate ?object.}
# WHERE
# {
#   GRAPH <https://www.openaire.eu>
#   {
#     ?organisation a <http://lod.openaire.eu/vocab/OrganizationEntity> .
#     ?organisation ?predicate ?object.
#   }
# }"""
#
# count_query = """SELECT(COUNT(?organisation) AS ?Total)
# WHERE
# {
#   GRAPH <https://www.openaire.eu>
#   {
#     ?organisation a <http://lod.openaire.eu/vocab/OrganizationEntity> .
#     ?organisation ?predicate ?object.
#   }
# }"""
#
# download_data(endpoint=endpoint, entity_type=e_type, graph=graph, directory=directory,  limit=10000, load=False,
#                   start_at=0, main_query=main_query, count_query=count_query, activated=True)
