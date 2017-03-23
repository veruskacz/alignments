import src.Alignments.Settings as St
import src.Alignments.NameSpace as Ns
import src.Alignments.Query as Qry
import src.Alignments.GenericMetadata as Gn
from Linkset import write_to_file, update_specification
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)
handler = logging.StreamHandler()
logger.addHandler(handler)


def spa_linkset_subset(specs, database_name, host, activated=False):

    if activated is True:

        specs[St.sameAsCount] = Qry.get_same_as_count(specs[St.mechanism], database_name, host)
        # print data[_sameAsCount]

        # Check whether this linkset was already generated. If yes, delete it or change the context code
        ask_query = "\nPREFIX linkset: <http://risis.eu/linkset/> \nASK {{ <{}> ?p ?o . }}".format(specs[St.linkset])
        ask = Qry.boolean_endpoint_response(ask_query, database_name, host)
        ask = True if ask == "true" else False
        if ask is True:
            # logger.warning("\n{} ALREADY EXISTS. \nTO PROCEED ANYWAY, PLEASE DELETE "
            #                "THE LINKSET FIRST OR CHANGE THE CONTEXT CODE\n".format(data[St.linkset]))
            print "{} ALREADY EXISTS. \nTO PROCEED ANYWAY, PLEASE DELETE " \
                  "THE LINKSET FIRST OR CHANGE THE CONTEXT CODE\n".format(specs[St.linkset])
            return specs[St.linkset]

        ##########################################################
        """ 1. GENERATE SUBSET LINKSET INSERT QUERY            """
        ##########################################################
        insert_query = spa_subset_insert(specs)

        #############################################################
        """ 2. EXECUTING INSERT SUBSET LINKSET QUERY AT ENDPOINT  """
        #############################################################
        Qry.endpoint(insert_query, database_name, host)

        #############################################################
        """ 3. LINKSET SIZE (NUMBER OF TRIPLES)                   """
        #############################################################
        # LINKSET SIZE (NUMBER OF TRIPLES)
        specs[St.triples] = Qry.get_namedgraph_size(specs[St.linkset], database_name, host)
        print "\t>>> {} TRIPLES INSERTED".format(specs[St.triples])

        if specs[St.triples] == "0":
            # logger.warning("WE DID NOT INSERT A METADATA AS NO TRIPLE WAS INSERTED.")
            print "WE DID NOT INSERT A METADATA AS NO TRIPLE WAS INSERTED."
            specs[St.insert_query] = insert_query
            # metadata = spa_subset_metadata(source, target, data, size)

            explain_q = "ask {{ GRAPH <{}> {{ ?s <{}> ?o }} }}".format(specs[St.linkset], specs[St.source][St.link_old])
            response = Qry.boolean_endpoint_response(explain_q, database_name, host)
            explain = True if response == "true" else False
            # print explain
            if explain is False:
                # logger.warning("{} DOES NOT EXIST IS {}.".format(data[St.link_old], source[St.graph]))
                print "{} DOES NOT EXIST IS {}.".format(specs[St.source][St.link_old], specs[St.source][St.graph])
            return

        construct_query = "\n{}\n{}\n{}\n".format(
            "PREFIX predicate: <{}>".format(Ns.alivocab),
            "construct { ?x ?y ?z }",
            "where     {{ graph <{}> {{ ?x ?y ?z }} }}".format(specs[St.linkset]),
        )
        # print construct_query
        construct_response = Qry.endpointconstruct(construct_query, database_name, host)
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
        singleton_construct = Qry.endpointconstruct(singleton_metadata_query, database_name, host)
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
        Qry.endpoint(metadata, database_name, host)

        print "\t>>> WRITING TO FILE"
        write_to_file(graph_name=specs[St.linkset_name], metadata=metadata.replace("INSERT DATA", ""),
                      correspondences=construct_response, singletons=singleton_construct)
        print "\tLinkset created as [SUBSET]: ", specs[St.linkset]
        print "\t*** JOB DONE! ***"

        return specs[St.linkset]


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


def specification_2_linkset_subset(specs, database_name, host, activated=False):

    if activated is False:
        logger.warning("THE FUNCTION IS NOT ACTIVATED.")

    if activated is True:

        print "\nEXECUTING LINKSET SUBSET SPECS" \
              "\n======================================================" \
              "========================================================"

        source = specs[St.source]
        target = specs[St.target]
        update_specification(source)
        update_specification(target)

        linkset_label = "subset_{}_{}_C{}_{}".format(
            specs[St.source][St.graph_name], specs[St.target][St.graph_name],
            specs[St.context_code], specs[St.mechanism])

        specs[St.link_name] = "same"
        specs[St.linkset_name] = linkset_label
        specs[St.link] = "http://risis.eu/linkset/predicate/{}".format(specs[St.link_name])
        specs[St.link_subpropertyof] = "http://risis.eu/linkset/predicate/{}".format(specs[St.link_name])
        specs[St.linkset] = "{}{}".format(Ns.linkset, linkset_label)
        specs[St.assertion_method] = "{}{}".format(Ns.method, linkset_label)
        specs[St.justification] = "{}{}".format(Ns.justification, linkset_label)

        specs[St.link_comment] = "The predicate <{}> is used in replacement of the linktype <{}> used in the " \
                                 "original <{}> dataset.".format(
            specs[St.link], specs[St.source][St.link_old], specs[St.source][St.graph])

        specs[St.justification_comment] = "In OrgRef's a set of entities are linked to GRID. The linking method used " \
                                          "by OrgRef is unknown. Here we assume that it is a curated work and " \
                                          "extracted it as a linkset.",

        specs[St.linkset_comment] = "The current linkset is a subset of the <{0}> dataset that links <{0}> to <{1}>. " \
                                    "The methodology used by <{0}> to generate this builtin linkset in unknown.".format(
            specs[St.source][St.graph], specs[St.target][St.graph])

        source[St.entity_ns] = str(source[St.entity_datatype]).replace(source[St.entity_name], '')
        target[St.entity_ns] = str(target[St.entity_datatype]).replace(target[St.entity_name], '')

        return spa_linkset_subset(specs, database_name, host, activated)
