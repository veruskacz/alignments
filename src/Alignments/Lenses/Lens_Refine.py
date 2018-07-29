import time
import datetime
import traceback
import Alignments.Query as Qry
import Alignments.Utility as Ut
import Alignments.Settings as St
import Alignments.NameSpace as Ns
import Alignments.ErrorCodes as Ec
import Alignments.Server_Settings as Ss
import Alignments.GenericMetadata as Gn
import Alignments.Linksets.Linkset as Ls
import Alignments.Lenses.LensUtility as lensUt
import Alignments.UserActivities.UserRQ as Urq
import Alignments.Lenses.Lens_Union as Lens_Union
from Alignments.Linksets.Linkset import writelinkset
# import Alignments.Linksets.SPA_LinksetRefine as Refine

DIRECTORY = Ss.settings[St.lens_Refined_dir]


specs_example = {
    "subjectsTarget": u"http://risis.eu/dataset/grid_20170712",
    "objectsTarget": u"http://risis.eu/dataset/eter_2014",
    "subjectsDatatype": u"http://xmlns.com/foaf/0.1/Organization",
    "objectsDatatype": u"http://risis.eu/eter_2014/ontology/class/University",
    St.unit: Ns.kilometer,
    St.unit_value: 0.5,

    "source": {
        # "aligns": u"<http://www.w3.org/2000/01/rdf-schema#label>",
        "graph": u"http://risis.eu/dataset/grid_20170712",
        "entity_datatype": u"http://xmlns.com/foaf/0.1/Organization",
        St.latitude: "<http://www.grid.ac/ontology/hasAddress>/<http://www.w3.org/2003/01/geo/wgs84_pos#lat>",
        St.longitude: "<http://www.grid.ac/ontology/hasAddress>/<http://www.w3.org/2003/01/geo/wgs84_pos#long>",
        St.crossCheck: u"<http://www.w3.org/2000/01/rdf-schema#label>",
    },

    "numeric_approx_type": u"number",

    "target": {
        # "aligns": u"<http://risis.eu/eter_2014/ontology/predicate/English_Institution_Name>",
        "graph": u"http://risis.eu/dataset/eter_2014",
        "entity_datatype": u"http://risis.eu/eter_2014/ontology/class/University",
        St.longitude: "http://risis.eu/eter_2014/ontology/predicate/Geographic_coordinates__longitude",
        St.latitude: "http://risis.eu/eter_2014/ontology/predicate/Geographic_coordinates__latitude",
        St.crossCheck: u"<http://risis.eu/eter_2014/ontology/predicate/English_Institution_Name>",
    },

    "researchQ_URI": u"http://risis.eu/activity/idea_67a6ce",
    "linkset": u"http://risis.eu/lens/union_Grid_20170712_Eter_2014_N291690309",
    "intermediate_graph": u"",
    "delta": u"0",
    # "mechanism": u"geoSim",
    "mechanism": u"nearbyGeoSim",
}

specs_example_2 = {

    "subjectsTarget": u"http://risis.eu/dataset/orgreg_20170718",
    "objectsTarget": u"http://risis.eu/dataset/eter_2014",
    "subjectsDatatype": u"http://risis.eu/orgreg_20170718/ontology/class/University",
    "objectsDatatype": u"http://risis.eu/eter_2014/ontology/class/University",
    "linkset": u"http://risis.eu/lens/union_Orgreg_20170718_Eter_2014_P1061032980",

    "source": {
        "graph": u"http://risis.eu/dataset/orgreg_20170718",
        "entity_datatype": u"http://risis.eu/orgreg_20170718/ontology/class/University",
        St.latitude: "<http://risis.eu/orgreg_20170718/ontology/predicate/locationOf>/"
                     "<http://risis.eu/orgreg_20170718/ontology/predicate/Geographical_coordinates__latitude>",
        St.longitude: "<http://risis.eu/orgreg_20170718/ontology/predicate/locationOf>/"
                      "<http://risis.eu/orgreg_20170718/ontology/predicate/Geographical_coordinates__longitude>",
        St.crossCheck: "<http://risis.eu/orgreg_20170718/ontology/predicate/Entity_current_name_English>",
    },

    "numeric_approx_type": u"number",

    "target": {
        "graph": u"http://risis.eu/dataset/eter_2014",
        "entity_datatype": u"http://risis.eu/eter_2014/ontology/class/University",
        St.longitude: "http://risis.eu/eter_2014/ontology/predicate/Geographic_coordinates__longitude",
        St.latitude: "http://risis.eu/eter_2014/ontology/predicate/Geographic_coordinates__latitude",
        St.crossCheck: u"<http://risis.eu/eter_2014/ontology/predicate/English_Institution_Name>",
    },

    St.unit: Ns.kilometer,
    St.unit_value: 2,
    "researchQ_URI": u"http://risis.eu/activity/idea_67a6ce",
    "intermediate_graph": u"",
    "delta": u"0",
    "mechanism": u"nearbyGeoSim",
}

specs_example_3 = {

    "subjectsTarget": u"http://risis.eu/dataset/orgreg_20170718",
    "objectsTarget": u"http://risis.eu/dataset/grid_20170712",
    "subjectsDatatype": u"http://risis.eu/orgreg_20170718/ontology/class/University",
    "objectsDatatype": u"http://xmlns.com/foaf/0.1/Organization",
    "linkset": u"http://risis.eu/lens/union_Orgreg_20170718_Grid_20170712_N1966224323",

    "source": {
        "graph": u"http://risis.eu/dataset/orgreg_20170718",
        "entity_datatype": u"http://risis.eu/orgreg_20170718/ontology/class/University",
        St.latitude: "<http://risis.eu/orgreg_20170718/ontology/predicate/locationOf>/"
                     "<http://risis.eu/orgreg_20170718/ontology/predicate/Geographical_coordinates__latitude>",
        St.longitude: "<http://risis.eu/orgreg_20170718/ontology/predicate/locationOf>/"
                      "<http://risis.eu/orgreg_20170718/ontology/predicate/Geographical_coordinates__longitude>",
        St.crossCheck: "<http://risis.eu/orgreg_20170718/ontology/predicate/Entity_current_name_English>",
    },

    "numeric_approx_type": u"number",

    "target": {
        # "aligns": u"<http://www.w3.org/2000/01/rdf-schema#label>",
        "graph": u"http://risis.eu/dataset/grid_20170712",
        "entity_datatype": u"http://xmlns.com/foaf/0.1/Organization",
        St.latitude: "<http://www.grid.ac/ontology/hasAddress>/<http://www.w3.org/2003/01/geo/wgs84_pos#lat>",
        St.longitude: "<http://www.grid.ac/ontology/hasAddress>/<http://www.w3.org/2003/01/geo/wgs84_pos#long>",
        St.crossCheck: u"<http://www.w3.org/2000/01/rdf-schema#label>",
    },

    St.unit: Ns.kilometer,
    St.unit_value: 2,
    "researchQ_URI": u"http://risis.eu/activity/idea_67a6ce",
    "intermediate_graph": u"",
    "delta": u"0",
    "mechanism": u"nearbyGeoSim",
}


def geo_load_query(specs, is_source):

    # UPDATE THE SPECS OF SOURCE AND TARGETS
    if is_source is True:
        info = specs[St.source]
        load = "_{}_1".format(specs[St.lens_name])
        links = "?resource   ?singPre    ?target ."
    else:
        info = specs[St.target]
        load = "_{}_2".format(specs[St.lens_name])
        links = "?source   ?singPre    ?resource ."

    # REPLACE RDF TYPE "rdf:type" IN CASE ANOTHER TYPE IS PROVIDED
    if St.rdf_predicate in info and info[St.rdf_predicate] is not None:
        rdf_pred = info[St.rdf_predicate] \
            if Ls.nt_format(info[St.rdf_predicate]) else "<{}>".format(info[St.rdf_predicate])
    else:
        rdf_pred = "a"

    # FORMATTING THE LONGITUDE PROPERTY
    longitude = info[St.longitude] \
        if Ls.nt_format(info[St.longitude]) else "<{}>".format(info[St.longitude])

    # FORMATTING THE LATITUDE PROPERTY
    latitude = info[St.latitude] \
        if Ls.nt_format(info[St.latitude]) else "<{}>".format(info[St.latitude])

    # EXTRACTING THE RESOURCE GRAPH URI LOCAL NAME
    # name = info[St.graph_name]

    # EXTRACTING THE RESOURCE GRAPH URI
    uri = info[St.graph]

    # ADD THE REDUCER IF SET
    # if St.reducer not in info:
    #     reducer_comment = "#"
    #     reducer = ""
    # else:
    #     reducer_comment = ""
    #     reducer = info[St.reducer]

    if is_source is True:
        message = """######################################################################
    ### INSERTING DATA FROM THE SOURCE
    ######################################################################"""
    else:
        message = """######################################################################
    ### INSERTING MESSAGE FROM THE TARGET
    ######################################################################"""

    query = """
    {5}
    PREFIX geof: <http://www.opengis.net/def/function/geosparql/>
    PREFIX wgs:  <http://www.w3.org/2003/01/geo/wgs84_pos#>
    INSERT
    {{
        GRAPH <{0}load{1}>
        {{
            ?resource  wgs:long  ?longitude .
            ?resource  wgs:lat   ?latitude .
        }}
    }}
    WHERE
    {{
        GRAPH <{8}>
        {{
            {9}
        }}

        GRAPH <{2}>
        {{
            ### LOCATION COORDINATES
            ?resource  {6}  <{7}> .
            ?resource  {3}  ?long .
            ?resource  {4}  ?lat .

            ### MAKING SURE THE COORDINATES ARE WELL FORMATTED
            BIND( STRDT(REPLACE(STR(?long), ",", "."), xsd:float)  as ?longitude )
            BIND( STRDT(REPLACE(STR(?lat), ",", "."), xsd:float)  as ?latitude )

            ### MAKING SURE THE COORDINATES AT DIGITS AND NOT LITERALS
            Filter (?longitude >= 0 || ?longitude <= 0 )
            Filter (?latitude  >= 0 || ?latitude  <= 0 )

            ### GENERATE A LOCATION URI
            BIND( replace("http://risis.eu/#","#", STRAFTER(str(UUID()),"uuid:")) as ?name )
            BIND(iri(?name) as ?location)
        }}
    }}
    """.format(
        # 0          1     2    3          4         5        6         7
        Ns.tmpgraph, load, uri, longitude, latitude, message, rdf_pred, info[St.entity_datatype],
        # 8                9
        specs[St.refined], links)
    # print query
    return query


def geo_match_query(specs):

    # Note that for WKT formatted points,
    # the location is <long, lat>. The location of the White House can also be encoded using the WGS 84

    # source = specs[St.source]
    # target = specs[St.target]
    # src_lat = source[St.latitude]
    # src_long = source[St.longitude]

    is_de_duplication = (specs[St.source][St.graph] == specs[St.target][St.graph]) and \
                        (specs[St.source][St.entity_datatype] == specs[St.target][St.entity_datatype])

    number_of_load = '{}_1'.format(specs[St.lens_name]) if is_de_duplication is True \
        else "{}_2".format(specs[St.lens_name])

    unit = "{}(s)".format(Ut.get_uri_local_name(specs[St.unit]).lower())

    match = """
    ######################################################################
    ### INSETTING MATCH FOUND IN A TEMPORARY GRAPH
    ######################################################################
    PREFIX ll:          <{0}>
    PREFIX tmpvocab:    <{0}>
    PREFIX tmpgraph:    <{1}>
    prefix lens:        <{5}>
    prefix singleton:   <{7}>
    prefix prov:        <{12}>
    PREFIX geof:        <http://www.opengis.net/def/function/geosparql/>
    PREFIX wgs:         <http://www.w3.org/2003/01/geo/wgs84_pos#>
    INSERT
    {{

        GRAPH lens:{6}
        {{
            ?src_resource  ?singPre  ?trg_resource .
        }}

        GRAPH singleton:{6}
        {{
            ?singPre rdf:singletonPropertyOf     ll:nearbyGeoSim{10} .
            ?singPre ll:hasEvidence             "Near each other by at most {3} {9}" .
            ?singPre ll:hasStrength             1 .
            ?singPre ?pre_derived               ?obj_derived .
            ?singPre ?der_pre                    ?der_obj .
        }}
    }}
    WHERE
    {{
        ### THE ALIGNMENT TO REFINE
        GRAPH lens:{11}
        {{
            ?src_resource ?singleton ?trg_resource .
        }}

        GRAPH singleton:{11}
        {{
            ?singleton ?pre_derived ?obj_derived  .
            OPTIONAL{{
                ?obj_derived prov:wasDerivedFrom* ?der_from .
                ?der_from ?der_pre ?der_obj .

            }}
        }}

        ### SOURCE DATASET WITH GEO-COORDINATES
        GRAPH tmpgraph:load_{6}_1
        {{
            ?src_resource  wgs:long  ?src_longitude .
            ?src_resource  wgs:lat   ?src_latitude .
            ### Create A SINGLETON URI
            BIND( replace("{0}{8}_#", "#", STRAFTER(str(UUID()),"uuid:")) as ?pre )
            BIND( iri(?pre) as ?singPre )
        }}

        ### TARGET DATASET WITH GEO-COORDINATES
        GRAPH tmpgraph:load_{2}
        {{
            ?trg_resource  wgs:long  ?trg_longitude .
            ?trg_resource  wgs:lat   ?trg_latitude .
        }}

        ### MATCHING TARGETS NEAR BY SOURCE
        ?src_resource  geof:nearby (?trg_resource {3} <{4}>).
    }}
    """.format(
        # 0          1            2               3                     4
        Ns.alivocab, Ns.tmpgraph, number_of_load, specs[St.unit_value], specs[St.unit],
        # 5         6                       7              8              9     10
        Ns.lens, specs[St.lens_name], Ns.singletons, specs[St.mechanism], unit, specs[St.sameAsCount],
        # 11                    12
        specs[St.refined_name], Ns.prov
    )

    return match


def geo_match(specs):

    # geo_query(ls_specs_1, True)
    # geo_query(ls_specs_1, False)
    # geo_match_query(ls_specs_1)
    drop_1 = """
    PREFIX tmp: <{0}>
    DROP SILENT GRAPH tmp:load_{1}_1 ;
    drop silent graph tmp:load_{1}_2
    """.format(Ns.tmpgraph, specs[St.lens_name], Ns.lens, Ns.singletons)

    drop_2 = """
    PREFIX lens: <{0}>
    PREFIX singletons: <{1}>
    drop silent graph lens:{2} ;
    drop silent graph singletons:{2}
    """.format(Ns.lens, Ns.singletons, specs[St.lens_name])

    print "\n\t4.1 >>> DROPPING GRAPH LOAD_1 & LOAD_2 IF THEY EXIST"
    # print drop_1
    print "\t", Qry.boolean_endpoint_response(drop_1)
    # print drop_2
    print "\t", Qry.boolean_endpoint_response(drop_2)

    print "\n\t4.2 >>> LOADING SOURCE INTO GRAPH LOAD-1"
    # print geo_load_query(specs, True)
    print "\t", Qry.boolean_endpoint_response(geo_load_query(specs, True))

    print "\n\t4.3 >>> LOADING SOURCE INTO GRAPH LOAD-2"
    # print geo_load_query(specs, False)
    print "\t", Qry.boolean_endpoint_response(geo_load_query(specs, False))

    print "\n\t4.4 >>> LOOKING FOR GEO-SIM BETWEEN SOURCE AND TARGET"
    print geo_match_query(specs)
    print "\t", Qry.boolean_endpoint_response(geo_match_query(specs))

    print "\n\t4.5 >>> DROPPING GRAPH LOAD_1 & LOAD_2"
    print "\t", Qry.boolean_endpoint_response(drop_1)


def refine_lens(specs, activated=False, check_file=False):

    try:

        message = Ec.ERROR_CODE_0.replace('\n', "<br/>")
        if activated is False:
            print Ut.headings("THE FUNCTION [refine_lens] IS NOT ACTIVATED")
            return {St.message: message, St.error_code: 4, St.result: None}

        # 1. UPDATING THE SPECS BY CHANGING LINKSET TO TENS
        specs[St.refined] = specs['linkset']
        specs.pop('linkset')
        Ut.update_specification(specs)

        # CHECKING WHETHER THE LENS IS REFINENABLE
        # Refine.is_refinable(specs[St.refined])

        # PRINTING THE SPECIFICATIONS
        # lensUt.print_specs(specs)

        # ASSIGN THE SAME AS COUNT
        specs[St.sameAsCount] = Qry.get_same_as_count(specs[St.mechanism])

        message = Ec.ERROR_CODE_4.replace('\n', "<br/>")
        if specs[St.sameAsCount]:

            source = specs[St.source]
            target = specs[St.target]

            # 2. SET THE LENS NAME
            # *******************************
            print "\n2. SET THE LENS NAME"
            # *******************************
            lensUt.lens_refine_name(specs, 'refine')

            #*******************************
            # GOOD TO GO CHECK
            # *******************************
            query = """
        SELECT *
        {{
            <{}> ?predicate ?object .
        }}
            """.format(specs[St.lens])
            check = Lens_Union.run_checks(specs, query, operator="refine")

            # NOT GOOD TO GO, IT ALREADY EXISTS
            if check[St.message].__contains__("ALREADY EXISTS"):
                return {St.message: check[St.message], St.error_code: 71, St.result: specs[St.lens]}

            # *******************************
            # GOOD TO GO
            # *******************************
            else:

                lens_start = time.time()
                # UPDATE THE SPECIFICATION
                Ut.update_specification(specs[St.source])
                Ut.update_specification(specs[St.target])

                # PRINTING THE SPECIFICATIONS
                lensUt.print_specs(specs)

                ########################################################################
                print """\n4. EXECUTING THE GEO-MATCH                                """
                ########################################################################
                geo_match(specs)

                ########################################################################
                print """\n5. EXTRACT THE NUMBER OF TRIPLES                          """
                ########################################################################
                specs[St.triples] = Qry.get_namedgraph_size("{0}{1}".format(Ns.lens, specs[St.lens_name]))

                ########################################################################
                print """\n6. ASSIGN THE SPARQL INSERT QUERY                         """
                ########################################################################
                specs[St.insert_query] = "{} ;\n{};\n{}".format(
                    geo_load_query(specs, True), geo_load_query(specs, False), geo_match_query(specs))

                lens_end = time.time()
                diff = lens_end - lens_start
                print "\n\t>>> Executed so far in    : {:<14}".format(str(datetime.timedelta(seconds=diff)))

                if int(specs[St.triples]) > 0:

                    ########################################################################
                    print """\n4. INSERTING THE GENERIC METADATA                         """
                    ########################################################################
                    metadata = Gn.lens_refine_geo_metadata(specs)
                    Qry.boolean_endpoint_response(metadata)

                    ########################################################################
                    print """\n5. WRITING TO FILE                                        """
                    ########################################################################
                    src = [source[St.graph_name], "", source[St.entity_ns]]
                    trg = [target[St.graph_name], "", target[St.entity_ns]]

                    # linkset_path = "D:\datasets\Linksets\ExactName"
                    linkset_path = DIRECTORY
                    writelinkset(src, trg, specs[St.lens_name], linkset_path, metadata, check_file=check_file)
                    server_message = "Linksets created as: {}".format(specs[St.lens])
                    message = "The linkset was created as [{}] with {} triples found!".format(
                        specs[St.lens], specs[St.triples])

                    print "\n\t", server_message

                    Urq.register_lens(specs, is_created=True)

                    ls_end_2 = time.time()
                    diff = ls_end_2 - lens_end
                    print ">>> Executed in    : {:<14}".format(str(datetime.timedelta(seconds=diff)))

                    print "\t*** JOB DONE! ***"

                    return {St.message: message, St.error_code: 0, St.result: specs[St.lens]}

                else:
                    print "\tThe linkset was not generated as no match could be found"
                    print "\t*** JOB DONE! ***"
                    return {St.message: message, St.error_code: 4, St.result: None}


    except Exception as err:
        traceback.print_exc()
        return {St.message: Ec.ERROR_CODE_1, St.error_code: 5, St.result: None}
            # print geo_load_query(specs, is_source=True)
            # print geo_load_query(specs, is_source=False)
            # geo_match_query(specs)

            # traceback.print_exception()

import Alignments.Manage.AdminGraphs as adm

adm.drop_a_lens("http://risis.eu/lens/refine_union_Grid_20170712_Eter_2014_N291690309", display=True, activated=True)
refine_lens(specs_example, activated=True, check_file=False)
#
# adm.drop_a_lens("http://risis.eu/lens/refine_union_Orgreg_20170718_Eter_2014_P1061032980", display=True, activated=True)
# refine_lens(specs_example_2, activated=True, check_file=False)
#
# adm.drop_a_lens("http://risis.eu/lens/refine_union_Orgreg_20170718_Grid_20170712_N1966224323", display=True, activated=True)
# refine_lens(specs_example_3, activated=True, check_file=False)