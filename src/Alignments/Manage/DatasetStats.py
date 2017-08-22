import math
import Alignments.Query as Qr
import Alignments.Utility as Ut
from cStringIO import StringIO as buffer
from Alignments.Query import sparql_xml_to_matrix, display_matrix

# TODO Not optimised...
def stats(graph, display_table=False, display_text=False):
    optional = dict()
    stat = {}
    text = buffer()

    # 1. FIND ALL TYPES IN THE GRAPH
    qry_types = """
    ### RETRIEVE ALL TYPES FROM THE GRAPH
    SELECT DISTINCT ?Types (count(distinct ?resource) as ?EntityCount)
    {{
        GRAPH <{}>
        {{
            ?resource a ?Types .
        }}
    }} GROUP by ?Types ?EntityType ORDER BY ?Graph
    """.format(graph)
    types_matrix = sparql_xml_to_matrix(qry_types)
    # print types_matrix

    if display_table:
        display_matrix(types_matrix, spacing=70, limit=100, is_activated=True)

    # 2. OR EACH TYPES GET ALL PROPERTIES
    if types_matrix["result"] is not None:

        types = types_matrix["result"]

        for i in range(1, len(types)):
            curr_type = types[i][0]
            type_name = Ut.get_uri_local_name(curr_type )
            instances = int(types[i][1])
            optional[type_name] = dict()
            qry_properties = """
            ### RETRIEVE ALL PROPERTIES FOR THE TYPE [{0}]
            SELECT DISTINCT ?Properties_for_{0}
            {{
                GRAPH <{1}>
                {{
                    ?resource   a                       <{2}> ;
                                ?Properties_for_{0}     ?object .
                }}
            }}
            """.format(type_name, graph, curr_type)
            properties_matrix = sparql_xml_to_matrix(qry_properties)

            if properties_matrix["result"] is not None:

                columns = 4
                rows = len(properties_matrix["result"])

                if display_table:
                    print "\nPROPERTY COUNT:", len(properties_matrix["result"]) - 1
                    display_matrix(properties_matrix, spacing=70, limit=100, is_activated=False)

                # PROPERTY OCCURENCE COUNT
                matrix = [[str(x * y * 0).replace("0", "") for x in range(columns)] for y in range(rows)]


                properties = properties_matrix["result"]
                matrix[0][0] = properties[0][0]
                matrix[0][1] = "Optional"
                matrix[0][2] = "Instances"
                matrix[0][3] = "Percentage"
                # print type_name
                cur_dic = optional[type_name]
                for i in range(1, len(properties)):
                    qry_occurence = """
                    ### RETRIEVE THE NUMBER OF OCCURRENCES FOR THIS PROPERTY
                    ### TYPE        : {2}
                    ### PROPERTY    : {3}
                    ### GRAPH       : {1}
                    SELECT (count(?object) as ?Occurrences)
                    {{
                        GRAPH <{1}>
                        {{
                            ?resource   a   <{2}> ;
                                        <{3}>   ?object .
                        }}
                    }}
                    """.format(type_name, graph, curr_type, properties[i][0])
                    # print qry_occurence
                    Occurrences_matrix = sparql_xml_to_matrix(qry_occurence)
                    if Occurrences_matrix["result"] is not None:
                        # print Occurrences_matrix["result"][1][0]
                        # print i
                        matrix[i][0] = properties[i][0]
                        matrix[i][2] = Occurrences_matrix["result"][1][0]
                        matrix[i][3] = int(Occurrences_matrix["result"][1][0])/float(instances)
                        if int(Occurrences_matrix["result"][1][0])%float(instances) == 0:
                            matrix[i][1] = False
                            cur_dic[properties[i][0]] = False
                        else:
                            matrix[i][1] = True
                            cur_dic[properties[i][0]] = True

                        # matrix = properties_matrix["result"]  + matrix
                # print matrix
                to_display = {"message": "OK", "result": matrix}

                if display_table:
                    display_matrix(to_display, spacing=50, limit=100, is_activated=True)
                stat[type_name] = matrix

    text.write("\nGRAPH: {}".format(graph))
    for key, value in optional.items():
        line = "-------------------------------------------------------------------------------------------------"
        text.write("\n\n\tENTITY TYPE: {}".format(key))
        text.write("\n\t\t{:100}{}".format(line, "------------"))
        text.write("\n\t\t{:<3}{:97}{}".format(len(optional[key]), "Properties", "Optional"))
        text.write("\n\t\t{:100}{}".format(line, "------------"))

        for pro, opt in value.items():
            if opt:
                text.write("\n\t\t{:100}{}".format("{} ***".format(pro), opt))
            else:
                text.write("\n\t\t{:100}{}".format(pro, opt))

    if display_text:
        print text.getvalue()

    return optional


def stats_optimised(graph, display_table=False, display_text=False):

    optional = dict()
    stat = {}
    text = buffer()

    # 1. FIND ALL TYPES IN THE GRAPH
    qry_types = """
    ### RETRIEVE ALL TYPES FROM THE GRAPH
    SELECT DISTINCT ?Types (count(distinct ?resource) as ?EntityCount)
    {{
        GRAPH <{}>
        {{
            ?resource a ?Types .
        }}
    }} GROUP by ?Types ?EntityType ORDER BY ?Graph
    """.format(graph)
    types_matrix = sparql_xml_to_matrix(qry_types)
    # print types_matrix
    # if display_table:
    display_matrix(types_matrix, spacing=70, limit=100, is_activated=display_table)

    # 2. FOR EACH TYPES GET ALL PROPERTIES
    if types_matrix["result"] is not None:
        types = types_matrix["result"]
        for i in range(1, len(types)):
            curr_type = types[i][0]
            type_name = Ut.get_uri_local_name(curr_type)
            instances = int(types[i][1])
            optional[curr_type] = dict()
            qry_properties = """
            ### RETRIEVE ALL PROPERTIES FOR THE TYPE [{0}]
            SELECT DISTINCT ?Properties_for_{0}
            {{
                GRAPH <{1}>
                {{
                    ?resource   a                       <{2}> ;
                                ?Properties_for_{0}     ?object .
                }}
            }}
            """.format(type_name, graph, curr_type)
            properties_matrix = sparql_xml_to_matrix(qry_properties)
            # if display_table:
            # print "\nPROPERTY COUNT:", len(properties_matrix["result"]) - 1
            display_matrix(properties_matrix, spacing=70, limit=100, is_activated=display_table)

            # PROPERTY OCCURENCE COUNT
            pro_text = buffer()
            sel_text = buffer()
            grp_text = buffer()
            if properties_matrix["result"] is not None:

                pro_text.write("\nSELECT ?predicate (COUNT(distinct ?resource) as ?Occurrences)")
                pro_text.write("\n{{\n\tGRAPH <{}> ".format(graph))
                pro_text.write("\n\t{{\n\t\t?resource a             <{}> .".format(curr_type))
                pro_text.write("\n\t\t?resource ?predicate    ?object .")
                pro_text.write("\n\t}}\n}}\nGROUP BY ?predicate".format(grp_text.getvalue()))
                properties = properties_matrix["result"]
                cur_dic = optional[curr_type]
                count = 0
                append = ""

                # RUN THE QUERY FOR PROPERTIES OCCURRENCES
                qry_property_stats = pro_text.getvalue()
                # print qry_property_stats
                Occurrences_matrix = sparql_xml_to_matrix(qry_property_stats)
                # if display_table:
                display_matrix(Occurrences_matrix, spacing=70, limit=100, is_activated=display_table)
                if Occurrences_matrix["result"] != None:
                    Occurrences = Occurrences_matrix["result"]
                    for i in range(1, len(Occurrences)):

                        # THE PROPERTY IS THE KEY OF THE DICTIONARY
                        cur_dic[Occurrences[i][0]] = int(Occurrences[i][1]) % float(instances) != 0

    text.write("\nGRAPH: {}".format(graph))
    for key, value in optional.items():
        line = "-------------------------------------------------------------------------------------------------"
        text.write("\n\n\tENTITY TYPE: {}".format(key))
        text.write("\n\t\t{:100}{}".format(line, "------------"))
        text.write("\n\t\t{:<5}{:97}{}".format(len(optional[key]), "Properties", "Optional"))
        text.write("\n\t\t{:100}{}".format(line, "------------"))

        for pro, opt in value.items():
            if opt:
                text.write("\n\t\t{:100}{}".format("{} ***".format(pro), opt))
            else:
                text.write("\n\t\t{:100}{}".format(pro, opt))

    if display_text:
        print text.getvalue()
    return optional

# stats_optimised("http://risis.eu/dataset/leidenRanking", display_table=False, display_text=True)
# stats_optimised("http://risis.eu/dataset/eter", display_table=False, display_text=True)
# stats_optimised("http://risis.eu/genderc/Applicant", display_table=False, display_text=True)
# stats_optimised("http://risis.eu/dataset/grid_20170522", display_table=False, display_text=True)
# stats("http://risis.eu/dataset/grid_20170522", display_table=False, display_text=True)
# stats("http://risis.eu/dataset/Panellists", display_table=False, display_text=True)
# stats("http://risis.eu/genderc/Applicant", display_table=True, display_text=True)
# stats_optimised("http://risis.eu/dataset/grid", display_table=False, display_text=True)

