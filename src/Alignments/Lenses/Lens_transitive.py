
import Alignments.Query as Qry
import Alignments.Settings as St
import Alignments.NameSpace as Ns
from Alignments.Utility import intersect, write_to_file, get_uri_local_name
import logging


logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)
handler = logging.StreamHandler()
logger.addHandler(handler)

import Alignments.Server_Settings as Ss
DIRECTORY = Ss.settings[St.lens_transitive__dir]


def lens_transitive(data, activated=False):

    # CHECK BOTH DATASETS FOR SAME MECHANISM

    same_as_count = Qry.get_same_as_count(data[St.mechanism])
    # print same_as_count

    # GENERATE THE INSERT QUERY FOR TRANSITIVITY
    transitive_analyses = lens_transitive_query(data)
    if transitive_analyses is None:
        return

    insert_query = transitive_analyses[1]
    # print insert_query
    # exit(0)
    data['is_transitive_by'] = transitive_analyses[0]

    # RUN THE QUERY AT THE END POINT
    if activated is True:
        Qry.boolean_endpoint_response(insert_query)

    # GET THE SIZE OF THE LENS JUST CREATED ABOVE
    size = Qry.get_namedgraph_size(data[St.lens], isdistinct=False)

    # GENERATE THE METADATA ABOUT THE LENS JUST CREATED
    metadata = transitive_metadata(data, size, insert_query, same_as_count)
    print metadata

    # IF ACTIVATED, INSERT THE METADATA
    if activated is True:
        Qry.boolean_endpoint_response(metadata)

    # RUN A CORRESPONDENCE CONSTRUCT QUERY FOR BACKING UP THE DATA TO DISC
    construct_correspondence = Qry.endpointconstruct(Qry.construct_namedgraph(data[St.lens]))

    if construct_correspondence is not None:
        construct_correspondence = construct_correspondence.replace('{', "<{}>\n{{".format(data[St.lens]), 1)

    # RUN A SINGLETON METADATA CONSTRUCT QUERY FOR BACKING UP THE DATA TO DISC
    construct_singletons = Qry.endpointconstruct(Qry.construct_namedgraph(data['singleton_graph']))

    if construct_singletons is not None:
        construct_singletons = construct_singletons. \
            replace('{', "<{}>\n{{".format(data['singleton_graph']), 1)

    # WRITE TO FILE
    if activated is True:
        write_to_file(graph_name=data['link_label'], metadata=metadata, directory=DIRECTORY,
                      correspondences=construct_correspondence, singletons=construct_singletons)

    if activated is False:
        logger.warning("THE FUNCTION IS NOT ACTIVATED BUT THE METADATA THAT IS "
                       "SUPPOSED TO BE ENTERED IS WRITEN TO THE CONSOLE.")


def lens_transitive_query(data):

    """
    :param data:
    :return: a list of:
        is transitive by : the graph by with the other are transitive
        the insert query : that is used to generate the transitive LS
    """

    # print "TRANSITIVITY"
    insert_query = ""
    is_transitive_by = ""
    # pattern = re.compile('[^a-zA-Z]')

    # CHECK WHETHER THE GRAPH ALREADY EXIST
    ask_lens = Qry.graph_exists(data[St.lens])
    # print "lens: {}".format(data[ST.lens_uri])
    if ask_lens is True:
        logger.warning("\n{} ALREADY EXISTS. \nTO PROCEED ANYWAY, PLEASE DELETE "
                       "THE LINKSET FIRST OR CHANGE THE CONTEXT CODE\n".format(data[St.lens]))
        return

    # CHECK WHETHER THE GRAPHS EXIST
    ask_src = Qry.graph_exists(data[St.src_dataset])
    ask_trg = Qry.graph_exists(data[St.trg_dataset])
    if (ask_src is False) or (ask_trg is False):
        message = "SOURCE: {} [exist={}]\nTARGET: {} [exist={}]\n{}".format(
            data[St.src_dataset], ask_src, data[St.trg_dataset], ask_trg,
            "WE CAN NOT POSSIBLY RUN A TRANSITIVITY OPERATION OVER NON EXITING GRAPH")
        print message
        # logger.warning("\nWE CAN NOT POSSIBLY RUN A TRANSITIVITY OPERATION OVER NON EXITING GRAPH")
        return

    # #####################################################################
    """ RECONSTRUCTION OF THE WHERE QUERIES                            """
    # ###############################2#####################################

    s_predicate = "s_predicate"
    o_predicate = "o_predicate"
    result1 = reconstruct(data[St.src_dataset], data[St.src_graph_type], s_predicate)
    result2 = reconstruct(data[St.trg_dataset], data[St.trg_graph_type], o_predicate)

    # #####################################################################
    """ EXIT IF ONE OF THE DATASETS INPUT IS NOT COMPLIANT             """
    # ###############################2#####################################
    if (result1 is None) or (result2 is None):
        print "\nWE CANNOT PROCEED BECAUSE THERE IS NO TRANSITIVITY HERE :)"
        return None

    intersection_result = intersect(result1[0], result2[0])

    if intersection_result is None:
        print "\tSource:", result1[0]
        print "\tTarget:", result2[0]
        print "\nWE CANNOT PROCEED BECAUSE WE COULD NOT FIND ANY INTERSECTION BETWEEN THE DATASETS."
        return None

    if intersection_result is not None:

        if len(intersection_result) > 0:

            # print "VALUE", result1[0]
            is_transitive = intersect(result1[0], result2[0])
            # print is_transitive
            if len(is_transitive) > 1:
                print is_transitive
                print "\nWE CANNOT PROCEED BECAUSE THERE IS NO TRANSITIVITY HERE :)"
                return None

            is_transitive_by = is_transitive[0]

            # #####################################################################
            """ ACCESS SINGLETON GRAPH                                         """
            # #####################################################################
            subject_sing_query = ""
            string = "\t\t?{:50} ?{:20} ?{} .".format("subject", "sing_predicate", "object")
            singleton_gph_count = 0
            alternative1 = ""
            alternative2 = ""

            # THE SUBJECT DATASET CONTAINS A SINGLETON NAMED GRAPH
            if result1[1].__contains__(string):
                singleton_gph_count += 1
                alternative1 = "\n\t\t\t?{:20} ?{} ;".format("sing_predicate1", "object1")

            if result2[1].__contains__(string):
                singleton_gph_count += 1
                alternative2 = "\n\t\t\t?{:20} ?{} .".format("sing_predicate2", "object2")

            if alternative2 == "":
                alternative1 = "\n\t\t\t?{:20} ?{} .".format("sing_predicate1", "object1")

            linktype = "singPre"
            # object_sing_query = ""
            if singleton_gph_count > 0:
                subject_sing_query = "\n{}\n{}\n{}{}{}\n{}"\
                    .format("\tGRAPH tmpgraph:sing",
                            "\t{",
                            "\t\t?{}".format(s_predicate),
                            "{}".format(alternative1),
                            "{}".format(alternative2),
                            "\t}")

            # elif singleton_graph_count == 0:
            #     linktype = "<{}>".format(linktype)

            _subject = list(set(result1[0]).difference(result2[0]))

            if len(_subject) > 0:
                # _subject = pattern.sub("", str(_subject[0]))
                _subject = get_uri_local_name(_subject[0])

                _object = list(set(result2[0]).difference(result1[0]))
                if len(_object) > 0:
                    # _object = pattern.sub("", str(_object[0]))
                    _object = get_uri_local_name(_object[0])

                    print "\nTRANSITIVITY ANALYSES"
                    print "\t{:15}: {}".format("SUBJECT", _subject)
                    print "\t{:15}: {}".format("OBJECT", _object)
                    print "\t{:15}: {}".format("TRANSITIVE by", is_transitive[0])

                string1 = "\t\t?{:50} ?{:20} ?{} .".format(s_predicate, "sing_predicate1", "object1")
                string2 = "\t\t?{:50} ?{:20} ?{} .".format(o_predicate, "sing_predicate2", "object2")
                insert_query = "\n{}\n{}" \
                               "\n\n###### PART 1: {} \n{}" \
                               "\n\n###### PART 2: {}\n{}" \
                               "\n\n###### PART 3: {}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}" \
                               "\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}" \
                               "\n\n###### PART 4: {}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}" \
                               "\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}" \
                               "\n\n###### PART 5: {}\n{}\n{}\n{}\n{}\n{}\n{}\n{}" \
                               "\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}" \
                               "\n\n###### PART 6: {}\n{}\n{}\n{}\n{}\n{}" \
                    .format("prefix tmpgraph:<{}>".format(Ns.tmpgraph),
                            "prefix tmpvocab:<{}>".format(Ns.tmpvocab),

                            # ### PART 1 ##########################################
                            # #####################################################
                            "LOAD SUBJECT CORRESPONDENCES AND SINGLETON METADATA (TEMPORARILY)",
                            "{} ;".format(result1[1].replace(string, string1)),

                            # ### PART 2 ##########################################
                            # #####################################################
                            "LOAD OBJECT CORRESPONDENCES AND SINGLETON METADATA (TEMPORARILY)",
                            "{} ;".format(result2[1].replace(string, string2)),

                            # ### PART 3 ##########################################
                            # #####################################################
                            "LOAD TEMPORARY CORRESPONDENCE  GRAPH",
                            # INSERT CORRESPONDENCE IN TEMPORARY GRAPH
                            "INSERT",
                            "{",
                            "\tGRAPH tmpgraph:corr01",
                            "\t{",
                            "\t\t?{} ?{} ?{} .".format(_subject, s_predicate, _object),
                            "\t}",
                            "{}".format(subject_sing_query),
                            "}",
                            "WHERE",
                            "{",
                            # WHERE SUBJECT CORRESPONDENCES  AND METADATA
                            "\tGRAPH tmpgraph:{}".format(s_predicate),
                            "\t{",
                            "\t\t?{:50} ?{:20} ?{} .".
                            # format(pattern.sub("", result1[0][0]), s_predicate, pattern.sub("", result1[0][1])),
                            format(get_uri_local_name(result1[0][0]), s_predicate, get_uri_local_name(result1[0][1])),

                            "\t\t?{:50} ?{:20} ?{} .".format(s_predicate, "sing_predicate1", "object1"),
                            "\t}",
                            # WHERE OBJECT CORRESPONDENCES AND METADATA
                            "\tGRAPH tmpgraph:{}".format(o_predicate),
                            "\t{",
                            "\t\t?{:50} ?{:20} ?{} .".
                            # format(pattern.sub("", result2[0][0]), o_predicate, pattern.sub("", result2[0][1])),
                            format(get_uri_local_name(result2[0][0]), o_predicate, get_uri_local_name(result2[0][1])),
                            "\t\t?{:50} ?{:20} ?{} .".format(o_predicate, "sing_predicate2", "object2"),
                            "\t}",
                            "} ;",

                            # ### PART 4 ##########################################
                            # #####################################################
                            "LOAD THE DEFINITIVE CORRESPONDENCE GRAPH",
                            "INSERT",
                            "{",
                            # INSERT DEFINITE CORRESPONDENCES
                            "\tGRAPH <{}>".format(data[St.lens]),
                            "\t{",
                            "\t\t?{:50} ?{:20} ?{} .".format(_subject, linktype, _object),
                            "\t}",
                            # INSERT TEMPORALLY THE MAPPING BETWEEN NEWLY GENERATED SINGLETONS AND OLD ONCE
                            "\tGRAPH tmpgraph:sing_replaced",
                            "\t{",
                            "\t\t?{:50} {:20} ?{} .".format(linktype, "tmpvocab:replaced", s_predicate),
                            "\t}",

                            "}",
                            "WHERE",
                            "{",
                            # LOAD FROM TEMPORARY CORRESPONDENCE GRAPH
                            "\tGRAPH tmpgraph:corr01",
                            "\t{",
                            "\t\t?{} ?{} ?{} .".format(_subject, s_predicate, _object),
                            "\t\t### Create A SINGLETON URI",
                            "\t\tBIND( replace(\"{}_#\",\"#\",".format(data['link_predicate']),
                            "\t\tSTRAFTER(str(UUID()),\"uuid:\")) as ?pre )",
                            "\t\tBIND(iri(?pre) as ?singPre)",
                            "\t}",
                            "} ;",

                            # ### PART 5 ##########################################
                            # #####################################################
                            "###### LOAD THE DEFINITIVE SINGLETON GRAPH",
                            "INSERT",
                            "{",
                            "\tGRAPH <{}>".format(data['singleton_graph']),
                            "\t{",
                            "\t\t?{:50} ?{:20} ?{} .".format(linktype, "predicate", "object"),
                            "\t}",
                            "}",

                            "WHERE",
                            "{",
                            "\tGRAPH tmpgraph:sing",
                            "\t{",
                            "\t\t?{:50} ?{:20} ?{} .".format(s_predicate, "predicate", "object"),

                            "\t}",

                            "\tGRAPH tmpgraph:sing_replaced",
                            "\t{",
                            "\t\t?{:50} {:20} ?{} .".format(linktype, "tmpvocab:replaced", s_predicate),
                            "\t}",
                            "} ;",

                            # #### PART 5 ##########################################
                            # #####################################################
                            "DROP ALL TEMPORARY GRAPHS",
                            "DROP SILENT GRAPH tmpgraph:{} ;".format(o_predicate),
                            "DROP SILENT GRAPH tmpgraph:{} ;".format(s_predicate),
                            "DROP SILENT GRAPH tmpgraph:corr01 ;",
                            "DROP SILENT GRAPH tmpgraph:sing ;",
                            "DROP SILENT GRAPH tmpgraph:sing_replaced")

        # print "\n### INSERT QUERY"
        # print insert_query
        return is_transitive_by, insert_query


def reconstruct(linkset, gr_type, predicate):

    # pattern = re.compile('[^a-zA-Z]')
    graph_format = "\t{:40} {}"
    sub_obj = None
    source = ""
    target = ""
    correspondence = ""
    singleton = ""
    singleton_triple = "\n\t\t?{:50} ?{:20} ?{} .".format("subject", "sing_predicate", "object")

    singleton_matrix = Qry.sparql_xml_to_matrix(Qry.get_singleton_graph(linkset))
    # print "Singleton graph of {}".format(linkset), singleton_matrix
    # exit(0)
    # SINGLETON EXAMPLE
    # GRAPH <http://risis.eu/lens/singletonMetadata/transitive_C000_ExactName>
    # {
    # 	?subject            sing_predicate          ?object .
    # }
    if singleton_matrix is not None and singleton_matrix[St.result] is not None:
        singleton_graph = singleton_matrix[St.result][1][0]
        if singleton_graph is not None:
            singleton = "\n{}\n{}\n{}\n{}\n" \
                .format("\tGRAPH <{}>".format(singleton_graph),
                        "\t{",
                        "\t\t?{:50} ?{:20} ?{} .".format("subject", "sing_predicate", "object"),
                        "\t}")
            # print  "\t", singleton

    # print str(graph_type).upper()
    # print str(graph_type).upper() == "LINKSET"
    # ABOUT LINKSET UNION
    if str(gr_type).upper() == "LINKSET":

        print "\nRECONSTRUCTING CASE: Linkset"

        datatype_matrix = Qry.get_linkset_datatypes(linkset)
        # print datatype_matrix

        if datatype_matrix is not None and datatype_matrix[St.result]:
            sub_obj = datatype_matrix[St.result][1][4:6]
            # source = pattern.sub("", str(datatype_matrix [St.result][1][4]))
            source = get_uri_local_name(str(datatype_matrix[St.result][1][4]))
            # target = pattern.sub("", str(datatype_matrix [St.result][1][5]))
            target = get_uri_local_name(str(datatype_matrix[St.result][1][5]))

            # CORRESPONDENCE EXAMPLE
            # GRAPH <http://risis.eu/lens/transitive_C000_ExactName>
            # {
            # 	?leidenRanking ?singPre ?eter .
            # }
            correspondence = "{}\n{}\n{}\n{}".\
                format("\tGRAPH <{}>".format(linkset),
                       "\t{",
                       "\t\t?{:50} ?{:20} ?{} .".format(source, predicate, target),
                       "\t}")

    # DETERMINING WHETHER A LENS IS STEMMED FROM THE SAME subjectsTarget & objectsTarget
    elif str(gr_type).upper() == "LENS":
        print "\nRECONSTRUCTING CASE: Lens"

        query = """
        PREFIX bdb: <http://vocabularies.bridgedb.org/ops#>
        PREFIX void: <http://rdfs.org/ns/void#>
        SELECT ?target ?subjectsTarget ?objectsTarget
        {{
          <{}> void:target ?target .
          ?target
            void:subjectsTarget     ?subjectsTarget ;
            void:objectsTarget      ?objectsTarget .
        }}
        """.format(linkset)
        # print query
        evaluation = False

        datatype_matrix = Qry.sparql_xml_to_matrix(query)
        # print "DATATYPE: ", datatype_matrix
        # print len(datatype_matrix)

        if datatype_matrix is None:
            print "THERE IS NO METADATA FOR THIS DATASET. "
            print "\nNO POSSIBLE RECONSTRUCTION FOR {}: {}".format(gr_type, linkset)
            print "ARE YOU SURE THE GRAPH IS OF TYPE [{}]?".format(gr_type)
            return None

        elif (datatype_matrix is not None) and (len(datatype_matrix) > 1):
            element = datatype_matrix[St.result][1][1:]
            # print element
            for i in range(1, len(datatype_matrix)):
                check = datatype_matrix[St.result][i][1:]
                evaluation = element == check
                # print check
                # print "result: ", evaluation
                if evaluation is not True:
                    evaluation = False
                    break
                else:
                    evaluation = True

            if evaluation is True:

                # singleton_matrix = sparql_xml_to_matrix(singleton_graph_query, database_name, host)

                sub_obj = element
                # source = pattern.sub("", str(element[0]))
                source = get_uri_local_name(str(element[0]))
                # target = pattern.sub("", str(element[1]))
                target = get_uri_local_name(str(element[1]))

                correspondence = "{}\n{}\n{}\n{}" \
                    .format("\tGRAPH <{}>".format(linkset),
                            "\t{",
                            "\t\t?{:50} ?{:20} ?{} .".format(source, predicate, target),
                            "\t}")

                print graph_format.format(sub_obj[0], sub_obj[1])

            else:
                return None

    # TEMPORARY GRAPH EXAMPLE
    # INSERT
    # {
    #   GRAPH temp:load001
    #   {
    #       ?leidenRanking  ?singPre                ?eter .
    #       ?subject        ?sing_predicate         ?object .
    #   }
    # }
    # WHERE
    # {
    #   GRAPH <http://risis.eu/lens/transitive_C000_ExactName>
    #   {
    # 	    ?leidenRanking  ?singPre                ?eter .
    #   }
    #   GRAPH <http://risis.eu/lens/singletonMetadata/transitive_C000_ExactName>
    #   {
    # 	    ?subject        ?sing_predicate          ?object .
    #   }
    # }
    insert_q = "{}\n{}\n{}\n{}\n{}{}\n{}\n{}" \
               "\n{}\n{}\n{}\n{}{}". \
        format("INSERT",
               "{",
               "   GRAPH tmpgraph:{}".format(predicate),
               "   {",
               "\t\t?{:50} ?{:20} ?{} .".format(source, predicate, target),
               "{}".format(singleton_triple),
               "    }",
               "}",

               "WHERE",
               "{",
               "{}".format(correspondence),
               "{}".format(singleton),
               "}")

    if singleton is not None:
        correspondence += singleton

    if sub_obj is not None:
        print graph_format.format(sub_obj[0], sub_obj[1])

    return [sub_obj, insert_q]


def transitive_metadata(data, size, insert_query, same_as_count):

    metadata = "\n{}\n{}\n{}\n{}" \
               "\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}" \
               "\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}" \
               "\n{}\n{}\n{}\n{}\n{}" \
               "\n{}\n{}\n{}" \
               "\n{}\n{}\n{}\n{}". \
        format("##################################################################",
               "### METADATA ",
               "### in the linkset: {}".format(data[St.lens]),
               "##################################################################",

               "PREFIX rdfs:        <{}>".format(Ns.rdfs),
               "PREFIX alivocab:    <{}>".format(Ns.alivocab),
               "PREFIX void:        <{}>".format(Ns.void),
               "PREFIX bdb:         <{}>".format(Ns.bdb),
               "PREFIX lensOp:      <{}>".format(Ns.lensOp),

               "INSERT DATA",
               "{",
               "    <{}>".format(data[St.lens]),
               "        a                           bdb:Lens ;",
               "        alivocab:operator           lensOp:transitivity ;",
               "        void:triples                {} ;".format(size),
               "        alivocab:alignsMechanism    <{}{}> ;".format(Ns.mechanism, data[St.mechanism]),
               "        alivocab:sameAsCount        {} ;".format(same_as_count),
               "        void:linkPredicate          <{}{}> ;".format(data['link_predicate'], same_as_count),
               "        void:subjectsTarget         <{}> ;".format(data['src_dataset']),
               "        void:objectsTarget          <{}> ;".format(data['trg_dataset']),
               "        alivocab:isTransitiveBy     <{}> ;".format(data['is_transitive_by']),
               "        alivocab:singletonGraph     <{}> ;".format(data['singleton_graph']),
               "        bdb:linksetJustification    <{}> ;".format(data['lens_justification_uri']),
               "        bdb:assertionMethod         <{}> ;".format(data['assertion_method']),
               "        rdfs:comment                \"\"\"{}\"\"\" .".format(data['lens_comment']),

               "\n    ### METADATA ABOUT THE LINKTYPE",
               "    <{}{}>".format(data['link_predicate'], same_as_count),
               "        rdfs:comment                \"\"\"{}\"\"\" ;".format(data['link_comment']),
               "        rdfs:label                  \"{}\" ;".format(data['link_label']),
               "        rdfs:subPropertyOf          <{}> .".format(data['link_subpropertyof']),

               "\n    ### METADATA ABOUT THE LINKSET JUSTIFICATION",
               "    <{}>".format(data['lens_justification_uri']),
               "        rdfs:comment              \"\"\"{}\"\"\" .".format(data['justification']),

               "\n    ### ASSERTION METHOD",
               "    <{}>".format(data['assertion_method']),
               "        alivocab:sparql           \"\"\"{}\"\"\" .".format(insert_query),

               "}")

    return metadata
