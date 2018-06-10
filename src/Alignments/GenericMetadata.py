import Alignments.NameSpace as Ns
import Alignments.Settings as St
import Alignments.Query as Qry
import Alignments.Linksets.Linkset as Ls
# import numbers
import math
import Alignments.Utility as Ut


def linkset_metadata(specs, display=False):

    extra = ""
    if St.reducer in specs[St.source] and len(specs[St.source][St.reducer]) > 0:
        extra += "\n        alivocab:subjectsReducer    <{}> ;".format(specs[St.source][St.reducer])

    if St.reducer in specs[St.target] and len(specs[St.target][St.reducer]) > 0:
        extra += "\n        alivocab:objectsReducer     <{}> ;".format(specs[St.target][St.reducer])

    if St.intermediate_graph in specs and len(specs[St.intermediate_graph]) > 0:
        extra += "\n        alivocab:intermediate       <{}> ;".format(specs[St.intermediate_graph])

    if St.threshold in specs and len(str(specs[St.threshold])) > 0:
        extra += "\n        alivocab:threshold          {} ;".format(str(specs[St.threshold]))

    if St.delta in specs and len(str(specs[St.delta])) > 0:
        extra += "\n        alivocab:delta              {} ;".format(str(specs[St.delta]))

    source = specs[St.source]
    target = specs[St.target]

    src_aligns = Ls.format_aligns(source[St.aligns])
    trg_aligns = Ls.format_aligns(target[St.aligns])

    # cCROSS CHECK INFORMATION IS USED IN CASE THE ALIGN PROPERTY APPEARS MEANINGLESS
    src_cross_check = Ls.format_aligns(source[St.crossCheck]) if St.crossCheck in source else None
    trg_cross_check = Ls.format_aligns(target[St.crossCheck]) if St.crossCheck in target else None

    # CROSS CHECK FOR THE WHERE CLAUSE
    cross_check_where = ''
    cross_check_where += "\n    BIND(iri({}) AS ?src_crossCheck)".format(
        src_cross_check) if src_cross_check is not None else ''
    cross_check_where += "\n    BIND(iri({}) AS ?trg_crossCheck)".format(
        trg_cross_check) if trg_cross_check is not None else ''

    # CROSS CHECK FOR THE INSERT CLAUSE
    cross_check_insert = ''
    cross_check_insert += "\n        alivocab:crossCheckSubject        ?src_crossCheck ;" \
        if src_cross_check is not None else ''
    cross_check_insert += "\n        alivocab:crossCheckObject         ?trg_crossCheck ;" \
        if trg_cross_check is not None else ''

    # specs[St.linkset] = "{}{}".format(Ns.linkset, specs[St.linkset_name])
    specs[St.singleton] = "{}{}".format(Ns.singletons, specs[St.linkset_name])
    specs[St.link] = "{}{}{}".format(Ns.alivocab, "exactStrSim", specs[St.sameAsCount])
    specs[St.assertion_method] = "{}{}".format(Ns.method, specs[St.linkset_name])
    specs[St.justification] = "{}{}".format(Ns.justification, specs[St.linkset_name])
    specs[St.link_comment] = "The predicate <{}> used in this linkset is a property that reflects an entity " \
                             "linking approach based on the <{}{}> mechanism.". \
        format(specs[St.link], Ns.mechanism, specs[St.mechanism])

    if str(specs[St.mechanism]).lower() == "intermediate":
        specs[St.link_name] = "Exact String Similarity via intermediate dataset"
        specs[St.link_subpropertyof] = "http://risis.eu/linkset/predicate/{}".format(specs[St.mechanism])
        specs[St.justification_comment] = "The method MATCH VIA INTERMEDIATE DATASET is used to align the" \
                                          " source and the target by using properties that present different " \
                                          "descriptions of a same entity, such as country name and country code. " \
                                          "This is possible by providing an intermediate dataset that binds the " \
                                          "two alternative descriptions to the very same identifier."
        specs[St.linkset_comment] = "Linking <{}> to <{}> by aligning {} with {} using the mechanism: {}". \
            format(source[St.graph], target[St.graph], src_aligns, trg_aligns, specs[St.mechanism])

    if str(specs[St.mechanism]).lower() == "exactstrsim":
        specs[St.link_name] = "Exact String Similarity"
        specs[St.link_subpropertyof] = "http://risis.eu/linkset/predicate/{}".format(specs[St.mechanism])
        specs[St.justification_comment] = "We assume that entities with the aligned predicates sharing the " \
                                          "exact same content are the same. This assumption applies when dealing " \
                                          "with entities such as Organisation."
        specs[St.linkset_comment] = "Linking <{}> to <{}> by aligning {} with {} using the mechanism: {}". \
            format(source[St.graph], target[St.graph], src_aligns, trg_aligns, specs[St.mechanism])

    elif str(specs[St.mechanism]).lower() == "identity":
        specs[St.link_name] = "Same URI"
        specs[St.link_subpropertyof] = "http://risis.eu/linkset/predicate/{}".format(specs[St.mechanism])
        specs[St.justification_comment] = "We assume that entities with the same URI are identical."
        specs[St.linkset_comment] = "Linking <{}> to <{}> based on their identical URI using the mechanism: {}". \
            format(source[St.graph], target[St.graph], specs[St.mechanism])

    elif str(specs[St.mechanism]).lower() == "approxstrsim":
        specs[St.link_name] = "Approximate String Similarity"
        specs[St.link_subpropertyof] = "http://risis.eu/linkset/predicate/{}".format(specs[St.mechanism])
        specs[St.justification_comment] = "This includes entities with a string similarity in the interval [{} 1[.".\
            format(specs[St.threshold])
        specs[St.linkset_comment] = "Linking <{}> to <{}> based on their approximate string similarity" \
                                    " using the mechanism: {}". \
            format(source[St.graph], target[St.graph], specs[St.mechanism])

    elif str(specs[St.mechanism]).lower() == "nearbygeosim":
        specs[St.link_name] = "Near by Geo-Similarity"
        specs[St.link_subpropertyof] = "http://risis.eu/linkset/predicate/{}".format(specs[St.mechanism])
        specs[St.justification_comment] = "This includes entities near each other by at most {} <{}>.". \
            format(specs[St.unit_value], specs[St.unit_value])
        specs[St.linkset_comment] = "Linking <{}> to <{}> based on their nearby Geo-Similarity" \
                                    " using the mechanism: {}". \
            format(source[St.graph], target[St.graph], specs[St.mechanism])

    specs[St.triples] = Qry.get_namedgraph_size(specs[St.linkset], isdistinct=False)
    print "\t>>> {} CORRESPONDENCES INSERTED".format(specs[St.triples])

    query = "\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}" \
            "\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}" \
            "\n{}\n{}\n{}\n{}\n{}" \
            "\n{}\n{}\n{}" \
            "\n{}\n{}\n{}\n{}\n{}" \
            "\n{}\n{}\n{}\n{}\n{}". \
        format("##################################################################",
               "### METADATA FOR {}".format(specs[St.linkset]),
               "##################################################################",
               "PREFIX prov:        <{}>".format(Ns.prov),
               "PREFIX alivocab:    <{}>".format(Ns.alivocab),
               "PREFIX rdfs:        <{}>".format(Ns.rdfs),
               "PREFIX void:        <{}>".format(Ns.void),
               "PREFIX bdb:         <{}>".format(Ns.bdb),

               "INSERT",
               "{",
               "    <{}>".format(specs[St.linkset]),
               "        rdfs:label                  \"{}\" ; ".format(specs[St.linkset_name]),
               "        a                           void:Linkset ;",
               "        void:triples                {} ;".format(specs[St.triples]),
               "        alivocab:sameAsCount        {} ;".format(specs[St.sameAsCount]),
               "        alivocab:alignsMechanism    <{}{}> ;".format(Ns.mechanism, specs[St.mechanism]),
               "        void:subjectsTarget         <{}> ;".format(source[St.graph]),
               "        void:objectsTarget          <{}> ;".format(target[St.graph]),
               "        void:linkPredicate          <{}> ;".format(specs[St.link]),
               "        bdb:subjectsDatatype        <{}> ;".format(source[St.entity_datatype]),
               "        bdb:objectsDatatype         <{}> ;".format(target[St.entity_datatype]),
               "        alivocab:singletonGraph     <{}> ;".format(specs[St.singleton]),
               "        bdb:assertionMethod         <{}> ;".format(specs[St.assertion_method]),
               "        bdb:linksetJustification    <{}> ;{}".format(specs[St.justification], extra),
               "        alivocab:alignsSubjects     ?src_aligns ;",
               "        alivocab:alignsObjects      ?trg_aligns ;{}".format(cross_check_insert),
               "        rdfs:comment                \"\"\"{}\"\"\" .".format(specs[St.linkset_comment]),

               "\n    ### METADATA ABOUT THE LINKTYPE",
               "      <{}>".format(specs[St.link]),
               "        rdfs:comment                \"\"\"{}\"\"\" ;".format(specs[St.link_comment]),
               "        rdfs:label                  \"{} {}\" ;".format(specs[St.link_name], specs[St.sameAsCount]),
               "        rdfs:subPropertyOf          <{}> .".format(specs[St.link_subpropertyof]),

               "\n    ### METADATA ABOUT THE LINKSET JUSTIFICATION",
               "    <{}>".format(specs[St.justification]),
               "        rdfs:comment              \"\"\"{}\"\"\" .".format(specs[St.justification_comment]),

               "\n    ### ASSERTION METHOD",
               "    <{}>".format(specs[St.assertion_method]),
               "        alivocab:sparql           \"\"\"{}\"\"\" .".format(specs[St.insert_query]),
               "}",

               "WHERE",
               "{",
               "    BIND(iri({}) AS ?src_aligns)".format(src_aligns),
               "    BIND(iri({}) AS ?trg_aligns){}".format(trg_aligns, cross_check_where),
               "}")
    print query
    if display is True:
        print query
    return query


def linkset_refined_metadata(specs, display=False):

    # CONDITIONAL METADATA TO APPEND TO THE REFINED LINKSET

    extra = ""

    if St.extended_graph in specs[St.source] and len(specs[St.source][St.extended_graph]) > 0:
        extra += "\n        alivocab:subjectsExtended    <{}> ;".format(specs[St.source][St.extended_graph])

    if St.extended_graph in specs[St.target] and len(specs[St.target][St.extended_graph]) > 0:
        extra += "\n        alivocab:objectsExtended     <{}> ;".format(specs[St.target][St.extended_graph])

    if St.reducer in specs[St.source] and len(specs[St.source][St.reducer]) > 0:
        extra += "\n        alivocab:subjectsReducer     <{}> ;".format(specs[St.source][St.reducer])

    if St.reducer in specs[St.target] and len(specs[St.target][St.reducer]) > 0:
        extra += "\n        alivocab:objectsReducer      <{}> ;".format(specs[St.target][St.reducer])

    if St.intermediate_graph in specs and len(specs[St.intermediate_graph]) > 0:
        extra += "\n        alivocab:intermediatesTarget <{}> ;".format(specs[St.intermediate_graph])

    if St.threshold in specs and len(str(specs[St.threshold])) > 0:
        extra += "\n        alivocab:threshold           {} ;".format(str(specs[St.threshold]))

    if St.delta in specs and str(specs[St.delta]) != "0":
        converted = convert_to_float(str(specs[St.delta]))
        if math.isnan(converted) is False:
            extra += "\n        alivocab:delta               {} ;".format(converted)

    source = specs[St.source]
    target = specs[St.target]
    src_aligns = Ls.format_aligns(source[St.aligns])
    trg_aligns = Ls.format_aligns(target[St.aligns])

    specs[St.singleton] = "{}{}".format(Ns.singletons, specs[St.refined_name])
    specs[St.link] = "{}{}{}".format(Ns.alivocab, "exactStrSim", specs[St.sameAsCount])
    specs[St.assertion_method] = "{}{}".format(Ns.method, specs[St.refined_name])
    specs[St.justification] = "{}{}".format(Ns.justification, specs[St.refined_name])
    specs[St.link_comment] = "The predicate <{}> used in this linkset is a property that reflects an entity " \
                             "linking approach based on the <{}{}> mechanism.". \
        format(specs[St.link], Ns.mechanism, specs[St.mechanism])

    if str(specs[St.mechanism]).lower() == "exactstrsim":
        specs[St.link_name] = "Exact String Similarity"
        specs[St.link_subpropertyof] = "http://risis.eu/linkset/predicate/{}".format(specs[St.mechanism])
        specs[St.justification_comment] = "We assume that entities with the aligned predicates sharing the " \
                                          "exact same content are same. This assumption applies when dealing " \
                                          "with entities such as Organisation."
        specs[St.linkset_comment] = "Linking <{}> to <{}> by aligning {} with {} using the mechanism: {}". \
            format(source[St.graph], target[St.graph], src_aligns, trg_aligns, specs[St.mechanism])

    elif str(specs[St.mechanism]).lower() == "identity":
        specs[St.link_name] = "Same URI"
        specs[St.link_subpropertyof] = "http://risis.eu/linkset/predicate/{}".format(specs[St.mechanism])
        specs[St.justification_comment] = "We assume that entities with the same URI are identical."
        specs[St.linkset_comment] = "Linking <{}> to <{}> based on their identical URI using the mechanism: {}". \
            format(source[St.graph], target[St.graph], specs[St.mechanism])

    elif str(specs[St.mechanism]).lower() == "approxnbrsim":
        specs[St.link_name] = "Approximate Number Similarity"
        specs[St.link_subpropertyof] = "http://risis.eu/linkset/predicate/{}".format(specs[St.mechanism])
        specs[St.justification_comment] = "This includes entities with an approximate number similarity" \
                                          " in the interval [0 {}].".format(specs[St.delta])
        specs[St.linkset_comment] = "Linking <{}> to <{}> based on their approximate number similarity" \
                                    " using the mechanism: {}". \
            format(source[St.graph], target[St.graph], specs[St.mechanism])

    elif str(specs[St.mechanism]).lower() == "approxstrsim":
        specs[St.link_name] = "Approximate String Similarity"
        specs[St.link_subpropertyof] = "http://risis.eu/linkset/predicate/{}".format(specs[St.mechanism])
        specs[St.justification_comment] = "This includes entities with a string similarity in the interval [{} 1[.".\
            format(specs[St.threshold])
        specs[St.linkset_comment] = "Linking <{}> to <{}> based on their approximate string similarity" \
                                    " using the mechanism: {}". \
            format(source[St.graph], target[St.graph], specs[St.mechanism])

    elif str(specs[St.mechanism]).lower() == "intermediate":
        specs[St.link_name] = "Exact String Similarity"
        specs[St.link_subpropertyof] = "http://risis.eu/linkset/predicate/{}".format(specs[St.mechanism])
        specs[St.justification_comment] = "This is an implementation of the Exact String Similarity Mechanism over " \
                                          "the aligned predicates."
        specs[St.linkset_comment] = "Linking <{}> to <{}> by aligning {} with {} using the mechanism: {}". \
            format(source[St.graph], target[St.graph], src_aligns, trg_aligns, specs[St.mechanism])

    # CHECKING WHETHER THE REFINED HAS SOME TRIPLES INSERTED
    specs[St.triples] = Qry.get_namedgraph_size(specs[St.refined], isdistinct=False)

    triples = Qry.get_namedgraph_size(specs[St.linkset], isdistinct=False)
    print "\t>>> {} CORRESPONDENCES IN THE SOURCE".format(triples)
    print "\t>>> {} CORRESPONDENCES INSERTED".format(specs[St.triples])
    print "\t>>> {} CORRESPONDENCES DO NOT COMPLY WITH THE NEW CONDITION".format(
        str(int(triples) - int(specs[St.triples])))

    message = "{}<br/>{}<br/>{}".format(
        "{} CORRESPONDENCES IN THE SOURCE".format(triples),
        "{} CORRESPONDENCES INSERTED".format(specs[St.triples]),
        "{} CORRESPONDENCES DO NOT COMPLY WITH THE NEW CONDITION".format(str(int(triples) - int(specs[St.triples]))))

    if int(specs[St.triples]) > 0:
        derived_from = specs[St.derivedfrom] if St.derivedfrom in specs else ""
        intermediate = "\n        alivocab:intermediatesTarget    <{}> ;".format(specs[St.intermediate_graph]) \
            if str(specs[St.mechanism]).lower() == "intermediate" else ""

        query = "\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}" \
                "\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}" \
                "\n{}\n{}\n{}\n{}\n{}" \
                "\n{}\n{}\n{}" \
                "\n{}\n{}\n{}\n{}\n{}" \
                "\n{}\n{}\n{}\n{}\n{}". \
            format("##################################################################",
                   "### METADATA FOR {}".format(specs[St.refined]),
                   "##################################################################",
                   "PREFIX prov:        <{}>".format(Ns.prov),
                   "PREFIX alivocab:    <{}>".format(Ns.alivocab),
                   "PREFIX rdfs:        <{}>".format(Ns.rdfs),
                   "PREFIX void:        <{}>".format(Ns.void),
                   "PREFIX bdb:         <{}>".format(Ns.bdb),

                   "INSERT",
                   "{",
                   "    <{}>".format(specs[St.refined]),
                   "        a                               void:Linkset ;\n{}".format(derived_from),
                   "        rdfs:label                      \"{}\" ; ".format(specs[St.refined_name]),
                   "        void:triples                    {} ;".format(specs[St.triples]),
                   "        alivocab:sameAsCount            {} ;".format(specs[St.sameAsCount]),
                   "        alivocab:alignsMechanism        <{}{}> ;".format(Ns.mechanism, specs[St.mechanism]),
                   "        void:subjectsTarget             <{}> ;{}".format(source[St.graph], intermediate),
                   "        void:objectsTarget              <{}> ;".format(target[St.graph]),
                   "        void:linkPredicate              <{}> ;".format(specs[St.link]),
                   "        bdb:subjectsDatatype            <{}> ;".format(source[St.entity_datatype]),
                   "        bdb:objectsDatatype             <{}> ;".format(target[St.entity_datatype]),
                   "        alivocab:singletonGraph         <{}> ;".format(specs[St.singleton]),
                   "        bdb:assertionMethod             <{}> ;".format(specs[St.assertion_method]),
                   "        bdb:linksetJustification        <{}> ;{}".format(specs[St.justification], extra),
                   "        alivocab:alignsSubjects         ?src_aligns ;",
                   "        alivocab:alignsObjects          ?trg_aligns ;",
                   "        rdfs:comment                    \"\"\"{}\"\"\" .".format(specs[St.linkset_comment]),

                   "\n    ### METADATA ABOUT THE LINKTYPE",
                   "      <{}>".format(specs[St.link]),
                   "        rdfs:comment                \"\"\"{}\"\"\" ;".format(specs[St.link_comment]),
                   "        rdfs:label                  \"{} {}\" ;".format(specs[St.link_name], specs[St.sameAsCount]),
                   "        rdfs:subPropertyOf          <{}> .".format(specs[St.link_subpropertyof]),

                   "\n    ### METADATA ABOUT THE LINKSET JUSTIFICATION",
                   "    <{}>".format(specs[St.justification]),
                   "        rdfs:comment              \"\"\"{}\"\"\" .".format(specs[St.justification_comment]),

                   "\n    ### ASSERTION METHOD",
                   "    <{}>".format(specs[St.assertion_method]),
                   "        alivocab:sparql           \"\"\"{}\"\"\" .".format(specs[St.insert_query]),
                   "}",

                   "WHERE",
                   "{",
                   "    BIND(iri({}) AS ?src_aligns)".format(src_aligns),
                   "    BIND(iri({}) AS ?trg_aligns)".format(trg_aligns),
                   "}")

        if display is True:
            print query
        print "\t>>> Done generating the metadata"
        return {"query": query, "message": message}
    else:
        return {"query": None, "message": message}


def linkset_geo_metadata(specs, display=False):

    extra = ""
    if St.reducer in specs[St.source] and len(specs[St.source][St.reducer]) > 0:
        extra += "\n        ll:subjectsReducer      <{}> ;".format(specs[St.source][St.reducer])

    if St.reducer in specs[St.target] and len(specs[St.target][St.reducer]) > 0:
        extra += "\n        ll:objectsReducer       <{}> ;".format(specs[St.target][St.reducer])

    if St.intermediate_graph in specs and len(specs[St.intermediate_graph]) > 0:
        extra += "\n        ll:intermediate         <{}> ;".format(specs[St.intermediate_graph])

    if St.threshold in specs and len(str(specs[St.threshold])) > 0:
        extra += "\n        ll:threshold            {} ;".format(str(specs[St.threshold]))

    if St.delta in specs and len(str(specs[St.delta])) > 0:
        extra += "\n        ll:delta                {} ;".format(str(specs[St.delta]))

    source = specs[St.source]
    target = specs[St.target]

    src_cross_check = Ls.format_aligns(source[St.crossCheck])
    src_long = Ls.format_aligns(source[St.longitude])
    src_lat = Ls.format_aligns(source[St.latitude])

    trg_cross_check = Ls.format_aligns(target[St.crossCheck])
    trg_long = Ls.format_aligns(target[St.longitude])
    trg_lat = Ls.format_aligns(target[St.latitude])

    # specs[St.linkset] = "{}{}".format(Ns.linkset, specs[St.linkset_name])
    specs[St.singleton] = "{}{}".format(Ns.singletons, specs[St.linkset_name])
    specs[St.link] = "{}{}{}".format(Ns.alivocab, "exactStrSim", specs[St.sameAsCount])
    specs[St.assertion_method] = "{}{}".format(Ns.method, specs[St.linkset_name])
    specs[St.justification] = "{}{}".format(Ns.justification, specs[St.linkset_name])
    specs[St.link_comment] = "The predicate <{}> used in this linkset is a property that reflects an entity " \
                             "linking approach based on the <{}{}> mechanism.". \
        format(specs[St.link], Ns.mechanism, specs[St.mechanism])

    if str(specs[St.mechanism]).lower() == "nearbygeosim":
        specs[St.link_name] = "Near by Geo-Similarity"
        specs[St.link_subpropertyof] = "http://risis.eu/linkset/predicate/{}".format(specs[St.mechanism])
        specs[St.justification_comment] = "This includes entities near each other by at most {} <{}>.". \
            format(specs[St.unit_value], specs[St.unit])
        specs[St.linkset_comment] = "Linking <{}> to <{}> based on their nearby Geo-Similarity" \
                                    " using the mechanism: {}". \
            format(source[St.graph], target[St.graph], specs[St.mechanism])

    specs[St.triples] = Qry.get_namedgraph_size(specs[St.linkset], isdistinct=False)
    print "\t>>> {} CORRESPONDENCES INSERTED".format(specs[St.triples])

    query = "\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}" \
            "\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}" \
            "\n{}\n{}\n{}\n{}\n{}" \
            "\n{}\n{}\n{}" \
            "\n{}\n{}\n{}\n{}\n{}" \
            "\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}". \
        format("##################################################################",
               "### METADATA FOR {}".format(specs[St.linkset]),
               "##################################################################",
               "PREFIX prov:        <{}>".format(Ns.prov),
               "PREFIX ll:          <{}>".format(Ns.alivocab),
               "PREFIX rdfs:        <{}>".format(Ns.rdfs),
               "PREFIX void:        <{}>".format(Ns.void),
               "PREFIX bdb:         <{}>".format(Ns.bdb),

               "INSERT",
               "{",
               "    <{}>".format(specs[St.linkset]),
               "        rdfs:label                  \"{}\" ; ".format(specs[St.linkset_name]),
               "        a                           void:Linkset ;",
               "        void:triples                {} ;".format(specs[St.triples]),
               "        ll:sameAsCount              {} ;".format(specs[St.sameAsCount]),
               "        ll:alignsMechanism          <{}{}> ;".format(Ns.mechanism, specs[St.mechanism]),
               "        void:subjectsTarget         <{}> ;".format(source[St.graph]),
               "        void:objectsTarget          <{}> ;".format(target[St.graph]),
               "        void:linkPredicate          <{}> ;".format(specs[St.link]),
               "        bdb:subjectsDatatype        <{}> ;".format(source[St.entity_datatype]),
               "        bdb:objectsDatatype         <{}> ;".format(target[St.entity_datatype]),
               "        ll:singletonGraph           <{}> ;".format(specs[St.singleton]),
               "        bdb:assertionMethod         <{}> ;".format(specs[St.assertion_method]),
               "        bdb:linksetJustification    <{}> ;{}".format(specs[St.justification], extra),
               "        ll:crossCheckSubject        ?src_crossCheck ;",
               "        ll:crossCheckObject         ?trg_crossCheck ;",

               "        ll:unit                     <{}> ;".format(specs[St.unit]),
               "        ll:unitValue                {} ;".format(specs[St.unit_value]),

               "        ll:alignsSubjects           ( ?src_long ?src_lat ) ;",
               "        ll:alignsObjects            ( ?trg_long ?trg_lat ) ;",

               "        rdfs:comment                \"\"\"{}\"\"\" .".format(specs[St.linkset_comment]),

               "\n    ### METADATA ABOUT THE LINKTYPE",
               "      <{}>".format(specs[St.link]),
               "        rdfs:comment                \"\"\"{}\"\"\" ;".format(specs[St.link_comment]),
               "        rdfs:label                  \"{} {}\" ;".format(specs[St.link_name], specs[St.sameAsCount]),
               "        rdfs:subPropertyOf          <{}> .".format(specs[St.link_subpropertyof]),

               "\n    ### METADATA ABOUT THE LINKSET JUSTIFICATION",
               "    <{}>".format(specs[St.justification]),
               "        rdfs:comment              \"\"\"{}\"\"\" .".format(specs[St.justification_comment]),

               "\n    ### ASSERTION METHOD",
               "    <{}>".format(specs[St.assertion_method]),
               "        ll:sparql                   \"\"\"{}\"\"\" .".format(specs[St.insert_query]),
               "}",

               "WHERE",
               "{",
               "    BIND(iri({}) AS ?src_crossCheck)".format(src_cross_check),
               "    BIND(iri({}) AS ?trg_crossCheck)".format(trg_cross_check),

               "    BIND(iri({}) AS ?src_long)".format(src_long),
               "    BIND(iri({}) AS ?src_lat)".format(src_lat),

               "    BIND(iri({}) AS ?trg_long)".format(trg_long),
               "    BIND(iri({}) AS ?trg_lat)".format(trg_lat),

               "}")
    print query
    if display is True:
        print query
    return query


def spa_subset_metadata(specs):
    source = specs[St.source]
    target = specs[St.target]
    src_aligns = Ls.format_aligns(source[St.link_old])

     # cCROSS CHECK INFORMATION IS USED IN CASE THE ALIGN PROPERTY APPEARS MEANINGLESS
    src_cross_check = Ls.format_aligns(source[St.crossCheck]) if St.crossCheck in source else None
    trg_cross_check = Ls.format_aligns(target[St.crossCheck]) if St.crossCheck in target else None

    # CROSS CHECK FOR THE WHERE CLAUSE
    cross_check_where = ''
    cross_check_where += "\n    BIND(iri({}) AS ?src_crossCheck)".format(
        src_cross_check) if src_cross_check is not None else ''
    cross_check_where += "\n    BIND(iri({}) AS ?trg_crossCheck)".format(
        trg_cross_check) if trg_cross_check is not None else ''

    # CROSS CHECK FOR THE INSERT CLAUSE
    cross_check_insert = ''
    cross_check_insert += "\n        alivocab:crossCheckSubject        ?src_crossCheck ;" \
        if src_cross_check is not None else ''
    cross_check_insert += "\n        alivocab:crossCheckObject         ?trg_crossCheck ;" \
        if trg_cross_check is not None else ''

    metadata = "\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}" \
               "\n{}\n{}\n{}\n{}" \
               "\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}" \
               "\n{}\n{}\n{}\n{}\n{}\n{}" \
               "\n{}\n{}\n{}\n{}\n{}\n{}" \
               "\n{}\n{}\n{}\n{}". \
        format("\t###### METADATA",
               "\tPREFIX prov:        <{}>".format(Ns.prov),
               "\tPREFIX rdfs:      <{}>".format(Ns.rdfs),
               "\tPREFIX void:      <{}>".format(Ns.void),
               "\tPREFIX alivocab:  <{}>".format(Ns.alivocab),
               "\tPREFIX bdb:       <{}>".format(Ns.bdb),

               "\tINSERT",
               "\t{",
               "\t     ### [SUBSET of {}]".format(source[St.graph]),
               "\t     ### METADATA ABOUT THE SUBSET LINKSET",
               "\t     <{}>".format(specs[St.linkset]),
               "\t       a                         void:Linkset ;",
               "\t       rdfs:label                \"{}\" ; ".format(specs[St.linkset_name]),
               "\t       alivocab:alignsMechanism  <{}{}> ;".format(Ns.mechanism, specs[St.mechanism]),
               "\t       alivocab:sameAsCount      {} ;".format(specs[St.sameAsCount]),
               "\t       void:subset               <{}> ;".format(source[St.graph]),
               "\t       void:subjectsTarget       <{}> ;".format(source[St.graph]),
               "\t       void:objectsTarget        <{}> ;".format(target[St.graph]),
               "\t       void:triples              {} ;".format(specs[St.triples]),
               "\t       void:linkPredicate        <{}{}> ;".format(specs[St.link], specs[St.sameAsCount]),
               "\t       bdb:subjectsDatatype      <{}> ;".format(source[St.entity_datatype]),
               "\t       bdb:objectsDatatype       <{}> ;".format(target[St.entity_datatype]),
               "\t       alivocab:singletonGraph   <{}{}> ;".format(Ns.singletons, specs[St.linkset_name]),
               "\t       bdb:assertionMethod       <{}> ;".format(specs[St.assertion_method]),
               "\t       bdb:linksetJustification  <{}> ;".format(specs[St.justification]),
               "\t       alivocab:alignsSubjects   ?src_aligns ;",
               "\t       alivocab:alignsObjects   <{}> ;{}".format(Ns.rsrId, cross_check_insert),
               "\t       rdfs:comment              \"\"\"{}\"\"\" .".format(specs[St.linkset_comment]),

               "\n\t     ### METADATA ABOUT THE LINKSET JUSTIFICATION",
               "\t     <{}>".format(specs[St.justification]),
               "\t       rdfs:comment              \"\"\"{}\"\"\" .".format(specs[St.justification_comment]),
               "\n\t     ### METADATA ABOUT THE LINKTYPE",
               "\t     <{}{}>".format(specs[St.link], specs[St.sameAsCount]),
               "\t       rdfs:comment              \"\"\"{}\"\"\" ;".format(specs[St.link_comment]),
               "\t       rdfs:label                \"{} {}\" ;".format(specs[St.link_name], specs[St.sameAsCount]),
               "\t       rdfs:subPropertyOf        <{}> .".format(specs[St.link_subpropertyof]),

               "\n\t     ### ASSERTION METHOD",
               "\t     <{}>".format(specs[St.assertion_method]),
               "\t       alivocab:sparql           \"\"\"{}\"\"\" .".format(specs[St.insert_query]),
               "\t}",

               "\tWHERE",
               "\t{",
               "\t      BIND(iri({}) AS ?src_aligns){}".format(src_aligns, cross_check_where),
               "\t}"
               )
    # print metadata
    return metadata


def union_meta(specs):
    """
    :param specs: is of type dictionary.
    For this, it needs the following keys:
        lens_name: the name of this lens
        lens: the URI of the lens about to be created
        lens_target_triples: predicate object for each graph directly involved in the lens
        triples: The number of triples in this graph
        expectedTriples: Because of possible triple removal, this provides the sum of all correspondences
        from all direct target graphs
        removedDuplicates: The number of removed triples in case of duplicates
        insert_query: the insert query that let to the creation of the current lens.
    :return:
    """

    metadata = """
    ##################################################################
    ### METADATA
    ### for the lens: {0}
    ##################################################################
    PREFIX rdfs:        <{1}>
    PREFIX alivocab:    <{2}>
    PREFIX void:        <{3}>
    PREFIX bdb:         <{4}>
    PREFIX lensOp:      <{5}>
    PREFIX specific:    <{13}>

    INSERT DATA
    {{
        ### RESOURCE
        <{0}>
            a                                   bdb:Lens ;
            rdfs:label                          "{11}" ;
            alivocab:operator                   lensOp:union ;{6}
            void:triples                        {7} ;
            alivocab:expectedCorrespondences    {8} ;
            alivocab:removedDuplicates          {9} ;
            alivocab:singletonGraph             specific:{11} ;
            bdb:assertionMethod                 <{10}{11}> .
        ### ASSERTION METHOD"
        <{10}{11}>
            alivocab:sparql           \"\"\"{12}\"\"\" .
    }}""".format(specs[St.lens], Ns.rdfs, Ns.alivocab, Ns.void, Ns.bdb, Ns.lensOp,
                 specs[St.lens_target_triples], specs[St.triples], specs[St.expectedTriples],
                 specs[St.removedDuplicates], Ns.method, specs[St.lens_name],
                 specs[St.insert_query], Ns.singletons)

    # print metadata
    return metadata


def diff_meta(specs):
    """
    :param specs: is of type dictionary.
    For this, it needs the following keys:
        lens_name: the name of this lens
        lens: the URI of the lens about to be created
        lens_target_triples: predicate object for each graph directly involved in the lens
        triples: The number of triples in this graph
        expectedTriples: Because of possible triple removal, this provides the sum of all correspondences
        from all direct target graphs
        removedDuplicates: The number of removed triples in case of duplicates
        insert_query: the insert query that let to the creation of the current lens.
    :return:
    """

    specs[St.triples] = Qry.get_namedgraph_size(specs[St.lens], isdistinct=False)

    metadata = """
    ##################################################################
    ### METADATA
    ### for the lens: {0}
    ##################################################################
    PREFIX rdfs:        <{1}>
    PREFIX alivocab:    <{2}>
    PREFIX void:        <{3}>
    PREFIX bdb:         <{4}>
    PREFIX lensOp:      <{5}>
    PREFIX specific:    <{12}>

    INSERT DATA
    {{
        ### RESOURCE
        <{0}>
            a                                   bdb:Lens ;
            rdfs:label                          "{10}" ;
            alivocab:operator                   lensOp:difference ;
            void:triples                        {6} ;
            void:subjectsTarget                 <{7}> ;
            void:objectsTarget                  <{8}> ;
            alivocab:singletonGraph             specific:{10} ;
            bdb:assertionMethod                 <{9}{10}> .

        ### ASSERTION METHOD"
        <{9}{10}>
            alivocab:sparql           \"\"\"{11}\"\"\" .
    }}""".format(specs[St.lens], Ns.rdfs, Ns.alivocab, Ns.void, Ns.bdb, Ns.lensOp,
                 specs[St.triples], specs[St.subjectsTarget], specs[St.objectsTarget],
                 Ns.method, specs[St.lens_name], specs[St.insert_query], Ns.singletons)

    # print metadata
    return metadata


def convert_to_float(value):
    # print isinstance(u'\x30', numbers.Rational)
    try:
        return float(value)
    except Exception as err:
        print err
        return float("NaN")


# FUNCTION FOR TARGET DATATYPE AND PROPERTIES
def target_datatype_properties(model, label, linkset_label):

    main_tabs = "\t\t\t"
    tabs = "{}\t\t\t\t\t\t\t\t\t\t\t\t".format(main_tabs)
    # ALIGNMENT COMBINATION: LIST OD DICTIONARIES
    alignment_targets = ""
    property_list_bind = ""
    count = 0
    for item in model:
        count += 1
        target = item[St.graph]
        data = item[St.data]

        # LIST OF DICTIONARIES
        for n in range(0, len(data)):
            code = "llTarget:{}_{}".format(label, Ut.hash_it(target + str(data[n])))
            datatype = data[n][St.entity_datatype]
            properties = data[n][St.properties]
            property_list = ""

            # LIST OF PROPERTIES
            for i in range(0, len(properties)):
                i_property = properties[i] if Ut.is_nt_format(
                    properties[i]) else "<{}>".format(data[i][St.properties][i])
                property_list += "?property_{}_{}_{} ".format(count, n, i) if i == 0 \
                    else ",\n{}?property_{}_{}_{} ".format(tabs, count, n, i)

                if i == 0 and count == 1:
                    property_list_bind += """BIND( IRI("{}") AS ?property_{}_{}_{})""".format(i_property, count, n, i)
                else:
                    property_list_bind += """\n{}BIND( IRI("{}") AS ?property_{}_{}_{})""".format(
                        main_tabs, i_property, count, n, i)

            triples = """
    {5}linkset:{4}  ll:hasAlignmentTarget  {0} .
    {5}{0}  ll:hasTarget    <{1}> .
    {5}{0}  ll:hasDatatype  <{2}> .
    {5}{0}  ll:aligns       {3}.
    """ .format(code, target, datatype, property_list, linkset_label, main_tabs)
            # print triples
            alignment_targets += triples

    return {"list": alignment_targets, "binds": property_list_bind}


def cluster_2_linkset_metadata(specs):
    # METADATA
    # A TARGET COMBINES A DATATYPE AND A LIST OF PROPERTIES
    alignment_targets = target_datatype_properties(specs[St.targets], "alignmentTarget", specs[St.linkset_name])
    query = """
        # CREATION OF A LINKSET OF MIXED-RESOURCES
        PREFIX ll:          <{0}>
        PREFIX void:        <{1}>
        PREFIX rdfs:        <{2}>
        PREFIX bdb:         <{3}>
        PREFIX prov:        <{4}>
        PREFIX singleton:   <{5}>
        prefix linkset:     <{6}>
        PREFIX llTarget:    <{7}>
        prefix stardog:     <tag:stardog:api:context:>
        INSERT
        {{
            # GENERIC METADATA

            linkset:{8}
                rdfs:label                  "{8}" ;
                a                           void:Linkset ;
                ll:alignsMechanism          <{9}exact> .
            {10}
        }}
        WHERE
        {{
            {11}
        }}
    """.format(Ns.alivocab, Ns.void, Ns.rdfs, Ns.bdb, Ns.prov, Ns.singletons, Ns.linkset, Ns.alignmentTarget,
               # 8                      9            10                       11
               specs[St.linkset_name], Ns.mechanism, alignment_targets["list"], alignment_targets["binds"])

    specs["metadata"] = query
    Qry.boolean_endpoint_response(query)
