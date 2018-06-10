# -*- coding: utf-8 -*-
# coding=utf-8

import re
import Alignments.ErrorCodes as Ec
import Alignments.Query as Qry
import Alignments.Settings as St
import Alignments.Utility as Ut
from kitchen.text.converters import to_bytes, to_unicode

INFO = False
DETAIL = False

PREFIX = """
    PREFIX bdb:         <http://vocabularies.bridgedb.org/ops#>
    PREFIX rdf:         <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX linkset:     <http://risis.eu/linkset/>
    PREFIX void:        <http://rdfs.org/ns/void#>
    PREFIX alivocab:    <http://risis.eu/alignment/predicate/>
    PREFIX tmpgraph:    <http://risis.eu/alignment/temp-match/>
    PREFIX prov:        <http://www.w3.org/ns/prov#>
"""

MESSAGE_1 = "THIS RESEARCH QUESTION HAS ALREADY BEEN REGISTERED" \
            "\nAS [@]" \
            "\nPLEASE UPDATE YOUR RESEARCH QUESTION ACCORDINGLY."

MESSAGE_2 = "Y0UR RESEARCH QUESTION WAS SUCCESSFULLY REGISTERED" \
            "\nAS [@]"

MESSAGE_3 = "THE INSERTION OF YOUR RESEARCH QUESTION WAS NOT SUCCESSFUL DUE TO SOME INTERNAL ERROR"

MESSAGE_4 = "Y0UR RESEARCH QUESTION WAS SUCCESSFULLY REGISTERED" \
            "\nBUT, DUE TO SOME INTERNAL ERROR, THE URI COULD NOT BE RETRIEVED AT THIS POINT IN TIME." \
            "\nPLEASE, RESUBMIT AT A LATER TIME."


STARDOG_BOOLEAN_BUG_MESSAGE = "The query was successfully executed but no feedback was returned"

# RESEARCH QUESTIONS ARE INSERTED IN THIS GRAPH
# GRAPH = "{}researchQ".format(Ns.dataset)


#####################################################################################
# REGISTER A RESEARCH QUESTION
#####################################################################################

def register_research_question(question):

    print "REGISTERING A RESEARCH QUESTION." \
          "\n======================================================" \
          "========================================================"

    if True:
        # CHECK WHETHER THE RESEARCH QUESTION ALREADY EXISTS
        question = to_bytes(to_unicode(question, "utf-8"))
        existence_query = check_rq_existence(question)
        check = Qry.boolean_endpoint_response(existence_query)

        # LOOK FOR A RESEARCH QUESTION OF THE SAME NAMES GRAPH
        find_query = find_rq(question)

        # AN INTERNAL PROBLEM OCCURRED
        if check is None:
            return check

        # THE RESEARCH QUESTION WAS ALREADY REGISTERED
        elif check == "true":

            find = Qry.sparql_xml_to_matrix(find_query)
            # print find
            if find:
                if find[St.result]:
                    message = MESSAGE_1.replace("@", find[St.result][1][0])
                    print message
                    return {St.message: message.replace("@", "<br/>"), St.result: find[St.result][1][0]}
                return find
            else:
                return find

        # REGISTERING YOUR RESEARCH QUESTION
        else:
            print "REGISTERING THE RESEARCH QUESTION"
            ins_rq = research_question(question)
            # print ins_rq
            inserted = Qry.boolean_endpoint_response(ins_rq)
            print "INSERTED RESULT:", inserted

            #  THE REGISTRATION WAS NOT SUCCESSFUL
            if inserted is None:
                print "THE RESEARCH QUESTION WAS REGISTERED"
                print MESSAGE_3

            # THE REGISTRATION WAS SUCCESSFUL. RETRIEVE THE URI
            if inserted == "true" or inserted == STARDOG_BOOLEAN_BUG_MESSAGE:
                print "THE RESEARCH QUESTION IS REGISTERED"
                find = Qry.sparql_xml_to_matrix(find_query)
                if find:
                    if find[St.result]:
                        message = MESSAGE_2.replace("@", find[St.result][1][0])
                        print message
                        return {St.message: message.replace("@", "<br/>"), St.result: find[St.result][1][0]}

                    return {St.message: MESSAGE_4.replace("@", "<br/>"), St.result: None}
                else:
                    return find

            print {St.message: MESSAGE_3.replace("@", "<br/>"), St.result: None}

    # except Exception as err:
    #     # logger.warning(err)
    #     print "ERROR IN function [register_research_question]", err
    #     return {St.message: Ec.ERROR_CODE_4, St.error_code: 4, St.result: None}


def research_question(question):

    query = """
    ### CREATING A RESEARCH QUESTION RESOURCE
    INSERT
    {{
        GRAPH ?subject
        {{
            ?subject
                a               <http://risis.eu/class/ResearchQuestion> ;
                rdfs:label      ""\"{}\""" .
        }}
    }}
    WHERE
    {{
        BIND( iri(replace('http://risis.eu/activity/idea_#', "#", SUBSTR(str(UUID()), 40))) as ?subject)
    }}
    """.format(question)

    if DETAIL:
        print query
    return query


#####################################################################################
# REGISTER A DATASET MAPPING
#####################################################################################


def register_dataset_mapping(question_uri, mapping, activated=True):

    if activated:
        print "\nREGISTERING A [DATASET-MAPPING]" \
              "\n======================================================" \
              "========================================================"
        ds_mapping_query = ds_mapping(question_uri, mapping)
        inserted = Qry.boolean_endpoint_response(ds_mapping_query)
        message = "THE DATASET MAPPING WAS SUCCESSFULLY INSERTED." if inserted \
            else "DUE TO A SYSTEM FAILURE, THE MAPPING COULD NOT BE INSERTED."
        print message
        return {St.message: message, St.result: message}


#####################################################################################
# REGISTER A LINKSET
#####################################################################################


def register_alignment_mapping(alignment_mapping, created):

    print "\nREGISTERING AN [ALIGNMENT-MAPPING]"
    question_uri = alignment_mapping[St.researchQ_URI]

    # MAKE URE THE WRITE URI IS USED WHEN REGISTERING A REFINED LINKSET
    linkset_uri = alignment_mapping[St.refined] if St.refined in alignment_mapping else alignment_mapping[St.linkset]
    print "\tLINKSET TO REGISTER:", linkset_uri

    # LINKSET EXISTS
    if linkset_uri:

        # 1 CHECK WHETHER THE ALIGNMENT WAS REGISTERED
        ask_query = linkset_composition(alignment_mapping, request_ask_select_or_insert="ask")
        # print ask_query

        if ask_query is None:
            return

        ask = Qry.boolean_endpoint_response(ask_query)
        # print ask_query
        print "\t>>> ASK WHETHER THE [ALIGNMENT] WAS REGISTERED:", ask

        # 2 THE ALIGNMENT WAS NOT REGISTERED
        if ask == "false":

            # REGISTER THE ALIGNMENT-MAPPING
            insert_alignment_query = linkset_composition(alignment_mapping, request_ask_select_or_insert="insert")
            insert_alignment = Qry.boolean_endpoint_response(insert_alignment_query)
            # print insert_alignment_query
            print "\t>>> IS THE [ALIGNMENT] NOW INSERTED?:", insert_alignment

            # 2.1 RETRIEVE THE ALIGNMENT-MAPPING URI
            alignment_uri = None
            alignment_uri_query = ask_query.replace("ASK", "SELECT ?alignmentMapping")
            alignment_uri_resp = Qry.sparql_xml_to_matrix(alignment_uri_query)
            if alignment_uri_resp:
                if alignment_uri_resp[St.result]:
                    alignment_uri = alignment_uri_resp[St.result][1][0]
            print "\t>>> ALIGNMENT REGISTERED AS:", alignment_uri

            if alignment_uri:

                # IF WE ARE DEALING WITH A REFINED LINKSET, REGISTER ITS EVOLUTION
                if St.refined in alignment_mapping:
                    print "REGISTERING THE EVOLUTION OF THIS REFINED LINKSET TO\n\t{}".format(alignment_uri)
                    evolution_str = linkset_evolution(question_uri, linkset_uri)
                    register_evolution(question_uri, alignment_uri, evolution_str)

                # 2.2 ADD THE LINKSET TO THE ALIGNMENT
                assign_ls_query = linkset_createdorused(
                    question_uri, alignment_uri, alignment_mapping, is_created=created)

                is_linkset_registered = Qry.boolean_endpoint_response(assign_ls_query)
                print ">>> IS THE [LINKSET] REGISTERED?:", is_linkset_registered

        # 3 THE ALIGNMENT WAS REGISTERED
        else:

            # CHECK IF THE LINKSET WAS REGISTERED
            # is_linkset_registered_query = ask_query.replace("> .", "> ;\n\t\t?pred\t<{}> .".format(linkset_uri))
            # is_linkset_registered_query = is_linkset_registered_query.replace(">\" .", ">\" ;\n\t\t?pred\t<{}> .".format(linkset_uri))

            is_linkset_registered_query = ask_query.replace(
                "###@SLOT", "\n\t\t\t?alignmentMapping ?pred\t<{}> .".format(linkset_uri))

            # print "CHECKING WHETHER THE LINKSET WAS TRULY REGISTERED QUERY:", is_linkset_registered_query
            is_linkset_registered = Qry.boolean_endpoint_response(is_linkset_registered_query)
            # print is_linkset_registered_query
            print "\t>>> ASK WHETHER [LINKSET] WAS REGISTERED?:", is_linkset_registered

            if is_linkset_registered == "false":

                # RETRIEVE THE ALIGNMENT-MAPPING URI
                alignment_uri = None
                alignment_uri_query = ask_query.replace("ASK", "SELECT ?alignmentMapping")
                # print "alignment_uri_query:", alignment_uri_query
                alignment_uri_resp = Qry.sparql_xml_to_matrix(alignment_uri_query)
                if alignment_uri_resp:
                    if alignment_uri_resp[St.result]:
                        alignment_uri = alignment_uri_resp[St.result][1][0]

                if alignment_uri:

                    # IF WE ARE DEALING WITH A REFINED LINKSET,
                    # REGISTER ITS EVOLUTION IF NOT REGISTERED YET
                    if St.refined in alignment_mapping:
                        print "REGISTERING THE EVOLUTION OF THIS REFINED LINKSET"
                        evolution_str = linkset_evolution(question_uri, linkset_uri)
                        register_evolution(question_uri, alignment_uri, evolution_str)

                    # 2.3 ADD THE LINKSET TO THE ALIGNMENT
                    assign_ls_query = linkset_createdorused(
                        question_uri, alignment_uri, alignment_mapping, is_created=created)

                    is_linkset_registered = Qry.boolean_endpoint_response(assign_ls_query)
                    print "\t>>> IS LINKSET NOW REGISTERED?:", is_linkset_registered

    # ELSE, NO NEED TO REGISTER AN ALIGNMENT FOR A NON EXISTING LINKSET
    # 2. LINKSET DOES NOT EXIST
        # 2.1 THIS CONDITION IS NOT SUPPORTED BECAUSE THIS FUNCTION IS CALLED AFTER
        # CREATING A LINKSET. IF IT RETURNS NONE, IT MEANS AN ERROR OCCURS IN THE
        # SYSTEM


def linkset_composition(alignment_mapping, request_ask_select_or_insert="ask", get_composition=False):

    question_uri = alignment_mapping[St.researchQ_URI]
    linkset_uri = alignment_mapping[St.refined] if St.refined in alignment_mapping else alignment_mapping[St.linkset]

    # 1.1 GET THE LINKSET ALIGNMENT
    linkset_alignment_query = get_linkset_alignment(question_uri, linkset_uri)
    # print "ALIGNMENT QUERY:", linkset_alignment_query

    construct = Qry.endpointconstruct(linkset_alignment_query)
    # print "CONSTRUCT:", construct

    composition_init = re.findall('{(.*\)).*<.*> a <.*?> ;.*}', construct, re.S)
    if len(composition_init) > 0:
        composition_init = composition_init[0]
    else:
        composition_init = ""
    # print "COMPOSITION BINDINGS:", composition_init
    composition = re.findall('{.*a <.*?> ;(.*)}', construct, re.S)

    if get_composition:
        return composition[0]

    if len(composition) == 0:
        # INSPECT linkset_alignment_query = get_linkset_alignment(question_uri, linkset_uri)
        # print "construct", construct
        print "\tcomposition:", type(composition), len(composition), composition
        print "\tTHE LINKSET <{}> DOES NOT EXIST".format(linkset_uri)
        print linkset_alignment_query
        return None

    composition_str = composition[0]

    composition_str = composition_str.replace("\t\t", "\t\t\t\t")
    # print "COMPOSITION STRING EXTRACTED:", composition_str

    ask = "ASK"
    where = ""

    if request_ask_select_or_insert.upper() == "SELECT *":
        ask = "SELECT "

    elif request_ask_select_or_insert.upper() == "INSERT":
        ask = "INSERT"
        where = """
    WHERE
    {{
        {}
       BIND(iri(replace('http://risis.eu/activity/idea_algmt_#','#',SUBSTR(str(uuid()), 40))) as ?alignmentMapping)
    }}""".format(composition_init)
        # SO THAT IT IS NOT INSERTED MORE THAN ONES
        composition_init = ""

    # 1.2 CHECK WHETHER THE ALIGNMENT WAS REGISTERED
    query = PREFIX + """
    {0}
    {{
        {4}
        GRAPH <{1}>
        {{
            <{1}>   alivocab:created   ?alignmentMapping .
            ?alignmentMapping a <http://risis.eu/class/AlignmentMapping> ;{2}\t\t\t\t###@SLOT\n\t\t}}
    }}
    {3}""".format(ask, question_uri, composition_str, where, composition_init)

    if ask:
        return query


def get_linkset_alignment(question_uri, linkset_uri):

    alignment_query = PREFIX + """
    construct
    {{
        <{0}>
        #    alivocab:alignmentMapping       ?alignmentMapping .

        #?alignmentMapping
            a						<http://risis.eu/class/AlignmentMapping> ;
            void:target		        ?target ;
            void:subjectsTarget		?subjectsTarget ;
            void:objectsTarget		?objectsTarget ;
            bdb:subjectsDatatype	?subjectsDatatype ;
            bdb:objectsDatatype		?objectsDatatype ;
            alivocab:alignsSubjects	?alignsSubjects ;
            alivocab:alignsObjects	?alignsObjects .
    }}
    where
    {{
      #BIND(iri(replace('http://risis.eu/activity/idea_algmt_#','#',SUBSTR(str(uuid()), 40))) as ?alignmentMapping)
        {{ <{1}>    void:subjectsTarget		?subjectsTarget . }}
        UNION {{ <{1}>   alivocab:hasAlignmentTarget		?target .  }}
        optional {{ <{1}>    void:objectsTarget		    ?objectsTarget . }}
        optional {{ <{1}>    bdb:subjectsDatatype	    ?subjectsDatatype . }}
        optional {{ <{1}>    bdb:objectsDatatype		?objectsDatatype . }}
        optional {{ <{1}>    alivocab:alignsSubjects	?alignsSubjects . }}
        optional {{ <{1}>    alivocab:alignsObjects	    ?alignsObjects . }}
    }}
    """.format(question_uri, linkset_uri)
    # print alignment_query
    return alignment_query


def import_linkset(question_uri, linkset_list):

    message = ""

    # SET THE SPECIFICATION DICTIONARY
    spec = {St.researchQ_URI: question_uri}

    for linkset in linkset_list:

        # CHECK WHETHER WE ARE DEALING WITH A REGULAR LINKSET OR A REFINED LINKSET
        is_refined = True if str(linkset).__contains__("refined_") else False

        # REFINED LINKSET
        if is_refined is True:
            spec[St.refined] = linkset

        # REGULAR LINKSET
        else:
            spec[St.linkset] = linkset

        register_alignment_mapping(spec, False)

        message += "{} was imported\n".format(linkset)

    print "Message:", message
    return message.replace("\n", "<br/>")


#####################################################################################
# REGISTER A LENS
#####################################################################################


def register_lens(specs, is_created=True):

    # inverse = ""

    if is_created is True:
        created = "alivocab:created"
        inverse = "prov:used"
        print "REGISTERING [{}] AS CREATED".format(specs[St.lens])

    else:
        created = "prov:used\t\t"
        inverse = "alivocab:created"
        print "REGISTERING [{}] AS IMPORTED".format(specs[St.lens])

    query = PREFIX + """
    INSERT
    {{
        GRAPH <{0}>
        {{
            <{0}>   {1}        <{2}> .
            <{2}>   a          bdb:Lens .
        }}
    }}
    WHERE
    {{
        GRAPH <{0}>
        {{
            FILTER NOT EXISTS
            {{
                <{0}>    {3}       <{2}> .
            }}
        }}
    }}""".format(specs[St.researchQ_URI], created, specs[St.lens], inverse)
    # print query
    registered = Qry.boolean_endpoint_response(query)
    print "\t>>> IS THE LENS REGISTERED?:", registered


def linkset_wasderivedfrom(refined_linkset_uri):
    query = """
    select *
    {{
        <{}>
            <http://www.w3.org/ns/prov#wasDerivedFrom> ?wasDerivedFrom .
    }}
    """.format(refined_linkset_uri)
    # print query
    dictionary_result = Qry.sparql_xml_to_matrix(query)
    # print dictionary_result
    # print dictionary_result
    if dictionary_result:
        if dictionary_result[St.result]:
            return dictionary_result[St.result][1][0]
    return None


def import_lens(question_uri, linkset_list):

    # SET THE SPECIFICATION DICTIONARY
    message = ""
    spec = {St.researchQ_URI: question_uri}

    for lens in linkset_list:

        # REFINED LINKSET
        spec[St.lens] = lens

        register_lens(spec, False)

        message += "{} was imported\n".format(lens)

    print message
    return message.replace("\n", "<br/>")


#####################################################################################
# REGISTER LINKSET EVOLUTION
#####################################################################################


def register_evolution(research_question_uri, alignment_uri, evolution_str):

    if alignment_uri.__contains__("<<"):
        alignment_uri = str(alignment_uri).replace("<<", "<").replace(">>", ">")
        bind = "BIND(iri(\"{}\") AS ?LINK)".format(alignment_uri)

        query = """
            PREFIX alivocab:    <http://risis.eu/alignment/predicate/>
            INSERT DATA
            {{
                {0}
                GRAPH <{1}>
                {{
                    ?LINK   alivocab:evolution        ""\"{2}\""" .
                }}
            }}
            """.format(bind, research_question_uri, evolution_str)
    else:
        query = """
        PREFIX alivocab:    <http://risis.eu/alignment/predicate/>
        INSERT DATA
        {{
            GRAPH <{0}>
            {{
                <{1}>   alivocab:evolution        ""\"{2}\""" .
            }}
        }}
        """.format(research_question_uri, alignment_uri, evolution_str)

    # print query
    registered = Qry.boolean_endpoint_response(query)
    print "\t>>> IS EVOLUTION REGISTERED FOR {}?: {}".format(alignment_uri, registered)


def linkset_evolution(research_question_uri, refined_linkset_uri):

    # BUILD THE SPECIFICATION
    specs = {St.researchQ_URI: research_question_uri.strip(), St.linkset: refined_linkset_uri}
    # print specs

    # DOCUMENT THE ALIGNMENT
    document = ""
    metadata = linkset_evolution_composition(alignment_mapping=specs)
    # print "METADATA:", metadata

    if metadata:
        # 1: GETTING SUBJECT - OBJECT & MECHANISM-
        elements1 = re.findall('\t.*:aligns(.*) "<{0,1}', metadata)
        # elements2 = re.findall('(<.*?>)', metadata, re.S)
        elements2 = re.findall('"(<{0,1}.*?>{0,1})"', metadata, re.S)
        # print "1: ", elements1
        # print "2:", elements2
        # print ""
        if len(elements1) == len(elements2) == 3:
            for i in range(3):
                append = " | " if i < 2 else ""
                two = elements2[i] if Ut.is_nt_format(elements2[i]) else "<{}>".format(elements2[i])
                document += "{}={}{}".format(elements1[i], two, append)
            document = "[{}]".format(document)

        # FOLLOW DOWN THE PATH
        new_link = linkset_wasderivedfrom(refined_linkset_uri)
        new_document = linkset_evolution(research_question_uri, new_link)
        # print "DONE!!!!"
        # RECURSIVE CALL
        return document + ";\n" + linkset_evolution(research_question_uri, new_link) if new_document else document

    # print "NO EVOLUTION RESULT"
    return document


def linkset_evolution_composition(alignment_mapping):

    question_uri = alignment_mapping[St.researchQ_URI]
    linkset_uri = alignment_mapping[St.refined] if St.refined in alignment_mapping else alignment_mapping[St.linkset]

    # 1.1 GET THE LINKSET ALIGNMENT
    alignment_query = PREFIX + """
    construct
    {{
        <{1}>
            a						    <http://risis.eu/class/AlignmentMapping> ;
            alivocab:alignsSubjects	    ?srcAligns ;
            alivocab:alignsObjects	    ?trgAligns ;
            alivocab:alignsMechanism	?mechanism .
    }}
    where
    {{
      #BIND(iri(replace('http://risis.eu/activity/idea_algmt_#','#',SUBSTR(str(uuid()), 40))) as ?alignmentMapping)
        <{1}>
            alivocab:alignsSubjects	    ?alignsSubjects ;
            alivocab:alignsObjects	    ?alignsObjects ;
            alivocab:alignsMechanism	?alignsMechanism .
            bind( str( ?alignsSubjects) as  ?srcAligns )
            bind( str( ?alignsObjects ) as  ?trgAligns )
            bind( str( ?alignsMechanism) as ?mechanism )
    }}
    """.format(question_uri, linkset_uri)
    construct = Qry.endpointconstruct(alignment_query)
    # print construct
    composition = re.findall('{.*a <.*?> ;(.*)}', construct, re.S)

    if composition:
        return composition[0]
    return None


def linkset_createdorused(question_uri, alignment_mapping_uri, specs, is_created=True):

    if alignment_mapping_uri.__contains__("<<"):
        alignment_mapping_uri = str(alignment_mapping_uri).replace("<<", "<").replace(">>", ">")

    if Ut.is_nt_format(alignment_mapping_uri) is False:
        alignment_mapping_uri = "<{}>".format(alignment_mapping_uri)

    linkset_uri = specs[St.refined] if St.refined in specs else specs[St.linkset]

    comment = "#"

    if is_created is True:
        created = "alivocab:created"
        opposed = "prov:used\t\t"
        print "REGISTERING [{}] AS CREATED".format(linkset_uri)

    else:
        created = "prov:used\t\t"
        opposed = "alivocab:created"
        comment = "#"
        print "REGISTERING [{}] AS IMPORTED".format(linkset_uri)

    query = PREFIX + """
    INSERT
    {{
        GRAPH <{0}>
        {{
            {1}   {2}        <{3}> .
            {4}{1}  prov:wasDerivedFrom     <{3}> .
        }}
    }}
    WHERE
    {{
        GRAPH <{0}>
        {{
            FILTER NOT EXISTS
            {{
                {1}    {5}        <{3}> .
            }}
        }}
        ### BIND(iri(\"{1}\") AS ?aligns)
    }}
    """.format(question_uri, alignment_mapping_uri, created, linkset_uri, comment, opposed)

    # print query

    return query


#####################################################################################
# ABOUT
#####################################################################################


def about_registered():

    query = """
    PREFIX alivocab:    <http://risis.eu/alignment/predicate/>
    PREFIX prov:        <http://www.w3.org/ns/prov#>
    PREFIX bdb:         <http://vocabularies.bridgedb.org/ops#>

    select  distinct ?researchQ ?obj ?pred ?object
        {
           graph <http://risis.eu/dataset/researchQ>
           {
                { ?researchQ	alivocab:created    ?obj . } UNION
                { ?researchQ	prov:used			?obj . } UNION
                { ?researchQ	alivocab:selected   ?obj . }

                ?obj
                    a							bdb:Lens ;
                    #a							<http://risis.eu/class/AlignmentMapping> ;
                    #a                           <http://risis.eu/class/Dataset> ;
                    ?pred                       ?object .
           }
        }
    """

    return query


def about_dataset_mapping(question_uri=None, dataset_and_datatypes=False):

    # PROVIDE A SPECIFIC RQ OR CHECK ALL RQs
    uri = "?researchQ" if question_uri is None else "<{}>".format(question_uri)

    # SELECT ONLY THE DATASET AND DATATYPE
    select = '*' if dataset_and_datatypes is False else "?target ?Datatype"
    """
    PREFIX alivocab:    <http://risis.eu/alignment/predicate/>
    PREFIX void:        <http://rdfs.org/ns/void#>
    SELECT  {}
    {{
       graph <http://risis.eu/dataset/researchQ>
       {{
            {}
               alivocab:selected     ?selectedSource .

            ?selectedSource
                a                     ?type ;
                alivocab:hasDatatype  ?Datatype .
       }}
    }} ORDER BY ?target
    """.format(select, uri)


def about_alignment_mapping():
    """
    :return:
    """

    # ALIGNMENT MAPPING DATASETS, DATATYPES AND PROPERTIES
    """
    PREFIX alivocab:    <http://risis.eu/alignment/predicate/>
    PREFIX void:        <http://rdfs.org/ns/void#>
    select   ?pred ?object
    {
       graph <http://risis.eu/dataset/researchQ>
       {
            ?researchQ
               alivocab:created    ?alignmentMapping .

            ?alignmentMapping
                a							<http://risis.eu/class/AlignmentMapping> ;
                ?pred
       }
    }
    """


#####################################################################################
# QUERIES
#####################################################################################


def alignment_composition(alignment_mapping):

    print alignment_mapping

    # SOURCE
    source = ""
    if St.graph in alignment_mapping[St.source]:
        source += "void:subjectsTarget\t\t\t<{}> ;".format(alignment_mapping[St.source][St.graph])
    if St.entity_datatype in alignment_mapping[St.source]:
        source += "\n\t\t\t\t\tbdb:subjectsDatatype\t\t<{}> ;".format(alignment_mapping[St.source][St.entity_datatype])
    if St.aligns in alignment_mapping[St.source]:
        source += "\n\t\t\t\t\tbdb:alignsSubjects\t\t\t<{}> ;".format(alignment_mapping[St.source][St.aligns])

    # TARGET
    target = ""
    if St.graph in alignment_mapping[St.target]:
        target += "\n\t\t\t\t\tvoid:objectsTarget\t\t\t<{}> ;".format(alignment_mapping[St.target][St.graph])
    if St.entity_datatype in alignment_mapping[St.target]:
        target += "\n\t\t\t\t\tbdb:objectsDatatype\t\t\t<{}> ;".format(alignment_mapping[St.target][St.entity_datatype])
    if St.aligns in alignment_mapping[St.target]:
        target += "\n\t\t\t\t\tbdb:alignsObjects\t\t\t<{}> ;".format(alignment_mapping[St.target][St.aligns])

    target = target[:len(target) - 1]

    triples = source + target

    return triples


def alignment_composition2(alignment_mapping):

    print alignment_mapping

    # SOURCE
    source = ""
    if St.graph in alignment_mapping[St.source]:
        source += "?subjectsTarget\t\t\t<{}> ;".format(alignment_mapping[St.source][St.graph])
    if St.entity_datatype in alignment_mapping[St.source]:
        source += "\n\t\t\t\t?subjectsDatatype\t\t<{}> ;".format(alignment_mapping[St.source][St.entity_datatype])
    if St.aligns in alignment_mapping[St.source]:
        source += "\n\t\t\t\t?alignsSubjects\t\t\t<{}> ;".format(alignment_mapping[St.source][St.aligns])

    # TARGET
    target = ""
    if St.graph in alignment_mapping[St.target]:
        target += "\n\t\t\t\t?objectsTarget\t\t\t<{}> ;".format(alignment_mapping[St.target][St.graph])
    if St.entity_datatype in alignment_mapping[St.target]:
        target += "\n\t\t\t\t?objectsDatatype\t\t<{}> ;".format(alignment_mapping[St.target][St.entity_datatype])
    if St.aligns in alignment_mapping[St.target]:
        target += "\n\t\t\t\t?alignsObjects\t\t\t<{}> ;".format(alignment_mapping[St.target][St.aligns])

    target = target[:len(target) - 1]

    triples = source + target

    return triples


def ds_mapping(question_uri, mapping):

    """
    :param question_uri: THE URI OF THE RESEARCH QUESTION
    :param mapping: A DICTIONARY FILLED WITH THE KEY:STR(DATASET_URI) VALUE:LIST(DATATYPE)
    :return: STR(QUERY) FOR ASSOCIATING A DATASET MAPPING TO A RESEARCH QUESTION
    """

    if question_uri is None or mapping is None:
        print "NEITHER THE RESEARCH QUESTION OR THE MAPPING ARE SUPPOSED TO BE NONE"
        return None

    # question_uri = "http://risis.eu/activity/idea_2d84ccb0-c19a-42f9-89d5-3a4e3a3f1a5d"
    #
    # mapping = {"http://risis.eu/dataset/grid": [
    #     "http://risis.eu/grid/ontology/class/Hospital",
    #     "http://risis.eu/grid/ontology/class/Education",
    #     "http://risis.eu/grid/ontology/class/Company"],
    #
    #     "http://risis.eu/dataset/leidenRanking": ["http://risis.eu/leidenRanking/ontology/class/University"]
    # }

    # print "\nEnter the function"
    insert_query = ""
    count_ds = 0

    # CREATE THE DATASET TRIPLES FIRST
    for dataset, datatypes in mapping.items():

        append0 = "### {}:".format(count_ds + 1) if count_ds == 0 else ";\n\n\t### {}:".format(count_ds + 1)

        # FOR EACH DATASET IN THE DICTIONARY, CREATE A DATASET MAPPING OBJECT
        ds_mapping_query = """
    {2} INSERTING DATASET: {1}
    INSERT
    {{
        GRAPH <{3}>
        {{
            <{3}>
                alivocab:selected           <{1}> .

            <{1}>
                a                           <http://risis.eu/class/Dataset> .
        }}
    }}
    WHERE
    {{
        FILTER NOT EXISTS
        {{
            GRAPH <{3}>
            {{
                <{3}>
                     alivocab:selected        <{1}> .
            }}
        }}
    }} ;
    """.format(count_ds, dataset, append0, question_uri)

        # FOR EACH DATASET MAPPING CREATED, ADD THE TYPES OF INTEREST
        selected_datatypes = ""
        for i in range(len(datatypes)):
            append1 = "" if i == 0 else " ;\n\t\t\t"
            selected_datatypes += "{}alivocab:hasDatatype   <{}>".format(append1, datatypes[i])

        datatype_query = """
    ### INSERTING DATATYPES OF INTEREST FOR DATASET: {1}
    INSERT
    {{
        GRAPH <{2}>
        {{
            <{1}>
                {0} .
        }}
    }}
    WHERE
    {{
        GRAPH <{2}>
        {{
             <{2}>
                alivocab:selected     <{1}> .

            <{1}>
                a                           <http://risis.eu/class/Dataset> .
        }}
    }}""".format(selected_datatypes, dataset, question_uri)

        insert_query += "{}{}".format(ds_mapping_query, datatype_query)

        count_ds += 1

    final_query = PREFIX + insert_query

    # print final_query

    if DETAIL:
        print final_query

    return final_query


def associate_linkset_lens_to_rq(question_uri, linkset, is_created=True):

    created = "alivocab:created"if is_created else "prov:used\t\t"

    query = """
    INSERT
    {{
        <{0}>   {2}     <{1}>
    }}
    WHERE
    {{
        <{0}>   ?pred   ?obj .
    }}
    """.format(question_uri, linkset, created)
    if DETAIL:
        print query
    return query


def check_rq_existence(question):

    query = """
    ask
    {{
        GRAPH ?subject
        {{
            ?subject a <http://risis.eu/class/ResearchQuestion> ;
                rdfs:label ""\"{}\""".
        }}
    }}""".format(question)
    if DETAIL:
        print query

    return query


def find_alignment(alignment_mapping, is_created=True, check_method=False):

    composition = alignment_composition2(alignment_mapping)

    # CHECK WHETHER THERE EXISTS AN [ALIGNMENT-MAPPING] OF THIS PARTICULAR [COMPOSITION],
    # REGISTERED UNDER THIS [RESEARCH QUESTION], AND WHICH WAS USED TO GENERATE A [LINKSET]
    # WITH THIS PARTICULAR [ALIGNMENT-METHOD]
    # RESEARCH QUESTION CREATED OR IMPORTED THIS
    #  "alivocab:created" "prov:used\t\t"
    created = "?created\t" if is_created else "?used\t\t\t"

    # IF THE CHECK METHOD IS ACTIVATED, WE WANT TO KNOW WHETHER
    # THE REGISTERED IMPORTED/CREATED ALIGNMENT USED/IMPORTED
    # THE LINKSET OF INTEREST
    method = "" if check_method else "#"

    query = PREFIX + """
    #select   ?pred ?object
    ASK
    {{
       graph <http://risis.eu/dataset/researchQ>
       {{
            # IS THERE AN ALIGNMENT
            ?researchQ
               alivocab:alignmentMapping     ?alignmentMapping .

            # REGISTERED UNDER THIS COMPOSITION?
            ?alignmentMapping
                {} ;

            # IS THIS LINKSET REGISTERED UNDER THIS ALIGNMENT?
                {}{}		?linkset ;
       }}
    }}
    """.format(composition, method, created)
    print query
    return query


def find_rq(question):

    query = """
    SELECT *
    {{
        GRAPH ?subject
        {{
            ?subject a <http://risis.eu/class/ResearchQuestion> ;
                rdfs:label ""\"{}\""".
        }}
    }}""".format(question)
    if DETAIL:
        print query

    return query


def delete_rq():
    query = """
    DELETE {  ?subject ?pred ?obj . }
    WHERE
    {
        ?subject    a           <http://risis.eu/class/ResearchQuestion> ;
                    ?pred      ?obj .
    }
    """
    if DETAIL:
        print query
    return query


def view_alignment_metadata():

    query = """

    """
