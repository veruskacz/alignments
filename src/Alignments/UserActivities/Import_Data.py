import re
import os
import codecs
import shutil
import rdflib
import cStringIO
import Alignments.Query as Qr
import Alignments.Query as Qry
import Alignments.Utility as Ut
import Alignments.Settings as St
import Alignments.NameSpace as Ns
import Alignments.Server_Settings as Ss
import Alignments.Server_Settings as Svr
from kitchen.text.converters import to_bytes  # , to_unicode

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

        return {"message": "OK", "result": loaded}

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


def download_data(endpoint, entity_type, graph, directory,  limit, main_query=None, count_query=None, activated=False):

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
    count_res = Qry.remote_endpoint_request(count_query, endpoint=endpoint)
    result = count_res['result']
    Qry.remote_endpoint_request(count_query, endpoint=endpoint)

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
    for i in range(0, iterations):

        if i == 0:
            offset = 0
        else:
            offset = i * limit + 1

        print "\t\tROUND: {} OFFSET: {}".format(i + 1, offset)

        #  CREATE THE FILE
        f_path = "{}/{}_{}.ttl".format(directory, entity_type, str(i+1))
        f_writer = open(f_path, "wb")
        current_q = "{} LIMIT {} OFFSET {}".format(main_query, limit, offset)
        # print current_q
        response = Qry.remote_endpoint_request(current_q, endpoint=endpoint)

        # GET THE TOTAL NUMBER OF TRIPLES
        if response[St.result] is None:
            print "NO RESULT FOR THIS ENRICHMENT."
            return count_res

        if response["response_code"] == 200:
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
    """.format(stardog_path, Svr.DATABASE, graph, directory)
    b_writer.write(load_text)
    b_writer.close()
    os.chmod(b_file, 0o777)
    # Ut.batch_load(b_file)

    message = "You have just successfully downloaded [{}] triples.\n" \
              "{} files where created in the folder [{}] and loaded into the [{}] dataset. ".format(
        triples, iterations, directory, Svr.DATABASE)

    print "\n\t{}".format(message)

    print "\n\tJOB DONE!!!"



    return {St.message: message, St.result: True}


file_2 = "C:\Users\Al\PycharmProjects\AlignmentUI\src\Alignments\Data\Linkset\Exact\\" + \
         "eter_eter_gadm_stat_identity_N307462801(Linksets)-20170526.trig"

file_1 = "C:\Users\Al\Dropbox\@VU\Ve\medical data\import_test_2.trig"

file_3 = "C:\Users\Al\Dropbox\@VU\Ve\medical data\LODmapping.ttl"

# import_graph(file_path=file_1, parent_predicate_index=0, detail=False)

# extract_predicates(file_1)
