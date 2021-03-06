
import time
import datetime
import traceback
import cStringIO as Buffer
import Alignments.Query as Qry
import Alignments.Utility as Ut
import Alignments.Settings as St
import Alignments.NameSpace as Ns
import Alignments.ErrorCodes as Ec
import Alignments.GenericMetadata as Gn
import Alignments.UserActivities.UserRQ as Urq
from Alignments.Lenses.LensUtility import generate_lens_name
import Alignments.Lenses.Lens_Union as Lens_Union
from Alignments.Query import get_graph_type, get_lens_operator, \
    get_graph_targets, get_graph_source_target, sparql_xml_to_matrix, display_matrix

short = 0

def intersection2(specification):



    print "\nINTERSECTION TASK" \
          "\n======================================================" \
          "========================================================\n"
    query = ""
    p_count = 0
    up_count = 0
    check = dict()
    union_check = dict()
    # target_check = dict()
    view_lens = specification[St.datasets]
    # print datasets

    for graph in view_lens:

        if type(graph) is not str and type(graph) is not unicode:
            # print dataset
            print "THE DATASET MUST BE OF TYPE STRING. {} WAS GIVEN.".format(type(graph))
            return None

        # NAME OF THE GRAPH
        graph_name = Ut.get_uri_local_name(graph)
        # print "Dataset:", dataset

        # GET THE TYPE OF THE GRAPH
        graph_type = get_graph_type(graph)

        if graph_type[St.message] != "NO RESPONSE":

            if graph_type[St.result] is not None:
                # print "\tABLE TO RETRIEVE THE TYPE {}".format(graph_type)

                # EXPECTING ONE RESULT. BECAUSE THE MATRIX HAS A HEADER, LENS NEED TO BE 2
                if len(graph_type[St.result] ) == 2:
                    # EXPECTING A LENS DATATYPE

                    if graph_type[St.result] [1][0] == "{}Lens".format(Ns.bdb):
                        operator = get_lens_operator(graph)
                        # print "\tLENS GENERATED BY {}".format(operator)

                        if (operator is not None) and (operator == "{}".format(Ns.lensOpu)):

                            if graph not in check:
                                check[graph] = 1
                                # print "\tGETTING TARGET GRAPHS"
                                targets = get_graph_targets(graph)

                                if targets[St.result] is not None:
                                    # print "\tABLE TO RETRIEVE TARGETS {}".format(targets)
                                    union_query = ""
                                    graphs = list()
                                    for i in range(1, len(targets[St.result])):
                                        target = targets[St.result][i][0]
                                        # print "target: ", target
                                        # GET SOURCE AND TARGET DATASETS
                                        src_trg = get_graph_source_target(target)

                                        if src_trg[St.result] is not None:
                                            src = Ut.get_uri_local_name(src_trg[St.result][1][0])
                                            trg = Ut.get_uri_local_name(src_trg[St.result][1][1])
                                            # print "\tSOURCE: {} TARGET:{}".format(src, trg)

                                            if "{}_{}".format(src, trg) in union_check:
                                                up_count += 1
                                                "\t{}_{} already exist".format(src, trg)
                                                # print "\t{}_{} already exist".format(src, trg)
                                            else:
                                                union_check["{}_{}".format(src, trg)] = up_count
                                                temp = "\n\t\tGRAPH <{}> \n\t\t{{ " \
                                                       "\n\t\t\t?{} ?pred_{} ?{} . " \
                                                       "\n\t\t}}".format(graph, src, up_count, trg)
                                                # print "\tTHE RESULTING GRAPH {}".format(temp)
                                                graphs.append(temp)

                                        else:
                                            "No source and target datasets"

                                    # query += "\n\tGRAPH <{}> \n\t{{ {} \n\t}}".format(dataset, triples)

                                    if len(union_check) > 1:
                                        for i in range(len(graphs)):
                                            if i == 0:
                                                union_query += "\n\t### LENS BY UNION: {}\n\t{{{}\n\t}}".format(
                                                    graph_name, graphs[i])
                                            elif i > 0:
                                                union_query += "\n\tUNION\n\t{{{}\n\t}}".format(graphs[i])
                                    else:
                                        union_query += "\n\t### LENS BY UNION: {}\n\t{{{}\n\t}}".format(
                                            graph_name, graphs[0])

                                    query += union_query

                                else:
                                    "No target for this grap"
                            else:
                                "\tTHE DATASET ALREADY EXISTS"
                                # print "\tTHE DATASET ALREADY EXISTS"
                        else:
                            "Not a union operator"

                    elif graph_type[St.result] [1][0] == "{}Linkset".format(Ns.void):
                        "It is a linkset"
                        # GET SOURCE AND TARGET DATASETS
                        src_trg = get_graph_source_target(graph)
                        if src_trg is not None:
                            src = Ut.get_uri_local_name(src_trg[St.result][1][0])
                            trg = Ut.get_uri_local_name(src_trg[St.result][1][1])
                            if graph in check:
                                print "already exist"
                            else:
                                p_count += 1
                                check[graph] = p_count
                                query += "\n\t### LINKSET: {}\n\tGRAPH <{}> \n\t{{\n\t\t?{} ?predicate_{} ?{} .\n\t}}".\
                                    format(graph_name, graph, src, p_count, trg)

            else:
                print "WE COULD NOT ACCESS THE TYPE OF THE GRAPH: <{}>.".format(graph)

        else:
            print Ec.ERROR_CODE_1
            return None
    # print query
    return query


def intersection(specs, display=False):

    inter = ""

    count_graph = 1
    for graph in specs[St.datasets]:

        query = """
    PREFIX void: <{}>
    PREFIX bdb: <{}>
    SELECT distinct ?subTarget ?objTarget ?subjectEntityType ?objectEntityType
    {{
        <{}>
            #void:target*/(void:subjectsTarget|void:objectsTarget)* ?x ;
            void:target*/(void:subjectsTarget|void:objectsTarget)* ?x .

        ?x
            void:subjectsTarget     ?subTarget ;
            void:objectsTarget      ?objTarget ;
            bdb:subjectsDatatype    ?subjectEntityType ;
            bdb:objectsDatatype     ?objectEntityType .

        FILTER NOT EXISTS {{ ?subTarget a void:Linkset }}
        FILTER NOT EXISTS {{ ?objTarget a void:Linkset }}
    }}""".format(Ns.void, Ns.bdb, graph)
        # print "INTERSECTION QUERY:", query
        response = sparql_xml_to_matrix(query)

        if display:
            print "INTERSECTION QUERY:", query
        # print "\nGRAPH:", graph
        # print "RESPONSE:", response
        # exit(0)

        if response:
            targets = response[St.result]

            # IF THE RESULT HAS MORE THAN
            # print "LENGTH:", len(targets)
            if targets is not None and len(targets) > 2:
                union = ""

                for i in range(1, len(targets)):

                    append = "UNION" if i < len(targets) -1 else ""
                    tab = "" if i == 1 else ""
                    src = Ut.get_uri_local_name(targets[i][0])
                    trg = Ut.get_uri_local_name(targets[i][1])

                    if src[0].isdigit():
                        src = "D{}".format(src)

                    if trg[0].isdigit():
                        trg = "D{}".format(trg)

                    src_TYPE = Ut.get_uri_local_name(targets[i][2])
                    trg_TYPE = Ut.get_uri_local_name(targets[i][3])

                    src_variable = "{}_{}_1".format(src, src_TYPE[short:])

                    if src == trg and src_TYPE == trg_TYPE:
                        trg_variable = "{}_{}_2".format(trg, trg_TYPE[short:])
                    else:
                        trg_variable = "{}_{}_1".format(trg, trg_TYPE[short:])

                    union += "\n\t\t{0}{{ ?{1}  ?predicate_{2}  ?{3} . }} {4}".format(
                        tab, src_variable, i, trg_variable, append)

                union = """
    ### ABOUT {0}
    GRAPH <{0}>
    {{
        {1}
    }}
    """.format(graph, union)
                # print "UNION:", union
                inter += union

            elif targets and len(targets) == 2:
                src = Ut.get_uri_local_name(targets[1][0])
                trg = Ut.get_uri_local_name(targets[1][1])

                if src[0].isdigit():
                    src = "D{}".format(src)

                if trg[0].isdigit():
                    trg = "D{}".format(trg)

                src_TYPE = Ut.get_uri_local_name(targets[1][2])
                trg_TYPE = Ut.get_uri_local_name(targets[1][3])

                src_variable = "{}_{}_1".format(src, src_TYPE[short:])

                if src == trg and src_TYPE == trg_TYPE:
                    trg_variable = "{}_{}_2".format(trg, trg_TYPE[short:])
                else:
                    trg_variable = "{}_{}_1".format(trg, trg_TYPE[short:])

                inter += """
    ### ABOUT {0}
    GRAPH <{0}>
    {{
        ?{1}    ?pred_{2}   ?{3} .
    }}
    """.format(graph, src_variable, count_graph, trg_variable)

        count_graph += 1

    # print inter
    # exit(0)
    return inter


def intersection_extended(specs, lens_name, display=False):

    # print Ut.headings("EXTENDED INTERSECTION")
    inter = ""
    insert = Buffer.StringIO()
    insert_sing = Buffer.StringIO()
    model_1 = """
    ### ABOUT {0}
    GRAPH <{0}>
    {{
        {1}
    }}
    """
    model_2 = """
    ### {2}. ABOUT {0}
    GRAPH <{0}>
    {{
        ?{1}    ?pred_{2}   ?{3} .
    }}
    ### SINGLETONS
    GRAPH <{4}>
    {{
        ?pred_{2}   ?x_{2}   ?y_{2} .
    }}"""

    count_graph = 1
    for graph in specs[St.datasets]:

        query = """
    PREFIX void: <{}>
    PREFIX bdb: <{}>
    SELECT distinct ?subTarget ?objTarget ?subjectEntityType ?objectEntityType
    {{
        <{}>
            #void:target*/(void:subjectsTarget|void:objectsTarget)* ?x ;
            void:target*/(void:subjectsTarget|void:objectsTarget)* ?x .

        ?x
            void:subjectsTarget     ?subTarget ;
            void:objectsTarget      ?objTarget ;
            bdb:subjectsDatatype    ?subjectEntityType ;
            bdb:objectsDatatype     ?objectEntityType .

        FILTER NOT EXISTS {{ ?subTarget a void:Linkset }}
        FILTER NOT EXISTS {{ ?objTarget a void:Linkset }}
    }}""".format(Ns.void, Ns.bdb, graph)
        # print "INTERSECTION QUERY:", query
        response = sparql_xml_to_matrix(query)

        if display:
            print "INTERSECTION QUERY:", query
        # print "\nGRAPH:", graph
        # print "RESPONSE:", response
        # exit(0)

        if response:

            targets = response[St.result]

            # IF THE RESULT HAS MORE THAN
            # print "LENGTH:", len(targets)
            if targets is not None and len(targets) > 2:
                union = ""

                for i in range(1, len(targets)):

                    append = "UNION" if i < len(targets) -1 else ""
                    tab = "" if i == 1 else ""
                    src = Ut.get_uri_local_name(targets[i][0])
                    trg = Ut.get_uri_local_name(targets[i][1])

                    if src[0].isdigit():
                        src = "D{}".format(src)

                    if trg[0].isdigit():
                        trg = "D{}".format(trg)

                    src_TYPE = Ut.get_uri_local_name(targets[i][2])
                    trg_TYPE = Ut.get_uri_local_name(targets[i][3])

                    src_variable = "{}_{}_1".format(src, src_TYPE[short:])

                    if src == trg and src_TYPE == trg_TYPE:
                        trg_variable = "{}_{}_2".format(trg, trg_TYPE[short:])
                    else:
                        trg_variable = "{}_{}_1".format(trg, trg_TYPE[short:])

                    union += "\n\t\t{0}{{ ?{1}  ?predicate_{2}  ?{3} . }} {4}".format(
                        tab, src_variable, i, trg_variable, append)

                union = model_1.format(graph, union)
                # print "UNION:", union
                inter += union

            # ONLY TWO TARGETS
            elif targets and len(targets) == 2:

                src = Ut.get_uri_local_name(targets[1][0])
                trg = Ut.get_uri_local_name(targets[1][1])

                if src[0].isdigit():
                    src = "D{}".format(src)

                if trg[0].isdigit():
                    trg = "D{}".format(trg)

                src_TYPE = Ut.get_uri_local_name(targets[1][2])
                trg_TYPE = Ut.get_uri_local_name(targets[1][3])

                src_variable = "{}_{}_1".format(src, src_TYPE[short:])

                if src == trg and src_TYPE == trg_TYPE:
                    trg_variable = "{}_{}_2".format(trg, trg_TYPE[short:])
                else:
                    trg_variable = "{}_{}_1".format(trg, trg_TYPE[short:])

                inter += model_2.format(graph, src_variable, count_graph, trg_variable,
               "{}{}".format(Ns.singletons, Ut.get_uri_local_name_plus(graph)))

                insert.write("\t\t?{}    ?pred_{}   ?{} .\n".format(src_variable, count_graph, trg_variable))
                insert_sing.write("\t\t?pred_{0}   ?x_{0}     ?y_{0}.\n".format(count_graph))

        count_graph += 1

    # print inter
    # exit(0)
    insert_query = """INSERT\n{{
    ### LINKS
    GRAPH <{5}{4}>
    {{\n{1}\t}}

    ### METADATA
    GRAPH <{6}{4}>
    {{\n{3}\t}}\n}}\nWHERE\n{{{2}\n}}
    """.format("", insert.getvalue(), inter, insert_sing.getvalue(), lens_name, Ns.lens, Ns.singletons)
    return insert_query


def intersecting(specs, activated=False):

    if activated is False:
        print ("THE FUNCTION [intersecting] IS NOT ACTIVATED")
        return {St.message: "THE FUNCTION [intersecting] IS NOT ACTIVATED.", St.error_code: 1, St.result: None}

    print Ut.headings("EXECUTING INTERSECTION SPECS...")

    # 1. GENERATE THE LENS NAME
    lens_name = generate_lens_name(specs['datasets'], operator="intersection")
    specs[St.lens] = "{}{}".format(Ns.lens, lens_name['name'])
    Ut.update_specification(specs)

    # **********************************
    # 3. GOOD TO GO CHECK
    # **********************************
    query = """
            SELECT *
            {{
                <{}> ?predicate ?object .
            }}
                """.format(specs[St.lens])
    check = Lens_Union.run_checks(specs, query, operator="intersection")

    # NOT GOOD TO GO, IT ALREADY EXISTS
    if check[St.message].__contains__("ALREADY EXISTS"):
        return {St.message: check[St.message], St.error_code: 71, St.result: specs[St.lens]}

    # **********************************
    # GOOD TO GO
    # **********************************
    else:

        try:
            specs[St.lens_target_triples] = ""

            # DOCUMENTING START TIME
            lens_start = time.time()

            print "\n4. GENERATE THE INSERT QUERY"
            specs[St.insert_query] = intersection_extended(specs, lens_name=specs[St.lens_name])
            print specs[St.insert_query]

            print "\n5. >>> LOOKING FOR INTERSECTING LINKS"
            print "\t", Qry.boolean_endpoint_response(specs[St.insert_query])

            print "\n6. EXTRACTING THE NUMBER OF TRIPLES"
            specs[St.triples] = Qry.get_namedgraph_size("{0}{1}".format(Ns.lens, specs[St.lens_name]))

            lens_end = time.time()
            diff = lens_end - lens_start
            print " \n>>> Executed so far in    : {:<14}".format(str(datetime.timedelta(seconds=diff)))

            if int(specs[St.triples]) > 0:

                for linkset in specs[St.datasets]:
                    specs[St.lens_target_triples] += \
                        "\n\t        void:target                         <{}> ;".format(linkset)

                print "\n7. INSERTING THE GENERIC METADATA"
                metadata = Gn.intersection_meta(specs)
                # print metadata
                Qry.boolean_endpoint_response(metadata)

                # print "\n8. WRITING TO FILE"

                server_message = "Linksets created as: {}".format(specs[St.lens])
                message = "The linkset was created as [{}] with {} triples found!".format(
                    specs[St.lens], specs[St.triples])

                print "\n\t", server_message

                Urq.register_lens(specs, is_created=True)

                ls_end_2 = time.time()
                diff = ls_end_2 - lens_end
                print ">>> Executed in    : {:<14}".format(str(datetime.timedelta(seconds=diff)))
                print "\t*** JOB DONE! ***"
                return {St.message: message, St.error_code: 0, St.result: specs[St.lens]}

            else:
                print "The linkset was not generated as no match could be found"
                print "\t*** JOB DONE! ***"
                return {St.message: "The linkset was not generated as no match could be found",
                        St.error_code: 4, St.result: None}

        except Exception as err:
            traceback.print_exc()
            return {St.message: Ec.ERROR_CODE_1, St.error_code: 5, St.result: None}


# specs = {
#     'lens_operation': u'intersection',
#     'datasets': [u'http://risis.eu/linkset/grid_20170712_eter_2014_approxStrSim_Organization_altLabel_P1079405301',
#                  u'http://risis.eu/linkset/grid_20170712_eter_2014_approxStrSim_Organization_altLabel_P1661430032',
#                  u'http://risis.eu/linkset/grid_20170712_eter_2014_approxStrSim_Organization_label_N1860664105'],
#     'researchQ_URI': u'http://risis.eu/activity/idea_67a6ce'}


# specs_2 = {'lens_operation': u'intersection',
#     'datasets': [u'http://risis.eu/lens/union_Grid_20170712_Eter_2014_N291690309',
#               u'http://risis.eu/lens/union_Orgreg_20170718_Eter_2014_P1061032980',
#               u'http://risis.eu/lens/union_Orgreg_20170718_Grid_20170712_N1966224323'],
#     'researchQ_URI': u'http://risis.eu/activity/idea_67a6ce'}
#
# specs_3 = {'lens_operation': u'intersection',
#            'datasets': [
#                u'http://risis.eu/linkset/orgreg_20170718_grid_20170712_approxStrSim_University_Entity_current_name_English_N682223883',
#                u'http://risis.eu/linkset/orgreg_20170718_grid_20170712_approxStrSim_University_Entity_current_name_English_P2117262605',
#                u'http://risis.eu/lens/union_Grid_20170712_Eter_2014_N291690309',
#                u'http://risis.eu/lens/union_Orgreg_20170718_Eter_2014_P1061032980',
#                u'http://risis.eu/lens/union_Orgreg_20170718_Grid_20170712_N1966224323'],
#            'researchQ_URI': u'http://risis.eu/activity/idea_67a6ce'}
#
#
#
# print intersection_extended(specs_3, "lens_name", display=False)

# import Alignments.Manage.AdminGraphs as adm
# adm.drop_a_lens("http://risis.eu/lens/intersection_Grid_20170712_Eter_2014_P1326988364", display=True, activated=True)
# print intersecting(specs, activated=True)