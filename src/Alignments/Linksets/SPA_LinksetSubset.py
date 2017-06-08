import logging

import Linkset as Ls
import Alignments.ErrorCodes as Ec
import Alignments.GenericMetadata as Gn
import Alignments.NameSpace as Ns
import Alignments.Query as Qry
import Alignments.Settings as St
import Alignments.UserActivities.UserRQ as Urq
from Alignments.Utility import write_to_file, update_specification

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)
handler = logging.StreamHandler()
logger.addHandler(handler)

import Alignments.Server_Settings as Ss
DIRECTORY = Ss.settings[St.linkset_Subset_dir]


def spa_linkset_subset(specs, activated=False):

    if activated is True:

        check = Ls.run_checks(specs, check_type="subset")
        if check[St.result] != "GOOD TO GO":
            return check

        # THE LINKSET DOES NOT EXIT, LETS CREATE IT NOW
        print Ls.linkset_info(specs, specs[St.sameAsCount])

        ##########################################################
        """ 1. GENERATE SUBSET LINKSET INSERT QUERY            """
        ##########################################################
        insert_query = spa_subset_insert(specs)
        # print insert_query

        #############################################################
        """ 2. EXECUTING INSERT SUBSET LINKSET QUERY AT ENDPOINT  """
        #############################################################
        Qry.endpoint(insert_query)

        #############################################################
        """ 3. LINKSET SIZE (NUMBER OF TRIPLES)                   """
        #############################################################
        # LINKSET SIZE (NUMBER OF TRIPLES)
        specs[St.triples] = Qry.get_namedgraph_size(specs[St.linkset])
        print "\t>>> {} TRIPLES INSERTED".format(specs[St.triples])

        # NO MATCH FOUND
        if specs[St.triples] == "0":

            # logger.warning("WE DID NOT INSERT A METADATA AS NO TRIPLE WAS INSERTED.")
            print "WE DID NOT INSERT A METADATA AS NO TRIPLE WAS INSERTED."
            specs[St.insert_query] = insert_query
            # metadata = spa_subset_metadata(source, target, data, size)

            explain_q = "ask {{ GRAPH <{}> {{ ?s <{}> ?o }} }}".format(specs[St.linkset], specs[St.source][St.link_old])
            response = Qry.boolean_endpoint_response(explain_q)
            explain = True if response == "true" else False
            # print explain
            if explain is False:
                # logger.warning("{} DOES NOT EXIST IS {}.".format(data[St.link_old], source[St.graph]))
                print "{} DOES NOT EXIST IS {}.".format(specs[St.source][St.link_old], specs[St.source][St.graph])

                message = "{} DOES NOT EXIST IS {}.".format(specs[St.source][St.link_old], specs[St.source][St.graph])

                return {St.message: message, St.error_code: 1, St.result: None}

        # SOME MATCHES WHERE FOUND
        construct_query = "\n{}\n{}\n{}\n".format(
            "PREFIX predicate: <{}>".format(Ns.alivocab),
            "construct { ?x ?y ?z }",
            "where     {{ graph <{}> {{ ?x ?y ?z }} }}".format(specs[St.linkset]),
        )
        # print construct_query
        construct_response = Qry.endpointconstruct(construct_query)
        if construct_response is not None:
            construct_response = construct_response.replace('{', "<{}>\n{{".format(specs[St.linkset]), 1)

        # GENERATE LINKSET SINGLETON METADATA QUERY
        singleton_metadata_query = "\n{}\n{}\n{}\n{}\n{}\n{}\n\n".format(
            "PREFIX singMetadata:   <{}>".format(Ns.singletons),
            "PREFIX predicate:      <{}>".format(Ns.alivocab),
            "PREFIX prov:           <{}>".format(Ns.prov),
            "PREFIX rdf:            <{}>".format(Ns.rdf),

            "construct { ?x ?y ?z }",
            "where     {{ graph <{}{}> {{ ?x ?y ?z }} }}".format(Ns.singletons, specs[St.linkset_name]),
        )
        # GET THE SINGLETON METADATA USING THE CONSTRUCT QUERY
        singleton_construct = Qry.endpointconstruct(singleton_metadata_query)
        if singleton_construct is not None:
            singleton_construct = singleton_construct.replace(
                '{', "singMetadata:{}\n{{".format(specs[St.linkset_name]), 1)

        #############################################################
        """ 4. LINKSET METADATA                                   """
        #############################################################
        # METADATA
        specs[St.insert_query] = insert_query
        metadata = Gn.spa_subset_metadata(specs)

        ###############################################################
        """ 5. EXECUTING INSERT LINKSET METADATA QUERY AT ENDPOINT  """
        ###############################################################
        # EXECUTING METADATA QUERY AT ENDPOINT
        Qry.endpoint(metadata)

        print "\t>>> WRITING TO FILE"
        write_to_file(graph_name=specs[St.linkset_name], metadata=metadata.replace("INSERT DATA", ""),
                      correspondences=construct_response, singletons=singleton_construct, directory=DIRECTORY)

        print "\tLinkset created as [SUBSET]: ", specs[St.linkset]
        print "\t*** JOB DONE! ***"

        message = "The linkset was created!<br/>URI = {}".format(specs[St.linkset])

        return {St.message: message, St.error_code: 0, St.result: specs[St.linkset]}


def spa_subset_insert(specs):

    insert_query = """
    ###### INSERT SUBSET LINKSET
    PREFIX rdf:        <{}>
    PREFIX singleton:   <{}>
    PREFIX alivocab:    <{}>

    INSERT
    {{
        GRAPH <{}>
        {{
            ?subject    ?singPre    ?object .
        }}

        GRAPH singleton:{}
        {{
            ?singPre    rdf:singletonPropertyOf     alivocab:exactStrSim{} ;
                        alivocab:hasEvidence        "Aligned by {} ." .
        }}
    }}
    WHERE
    {{
        GRAPH <{}>
        {{
            ?subject <{}>  ?object .
        }}

        ### Create A SINGLETON URI
        BIND( replace("{}{}{}_#", "#", STRAFTER(str(UUID()),"uuid:")) as ?pre )
        BIND(iri(?pre) as ?singPre)
    }}
    """.format(Ns.rdf, Ns.singletons, Ns.alivocab,
               specs[St.linkset], specs[St.linkset_name], specs[St.sameAsCount], specs[St.source][St.graph_name],
               specs[St.source][St.graph], specs[St.source][St.link_old], Ns.alivocab, specs[St.mechanism],
               specs[St.sameAsCount])
    # print insert_query
    return insert_query


def specification_2_linkset_subset(specs, activated=False):

    if activated is False:
        logger.warning("THE FUNCTION IS NOT ACTIVATED.")

    if activated is True:

        print "\nEXECUTING LINKSET SUBSET SPECS" \
              "\n======================================================" \
              "========================================================"

        # ACCESS THE TASK SPECIFIC PREDICATE COUNT
        specs[St.sameAsCount] = Qry.get_same_as_count(specs[St.mechanism])

        # UPDATE THE QUERY THAT IS GOING TO BE EXECUTED
        if specs[St.sameAsCount]:

            source = specs[St.source]
            target = specs[St.target]

            # UPDATE THE SPECS OF SOURCE AND TARGETS
            update_specification(source)
            update_specification(target)

            # GENERATE THE NAME OF THE LINKSET
            Ls.set_subset_name(specs)

            # SETTING SOME GENERIC METADATA INFO
            specs[St.link_name] = "same"
            specs[St.linkset_name] = specs[St.linkset_name]
            specs[St.link] = "http://risis.eu/linkset/predicate/{}".format(specs[St.link_name])
            specs[St.link_subpropertyof] = "http://risis.eu/linkset/predicate/{}".format(specs[St.link_name])
            specs[St.linkset] = "{}{}".format(Ns.linkset, specs[St.linkset_name])
            specs[St.assertion_method] = "{}{}".format(Ns.method, specs[St.linkset_name])
            specs[St.justification] = "{}{}".format(Ns.justification, specs[St.linkset_name])

            # COMMENT ON THE LINK PREDICATE
            specs[St.link_comment] = "The predicate <{}> is used in replacement of the linktype <{}> used in the " \
                                     "original <{}> dataset.".format(
                specs[St.link], specs[St.source][St.link_old], specs[St.source][St.graph])

            # COMMENT ON THE JUSTIFICATION FOR THIS LINKSET
            specs[St.justification_comment] = "In OrgRef's a set of entities are linked to GRID. The linking method " \
                                              "used by OrgRef is unknown. Here we assume that it is a curated work " \
                                              "and extracted it as a linkset.",

            # COMMENT ON THE LINKSET ITSELF
            specs[St.linkset_comment] = "The current linkset is a subset of the <{0}> dataset that links <{0}> to " \
                                        "<{1}>. The methodology used by <{0}> to generate this builtin linkset in " \
                                        "unknown.".format(specs[St.source][St.graph], specs[St.target][St.graph])

            source[St.entity_ns] = str(source[St.entity_datatype]).replace(source[St.entity_name], '')
            target[St.entity_ns] = str(target[St.entity_datatype]).replace(target[St.entity_name], '')

            # GENERATE THE LINKSET
            inserted_linkset = spa_linkset_subset(specs, activated)

            if specs[St.triples] > "0":

                # REGISTER THE ALIGNMENT
                if inserted_linkset[St.message].__contains__("ALREADY EXISTS"):
                    Urq.register_alignment_mapping(specs, created=False)
                else:
                    Urq.register_alignment_mapping(specs, created=True)

            return inserted_linkset

        else:
            print Ec.ERROR_CODE_1
            return {St.message: Ec.ERROR_CODE_1, St.error_code: 5, St.result: None}