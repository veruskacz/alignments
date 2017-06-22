import Linkset as Ls
import Alignments.ErrorCodes as Ec
import Alignments.GenericMetadata as Gn
import Alignments.Lenses.Lens_Difference as Df
import Alignments.NameSpace as Ns
import Alignments.Query as Qry
import Alignments.Settings as St
from Alignments.UserActivities.UserRQ import register_alignment_mapping
from Alignments.Utility import write_to_file, update_specification

import Alignments.Server_Settings as Ss
DIRECTORY = Ss.settings[St.linkset_Refined_dir]


def refine(specs, exact=False, exact_intermediate=False):

    # if True:
    try:
        check_none = 0
        check_not_none = 0
        insert_query = ""
        insert_code = 0

        if exact is False:
            check_none += 1
        else:
            check_not_none += 1
            insert_query = insert_exact_query
            insert_code = 1

        if exact_intermediate is False:
            check_none += 1
        else:
            check_not_none += 1
            insert_query = refine_intermediate_query
            insert_code = 2

        refined = {St.message: Ec.ERROR_CODE_1, St.error_code: 5, St.result: None}
        diff = {St.message: Ec.ERROR_CODE_4, St.error_code: 1, St.result: None}
        result = {'refined': refined, 'difference': diff}

        if check_none > 1 or check_not_none > 1:
            print "AT MOST, ONE OF THE ARGUMENTS (exact, exact_intermediate) SHOULD BE SET."

        if insert_code == 1:
            print "REFINING WITH EXACT"
            result = refining(specs, insert_query)

        elif insert_code == 2:
            print "REFINING WITH INTERMEDIATE"
            result = refining(specs, insert_query)

        return result

    except Exception as err:
        print err.message
        refined = {St.message: Ec.ERROR_CODE_1, St.error_code: 5, St.result: None}
        diff = {St.message: Ec.ERROR_CODE_4, St.error_code: 1, St.result: None}
        return {'refined': refined, 'difference': diff}


def refining(specs, insert_query):

    refined = {St.message: Ec.ERROR_CODE_1, St.error_code: 5, St.result: None}
    diff = {St.message: Ec.ERROR_CODE_4, St.error_code: 1, St.result: None}

    # UPDATE THE SPECS VARIABLE
    update_specification(specs)
    update_specification(specs[St.source])
    update_specification(specs[St.target])

    # ACCESS THE TASK SPECIFIC PREDICATE COUNT
    specs[St.sameAsCount] = Qry.get_same_as_count(specs[St.mechanism])
    # print "sameAsCount:", specs[St.sameAsCount]

    if specs[St.sameAsCount] is None:
        return {'refined': refined, 'difference': diff}

    # GENERATE THE NAME OF THE LINKSET
    Ls.set_refined_name(specs)
    # print "\nREFINED NAME:", specs[St.refined]
    # print "LINKSET TO REFINE BEFORE CHECK:", specs[St.linkset]

    # CHECK WHETHER OR NOT THE LINKSET WAS ALREADY CREATED
    check = Ls.run_checks(specs, check_type="refine")
    # print "\nREFINED NAME:", specs[St.refined]
    # print "LINKSET TO REFINE:", specs[St.linkset]

    if check[St.message] == "NOT GOOD TO GO":
        # refined = check[St.refined]
        # difference = check["difference"]
        return check

    # print "\nREFINED:", specs[St.refined]
    # print "LINKSET TO REFINE:", specs[St.linkset]
    print "CHECK:", check

    # THE LINKSET DOES NOT EXIT, LETS CREATE IT NOW
    print Ls.refined_info(specs, specs[St.sameAsCount])

    # POINT TO THE LINKSET THE CURRENT LINKSET WAS DERIVED FROM
    specs[St.derivedfrom] = "\t\tprov:wasDerivedFrom\t\t\t<{}> ;".format(specs[St.linkset])

    # print "REFINED NAME:",  specs[St.refined_name]
    # print "REFINED:", specs[St.refined]
    # print "LINKSET TO BE REFINED:", specs[St.linkset]

    # RETRIEVING THE METADATA ABOUT THE GRAPH TO REFINE
    metadata_q = Qry.q_linkset_metadata(specs[St.linkset])
    # print "QUERY:", metadata_q
    matrix = Qry.sparql_xml_to_matrix(metadata_q)
    # print "\nMETA DATA: ", matrix

    if matrix:
        if matrix[St.message] == "NO RESPONSE":
            print Ec.ERROR_CODE_1
            print matrix[St.message]
            return {'refined': refined, 'difference': diff}
        elif matrix[St.result] is None:
            print matrix[St.message]
            returned = {St.message: matrix[St.message], St.error_code: 666, St.result: None}
            return {'refined': returned, 'difference': diff}
    else:
        print Ec.ERROR_CODE_1
        return {'refined': refined, 'difference': diff}

    # GET THE SINGLETON GRAPH OF THE LINKSET TO BE REFINED
    specs[St.singletonGraph] = matrix[St.result][1][0]
    # print matrix[St.result][1][0]

    # RUN INSERT QUERY
    specs[St.insert_query] = insert_query(specs)
    # print specs[St.insert_query]
    is_run = Qry.boolean_endpoint_response(specs[St.insert_query])
    print ">>> RUN SUCCESSFULLY:", is_run

    # NO INSERTION HAPPENED
    if is_run:
        # GENERATE THE
        #   (1) LINKSET METADATA
        #   (2) LINKSET OF CORRESPONDENCES
        #   (3) SINGLETON METADATA
        # AND WRITE THEM ALL TO FILE
        pro_message = refine_metadata(specs)

        # SET THE RESULT ASSUMING IT WENT WRONG
        refined = {St.message: Ec.ERROR_CODE_4, St.error_code: 4, St.result: None}
        diff = {St.message: Ec.ERROR_CODE_4, St.error_code: 4, St.result: None}

        server_message = "Linksets created as: {}".format(specs[St.refined])
        message = "The linkset was created!<br/>URI = {}. <br/>{}".format(specs[St.linkset], pro_message)
        print "\t", server_message
        if int(specs[St.triples]) > 0:

            # UPDATE THE REFINED VARIABLE AS THE INSERTION WAS SUCCESSFUL
            refined = {St.message: message, St.error_code: 0, St.result: specs[St.linkset]}

            # REGISTER THE ALIGNMENT
            if refined[St.message].__contains__("ALREADY EXISTS"):
                register_alignment_mapping(specs, created=False)
            else:
                register_alignment_mapping(specs, created=True)

            # COMPUTE THE DIFFERENCE AND DOCUMENT IT
            diff_lens_specs = {
                St.researchQ_URI: specs[St.researchQ_URI],
                St.subjectsTarget: specs[St.linkset],
                St.objectsTarget: specs[St.refined]
            }
            diff = Df.difference(diff_lens_specs)
            message_2 = "\t>>> {} CORRESPONDENCES INSERTED AS THE DIFFERENCE".format(diff_lens_specs[St.triples])
            print message_2

        print "\tLinkset created as: ", specs[St.linkset]
        print "\t*** JOB DONE! ***"
        return {'refined': refined, 'difference': diff}

    else:
        print "NO MATCH COULD BE FOUND."


def insert_exact_query(specs):

    source = specs[St.source]
    target = specs[St.target]

    # FORMATTING THE ALIGNS PROPERTY
    src_aligns = source[St.aligns] \
        if Ls.nt_format(source[St.aligns]) else "<{}>".format(source[St.aligns])

    trg_aligns = target[St.aligns] \
        if Ls.nt_format(target[St.aligns]) else "<{}>".format(target[St.aligns])

    # GENERATE THE INSERT QUERY
    insert_query = """
    PREFIX prov:        <{}>
    PREFIX rdf:         <{}>
    PREFIX alivocab:    <{}>
    INSERT
    {{
        ### REFINED LINKSET
        GRAPH <{}>
        {{
            ?subject ?newSingletons ?object .
        }}

        ### SINGLETONS' METADATA
        GRAPH <{}{}>
        {{
            ?newSingletons
                rdf:singletonPropertyOf     alivocab:{}{} ;
                prov:wasDerivedFrom         ?singleton ;
                alivocab:hasEvidence        ?label .
        }}
    }}
    WHERE
    {{
        ### LINKSET
        GRAPH <{}>
        {{
            ?subject ?singleton ?object .
             bind( iri(replace("{}{}{}_#", "#",  strafter(str(uuid()), "uuid:") )) as ?newSingletons )
        }}

        ### METADATA
        graph <{}>
        {{
            ?singleton ?sP ?sO .
        }}

        ### SOURCE DATASET
        GRAPH <{}>
        {{
            ?subject   {} 	?s_label ;
            BIND(lcase(str(?s_label)) as ?label)
        }}

        ### TARGET DATASET
        GRAPH <{}>
        {{
          ?object      {} 	?o_label ;
            BIND(lcase(str(?o_label)) as ?label)
        }}
    }}
    """.format(Ns.prov, Ns.rdf, Ns.alivocab,
               specs[St.refined], Ns.singletons, specs[St.refined_name], specs[St.mechanism], specs[St.sameAsCount],
               specs[St.linkset], Ns.alivocab, specs[St.mechanism], specs[St.sameAsCount],
               specs[St.singletonGraph],
               source[St.graph], src_aligns,
               target[St.graph], trg_aligns)
    # print insert_query
    return insert_query


def refine_intermediate_query(specs):

    source = specs[St.source]
    target = specs[St.target]

    # FORMATTING THE ALIGNS PROPERTY
    src_aligns = source[St.aligns] \
        if Ls.nt_format(source[St.aligns]) else "<{}>".format(source[St.aligns])

    trg_aligns = target[St.aligns] \
        if Ls.nt_format(target[St.aligns]) else "<{}>".format(target[St.aligns])

    src_name = specs[St.source][St.graph_name]
    src_uri = specs[St.source][St.graph]
    # src_aligns = specs[St.source][St.aligns]

    trg_name = specs[St.target][St.graph_name]
    trg_uri = specs[St.target][St.graph]
    # trg_aligns = specs[St.target][St.aligns]

    insert = """
    PREFIX alivocab:    <{16}>
    PREFIX prov:        <{17}>

    DROP SILENT GRAPH <{0}load01> ;
    DROP SILENT GRAPH <{0}load02> ;
    DROP SILENT GRAPH <{10}> ;

    ### 1. LOADING SOURCE AND TARGET TO A TEMPORARY GRAPH
    INSERT
    {{
        GRAPH <{0}load01>
        {{
            ### SOURCE DATASET AND ITS ALIGNED PREDICATE
            ?{1} {2} ?src_value .
            ### TARGET DATASET AND ITS ALIGNED PREDICATE
            ?{3} {4} ?trg_value .
        }}
    }}
    WHERE
    {{
        ### LINKSET TO REFINE
        graph <{5}>
        {{
            ?{1} ?pred  ?{3} .
        }}
        ### SOURCE DATASET
        graph <{6}>
        {{
            ### SOURCE DATASET AND ITS ALIGNED PREDICATE
            ?{1} {2} ?value_1 .
            bind (lcase(str(?value_1)) as ?src_value)
        }}
        ### TARGET DATASET
        graph <{7}>
        {{
            ### TARGET DATASET AND ITS ALIGNED PREDICATE
            ?{3} {4} ?value_2 .
            bind (lcase(str(?value_2)) as ?trg_value)
        }}
    }} ;

    ### 2. FINDING CANDIDATE MATCH
    INSERT
    {{
        ### MATCH FOUND
        GRAPH <{0}load02>
        {{
            ?{1} <{8}relatesTo> ?{3} .
        }}
    }}
    WHERE
    {{
        ### LINKSET TO REFINE
        graph <{5}>
        {{
            ?{1} ?pred  ?{3} .
        }}
        ### SOURCE AND TARGET LOADED TO A TEMPORARY GRAPH
        GRAPH <{0}load01>
        {{
            ?{1} {2} ?src_value .
            ?{3} {4} ?trg_value .
        }}
        ### INTERMEDIATE DATASET
       graph <{9}>
       {{
            ?intermediate_uri
                ?intPred_1 ?value_3 ;
                ?intPred_2 ?value_4 .
            bind (lcase(?value_3) as ?src_value)
            bind (lcase(?value_4) as ?trg_value)
       }}
    }} ;

    ### 3. CREATING THE CORRESPONDENCES
    INSERT
    {{
        GRAPH <{10}>
        {{
            ?{1} ?newSingletons  ?{3} .
        }}
        ### SINGLETONS' METADATA
        GRAPH <{14}{15}>
        {{
            ?newSingletons
                rdf:singletonPropertyOf     alivocab:{12}{13} ;
                prov:wasDerivedFrom         ?pred ;
                alivocab:hasEvidence        ?evidence .
        }}
    }}
    WHERE
    {{
        ### LINKSET TO REFINE
        # graph <{5}>
        # {{
        #     ?{1} ?pred  ?{3} .
        #     bind( iri(replace("{11}{12}{13}_#", "#",  strafter(str(uuid()), "uuid:") )) as ?newSingletons )
        # }}

        ### MATCH FOUND
        GRAPH <{0}load02>
        {{
            ?{1} <{8}relatesTo> ?{3} .
             bind( iri(replace("{11}{12}{13}_#", "#",  strafter(str(uuid()), "uuid:") )) as ?newSingletons )
        }}
        {{
            SELECT ?grid ?orgref  ?evidence
            {{
                ### SOURCE AND TARGET LOADED TO A TEMPORARY GRAPH
                GRAPH <{0}load01>
                {{
                    ?{1} {2} ?src_value .
                    ?{3} {4} ?trg_value .
                    BIND(concat("[", ?src_value, "] aligns with [", ?trg_value, "]") AS ?evidence)
                }}
            }}
        }}
    }} ;

    DROP GRAPH <{0}load01> ;
    DROP GRAPH <{0}load02>
    """.format(
        # 0          1         2           3         4
        Ns.tmpgraph, src_name, src_aligns, trg_name, trg_aligns,
        # 5                6        7        8            9
        specs[St.linkset], src_uri, trg_uri, Ns.tmpvocab, specs[St.intermediate_graph],
        # 10               11           12                  13
        specs[St.refined], Ns.alivocab, specs[St.mechanism], specs[St.sameAsCount],
        # 14           15                      16           17
        Ns.singletons, specs[St.refined_name], Ns.alivocab, Ns.prov
    )

    # print insert
    return insert


def refine_metadata(specs):
    # GENERATE GENERIC METADATA
    metadata = Gn.linkset_refined_metadata(specs)
    # print metadata
    is_inserted = Qry.boolean_endpoint_response(metadata["query"])
    print ">>> THE METADATA IS SUCCESSFULLY INSERTED:", is_inserted

    if int(specs[St.triples]) > 0:

        # GENERATE LINKSET CONSTRUCT QUERY
        construct_query = "\n{}\n{}\n{}\n{}\n{}\n".format(
            "PREFIX predicate: <{}>".format(Ns.alivocab),
            "PREFIX {}: <{}>".format(specs[St.source][St.graph_name], specs[St.source][St.graph_ns]),
            "PREFIX {}: <{}>".format(specs[St.target][St.graph_name], specs[St.target][St.graph_ns]),
            "construct { ?x ?y ?z }",
            "where     {{ graph <{}> {{ ?x ?y ?z }} }}".format(specs[St.refined]),
        )

        # GENERATE LINKSET SINGLETON METADATA QUERY
        singleton_metadata_query = "\n{}\n{}\n{}\n{}\n{}\n{}\n\n".format(
            "PREFIX singMetadata:   <{}>".format(Ns.singletons),
            "PREFIX predicate:      <{}>".format(Ns.alivocab),
            "PREFIX prov:           <{}>".format(Ns.prov),
            "PREFIX rdf:            <{}>".format(Ns.rdf),

            "construct { ?x ?y ?z }",
            "where     {{ graph <{}> {{ ?x ?y ?z }} }}".format(specs[St.singleton]),
        )

        # GET THE CORRESPONDENCES INSERTED USING A THE CONSTRUCT QUERY
        singleton_construct = Qry.endpointconstruct(singleton_metadata_query)
        if singleton_construct is not None:
            singleton_construct = \
                singleton_construct.replace('{', "singMetadata:{}\n{{".format(specs[St.refined_name]), 1)

        # GET THE SINGLETON METADATA USING THE CONSTRUCT QUERY
        construct_response = Qry.endpointconstruct(construct_query)
        if construct_response is not None:
            construct_response = construct_response.replace('{', "<{}>\n{{".format(specs[St.refined]), 1)

        # WRITE TO FILE
        print "\t>>> WRITING TO FILE"
        write_to_file(graph_name=specs[St.refined_name], metadata=metadata["query"].replace("INSERT DATA", ""),
                      correspondences=construct_response, singletons=singleton_construct, directory=DIRECTORY)

        return metadata["message"]
