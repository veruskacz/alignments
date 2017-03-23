from imp import load_source as load
# linkset = load("Linkset", "C:\Users\Al\PycharmProjects\Linkset\Linksets\Linkset.py")

import src.Alignments.Settings as St
import src.Alignments.NameSpace as Ns
import src.Alignments.Query as Qry
from  src.Alignments.Linksets.Linkset import write_to_file, update_specification
import logging
import src.Alignments.GenericMetadata as Gn


logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)
handler = logging.StreamHandler()
logger.addHandler(handler)


#################################################################
"""
    LENS BY UNION
"""
#################################################################


def union(specs, database_name, host, activated=False):

    if activated is False:
        # logger.warning("THE FUNCTION IS NOT ACTIVATED")
        print ("THE FUNCTION IS NOT ACTIVATED")
        return {"message": "THE FUNCTION IS NOT ACTIVATED.", 'error_code': 1, 'lens': None}

    print "\nEXECUTING UNION SPECS" \
          "\n======================================================" \
          "========================================================"


    update_specification(specs)

    # CHECK WHETHER THE UNION ALREADY EXISTS.
    # THE CHECK COULD BE DONE BY NAME OR BY TARGETS

    check_message = "{} ALREADY EXISTS. \nTO PROCEED ANYWAY, PLEASE DELETE THE " \
                    "LENS AND ITS METADATA FIRST OR CHANGE THE CONTEXT CODE\n".format(specs[St.lens])

    message = "LENS \"{}\" ALREADY EXISTS.<br/>TO PROCEED ANYWAY, PLEASE DELETE " \
              "THE LENS FIRST OR CHANGE THE CONTEXT CODE".format(specs[St.lens])

    # 1. CHECK WHETHER IT HAS A METADATA
    check_01 = "\nASK {{ <{}> ?p ?o . }}".format(specs[St.lens])
    ask = Qry.boolean_endpoint_response(check_01, database_name, host)
    ask = True if ask == "true" else False
    if ask is True:
        # logger.warning(check_message)
        print check_message
        # return specs[St.lens]
        return {"message": message, 'error_code': 1, 'lens': specs[St.lens]}

    # 2. CHECK WHETHER THE ACTUAL LENS EXISTS
    check_02 = "\nASK {{ graph <{}> {{ ?S ?p ?o . }} }}".format(specs[St.lens])
    ask = Qry.boolean_endpoint_response(check_02, database_name, host)
    ask = True if ask == "true" else False
    if ask is True:
        # logger.warning(check_message)
        print check_message
        # return specs[St.lens]
        return {"message": message, 'error_code': 1, 'lens': specs[St.lens]}

    specs[St.lens_target_triples] = ""
    specs[St.expectedTriples] = 0
    specs[St.insert_query] = ""
    lens = specs[St.lens]
    source = "{}{}".format(Ns.tmpgraph, "load00")

    count = -1
    for linkset in specs[St.datasets]:

        count += 1
        # print linkset

        # GET THE TOTAL NUMBER OF CORRESPONDENCE TRIPLES INSERTED
        curr_triples = Qry.get_triples(linkset, database_name, host)

        # print "Current triples: ", curr_triples
        if curr_triples is not None:
            # print "Current triples: ", curr_triples
            specs[St.expectedTriples] += int(curr_triples)
        else:
            # logger.warning("THERE IS A PROBLEM WITH THIS GRAPH: {}"
            #                "\nEITHER BECAUSE THE GRAPH HAS NO METADATA WHERE THE NUMBER OF TRIPLES COULD BE FOUND"
            #                "\n OR THE GRAPH SIMPLY DOES NOT EXIST.".format(linkset))
            print ("THERE IS A PROBLEM WITH THIS GRAPH: {}"
                           "\nEITHER BECAUSE THE GRAPH HAS NO METADATA WHERE THE NUMBER OF TRIPLES COULD BE FOUND"
                           "\n OR THE GRAPH SIMPLY DOES NOT EXIST.".format(linkset))
            message = "THERE IS A PROBLEM WITH THIS GRAPH: {}" \
                      "<br/>EITHER BECAUSE THE GRAPH HAS NO METADATA WHERE THE NUMBER OF TRIPLES COULD BE FOUND" \
                      "<br/>OR THE GRAPH SIMPLY DOES NOT EXIST.".format(linkset)
            # return None
            return {"message": message, 'error_code': 1, 'lens': None}

        # GENERATE TRIPLES OUT OF THE TARGETS
        specs[St.lens_target_triples] += "\n\t        void:target                         <{}> ;".format(linkset)

        # GET THE INSERT QUERY
        # BOTH THE LINKSET AND THE SINGLETONS ARE MOVED TO A SINGLE GRAPH
        partial_query = Qry.q_copy_graph(source, source, linkset, database_name, host)
        if count == 0:
            specs[St.insert_query] += partial_query
        else:
            specs[St.insert_query] += " ;\n{}".format(partial_query)

    # INTERSECTION MANIPULATION OVER THE UNION (SOURCE)
    manipulation = Qry.q_union(lens, source, specs[St.lens_name])
    # print "manipulation:", manipulation
    specs[St.insert_query] += " ;\n{}".format(manipulation)

    # GENERATE THE LENS UNION
    if activated is True:
        # print data[St.insert_query]
        insert_ans = Qry.boolean_endpoint_response(specs[St.insert_query], database_name, host)

        specs[St.triples] = Qry.get_namedgraph_size(lens, database_name, host, isdistinct=False)
        if specs[St.triples] == "0":
            # logger.warning("NO TRIPLES WHERE INSERTED FOR THIS ACTION.\nFOR THAT WE DO NOT INSERT METADA FOR"
            #                "NON EXISTING LENS.")
            print "NO TRIPLES WHERE INSERTED FOR THIS ACTION.\nFOR THAT WE DO NOT INSERT METADA FOR NON EXISTING LENS."
            message = "NO TRIPLES WHERE INSERTED FOR THIS ACTION.<br/>FOR THAT WE DO NOT INSERT METADA FOR NON EXISTING LENS."
            # return None
            return {"message": message, 'error_code': 1, 'lens': None}

        # CHECK WHETHER THE RESULT CONTAINS DUPLICATES
        contains_duplicated = Qry. contains_duplicates(lens, database_name, host)
        print "contains_duplicated:", contains_duplicated
        # IF IT DOES, REMOVE THE DUPLICATES
        if contains_duplicated is True:
            # logger.warning("THE LENS CONTAINS DUPLICATES.")
            print "THE LENS CONTAINS DUPLICATES."
            Qry.remove_duplicates(lens, database_name, host)
            # logger.warning("THE DUPLICATES ARE NOW REMOVED.")
            print "THE DUPLICATES ARE NOW REMOVED."

        specs[St.triples] = Qry.get_namedgraph_size(lens, database_name, host, isdistinct=False)
        print "\t>>> INSERTED:  {}\n\t>>> INSERTED TRIPLES: {}".format(insert_ans, specs[St.triples])

        # LOAD THE METADATA
        inserted_correspondences = int(Qry.get_union_triples(lens, database_name, host))
        specs[St.removedDuplicates] = specs[St.expectedTriples] - inserted_correspondences
        metadata = Gn.union_meta(specs)
        meta_ans = Qry.boolean_endpoint_response(metadata, database_name, host)
        print "\t>>> Is the metadata generated and inserted?  {}".format(meta_ans)

    construct_response = Qry.get_constructed_graph(specs[St.lens], database_name, host)
    if construct_response is not None:
        print "\t>>> WRITING TO FILE"
        construct_response = construct_response.replace('{', "<{}>\n{{".format(specs[St.lens]), 1)
        write_to_file(graph_name=specs[St.lens_name], metadata=None, correspondences=construct_response)
    print "\tLens created as : ", specs[St.lens]
    print "\t*** JOB DONE! ***"
    # return specs[St.lens]
    message = "THE LENS WAS CREATED!<br/>URI = {}".format(specs[St.lens])
    return {"message": message, 'error_code': 0, 'lens': specs[St.lens]}



