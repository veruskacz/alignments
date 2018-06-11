# encoding=utf-8

import xmltodict
import re
import cStringIO as Buffer
from cStringIO import StringIO
import Alignments.Utility as Ut
import Alignments.Settings as St
import Alignments.NameSpace as Ns
from Alignments.Lenses.Lens_Intersection import intersection
import Alignments.ErrorCodes as Ec
from Alignments.Query import endpoint, sparql_xml_to_matrix, display_matrix, boolean_endpoint_response

PREFIX = """
    PREFIX bdb:         <http://vocabularies.bridgedb.org/ops#>
    PREFIX rdf:         <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX linkset:     <http://risis.eu/linkset/>
    PREFIX void:        <http://rdfs.org/ns/void#>
    PREFIX alivocab:    <http://risis.eu/alignment/predicate/>
    PREFIX tmpgraph:    <http://risis.eu/alignment/temp-match/>
    PREFIX prov:        <http://www.w3.org/ns/prov#>
"""

# AN EXAMPLE OF A VIEW
#     PREFIX bdb:         <http://vocabularies.bridgedb.org/ops#>
#     PREFIX rdf:         <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
#     PREFIX linkset:     <http://risis.eu/linkset/>
#     PREFIX void:        <http://rdfs.org/ns/void#>
#     PREFIX alivocab:    <http://risis.eu/alignment/predicate/>
#     PREFIX tmpgraph:    <http://risis.eu/alignment/temp-match/>
#     PREFIX prov:        <http://www.w3.org/ns/prov#>
#
#     INSERT DATA
#     {
#         GRAPH <http://risis.eu/activity/idea_77f81f>
#         {
#         	<http://risis.eu/activity/idea_77f81f>
# 				alivocab:created			<http://risis.eu/view/View_N389901427> .
#
# 			<http://risis.eu/view/View_N389901427>
# 				a							<http://risis.eu/class/View> ;
# 				alivocab:hasViewLens		<http://risis.eu/view/view_lens_N389901427> ;
# 				alivocab:hasFilter			<http://risis.eu/view/filter_eter_University_N389901427> ;
# 				alivocab:hasFilter			<http://risis.eu/view/filter_eter_gadm_stat_N389901427> ;
# 				alivocab:hasFilter			<http://risis.eu/view/filter_grid_N389901427> ;
# 				alivocab:hasFilter			<http://risis.eu/view/filter_grid_gadm_stat_N389901427> ;
# 				alivocab:hasFilter			<http://risis.eu/view/filter_leidenRanking_N389901427> .
#
# 			<http://risis.eu/view/view_lens_N389901427>
# 				alivocab:selected			<http://risis.eu/lens/union_Eter_LeidenRanking_P1614043027> ;
# 				alivocab:selected			<http://risis.eu/lens/union_Eter_Grid_N312479101> ;
# 				alivocab:selected			<http://risis.eu/linkset/eter_eter_gadm_stat_identity_N307462801> ;
# 				alivocab:selected			<http://risis.eu/linkset/grid_grid_gadm_stat_identity_N627321033> .
#
# 			<http://risis.eu/view/filter_eter_University_N389901427>
# 				void:target					<http://risis.eu/dataset/eter> ;
# 				void:hasDatatype			<http://risis.eu/eter/ontology/class/University> ;
# 				alivocab:selected			<http://risis.eu/eter/ontology/predicate/core_budget_EURO> ;
# 				alivocab:selected			<http://risis.eu/eter/ontology/predicate/foundation_year> ;
# 				alivocab:selected			<http://risis.eu/eter/ontology/predicate/geographic_coordinates_latitude> ;
# 				alivocab:selected			<http://risis.eu/eter/ontology/predicate/university_hospital> ;
# 				alivocab:selectedOptional	<http://risis.eu/eter/ontology/predicate/country_Code> ;
# 				alivocab:selectedOptional	<http://risis.eu/eter/ontology/predicate/english_Institution_Name> ;
# 				alivocab:selected			<http://risis.eu/eter/ontology/predicate/institution_Name> .
#
# 			<http://risis.eu/view/filter_eter_gadm_stat_N389901427>
# 				void:target					<http://risis.eu/dataset/eter_gadm_stat> ;
# 				alivocab:selected			<http://risis.eu//temp-match/temp-match/predicate/level> ;
# 				alivocab:selected			<http://risis.eu//temp-match/temp-match/predicate/total> .
#
# 			<http://risis.eu/view/filter_grid_N389901427>
# 				void:target					<http://risis.eu/dataset/grid> ;
# 				alivocab:selected			<http://risis.eu/grid/ontology/predicate/city> ;
# 				alivocab:selected			<http://risis.eu/grid/ontology/predicate/country> ;
# 				alivocab:selected			<http://risis.eu/grid/ontology/predicate/name> ;
# 				alivocab:selected			<http://risis.eu/grid/ontology/predicate/types> .
#
# 			<http://risis.eu/view/filter_grid_gadm_stat_N389901427>
# 				void:target					<http://risis.eu/dataset/grid_gadm_stat> ;
# 				alivocab:selected			<http://risis.eu//temp-match/temp-match/predicate/level> ;
# 				alivocab:selected			<http://risis.eu//temp-match/temp-match/predicate/typeCount> .
#
# 			<http://risis.eu/view/filter_leidenRanking_N389901427>
# 				void:target					<http://risis.eu/dataset/leidenRanking> ;
# 				alivocab:selected			<http://risis.eu/leidenRanking/ontology/predicate/Country> ;
# 				alivocab:selected			<http://risis.eu/leidenRanking/ontology/predicate/Field> ;
# 				alivocab:selected			<http://risis.eu/leidenRanking/ontology/predicate/Frac_counting> ;
# 				alivocab:selected			<http://risis.eu/leidenRanking/ontology/predicate/Period> ;
# 				alivocab:selected			<http://risis.eu/leidenRanking/ontology/predicate/University> .
# 		}
# 	}

short = 0

# GENERATING THE VIEW INSERT QUERY (META DATA)
def view_data(view_specs, view_filter, display=False):

    # GENERATING THE METADATA FOR REGISTERING A VIEW.
    #
    # THE VIEW IS COMPOSED OF
    #   - EXACTLY ONE LENS
    #   - ONE OR MORE FILTERS
    #
    # A FILTER IS COMPOSED OF
    #   - EXACTLY ONE DATASET
    #   - ONE OR MORE PROPERTIES

    # view_specs = {
    #     St.researchQ_URI: question_uri,
    #     St.datasets: view_lens,
    #     St.lens_operation: Ns.lensOpi
    # }
    # TEXT BUFFER
    string_buffer = StringIO()
    main_buffer = StringIO()
    dataset_opt = []  # LIST OF DATASET THAT HAVE ONLY OPTIONAL PROPERTIES

    # HOLDER VARIABLE (STRING) FOR THE RESEARCH QUESTION URI
    question_uri = str(view_specs[St.researchQ_URI]).strip()

    # HOLDER VARIABLE (LIST) FOR LINKSETS AND/OR LENSES THAT COMPOSE THE LENS
    view_lens = view_specs[St.datasets]

    # KEY FUNCTION FOR ACCESSING ELEMENT ON WHICH TO SORT ON
    def get_key(item):
        return item[St.graph]

    # SORT THE LIST BASED ON THE GRAPH NAME OF EACH DICTIONARY
    # SORTING THE LIST OF FILTERS BASED ON THE DATASET NAME
    sorted_datasets = sorted(view_filter, key=get_key)
    # print sorted_datasets

    # [DESCRIPTION] RESEARCH QUESTION X
    main_buffer.write("\t### THE VIEW\n".format(question_uri))
    main_buffer.write("\t\t\t<{}>\n".format(question_uri))

    # [DESCRIPTION] CREATED A VIEW
    main_buffer.write("\t\t\t\talivocab:created\t\t\t<@URI> .\n\n")

    # [DESCRIPTION] THE VIEW
    main_buffer.write("\t\t\t### THE COMPONENT OF THE VIEW: THE TYPE, THE LENS AND THE FILTERS\n".format(Ns.view))
    main_buffer.write("\t\t\t<@URI>\n".format(Ns.view))

    # [DESCRIPTION] IS A TYPE OF RISIS:VIEW
    main_buffer.write("\t\t\t\ta\t\t\t\t\t\t\t<{}View> ;\n".format(Ns.riclass))

    # [DESCRIPTION] THAT HAS A LENS
    main_buffer.write("\t\t\t\talivocab:hasViewLens\t\t<{}view_lens_@> ;".format(Ns.view))

    # SORT THE PROPERTIES IN EACH DICTIONARY
    count_ds = 0

    for filter in sorted_datasets:
        count_ds += 1
        append_ds = ";" if count_ds < len(sorted_datasets)  else ".\n"

        if St.graph in filter:

            # [DESCRIPTION] THAT HAS A NUMBER OF FILTERS
            dataset_name = Ut.get_uri_local_name(filter[St.graph])


            # DATA IS AN ARRAY OF DICTIONARIES WHERE, FOR EACH DATATYPE, WE HAVE A LIST OF PROPERTIES SELECTED
            data = filter["data"]
            count_sub_filter = 0
            for dictionary in data:
                count_sub_filter += 1
                ent_type = dictionary["entity_datatype"]
                pro_list = dictionary["properties"]

                # APPEND THE GRAPH
                string_buffer.write("\n\t\t\t### FILTER {}_{}".format(count_ds, count_sub_filter))

                if len(data) > 1:
                    append_ds = ";" if count_sub_filter < len(data)  else ".\n"

                if St.entity_datatype in filter:
                    entity_type_name = Ut.get_uri_local_name(filter[St.entity_datatype])
                    filter_c = "<{}filter_{}_{}_{}_@>".format(Ns.view, dataset_name, count_sub_filter, entity_type_name)
                else:
                    filter_c = "<{}filter_{}_{}_@>".format(Ns.view, dataset_name, count_sub_filter)
                string_buffer.write("\n\t\t\t{}".format(filter_c))

                # [DESCRIPTION] A FILTER HAS A DATASET
                string_buffer.write("\n\t\t\t\tvoid:target\t\t\t\t\t<{}> ;".format(filter[St.graph]))
                has_filter = "\n\t\t\t\talivocab:hasFilter\t\t\t{} {}".format(filter_c, append_ds)

                # [DESCRIPTION] ADDING THE FILTERS BELONGING TO THE VIEW
                main_buffer.write(has_filter)

                # ADDING THE DATATYPE IF ANY
                if St.entity_datatype in dictionary:
                    string_buffer.write("\n\t\t\t\tvoid:hasDatatype\t\t\t<{}> ;".format(dictionary[St.entity_datatype]))

                # APPEND THE PROPERTIES
                # print "\n>>>>>>> FILTER:", filter
                if St.properties in dictionary:
                    dictionary[St.properties].sort()
                    count = 0
                    pro = None

                    # [DESCRIPTION] WHERE EACH FILTER IS COMPOSED OF A NUMBER OF PROPERTIES
                    check_optional = False
                    total_properties = len(dictionary[St.properties])

                    for ds_property in dictionary[St.properties]:

                        append = ";" if count < total_properties - 1 else ".\n"

                        if type(ds_property) is tuple and len(ds_property) == 2:
                            cur_property = str(ds_property[0]).strip()

                            if len(cur_property) > 0 and ds_property[1] is True:
                                pro = "\n\t\t\t\talivocab:selectedOptional\t<{}> {}".format(ds_property[0], append)
                            else:
                                check_optional = True
                                pro = "\n\t\t\t\talivocab:selected\t\t\t<{}> {}".format(cur_property, append)
                        else:
                            cur_property = str(ds_property).strip()
                            if len(cur_property) > 0:
                                check_optional = True
                                pro = "\n\t\t\t\talivocab:selected\t\t\t<{}> {}".format(cur_property, append)
                        if pro is not None:
                            string_buffer.write(pro)
                            count += 1

                    # THESE DATASETS ARE COMPOSED OF ONLY OPTIONAL PROPERTIES
                    if check_optional is False:
                        dataset_opt += [filter[St.graph]]

    # THE VIEW_LENS IS COMPOSED OF A NUMBER OF LENSES AND LINKSETS SELECTED
    main_buffer.write("\n\t\t\t### THE COMPONENT OF THE LENS".format(Ns.view))
    main_buffer.write("\n\t\t\t<{}view_lens_@>".format(Ns.view))
    count_ls = 0
    for linkset_lens in view_lens:
        append_ls = ";" if count_ls < len(view_lens) - 1 else ".\n"
        main_buffer.write("\n\t\t\t\talivocab:selected\t\t\t<{}> {}".format(linkset_lens, append_ls))
        count_ls += 1

    main_triples = main_buffer.getvalue()
    triples = string_buffer.getvalue()

    # HASH THE STRING
    hash_value = hash(main_triples + triples)

    # CHANGE THE "-" NEGATIVE VALUE TO "N" AND POSITIVE TO "P"
    hash_value = str(hash_value).replace('-', "N") if str(hash_value).__contains__('-') else "P" + str(hash_value)

    # GENERATE THE URI FOR THE VIEW
    uri = "{}View_{}".format(Ns.view, hash_value)

    query = PREFIX + """
    INSERT DATA
    {{
        GRAPH <{}>
        {{
        {}{}\t\t}}\n\t}}
    """.format(question_uri, main_triples.replace("@URI", uri), triples).replace("@", hash_value)

    message = "\nThe metadata was generated as: {}".format(uri)
    print message
    print "\nVIEW INSERT QUERY:", query


    if display:
        print "\nVIEW INSERT QUERY:", query

    # return {St.message: message, St.insert_query: query, St.result: uri}
    return {St.message: message, St.insert_query: query, St.result: uri, "sparql_issue": dataset_opt}


# MAIN FUNCTION: METADATA + GENERATING THE VIEW SPARQL QUERY
def view(view_specs, view_filter, save=False, limit=10):
    """
    :param view_specs:
    :param view_filter:
    :param save:
    :param limit
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
    is_problematic = False

    try:
        # 1. GENERATE THE INSERT METADATA
        # RETURNS MESSAGE, INSERT QUERY AND RESULT (THE VIEW URI)
        # RETURNS{St.message:message, St.insert_query: final, St.result: uri}
        view_metadata = view_data(view_specs, view_filter)
        # print view_metadata
        # print view_filter

        # 2. CHECK FOR POTENTIAL SPARQL TIMEOUT
        opt_list = view_metadata["sparql_issue"]
        if len(opt_list) != 0:
            is_problematic = True
            the_list = ""
            for ds in opt_list:
                the_list += "{} ".format(ds)
            message = "The insertion metadata was generated but not inserted. The properties listed in theses " \
                      " datasets [{}] are ALL OPTIONAL. The presence of at least one non OPTIONAL property is " \
                      "required.".format(
                the_list)
            view_metadata[St.message] = message
            print message

        # 3. REGISTER THE METADATA IF SAVE ID SET TO TRUE
        if save:
            if is_problematic is False:
                print "We are in save mode!"
                is_metadata_inserted = boolean_endpoint_response(view_metadata[St.insert_query])
                print "IS THE METADATA INSERTED?: {}".format(is_metadata_inserted)
                message = "The insertion metadata was successfully inserted as: {}".format(view_metadata[St.result]) \
                    if (is_metadata_inserted == "true" or is_metadata_inserted == Ec.ERROR_STARDOG_1) \
                    else "The metadata could not be inserted."
                print message
                view_metadata[St.message] = message
                # print view_metadata[St.insert_query]

        # GENERATE THE INTERSECTION
        # AND DISPLAY THE QUERIES NEEDED
        inter = intersection(view_specs, display=False)

        if inter is None:
            print "WE CANNOT PROCEED AS THERE IS A PROBLEM WITH THE PROVIDED DATASETS."

        # For each design view, we have the dataset of interest
        #  and the list of properties to display in a filter
        # THE FILTER IS A LIST OF GRAPH DICTIONARIES
        # [GRAPH1, GRAPH2, GRAPH3, ...]
        for graph in view_filter:

            optional = ""

            # THE GRAPH CONTAINS GRAPH AND DATA
            graph_uri = graph[St.graph]

            # About the dataset: [NAMESPACE, NAME]
            ds_ns_name = Ut.get_uri_ns_local_name(graph_uri)
            if ds_ns_name[1][0].isdigit():
                ds_ns_name[1] = "D{}".format(ds_ns_name[1])
            print ds_ns_name
            # shortening prefix length
            short_name = ds_ns_name[1]

            # HOLDING INFORMATION ABOUT THIS GRAPH (FOR EACH ENTITY DATATYPE, THE PROPERTIES SELECTED)
            graph_data = graph["data"]

            # Adding the dataset name to the namespace dictionary [local name: namespace]
            if ds_ns_name is not None:
                if ds_ns_name[1] not in ns:
                    ns[ds_ns_name[1]] = ds_ns_name[0]

            # Generate the dataset design view WHICH LOOKS LIKE
            # ### DATASET: grid
            # GRAPH <http://risis.eu/genderc/grid>
            # {
            view_where += "\n\t### DATASET: {}\n\tGRAPH <{}>\n\t{{".format(ds_ns_name[1], graph_uri)

            # graph_data IS A LIST OF DICTIONARIES FOR HOLDING THE TYPES AND THEIR LISTED PROPERTIES
            count_ns = 0
            for data_info in graph_data:

                e_type_uri = data_info[St.entity_datatype]
                type_triple = ""
                if e_type_uri == "no_type":
                    e_type = ""
                    # print "!!!!!!!!!!!!!!!!!!!!!!!!!! NO TYPE"
                else:
                    e_type = Ut.get_uri_local_name(e_type_uri)
                    # print "!!!!!!!!!!!!!!!!!!!!!!!!!!e_type", e_type
                    if e_type:
                        e_type = "_{}".format(e_type[short:])

                        type_triple = "\n\t\t\ta{:54} <{}> ;".format("", e_type_uri)

                #   ?GRID
                # TODO ADD THE TYPE TO THE ALIGNMENTS IN THE INTERSECT
                # SUBJECT: ADDING 1 AT THE END SO THAT SAME SOURCE AND TARGET ARE TAKEN CARE OFF
                view_where += "\n\t\t?{}{}_1{}".format(ds_ns_name[1], e_type, type_triple)
                # view_where += "\n\t\t?{}{}{}".format(ds_ns_name[1], "", type_triple)

                # Adding the resource as a variable to the variable list
                view_select += " ?{}{}_1".format(ds_ns_name[1], e_type, )

                t_properties = data_info[St.properties]

                # FOR BACKWARD COMPATIBILITY, REMOVE "<" AND ">"
                for i in range(len(t_properties)):
                    # print "PROPERTY TUPLE:", t_properties[i]
                    if type(t_properties[i]) is tuple:
                        # print "PROPERTY:", t_properties[i][0]
                        t_properties[i] = (re.sub('[<>]', "", t_properties[i][0]), t_properties[i][1])
                        # print "PROPERTY:", t_properties[i]
                    else:
                        t_properties[i] = re.sub('[<>]', "", t_properties[i])
                # 3 characters string to differentiate the properties of a dataset
                attache = ds_ns_name[1][short:]

                # VARIABLES
                if type(t_properties) is not list:
                    print "THIS <PROPERTIES> NEED TO BE of TYPE A LIST"
                    return None

                # Going though the properties of interest
                for i in range(len(t_properties)):

                    # >>> PROPERTY IS JUST A STRING
                    if type(t_properties[i]) is str:

                        # EXTRACTING THE NAMESPACE TO USE FOR THE PROPERTY
                        curr_ns = Ut.get_uri_ns_local_name(t_properties[i])

                        if type(curr_ns) is list:

                            # Setting up the prefix and predicate
                            predicate = "{}voc:{}".format(short_name, curr_ns[1])
                            prefix = "{}voc".format(short_name)

                            # GENERATE THE LIST OF OPTIONAL PROPERTIES
                            # optional += "\n\t\tOPTIONAL{{ ?{}   {:55}   ?{}_{} .}}".format(
                            #     ds_ns_name[1], predicate, attache, curr_ns[1])

                            # ADDING NAMESPACE TO THE VIEW QUERY
                            if prefix not in namespace:
                                namespace[prefix] = curr_ns[0]
                                namespace_str += "\nPREFIX {}: <{}>".format(prefix, curr_ns[0])

                            # Adding predicates
                            if i == len(t_properties) - 1:

                                if namespace[prefix] != curr_ns[0]:
                                    view_where += "\n\t\t\t<{}> ?{}{}_{} .".format(
                                        t_properties[i], attache, e_type, curr_ns[1])
                                else:
                                    view_where += "\n\t\t\t{:55} ?{}{}_{} .".format(predicate, attache, e_type, curr_ns[1])
                            else:

                                if namespace[prefix] != curr_ns[0]:
                                    view_where += "\n\t\t\t<{}> ?{}{}_{} ;".format(
                                        t_properties[i], attache, e_type, curr_ns[1])
                                else:
                                    view_where += "\n\t\t\t{:55} ?{}{}_{} ;".format(predicate, attache, e_type, curr_ns[1])

                            # ADDING THE VARIABLE LIST and making it
                            # unique to a dataset with the variable attache
                            value = (" ?{}{}_{}".format(attache, e_type, curr_ns[1]))
                            if len(view_select + value) > str_limit:
                                variables_list[count] = view_select
                                view_select = value
                                count += 1
                            else:
                                view_select += value

                        # IN THIS CASE, ONLY THE SUBJECT IS PROVIDED
                        else:
                            # TODO check this
                            # ""
                            view_where += ".\n\t\t?{}\n\t\t\t?p ?o .".format(curr_ns)

                    # >>> HERE, WE ARE DEALING WITH A SUBJECT AND A PREDICATE
                    elif type(t_properties[i]) is list:

                        if len(t_properties[i]) == 2:
                            curr_ns = Ut.get_uri_ns_local_name(t_properties[i][1])

                            if type(curr_ns) is list:
                                predicate = "{}voc:{}".format(short_name, curr_ns[1])
                                prefix = "{}voc".format(short_name)

                                # ADDING NAMESPACE
                                if prefix not in namespace:
                                    namespace[prefix] = curr_ns[0]
                                    namespace_str += "\nPREFIX {}: <{}>".format(prefix, curr_ns[0])

                                # REMOVE PREVIOUS PUNCTUATION
                                # print "REMOVING PREDICATE"
                                view_where = view_where[:len(view_where) - 2]
                                view_where += " .\n\t\t?{}\n\t\t\t{:55} ?{}{}_{} .".format(
                                    t_properties[i][0], predicate, attache, e_type, curr_ns[1])

                                # ADDING THE VARIABLE LIST
                                value = (" ?{}{}_{}".format(attache, e_type, curr_ns[1]))
                                if len(view_select + value) > str_limit:
                                    variables_list[count] = view_select
                                    view_select = value
                                    count += 1

                                else:
                                    view_select += value

                    # >>> PROPERTY IS A SET OF TUPLE WITH THE PROPERTY AND A BOOLEAN
                    # VALE INDICATING WHETHER OR NOT THE PROPERTY IS OPTIONAL
                    elif type(t_properties[i]) is tuple:

                        # Setting up the prefix and predicate
                        curr_ns = Ut.get_uri_ns_local_name(t_properties[i][0])
                        prefix = "{}voc_{}".format(short_name, str(count_ns))

                        # ADDING NAMESPACE
                        if curr_ns[0] not in namespace:
                            count_ns += 1
                            namespace[curr_ns[0]] = prefix
                            namespace_str += "\nPREFIX {}: <{}>".format(prefix, curr_ns[0])

                        # ACCESSING THE RIGHT NAMESPACE
                        prefix = namespace[curr_ns[0]]

                        # SETTING THE PREDICATE WITH THE RIGHT NAMESPACE
                        predicate = "{}:{}".format(prefix, curr_ns[1])

                        # CHECKING IF TUPLE OF 2
                        if len(t_properties[i]) == 2:

                            # ADDING PREDICATE AND SPARQL PUNCTUATION
                            if i == len(t_properties) - 1:

                                if t_properties[i][1] is True:
                                    optional += "\n\t\tOPTIONAL{{ ?{}{:15} {:60} ?{}{}_{} . }}".format(
                                        ds_ns_name[1], "{}_1".format(e_type), predicate, attache, e_type, curr_ns[1])
                                else:
                                    view_where += "\n\t\t\t{:55} ?{}{}_{} .".format(
                                        predicate, attache, e_type, curr_ns[1])

                            else:
                                if t_properties[i][1] is True:
                                    optional += "\n\t\tOPTIONAL{{ ?{}{:15} {:60} ?{}{}_{} . }}".format(
                                        ds_ns_name[1], "{}_1".format(e_type), predicate, attache, e_type, curr_ns[1])
                                else:
                                    view_where += "\n\t\t\t{:55} ?{}{}_{} ;".format(
                                        predicate, attache, e_type, curr_ns[1])

                            # ADDING THE VARIABLE LIST
                            value = (" ?{}{}_{}".format(attache, e_type, curr_ns[1]))
                            if len(view_select + value) > str_limit:
                                variables_list[count] = view_select
                                view_select = value
                                count += 1

                            else:
                                view_select += value

                # IN CASE THE SELECTED PROPERTIES ARE ALL OPTIONAL, REMOVE THE RESOURCE
                # print "########################WERE", view_where
                # view_where = view_where.replace("?{}".format(ds_ns_name[1]), "")

                if len(optional) > 0:

                    if view_where[len(view_where) - 1] == ".":
                        "DO NOTHING"

                    elif view_where[len(view_where) - 1] == ";":
                        view_where = "{}.".format(view_where[:len(view_where) - 1])

                    else:
                        # IN CASE THE SELECTED PROPERTIES ARE ALL OPTIONAL, REMOVE THE RESOURCE
                        # print "########################WERE", view_where
                        # print "############", view_where[len(view_where) - 1]
                        view_where = view_where.replace("?{}".format(ds_ns_name[1]), "")

                    view_where += "\n\t\t### OPTIONAL PROPERTIES{}\n\t".format(optional)
                # refresh
                optional = ""

            # close
            view_where += "\n\t}\n"

        my_list = ""
        for key, variable in variables_list.items():
            my_list += "\n" + variable

        if limit == 0:
            lmt = ""
        else:
            lmt = "LIMIT {}".format(limit)

        query = "{}\n\nSELECT DISTINCT {}\n{{{}{}\n}} {}".format(
            namespace_str, my_list + view_select, inter, view_where, lmt)

        # print "\nVIEW QUERY FOR GENERATING TABLE:", query

        # table = sparql_xml_to_matrix(query)
        # display_matrix(table, spacing=80, limit=limit, is_activated=False)
        print "\nDONE GENERATING THE VIEW"
        # return {"metadata": view_metadata, "query": query, "table": table}
        return {"metadata": view_metadata, "query": query, "sparql_issue": is_problematic}

    except Exception as err:
        print ">>> ERROR:", err
        view_metadata = {St.message: "Fatal Error"}
        return {"metadata": view_metadata, "query": None, "sparql_issue": is_problematic}


def retrieve_view(question_uri, view_uri):

    view_lens_query = """
    PREFIX alivocab:    <http://risis.eu/alignment/predicate/>
    ### GETTING THE VIEW_LENS ELEMENTS (LINKSET OR/AND LENS)
    select ?linkset_lens
    {{
        GRAPH <{}>
        {{
            #?idea	alivocab:created ?view .
            <{}>
                a 						<http://risis.eu/class/View> ;
                alivocab:hasViewLens/alivocab:selected ?linkset_lens
        }}
    }}
    """.format(question_uri, view_uri)

    # RUN THE QUERY
    view_lens_matrix = sparql_xml_to_matrix(view_lens_query)

    # REDUCE
    view_lens = None
    if view_lens_matrix:
        if view_lens_matrix[St.result]:
            view_lens = reduce(lambda x, y: x + y, view_lens_matrix[St.result][1:])
    # print "view_lens:", view_lens
    # print "view_lens_query:", view_lens_query
    # print "view_lens_matrix:", view_lens_matrix

    view_filter_query = """
    PREFIX alivocab:    <http://risis.eu/alignment/predicate/>
    PREFIX void:        <http://rdfs.org/ns/void#>
    ### GETTING THE VIEW_FILTERS
    select ?target ?datatype ?selected ?selectedOptional
    {{
        GRAPH <{}>
        {{
            #?idea	alivocab:created ?view .
            <{}>
                a 						<http://risis.eu/class/View> ;
                alivocab:hasFilter 		?filter .

             ?filter
                void:target			?target ;
            OPTIONAL {{ ?filter void:hasDatatype	?datatype }} 

            OPTIONAL {{ SELECT ?filter (GROUP_CONCAT(DISTINCT ?sel; SEPARATOR=", ") as ?selected) 
			    {{  ?filter alivocab:selected	?sel }} 
              group by ?filter }}.
          
          	OPTIONAL {{ SELECT ?filter (GROUP_CONCAT(?selOpt; SEPARATOR=", ") as ?selectedOptional)
          	    {{ ?filter alivocab:selectedOptional	?selOpt }} 
            group by ?filter }}.
                
        }}
    }} ORDER BY ?target
    """.format(question_uri, view_uri)
    # print view_filter_query

    print view_filter_query

    # RUN QUERY
    view_filter_matrix = sparql_xml_to_matrix(view_filter_query)
    # print "view_filter_query:", view_filter_query

    if view_filter_matrix:
        if view_filter_matrix[St.result]:
            # print "view_filter_matrix:", view_filter_matrix[St.result]
            return {"view_lens": view_lens, "view_filter_matrix": view_filter_matrix[St.result]}

    return {"view_lens": view_lens, "view_filter_matrix": None}


def activity_overview(question_uri, get_text=True):

    idea = ""
    ds_mapping = ""
    alignments_data = ""
    lenses = ""
    views_data = ""

    """
    1. RESEARCH QUESTION LABEL
    """
    idea_result = research_label(question_uri)
    idea += "\tQuestion URI: {}\n\tLabel: {}\n".format(question_uri, idea_result)

    """
    2. RESEARCH QUESTION DATASETS
    """
    datasets = datasets_selected(question_uri)
    if datasets:
        for dataset in datasets:
            ds_mapping += "\t{} | {} | {} instances found\n".format(dataset[0], dataset[1], dataset[2])

    """
    3. RESEARCH QUESTION LINKSETS
    """
    alignments = alignments_mappings(question_uri)
    if alignments:
        for i in range(len(alignments)):
            # THE ALIGNMENT
            alignments_data += "\t{:2} - {}\n".format(i + 1, alignments[i])
            # HE DESCRIPTION OF THE ALIGNMENT
            ali_description = alignments_mappings_description(question_uri, alignments[i])
            for info in ali_description:
                pro = Ut.get_uri_local_name(info[0])
                ls = str(info[1]).replace("http://risis.eu/linkset/", "linkset:")

                # LINKSETS CREATED
                if pro == "created" or pro == "used":
                    size = get_namedgraph_size(info[1], isdistinct=False)
                    alignments_data += "\t\t>>> {:13}: \t{} | {} correspondences found\n".format(pro, ls, size)

                # DESCRIPTION + EVOLUTION
                elif pro != "type":
                    # print info
                    alignments_data += "\t\t{:17}:\t{}\n".format(pro, ls)
            alignments_data += "\n"

    """
    4. RESEARCH QUESTION LENSES
    """
    used_lenses = created_used_lens(question_uri)
    if used_lenses:
        for lens in used_lenses:
            pro = Ut.get_uri_local_name(lens[0])
            les = str(lens[1]).replace("http://risis.eu/lens/", "lens:")
            lenses += "\t\t{:17}:\t{} | {} correspondences\n".format(pro, les, lens[2])

    """
    RESEARCH QUESTION VIEWS
    """
    views_uri = views(question_uri)
    views_requested = 0
    # EXTRACTING ALL THE VIEWS FOR THIS RESEARCH QUESTION
    if views_uri:
        views_requested = len(views_uri) - 1
        for i in range(1, len(views_uri)):
            view_uri = views_uri[i][0]
            views_data += "\n\tView_Lens {}: {}".format(i, view_uri)
            view_composition = linksets_and_lenses(question_uri, view_uri)
            view_filters = filters(question_uri, view_uri)

            # DESCRIBING THE COMPOSITION OF EACH VIEW LENSES
            for element in view_composition:
                views_data += "\n\t\tComposition: {}".format(element)
            views_data += "\n"

            # EXTRACTING THE FILTERS
            for n in range(1, len(view_filters)):
                filter_uri = view_filters[n][0]
                views_data += "\n\t\tFilter {}: {}".format(n, view_filters[n][0])
                filter_dt = filter_data(question_uri, filter_uri)

                # FILTER'S DATASETS
                views_data += "\n\t\t\tDataset: {}".format(filter_dt[1][0])

                for m in range(1, len(filter_dt)):
                    views_data += "\n\t\t\tProperty: {}".format(filter_dt[m][1])

                views_data += "\n"

    if get_text:
        activity_buffer = StringIO()
        activity_buffer.write("\n>>> IDEA\n{}".format(idea))
        activity_buffer.write("\n>>> DATASET MAPPINGS\n{}".format(ds_mapping))
        activity_buffer.write("\n>>> ALIGNMENT & LINKSETS\n{}".format(alignments_data))
        activity_buffer.write("\n>>> LENSES\n{}".format(lenses))
        activity_buffer.write("\n>>> VIEW REQUESTED [{}].\n{}".format(views_requested, views_data)
                              if str(1) == 1 else "\n>>> VIEWS REQUESTED [{}].\n{}".format(views_requested, views_data))
        print activity_buffer.getvalue()
        return activity_buffer.getvalue()
    else:
        result = {"idea": idea, "dataset_mappings": ds_mapping, "alignment_mappings": alignments_data,
                  "lenses": lenses, "view_dic": views_data}
        # print alignments_data
        return result


def datasets_selected(question_uri):
    ds_mapping_query = """
    ### EXTRACTING DATASETS MAPPING
    PREFIX alivocab:    <http://risis.eu/alignment/predicate/>
    SELECT *
    {{
        GRAPH <{0}>
        {{
            <{0}>
                alivocab:selected           ?datasets .

            ?datasets
                a                           <http://risis.eu/class/Dataset> ;
                alivocab:hasDatatype        ?datatype .
        }}

        {{
          SELECT ?datasets (count(distinct ?s) as ?count)
          {{
            GRAPH ?datasets {{ ?s a ?datatype .}}
          }} GROUP BY ?datasets
        }}
    }}""".format(question_uri)
    # print ds_mapping_query

    # RUN THE QUERY
    ds_matrix = sparql_xml_to_matrix(ds_mapping_query)

    # REDUCE
    if ds_matrix:
        if ds_matrix[St.result]:
            datasets = ds_matrix[St.result][1:]
            # datasets = reduce(lambda x, y: x + y, ds_matrix[St.result][1:])
            return datasets
    return None


def alignments_mappings(question_uri):
    query = """
    PREFIX alivocab:    <http://risis.eu/alignment/predicate/>
    PREFIX void:        <http://rdfs.org/ns/void#>
    PREFIX prov:        <http://www.w3.org/ns/prov#>
    ### EXTRACT ALIGNMENT MAPPINGS
    select *
    {{
        GRAPH <{0}>
        {{
             <{0}>
                alivocab:created	?alignmentMapping .

            ?alignmentMapping
                a                   <http://risis.eu/class/AlignmentMapping> ;
        }}
    }}
    """.format(question_uri)
    # print query

    # RUN THE QUERY
    alg_matrix = sparql_xml_to_matrix(query)
    # print alg_matrix

    if alg_matrix:
        # display_matrix(alg_matrix, is_activated=True)
        if alg_matrix[St.result]:
            # alignments = alg_matrix[St.result]
            alignments = reduce(lambda x, y: x + y, alg_matrix[St.result][1:])
            return alignments

    return None


def alignments_mappings_description(question_uri, alignment_uri):
    query = """
    PREFIX alivocab:    <http://risis.eu/alignment/predicate/>
    PREFIX void:        <http://rdfs.org/ns/void#>
    PREFIX prov:        <http://www.w3.org/ns/prov#>
    ### EXTRACT ALIGNMENT MAPPINGS
    select *
    {{
        GRAPH <{0}>
        {{
             <{0}>
                alivocab:created	<{1}> .

            <{1}>
                ?pred               ?obj .
        }}
    }}
    """.format(question_uri, alignment_uri)
    # print query

    # RUN THE QUERY
    alg_matrix = sparql_xml_to_matrix(query)
    # print alg_matrix

    if alg_matrix:
        # display_matrix(alg_matrix, is_activated=True)
        if alg_matrix[St.result]:
            # alignments = alg_matrix[St.result]
            # alignments = reduce(lambda x , y: x + y, alg_matrix[St.result][1:])
            return alg_matrix[St.result][1:]
    return None


def created_used_lens(question_uri):
    query = """
    PREFIX alivocab:    <http://risis.eu/alignment/predicate/>
    PREFIX bdb:         <http://vocabularies.bridgedb.org/ops#>
    ### GETTING THE VIEW_LENS ELEMENTS (LINKSET OR/AND LENS)
    select ?created  ?lens ?count
    {{
        GRAPH <{0}>
        {{
            <{0}>
                ?created			?lens.

            ?lens
                a                   bdb:Lens .
        }}

        {{
          SELECT ?lens (count(distinct ?subj) as ?count)
          {{
            GRAPH ?lens
            {{
                ?subj ?sing ?pre .
            }}
            GRAPH ?singGraph
            {{
                ?sing ?sP   ?sO .
            }}
          }} GROUP BY ?lens
        }}
    }}
    """.format(question_uri)
    # print query

    # RUN THE QUERY
    lenses_matrix = sparql_xml_to_matrix(query)

    if lenses_matrix:
        # display_matrix(alg_matrix, is_activated=True)
        if lenses_matrix[St.result]:
            # alignments = alg_matrix[St.result]
            # alignments = reduce(lambda x , y: x + y, alg_matrix[St.result][1:])
            return lenses_matrix[St.result][1:]
    return None


#################################################################################################
#################################################################################################


def research_label(question_uri):
    # RESEARCH QUESTION
    rq_query = """
    PREFIX alivocab:    <http://risis.eu/alignment/predicate/>
    ### GETTING THE RESEARCH QUESTION LABEL
    select *
    {{
        GRAPH <{0}>
        {{
            <{0}>
                a 			<http://risis.eu/class/ResearchQuestion> ;
                rdfs:label	?researchQuestion .

        }}
    }}
    """.format(question_uri)
    question_matrix = sparql_xml_to_matrix(rq_query)
    if question_matrix and question_matrix[St.result]:
        return question_matrix[St.result][1][0]
    return None


def views(question_uri):
    query = """
    PREFIX alivocab:    <http://risis.eu/alignment/predicate/>
    ### GETTING THE VIEW_LENS ELEMENTS (LINKSET OR/AND LENS)
    select ?view
    {{
        GRAPH <{0}>
        {{
            <{0}>
                a 			            <http://risis.eu/class/ResearchQuestion> ;
                rdfs:label	            ?researchQuestion ;
                alivocab:created		?view .
            ?view
                alivocab:hasViewLens    ?viewLens .
        }}
    }}
    """.format(question_uri)
    # print query
    # RUN QUERY
    views_matrix = sparql_xml_to_matrix(query)
    # print "view_filter_query:", view_filter_query
    if views_matrix and views_matrix[St.result]:
        # print "view_filter_matrix:", view_filter_matrix[St.result]
        display_matrix(views_matrix, is_activated=False)
        return views_matrix[St.result]
    else:
        return None


def linksets_and_lenses(question_uri, view_uri):
    view_lens_query = """
    PREFIX alivocab:    <http://risis.eu/alignment/predicate/>
    ### GETTING THE VIEW_LENS ELEMENTS (LINKSET OR/AND LENS)
    select ?linkset_lens
    {{
        GRAPH <{}>
        {{
            <{}>
                a 						<http://risis.eu/class/View> ;
                alivocab:hasViewLens/alivocab:selected ?linkset_lens
        }}
    }} ORDER BY ?linkset_lens
    """.format(question_uri, view_uri)

    # RUN THE QUERY
    view_lens_matrix = sparql_xml_to_matrix(view_lens_query)

    # REDUCE
    if view_lens_matrix:
        if view_lens_matrix[St.result]:
            view_lens = reduce(lambda x, y: x + y, view_lens_matrix[St.result][1:])
            return view_lens
    return None


def filters(question_uri, view_uri):
    query = """
    PREFIX alivocab:    <http://risis.eu/alignment/predicate/>
    ### GETTING THE FILTERS OF THE VIEW
    ### [A FILTER IS COMPOSED OF A DATASET AND SELECTED PROPERTIES]
    select ?filters
    {{
        GRAPH <{}>
        {{
            <{}>
                alivocab:hasFilter 		?filters .

        }}
    }}
    """.format(question_uri, view_uri)
    # print query

    # RUN QUERY
    filters_matrix = sparql_xml_to_matrix(query)
    # print "view_filter_query:", view_filter_query

    if filters_matrix and filters_matrix[St.result]:
        # print "view_filter_matrix:", view_filter_matrix[St.result]
        display_matrix(filters_matrix, is_activated=False)
        return filters_matrix[St.result]

    else:
        return None


def filter_data(question_uri, filter_uri):

    view_filter_query = """
    PREFIX alivocab:    <http://risis.eu/alignment/predicate/>
    PREFIX void:        <http://rdfs.org/ns/void#>
    ### GETTING THE VIEW_FILTERS
    select ?target ?selected ?selected_selectedOptional
    {{
        GRAPH <{0}>
        {{
             <{1}>
                void:target			                            ?target ;
                ?selected_selectedOptional  	                ?selected .
                #alivocab:selected|alivocab:selectedOptional	?selected .
        }}
    }} ORDER BY ?target ?selected
    """.format(question_uri, filter_uri)
    # print view_filter_query
    # RUN QUERY
    view_filter_matrix = sparql_xml_to_matrix(view_filter_query)
    # print "view_filter_query:", view_filter_query
    if view_filter_matrix and view_filter_matrix[St.result]:
        # print "view_filter_matrix:", view_filter_matrix[St.result]
        # display_matrix(view_filter_matrix, is_activated=True)
        return view_filter_matrix[St.result]
    else:
        return None


def research_first_hops(question_uri):
    query = """
    PREFIX alivocab:    <http://risis.eu/alignment/predicate/>
    ### GETTING THE VIEW_LENS ELEMENTS (LINKSET OR/AND LENS)
    select ?researchQuestion ?view ?viewLens ?filters
    {{
        GRAPH <{0}>
        {{
            <{0}>
                a 			            <http://risis.eu/class/ResearchQuestion> ;
                rdfs:label	            ?researchQuestion ;
                alivocab:created		?view .

            ?view
                alivocab:hasViewLens    ?viewLens ;
                alivocab:hasFilter 		?filters .

        }}
    }}
    """.format(question_uri)
    # print query
    # RUN QUERY
    first_hop_info_matrix = sparql_xml_to_matrix(query)
    # print "view_filter_query:", view_filter_query
    if first_hop_info_matrix and first_hop_info_matrix[St.result]:
        # print "view_filter_matrix:", view_filter_matrix[St.result]
        display_matrix(first_hop_info_matrix, is_activated=False)
        return first_hop_info_matrix[St.result]
    else:
        return None


def get_namedgraph_size(linkset_uri, isdistinct=False):
    distinct = ""

    if isdistinct is True:
        distinct = "DISTINCT "

    check_query = "\n{}\n{}\n{}\n{}\n{}\n{}\n{}".format(
        # "PREFIX linkset: <http://risis.eu/linkset/>",
        # "PREFIX lsMetadata: <http://risis.eu/linkset/metadata/>",
        # "PREFIX predicate: <http://risis.eu/linkset/predicate/>",
        # "PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>",
        "    ##### GETTING THE LINKSET SIZE",
        "    select(count({}?source) as ?triples)".format(distinct),
        "    WHERE ",
        "    {",
        "       GRAPH <{}>".format(linkset_uri),
        "       { ?source ?predicate ?target }",
        "    }"
    )

    # print check_query

    result = endpoint(check_query)

    # print result

    if result[St.result] is not None:
        dropload_doc = xmltodict.parse(result[St.result])
        return dropload_doc['sparql']['results']['result']['binding']['literal']['#text']
    else:
        return None


def view_description(question_uri):
    """
    RESEARCH QUESTION VIEWS
    """
    views_data = Buffer.StringIO()
    views_uri = views(question_uri)
    views_requested = 0
    # EXTRACTING ALL THE VIEWS FOR THIS RESEARCH QUESTION

    if views_uri:
        views_requested = len(views_uri) - 1
        for i in range(1, len(views_uri)):
            view_uri = views_uri[i][0]
            views_data.write("\n\t\tView_Lens {}: {}\n".format(i, view_uri))
            view_composition = linksets_and_lenses(question_uri, view_uri)
            view_filters = filters(question_uri, view_uri)

            # DESCRIBING THE COMPOSITION OF EACH VIEW LENSES
            for element in view_composition:
                views_data.write("\n\t\t\tDATASET: {}".format(element))
            views_data.write("\n")

            # EXTRACTING THE FILTERS
            for n in range(1, len(view_filters)):
                filter_uri = view_filters[n][0]
                # views_data.write("\n\t\tFilter {}: {}".format(n, view_filters[n][0]))
                filter_dt = filter_data(question_uri, filter_uri)

                # FILTER'S DATASETS
                views_data.write("\n\t\t\t\tFilter for dataset: {}".format(filter_dt[1][0]))

                for m in range(1, len(filter_dt)):
                    views_data.write("\n\t\t\t\t\tProperty: {}".format(filter_dt[m][1]))

                views_data.write("\n")

    return views_data.getvalue()


