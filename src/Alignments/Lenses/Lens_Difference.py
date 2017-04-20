import src.Alignments.ErrorCodes as Ec
import src.Alignments.GenericMetadata as Gn
import src.Alignments.Lenses.LensUtility as Lu
import src.Alignments.NameSpace as Ns
import src.Alignments.Query as Qry
import src.Alignments.Settings as St
from src.Alignments.UserActivities.UserRQ import register_lens
from src.Alignments.Utility import write_to_file


def difference(specs):

    Lu.diff_lens_name(specs)

    # GENERATE THE LINKSET OF THE DIFFERENCE
    diff_insert_query = """
        PREFIX prov: <{}>
        ### Difference between
        ### <{}> and
        ### <{}>
        INSERT
        {{
            GRAPH <{}>
            {{
                ?subject        ?newSingletons          ?object .
                ?newSingletons	prov:wasDerivedFrom 	?predicate1 .
                ?predicate1	    ?pre 			        ?obj .
            }}
        }}
        WHERE
        {{
            {{
                GRAPH <{}>
                {{
                    ?subject ?predicate1 ?object .
                    bind( iri(replace("{}{}_#", "#",  strafter(str(uuid()), "uuid:") )) as ?newSingletons )
                }}
                GRAPH ?g
                {{
                    ?predicate1 ?pre ?obj .
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
        """.format(Ns.prov, specs[St.subjectsTarget], specs[St.objectsTarget], specs[St.lens],
                   specs[St.subjectsTarget], Ns.alivocab, "diff", specs[St.objectsTarget])
    # print diff_insert_query
    # print specs[St.lens_name]

    specs[St.insert_query] = diff_insert_query

    # RUN THE INSERT QUERY
    insertion_result = Qry.boolean_endpoint_response(diff_insert_query)
    print "\tDIFFERENCE INSERTED: {}".format(insertion_result)

    # RUN THE METADATA
    metadata = Gn.diff_meta(specs)
    insertion_metadata = Qry.boolean_endpoint_response(metadata)
    print "\tDIFFERENCE INSERTED METADATA: {}".format(insertion_metadata)
    # print metadata

    if int(specs[St.triples]) > 0:

        # GENERATE LINKSET CONSTRUCT QUERY
        construct_query = "\n{}\n{}\n{}\n".format(
            "PREFIX alivocab:<{}>".format(Ns.alivocab),
            "construct { ?x ?y ?z }",
            "where     {{ graph <{}> {{ ?x ?y ?z }} }}".format(specs[St.lens]),
        )
        # print construct_query

        # GET THE SINGLETON METADATA USING THE CONSTRUCT QUERY
        construct_response = Qry.endpointconstruct(construct_query)
        if construct_response is not None:
            construct_response = construct_response.replace('{', "<{}>\n{{".format(specs[St.lens]), 1)
            # print construct_response

        # WRITE TO FILE
        print "\t>>> WRITING TO FILE"
        write_to_file(graph_name=specs[St.lens_name], metadata=metadata.replace("INSERT DATA", ""),
                      correspondences=construct_response, singletons=None)

        server_message = "LENS created as: {}".format(specs[St.lens])
        message = "The LENS was created!<br/>URI = {}".format(specs[St.lens])
        print "\t", server_message
        print "\t*** JOB DONE! ***"

        # REGISTER THE LENS
        register_lens(specs, is_created=True)

        return {St.message: message, St.error_code: 0, St.result: specs[St.lens]}
    else:
        return {St.message: Ec.ERROR_CODE_4, St.error_code: 4, St.result: None}