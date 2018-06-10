# from imp import load_source as load
# linkset = load("Linkset", "C:\Users\Al\PycharmProjects\Linkset\Linksets\Linkset.py")

import logging
import Alignments.Lenses.LensUtility as Lu
import Alignments.Query as Qry
import Alignments.Settings as St
import Alignments.NameSpace as Ns
import Alignments.ErrorCodes as Ec
import Alignments.GenericMetadata as Gn
import Alignments.Server_Settings as Ss
import Alignments.UserActivities.UserRQ as Urq
from Alignments.Manage.AdminGraphs import drop_linkset
from Alignments.Utility import write_to_file, update_specification

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)
handler = logging.StreamHandler()
logger.addHandler(handler)

ERROR_CODE_11 = "DUE TO A SYSTEM ERROR, WE ARE UNABLE TO PROCESS YOUR REQUEST."
DIRECTORY = Ss.settings[St.lens_Union__dir]


#################################################################
"""
    LENS BY UNION
"""
#################################################################


def run_checks(specs, query):

    print "\n3. RUNNING GOOD TO GO CHECK"
    # print "QUERY FOR CHECK:", query
    # CHECK-1: CHECK WHETHER THE LENS EXIST BY ASKING ITS METADATA WHETHER IT IS COMPOSED OF THE SAME GRAPHS
    print "QUERY:", query
    ask = Qry.sparql_xml_to_matrix(query)
    print"\t3.1 ANSWER 1:", ask['message']

    # ASK IS NOT SUPPOSED TO BE NONE
    # CHECK-1-RESULT: PROBLEM CONNECTING WITH THE SERVER
    if ask is None:
        # print "IN 1"
        print Ec.ERROR_CODE_1
        return {St.message: Ec.ERROR_CODE_1, St.error_code: 1, St.result: None}

    # CHECK-1-RESULT: ASK HAS A RESULT, MEANING THE LENS EXIT UNDER THE SAME COMPOSITION OF GRAPHS
    elif ask[St.message] != "NO RESPONSE":
        print "\tFOUND"
        if ask[St.result]:
            for i in range(1, len(ask[St.result])):
                print "\t\t- {}".format(ask[St.result][i][0])
        # IF THERE IS RESULT WITH THE SAME NUMBER OF TARGETS THEN THE LENS ALREADY EXISTS
        if ask[St.result] and len(ask[St.result]) - 1 == len(specs[St.datasets]):

            message = Ec.ERROR_CODE_7.replace("#", specs[St.lens]).replace("@", ask[St.result][1][0])
            print message
            return {St.message: message.replace("\n", "<br/>"), St.error_code: 1, St.result: specs[St.lens]}
        print "\tCHECK 1: THERE IS NO METADATA FOR TIS LENS"
        # ELSE
        # WITH THE UNSTATED ELSE, WE GET OUT AND PROCEED TO THE CREATION OF A NEW LENS
    else:
        print "IN 3"
        print Ec.ERROR_CODE_1
        return {St.message: Ec.ERROR_CODE_1, St.error_code: 1, St.result: None}

    # print "GOT OUT!!!"
    update_specification(specs)

    # print "CHECK 2: CHECK WHETHER THE ACTUAL LENS EXISTS UNDER THIS NAME"
    check_02 = "\nASK {{ graph <{}> {{ ?S ?p ?o . }} }}".format(specs[St.lens])
    ask = Qry.boolean_endpoint_response(check_02)
    # print specs
    # print check_02
    # print ask

    if ask is None:
        # PROBLEM CONNECTING WITH THE SERVER
        print " CHECK 2: PROBLEM CONNECTING WITH THE SERVER"
        print Ec.ERROR_CODE_1
        return {St.message: Ec.ERROR_CODE_1, St.error_code: 1, St.result: specs[St.lens]}

    if ask == "true":
        print " CHECK 2: THE LINKSET ALREADY EXISTS"
        message = Ec.ERROR_CODE_6.replace("#", specs[St.lens])
        print message
        return {St.message: message.replace("\n", "<br/>"), St.error_code: 1, St.result: specs[St.lens]}

    print "\n\tDIAGNOSTICS: GOOD TO GO\n"
    return {St.message: "GOOD TO GO", St.error_code: 0, St.result: "GOOD TO GO"}


def union(specs, activated=False):

    if activated is False:
        # logger.warning("THE FUNCTION IS NOT ACTIVATED")
        print ("THE FUNCTION IS NOT ACTIVATED")
        return {St.message: "THE FUNCTION IS NOT ACTIVATED.", St.error_code: 1, St.result: None}

    print "\nEXECUTING UNION SPECS" \
          "\n======================================================" \
          "========================================================"

    """
    THE generate_lens_name FUNCTION RETURNS THE NAME OF THE UNION AND A
    QUERY THAT ALLOWS TO ASk WHETHER THE LENS TO BE CREATED EXIST BY CHECKING
    WHETHER THERE EXISTS A LENS WITH THE SAME COMPOSITION IN TERMS GRAPHS USED FOR THE UNION
    """

    # SET THE NAME OF THE UNION-LENS
    print "1. DATASETS:", len(specs[St.datasets])
    for ds in specs[St.datasets]:
        print "\t- {}".format(ds)
    info = Lu.generate_lens_name(specs[St.datasets])

    specs[St.lens] = "{}{}".format(Ns.lens, info["name"])
    print "\n2. LENS: ", info["name"]

    # CHECK WHETHER THE LENS EXISTS
    check = run_checks(specs, info["query"])
    if check[St.result] != "GOOD TO GO":
        if check[St.message].__contains__("ALREADY EXISTS"):
            Urq.register_lens(specs, is_created=False)
        return check
    # print "AFTER CHECK"

    # PREPARATION FOR THE CREATION OF THE LENS
    specs[St.lens_target_triples] = ""
    specs[St.expectedTriples] = 0
    specs[St.insert_query] = ""
    lens = specs[St.lens]
    source = "{}{}".format(Ns.tmpgraph, "load00")
    message_2 = Ec.ERROR_CODE_8.replace("#", specs[St.lens])
    count = -1
    insert_ans = False

    try:

        # GO THROUGH THE LINKSETS/LENSES IN THE LENS
        #   1-SUM UP THE EXPECTED NUMBER OF TRIPLES
        #   2-GENERATE THE TRIPLES REPRESENTATION OF GHE GRAPHS COMPOSING THIS LENS
        #   3-GENERATE THE INSERT QUERY FOR MOVING BOTH LINKSET AND SINGLETON GRAPHS TO THE UNION GRAPH
        total_size = 0

        # LOAD ALL GRAPHS IN LOAD00
        specs[St.insert_query] += "DROP SILENT GRAPH <{}{}> ;\n".format(Ns.tmpgraph, "load00")

        # ITERATE THROUGH THE PROVIDED GRAPHS
        for linkset in specs[St.datasets]:

            # print "TARGET: ", linkset
            count += 1

            # GET THE TOTAL NUMBER OF CORRESPONDENCE TRIPLES INSERTED
            curr_triples = Qry.get_triples(linkset)
            # PROBABLY THE LINKSET HAS NO SUCH PROPERTY " void:triples  ?triples ."

            if curr_triples is None:
                curr_triples = Qry.get_triples_count(linkset)

            total_size += int(curr_triples)
            print "{} Contains {} triples".format(linkset, curr_triples)

            if curr_triples is not None:
                specs[St.expectedTriples] += int(curr_triples)
            else:
                # THE IS A PROBLEM WITH THE GRAPH FOR SEVERAL POSSIBLE REASONS
                return {St.message: message_2.replace("\n", "<br/>"), St.error_code: 1, St.result: None}

            # GENERATE TRIPLES OUT OF THE TARGETS
            specs[St.lens_target_triples] += "\n\t        void:target                         <{}> ;".format(linkset)

            # GET THE INSERT QUERY
            # BOTH THE LINKSET AND THE SINGLETONS ARE MOVED TO A SINGLE GRAPH
            partial_query = Qry.q_copy_graph(source, source, linkset)
            if count == 0:
                specs[St.insert_query] += partial_query
            else:
                specs[St.insert_query] += " ;\n{}".format(partial_query)

        # INTERSECTION MANIPULATION OVER THE UNION (SOURCE)
        insert_query = union_insert_q(lens, source, specs[St.lens_name])
        # print "manipulation:", manipulation
        specs[St.insert_query] += " ;\n{}".format(insert_query)

        # GENERATE THE LENS UNION
        if activated is True:

            # print specs[St.insert_query]
            insert_ans = Qry.boolean_endpoint_response(specs[St.insert_query])

            specs[St.triples] = Qry.get_namedgraph_size(lens, isdistinct=False)
            if specs[St.triples] == "0":
                message = Ec.ERROR_CODE_9
                print message
                # return None
                return {St.message: message.replace("\n", "<br/>"), St.error_code: 1, St.result: None}

            # CHECK WHETHER THE RESULT CONTAINS DUPLICATES
            contains_duplicated = Qry.contains_duplicates(lens)
            print "Contains Opposite Direction Duplicated:", contains_duplicated

            # IF IT DOES, REMOVE THE DUPLICATES
            if contains_duplicated is True:
                # logger.warning("THE LENS CONTAINS DUPLICATES.")
                print "THE LENS CONTAINS DUPLICATES."
                Qry.remove_duplicates(lens)
                # logger.warning("THE DUPLICATES ARE NOW REMOVED.")
                print "THE DUPLICATES ARE NOW REMOVED."

            print "Number of triples loaded              : {}".format(total_size)

            specs[St.triples] = Qry.get_namedgraph_size(lens, isdistinct=False)
            print "\t>>> INSERTED:  {}\n\t>>> INSERTED TRIPLES: {}".format(insert_ans, specs[St.triples])

            print "Inserted : {}".format(specs[St.triples])
            print "Removed  : {}".format(total_size - int(specs[St.triples]))

            # LOAD THE METADATA
            # NOT GOOD AS THE LENS ALSO HAS A SINGLETON GRAPH
            # inserted_correspondences = int(Qry.get_union_triples(lens))
            inserted_correspondences = int(specs[St.triples])
            # print "inserted_correspondences:", inserted_correspondences
            specs[St.removedDuplicates] = specs[St.expectedTriples] - inserted_correspondences
            metadata = Gn.union_meta(specs)
            # print "METADATA:", metadata
            meta_ans = Qry.boolean_endpoint_response(metadata)
            print "\t>>> IS THE METADATA GENERATED AND INSERTED?  {}".format(meta_ans)

        construct_response = Qry.get_constructed_graph(specs[St.lens])
        if construct_response is not None:
            print "\t>>> WRITING TO FILE"
            construct_response = construct_response.replace('{', "<{}>\n{{".format(specs[St.lens]), 1)
            write_to_file(
                graph_name=specs[St.lens_name], metadata=None, correspondences=construct_response, directory=DIRECTORY)
        print "\tLens created as : ", specs[St.lens]

        # REGISTER THE LINKSET
        Urq.register_lens(specs, is_created=True)

        # return specs[St.lens]
        message = "THE LENS WAS CREATED as {}. " \
                  "With initially {} triples loaded, {} duplicated triples were found and removed.".\
            format(specs[St.lens], total_size, total_size - int(specs[St.triples]))

        print "\t*** JOB DONE! ***"
        return {St.message: message, St.error_code: 0, St.result: specs[St.lens]}

    except Exception as err:
        # logger.warning(err)
        if insert_ans == "true":
            "DROP THE INSERTED UNION"
            drop_linkset(lens, activated=True)

        print "ERROR IN UNION LENS CREATION:", err
        return {St.message: ERROR_CODE_11, St.error_code: 11, St.result: None}


def union_insert_q(lens, source, label):
    lens_name = label
    query = """
    PREFIX prov:<{0}>
    PREFIX specific:<{7}>
    PREFIX tmpgraph:<{1}>
    PREFIX tmpvocab:<{5}>
    PREFIX ll:<{3}>

    DROP SILENT GRAPH tmpgraph:load01 ;
    DROP SILENT GRAPH tmpgraph:load02 ;

    ###### CREATING THE INTERSECTION CORRESPONDENCES WITH A TEMPORARY PREDICATE
    ###### REMOVE DUPLICATES IN THE SAME DIRECTION
    INSERT
    {{
      GRAPH tmpgraph:load01
      {{
        ?sCorr 		tmpvocab:predicate		?oCorr  .
      }}
    }}
    WHERE
    {{
      graph <{2}>
      {{
        ?sCorr		?singCorr 				?oCorr  .
        FILTER NOT EXISTS {{ ?x ?sCorr ?z }}
        #?singCorr	?singCorrPr 			?singCorrobj .
      }}
    }} ;

    ###### UPDATE tmpgraph:load01 WITH UNIQUE PREDICATES
    INSERT
    {{
      GRAPH tmpgraph:load02
      {{
        ?sCorr ?singPre ?oCorr .
      }}
    }}
    WHERE
    {{
      GRAPH tmpgraph:load01
      {{
        ?sCorr ?y ?oCorr .

        ### Create A SINGLETON URI"
        BIND( replace("{3}union_#", "#", STRAFTER(str(UUID()),"uuid:")) as ?pre )
        BIND(iri(?pre) as ?singPre)
      }}
    }} ;

    INSERT
    {{
        ### {6}
        GRAPH <{4}>
        {{
            ?sCorr			?singPre 					?oCorr .
        }}

        GRAPH specific:{6}
        {{
            ?singPre		prov:wasDerivedFrom 	    ?singCorr .
            ?singCorr		?singCorrPr 				?singCorrobj .
            ?validation     ?vPred                      ?vObj .
            ?rQuestion      ll:created                  ?validation .
        }}
    }}
    WHERE
    {{
        GRAPH tmpgraph:load02
        {{
            ?sCorr			?singPre 					?oCorr .
        }}

        graph <{2}>
        {{
            ?sCorr			?singCorr 				    ?oCorr  .
            # THE DIRECT SINGLETONS
            OPTIONAL {{ ?singCorr			?singCorrPr 			?singCorrobj .  }}
            # THE VALIDATIONS
            OPTIONAL
            {{
               ?singCorr		ll:hasValidation 			?validation .
               ?validation      ?vPred                      ?vObj .
               ?rQuestion       ll:created                  ?validation .
            }}
            FILTER NOT EXISTS {{ ?x ?sCorr ?z }}
        }}
    }} ;

    DROP SILENT GRAPH tmpgraph:load00 ;
    DROP SILENT GRAPH tmpgraph:load01 ;
    DROP SILENT GRAPH tmpgraph:load02
    """.format(Ns.prov, Ns.tmpgraph, source, Ns.alivocab, lens, Ns.tmpvocab, lens_name, Ns.singletons)
    return query
# Codes for manipulating stardog data and querying stardog from shell