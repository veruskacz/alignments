import src.Alignments.Settings as St
import src.Alignments.NameSpace as Ns
import src.Alignments.Query as Qry
import src.Alignments.GenericMetadata as Gn
from src.Alignments.Linksets.Linkset import get_URI_local_name
from src.Alignments.Linksets.Linkset import write_to_file
from src.Alignments.Linksets.Linkset import update_specification


def refine_exact(specs, database, host):

    # UPDATE THE SPECS VARIABLE
    update_specification(specs)
    update_specification(specs[St.source])
    update_specification(specs[St.target])
    specs[St.sameAsCount] = Qry.get_same_as_count(specs[St.mechanism], database, host)
    specs[St.refined_name] = "refined_{}".format(specs[St.linkset_name])
    specs[St.refined] = specs[St.linkset].replace(specs[St.linkset_name], specs[St.refined_name])
    specs[St.derivedfrom] = "\t\tprov:wasDerivedFrom\t\t\t<{}> ;".format(specs[St.linkset])

    # GETTING ABOUT THIS GRAPH
    metadata_q = Qry.q_linkset_metadata(specs[St.linkset])
    matrix = Qry.sparql_xml_to_matrix(metadata_q, database, host)
    specs[St.singletonGraph] = matrix[1][0]

    # GENERATE THE INSERT QUERY
    insert_query = """
    PREFIX prov:    <{}>
    PREFIX rdf:     <{}>
    INSERT
    {{
        GRAPH <{}>
        {{
            ?subject ?newSingletons ?object .
        }}

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
    """.format(Ns.prov, Ns.rdf, specs[St.refined], Ns.singletons, specs[St.refined_name],
               specs[St.mechanism], specs[St.sameAsCount],
               specs[St.linkset], Ns.alivocab, specs[St.mechanism],
               specs[St.sameAsCount], specs[St.singletonGraph],
               specs[St.source][St.graph], specs[St.source][St.aligns],
               specs[St.target][St.graph], specs[St.target][St.aligns])

    # RUN INSERT QUERY
    specs[St.insert_query] = insert_query
    print Qry.boolean_endpoint_response(insert_query, database, host)

    # GENERATE THE
    #   (1) LINKSET METADATA
    #   (2) LINKSET OF CORRESPONDENCES
    #   (3) SINGLETON METADATA
    # AND WRITE THEM ALL TO FILE
    refine_metadata(specs, database, host)

    # COMPUTE THE DIFFERENCE AND DOCUMENT IT
    diff_lens_specs = {
        St.subjectsTarget: specs[St.linkset],
        St.objectsTarget: specs[St.refined]
    }
    refined_diff(diff_lens_specs, database, host)
    print "\t>>> {} CORRESPONDENCES INSERTED AS THE DIFFERENCE".format(diff_lens_specs[St.triples])
    print "\tLinkset created as [SUBSET]: ", specs[St.linkset]
    print "\t*** JOB DONE! ***"

    # print metadata


def refine_metadata(specs, database, host):

    # GENERATE GENERIC METADATA
    metadata = Gn.linkset_refined_metadata(specs, database, host)
    print Qry.boolean_endpoint_response(metadata, database, host)

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
    singleton_construct = Qry.endpointconstruct(singleton_metadata_query, database, host)
    if singleton_construct is not None:
        singleton_construct = singleton_construct.replace('{', "singMetadata:{}\n{{".format(specs[St.refined_name]), 1)

    # GET THE SINGLETON METADATA USING THE CONSTRUCT QUERY
    construct_response = Qry.endpointconstruct(construct_query, database, host)
    if construct_response is not None:
        construct_response = construct_response.replace('{', "<{}>\n{{".format(specs[St.refined]), 1)

    # WRITE TO FILE
    print "\t>>> WRITING TO FILE"
    write_to_file(graph_name=specs[St.refined_name], metadata=metadata.replace("INSERT DATA", ""),
                  correspondences=construct_response, singletons=singleton_construct)


def refined_diff(specs, database, host):

    specs[St.lens_operation] = Ns.lensOpd
    src_name = get_URI_local_name(specs[St.subjectsTarget])
    trg_name = get_URI_local_name(specs[St.objectsTarget])
    specs[St.lens] = "{}diff_{}_{}".format(Ns.lens, src_name, trg_name)
    diff_insert_query = """
        ### Difference between
        ### <{}> and
        ### <{}>
        INSERT
        {{
            GRAPH <{}>
            {{
                ?subject ?newSingletons ?object .
            }}
        }}
        WHERE
        {{
            {{
                GRAPH <{}>
                {{
                    ?subject ?predicate1 ?object .
                    bind( iri(replace("{}_#", "#",  strafter(str(uuid()), "uuid:") )) as ?newSingletons )
                }}
            }}
            MINUS
            {{
                GRAPH <{}>
                {{
                    ?subject ?predicate2 ?object .
                }}
            }}
        }}
        """.format(specs[St.subjectsTarget], specs[St.objectsTarget], specs[St.lens],
                   specs[St.subjectsTarget], specs[St.lens], specs[St.objectsTarget])
    # print diff_insert_query

    specs[St.insert_query] = diff_insert_query
    update_specification(specs)

    # RUN THE INERT QUERY
    insertion_result = Qry.boolean_endpoint_response(diff_insert_query, database, host)
    print "\tDIFFERENCE INSERTED: {}".format(insertion_result)

    # RUN THE METADATA
    metadata = Gn.diff_meta(specs, database, host)
    insertion_metadata = Qry.boolean_endpoint_response(metadata, database, host)
    print "\tDIFFERENCE INSERTED METADATA: {}".format(insertion_metadata)
    # print metadata
