# encoding=utf-8

from cStringIO import StringIO
import src.Alignments.Utility as Ut
import src.Alignments.Settings as St
import src.Alignments.NameSpace as Ns
from src.Alignments.Lenses.Lens_Intersection import intersection
from src.Alignments.Query import sparql_xml_to_matrix, display_matrix, boolean_endpoint_response

PREFIX ="""
    PREFIX bdb:         <http://vocabularies.bridgedb.org/ops#>
    PREFIX rdf:         <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX linkset:     <http://risis.eu/linkset/>
    PREFIX void:        <http://rdfs.org/ns/void#>
    PREFIX alivocab:    <http://risis.eu/alignment/predicate/>
    PREFIX tmpgraph:    <http://risis.eu/alignment/temp-match/>
    PREFIX prov:        <http://www.w3.org/ns/prov#>
"""


def view_data(view_specs, view_filter):

    # view_specs = {
    #     St.researchQ_URI: question_uri,
    #     St.datasets: view_lens,
    #     St.lens_operation: Ns.lensOpi
    # }

    question_uri = view_specs[St.researchQ_URI]
    view_lens = view_specs[St.datasets]

    # KEY FUNCTION FOR ACCESSING ELEMENT ON WHICH TO SORT ON
    def get_key(item):
        return item[St.graph]

    # SORT THE LIST BASED ON THE GRAPH NAME OF EACH DICTIONARY
    sorted_datasets = sorted(view_filter, key=get_key)

    # TEXT BUFFER
    string_buffer = StringIO()
    string_buffer2 = StringIO()

    # [DESCRIPTION] RESEARCH QUESTION X
    string_buffer2.write("\t<{}>\n".format(question_uri))

    # [DESCRIPTION] CREATED A VIEW
    string_buffer2.write("\t\t\t\talivocab:created\t\t<@URI> .\n\n")

    # [DESCRIPTION] THE VIEW
    string_buffer2.write("\t\t\t<@URI>\n".format(Ns.view))
    # [DESCRIPTION] IS A TYPE OF RISIS:VIEW
    string_buffer2.write("\t\t\t\ta\t\t\t\t\t\t<{}View> ;\n".format(Ns.riclass))
    # [DESCRIPTION] THAT HAS A LENS
    string_buffer2.write("\t\t\t\talivocab:hasViewLens\t<{}view_lens_@> ;".format(Ns.view))

    # SORT THE PROPERTIES IN EACH DICTIONARY
    count_ds = 0
    for dataset in sorted_datasets:
        append_ds = ";" if count_ds < len(sorted_datasets) - 1 else ".\n"
        count_ds += 1

        # APPEND THE GRAPH
        if St.graph in dataset:
            # [DESCRIPTION] THAT HAS A NUMBER OF FILTERS
            filter_c = "<{}filter_{}_@>".format(Ns.view, Ut.get_uri_local_name(dataset[St.graph]))
            string_buffer.write("\n\t\t\t{}".format(filter_c))

            # [DESCRIPTION] A FILTER HAS A DATASET
            string_buffer.write("\n\t\t\t\tvoid:target\t\t\t\t<{}> ;".format(dataset[St.graph]))

            has_filter = "\n\t\t\t\talivocab:hasFilter\t\t{} {}".format(filter_c, append_ds)
            string_buffer2.write(has_filter)

        # APPEND THE PROPERTIES
        if St.properties in dataset:
            dataset[St.properties].sort()
            count = 0

            # [DESCRIPTION] WHERE EACH FILTER IS COMPOSED OF A NUMBER OF PROPERTIES
            for ds_property in dataset[St.properties]:
                append = ";" if count < len(dataset[St.properties]) - 1 else ".\n"
                pro = "\n\t\t\t\talivocab:selected\t\t<{}> {}".format(ds_property, append)
                string_buffer.write(pro)
                count += 1

    # THE VIEW_LENS IS COMPOSED OF A NUMBER OF LENSES AND LINKSETS
    string_buffer2.write("\n\t\t\t<{}view_lens_@>".format(Ns.view))
    count_ls = 0
    for linkset_lens in view_lens:
        append_ls = ";" if count_ls < len(view_lens) - 1 else ".\n"
        string_buffer2.write("\n\t\t\t\talivocab:selected\t\t<{}> {}".format(linkset_lens, append_ls))
        count_ls += 1

    triples = string_buffer.getvalue()

    # HASH THE STRING
    hash_value = hash(string_buffer.getvalue())

    # CHANGE THE "-" NEGATIVE VALUE TO "N" AND POSITIVE TO "p"
    hash_value = str(hash_value).replace('-', "N") if str(hash_value).__contains__('-') else "P" + str(hash_value)

    # GENERATE THE URI
    uri = "{}View_{}".format(Ns.view, hash_value)

    query = PREFIX + """
    INSERT DATA
    {{
        GRAPH <{}>
        {{
        {}{}\t\t}}\n\t}}
    """.format(question_uri, string_buffer2.getvalue().replace("@URI", uri), triples).replace("@", hash_value)

    # print query
    message = "\nThe metadata was generated"

    print message
    return {St.message: message, St.insert_query: query, St.result: uri}


def view(view_specs, view_filter, limit=10):
    """
    :param view_specs:
    :param view_filter: AN ARRAY OF DICTIONARY. THE DICTIONARY
        CONTAINS GRAPH AND PROPERTIES KEYWORDS. THE VALUE OF THE
        PROPERTIES KEYWORDS IS AN ARRAY OF PROPERTIES AVAILABLE IN THE GRAPH
    :param limit: LIMIT FOR THE OUTPUT DISPLAY TABLE
    :return:
    """

    # LIMIT FOR THE VARIABLE IN THE SELECT
    str_limit = 70
    ns = dict()
    view_where = ""
    view_select = ""
    variables_list = dict()
    namespace = dict()
    namespace_str = ""
    count = 1

    # GENERATE THE INSERT METADATA
    # RETURNS MESSAGE, INSERT QUERY AND RESULT (THE VIEW URI)
    # {St.message:message, St.insert_query: final, St.result: uri}
    view_metadata = view_data(view_specs, view_filter)
    is_metadata_inserted = boolean_endpoint_response(view_metadata[St.insert_query])
    print is_metadata_inserted
    print "The insertion metadata was successfully inserted." if is_metadata_inserted == "true" \
        else "The metadata could not be inserted."

    print view_metadata[St.insert_query]

    # GENERATE THE INTERSECTION
    inter = intersection(view_specs)

    if inter is None:
        print "WE CANNOT PROCEED AS THERE IS A PROBLEM WITH THE PROVIDED DATASETS."

    # For each design view, we have the dataset of interest
    #  and the list of properties to display
    for d_view in view_filter:

        # Bout the dataset
        ds_ns_name = Ut.get_uri_ns_local_name(d_view[St.graph])
        # 3 characters string to differential the properties of a dataset
        attache = ds_ns_name[1][:3]

        # GRAPH
        # Adding the dataset name to the namespace dictionary [local name: namespace]
        if ds_ns_name is not None:
            if ds_ns_name[1] not in ns:
                ns[ds_ns_name[1]] = ds_ns_name[0]

        # Generate the dataset design view
        view_where += "\n\t### DATASET: {}\n\tGRAPH <{}>\n\t{{\n\t\t?{}".format(
            ds_ns_name[1], d_view[St.graph], ds_ns_name[1])

        # Adding the resource as a variable to the variable list
        view_select += (" ?{}".format(ds_ns_name[1]))

        # VARIABLES
        properties = d_view[St.properties]
        if type(properties) is not list:
            print "THIS <PROPERTIES> NEED TO BE of TYPE A LIST"
            return None

        # Going though the properties of interest
        for i in range(len(properties)):

            if type(properties[i]) is str:
                curr_ns = Ut.get_uri_ns_local_name(properties[i])
                # shortening prefix length
                short_name = ds_ns_name[1][:6]

                # Setting up the prefix and predicate
                if type(curr_ns) is list:
                    predicate = "{}voc:{}".format(short_name, curr_ns[1])
                    prefix = "{}voc".format(short_name)

                    # ADDING NAMESPACE
                    if prefix not in namespace:
                        namespace[prefix] = curr_ns[0]
                        namespace_str += "\nPREFIX {}: <{}>".format(prefix, curr_ns[0])

                    # Adding predicates
                    if i == len(properties) - 1:
                        view_where += "\n\t\t\t{:55} ?{}_{} .".format(predicate, attache, curr_ns[1])
                    else:
                        view_where += "\n\t\t\t{:55} ?{}_{} ;".format(predicate, attache, curr_ns[1])

                    # ADDING THE VARIABLE LIST and making it
                    # unique to a dataset with the variable attache
                    value = (" ?{}_{}".format(attache, curr_ns[1]))
                    if len(view_select + value) > str_limit:
                        variables_list[count] = view_select
                        view_select = value
                        count += 1
                    else:
                        view_select += value

                # IN THIS CASE, ONLY THE SUBJECT IS PROVIDED
                else:
                    view_where += ".\n\t\t?{}\n\t\t\t?p ?o .".format(curr_ns)

            # HERE, WE ARE DEALING WITH A SUBJECT AND A PREDICATE
            elif type(properties[i]) is list:
                if len(properties[i]) == 2:
                    curr_ns = Ut.get_uri_ns_local_name(properties[i][1])

                    if type(curr_ns) is list:
                        predicate = "{}voc:{}".format(short_name, curr_ns[1])
                        prefix = "{}voc".format(short_name)

                        # ADDING NAMESPACE
                        if prefix not in namespace:
                            namespace[prefix] = curr_ns[0]
                            namespace_str += "\nPREFIX {}: <{}>".format(prefix, curr_ns[0])

                        # REMOVE PREVIOUS PUNCTUATION
                        view_where = view_where[:len(view_where) - 2]
                        view_where += " .\n\t\t?{}\n\t\t\t{:55} ?{}_{} .".format(
                            properties[i][0], predicate, attache, curr_ns[1])

                        # ADDING THE VARIABLE LIST
                        value = (" ?{}_{}".format(attache, curr_ns[1]))
                        if len(view_select + value) > str_limit:
                            variables_list[count] = view_select
                            view_select = value
                            count += 1

                        else:
                            view_select += value

        view_where += "\n\t}"

    my_list = ""
    for key, variable in variables_list.items():
        my_list += "\n" + variable

    if limit == 0:
        lmt = ""
    else:
        lmt = "LIMIT {}".format(limit)

    query = "{}\n\nSELECT{}\n{{{}{}\n}} {}".format(namespace_str, my_list + view_select, inter, view_where, lmt)
    print query
    table = sparql_xml_to_matrix(query)
    # display_matrix(table, spacing=80, limit=limit, is_activated=True)

    view_query = {"select": view_select, "where": view_where}
    # {St.message:message, St.insert_query: final, St.result: uri}
    return {"metadata": view_metadata, "query": query, "table": table}


def retrieve_view(question_uri):

    view_lens_query = """
    PREFIX alivocab:    <http://risis.eu/alignment/predicate/>
    ### GETTING THE VIEW_LENS ELEMETS (LINKSET OR/AND LENSE)
    select ?linkset_lens
    {{
        GRAPH <{}>
        {{
            ?idea	alivocab:created ?view .
            ?view
                a 						<http://risis.eu/class/View> ;
                alivocab:hasViewLens/alivocab:selected ?linkset_lens

        }}
    }}
    """.format(question_uri)

    # RUN THE QUERY
    view_lens_matrix = sparql_xml_to_matrix(view_lens_query)

    # REDUCE
    view_lens = None
    if view_lens_matrix:
        if view_lens_matrix[St.result]:
            view_lens = reduce(lambda x, y: x + y, view_lens_matrix[St.result][1:])
    print "view_lens:", view_lens
    # print "view_lens_query:", view_lens_query
    # print "view_lens_matrix:", view_lens_matrix

    view_filter_query = """
    PREFIX alivocab:    <http://risis.eu/alignment/predicate/>
    PREFIX void:        <http://rdfs.org/ns/void#>
    ### GETTING THE VIEW_FILTERS
    select ?target ?selected
    {{
        GRAPH <{}>
        {{
            ?idea	alivocab:created ?view .
            ?view
                a 						<http://risis.eu/class/View> ;
                alivocab:hasFilter 		?filters .

             ?filters
                void:target			?target ;
                alivocab:selected	?selected .
        }}
    }} ORDER BY ?target
    """.format(question_uri)
    # RUN QUERY
    view_filter_matrix = sparql_xml_to_matrix(view_filter_query)
    # print "view_filter_query:", view_filter_query
    if view_filter_matrix:
        if view_filter_matrix[St.result]:

            print "view_filter_matrix:", view_filter_matrix[St.result]

            return {"view_lens": view_lens, "view_filter_matrix": view_filter_matrix[St.result]}

    return {"view_lens": view_lens, "view_filter_matrix": None}
