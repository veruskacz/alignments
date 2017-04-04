import Linkset as Ls
import src.Alignments.ErrorCodes as Ec
import src.Alignments.GenericMetadata as Gn
import src.Alignments.Lenses.Lens_Difference as Df
import src.Alignments.NameSpace as Ns
import src.Alignments.Query as Qry
import src.Alignments.Settings as St
from src.Alignments.UserActivities.UserRQ import register_alignment_mapping
from src.Alignments.Utility import write_to_file, update_specification


def refine_exact(specs):

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

    # CHECK WHETHER OR NOT THE LINKSET WAS ALREADY CREATED
    check = Ls.run_checks(specs)


    if check[St.message] == "NOT GOOD TO GO":
        # refined = check[St.refined]
        # difference = check["difference"]
        return check

    print "NAME:", specs[St.refined]
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
    matrix = Qry.sparql_xml_to_matrix(metadata_q)
    print matrix

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
            ?subject   <{}> 	?s_label ;
            BIND(lcase(str(?s_label)) as ?label)
        }}

        ### TARGET DATASET
        GRAPH <{}>
        {{
          ?object      <{}> 	?o_label ;
            BIND(lcase(str(?o_label)) as ?label)
        }}
    }}
    """.format(Ns.prov, Ns.rdf, Ns.alivocab,
               specs[St.refined], Ns.singletons, specs[St.refined_name], specs[St.mechanism], specs[St.sameAsCount],
               specs[St.linkset], Ns.alivocab, specs[St.mechanism], specs[St.sameAsCount],
               specs[St.singletonGraph],
               specs[St.source][St.graph], specs[St.source][St.aligns],
               specs[St.target][St.graph], specs[St.target][St.aligns])
    # print insert_query

    # RUN INSERT QUERY
    specs[St.insert_query] = insert_query
    is_run = Qry.boolean_endpoint_response(insert_query)
    print ">>> RUN SUCCESSFULLY:", is_run

    # GENERATE THE
    #   (1) LINKSET METADATA
    #   (2) LINKSET OF CORRESPONDENCES
    #   (3) SINGLETON METADATA
    # AND WRITE THEM ALL TO FILE
    refine_metadata(specs)

    # SET THE RESULT ASSUMING IT WENT WRONG
    refined = {St.message: Ec.ERROR_CODE_4, St.error_code: 4, St.result: None}
    diff = {St.message: Ec.ERROR_CODE_4, St.error_code: 4, St.result: None}

    server_message = "Linksets created as: {}".format(specs[St.refined])
    message = "The linkset was created!<br/>URI = {}".format(specs[St.linkset])
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
        print "\t>>> {} CORRESPONDENCES INSERTED AS THE DIFFERENCE".format(diff_lens_specs[St.triples])

    print "\tLinkset created as: ", specs[St.linkset]
    print "\t*** JOB DONE! ***"
    return {'refined': refined, 'difference': diff}

    # print metadata



def refine_metadata(specs):

    # GENERATE GENERIC METADATA
    metadata = Gn.linkset_refined_metadata(specs)
    is_inserted = Qry.boolean_endpoint_response(metadata)
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
        write_to_file(graph_name=specs[St.refined_name], metadata=metadata.replace("INSERT DATA", ""),
                      correspondences=construct_response, singletons=singleton_construct)



