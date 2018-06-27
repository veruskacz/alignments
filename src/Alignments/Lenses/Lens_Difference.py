import Alignments.ErrorCodes as Ec
import Alignments.GenericMetadata as Gn
import Alignments.Lenses.LensUtility as Lu
import Alignments.NameSpace as Ns
import Alignments.Query as Qry
import Alignments.Settings as St
from Alignments.UserActivities.UserRQ import register_lens
from Alignments.Utility import write_to_file

import Alignments.Server_Settings as Ss
DIRECTORY = Ss.settings[St.lens_Diff_dir]


def difference(specs, save=False, activated=False):

    # print "LINKSET FUNCTION ACTIVATED: {}".format(activated)
    if activated is False:
        print "THE FUNCTION IS NOT ACTIVATED" \
              "\n======================================================" \
              "========================================================"
        return {St.message: "THE FUNCTION IS NOT ACTIVATED.", St.error_code: 1, St.result: None}
    else:
        print "COMPUTING THE DIFFERENCE BETWEEN:\n\t{}\n\t{}".format(specs[St.subjectsTarget], specs[St.objectsTarget])

    Lu.diff_lens_name(specs)

    # GENERATE THE LINKSET OF THE DIFFERENCE
    diff_insert_query = """
        PREFIX prov: <{0}>
        PREFIX specific:<{8}>
        ### Difference between
        ### <{1}> and
        ### <{2}>
        INSERT
        {{
            GRAPH <{3}>
            {{
                ?subject        ?newSingletons          ?object .
            }}
            GRAPH specific:{9}
            {{
                ?newSingletons	prov:wasDerivedFrom 	?predicate1 .
                ?predicate1	    ?pre 			        ?obj .
            }}
        }}
        WHERE
        {{
            {{
                GRAPH <{4}>
                {{
                    ?subject ?predicate1 ?object .
                    bind( iri(replace("{5}{6}_#", "#",  strafter(str(uuid()), "uuid:") )) as ?newSingletons )
                }}
                GRAPH ?g
                {{
                    ?predicate1 ?pre ?obj .
                }}
            }}
            MINUS
            {{
                GRAPH <{7}>
                {{
                    ?subject ?predicate2 ?object .
                }}
            }}
        }}
        """.format(Ns.prov, specs[St.subjectsTarget], specs[St.objectsTarget], specs[St.lens],
                   specs[St.subjectsTarget], Ns.alivocab, "diff", specs[St.objectsTarget], Ns.singletons,
                   specs[St.lens_name])
    # print diff_insert_query
    # print specs[St.lens_name]

    specs[St.insert_query] = diff_insert_query

    # RUN THE INSERT QUERY
    insertion_result = Qry.boolean_endpoint_response(diff_insert_query)
    print "\tDIFFERENCE INSERTED: {}".format(insertion_result)

    # RUN THE METADATA
    metadata = Gn.diff_meta(specs)

    # print metadata

    if int(specs[St.triples]) > 0:

        insertion_metadata = Qry.boolean_endpoint_response(metadata)
        print "\tDIFFERENCE INSERTED METADATA: {}".format(insertion_metadata)

        if save is True:

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
            print "\t>>> WRITING THE DIFFERENCE TO FILE"
            write_to_file(graph_name=specs[St.lens_name], metadata=metadata.replace("INSERT DATA", ""),
                          correspondences=construct_response, singletons=None, directory=DIRECTORY)

        server_message = "LENS created as: {}".format(specs[St.lens])
        message = "The LENS DIFFERENCE was created as<br/> {}" \
                  "<br/>with {} CORRESPONDENCES INSERTED AS THE DIFFERENCE".format(specs[St.lens], specs[St.triples])
        print "\t", server_message
        print "\t*** JOB DONE! ***"

        # REGISTER THE LENS
        register_lens(specs, is_created=True)

        return {St.message: message, St.error_code: 0, St.result: specs[St.lens]}
    else:
        return {St.message: Ec.ERROR_CODE_4, St.error_code: 4, St.result: None}
