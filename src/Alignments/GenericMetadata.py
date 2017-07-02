import NameSpace as Ns
import Settings as St
import Query as Qry
import Linksets.Linkset as Ls


def linkset_metadata(specs, display=False):
    source = specs[St.source]
    target = specs[St.target]

    src_aligns = Ls.format_aligns(source[St.aligns])
    trg_aligns = Ls.format_aligns(target[St.aligns])

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
               "        bdb:linksetJustification    <{}> ;".format(specs[St.justification]),
               "        alivocab:alignsSubjects     ?src_aligns ;",
               "        alivocab:alignsObjects      ?trg_aligns ;",
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
               "    BIND(iri({}) AS ?trg_aligns)".format(trg_aligns),
               "}")
    # print query
    if display is True:
        print query
    return query


def spa_subset_metadata(specs):
    source = specs[St.source]
    target = specs[St.target]
    src_aligns = Ls.format_aligns(source[St.link_old])

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
               "\t       alivocab:alignsObjects   <{}> ;".format(Ns.rsrId),
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
               "\t      BIND(iri({}) AS ?src_aligns)".format(src_aligns),
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
            bdb:assertionMethod                 <{10}{11}> .
        ### ASSERTION METHOD"
        <{12}{13}>
            alivocab:sparql           \"\"\"{14}\"\"\" .
    }}""".format(specs[St.lens], Ns.rdfs, Ns.alivocab, Ns.void, Ns.bdb, Ns.lensOp,
                 specs[St.lens_target_triples], specs[St.triples], specs[St.expectedTriples],
                 specs[St.removedDuplicates], Ns.method, specs[St.lens_name],
                 Ns.method, specs[St.lens_name], specs[St.insert_query])

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
            bdb:assertionMethod                 <{9}{10}> .

        ### ASSERTION METHOD"
        <{9}{10}>
            alivocab:sparql           \"\"\"{11}\"\"\" .
    }}""".format(specs[St.lens], Ns.rdfs, Ns.alivocab, Ns.void, Ns.bdb, Ns.lensOp,
                 specs[St.triples], specs[St.subjectsTarget], specs[St.objectsTarget],
                 Ns.method, specs[St.lens_name], specs[St.insert_query])

    # print metadata
    return metadata


def linkset_refined_metadata(specs, display=False):

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
        "{} CORRESPONDENCES DO NOT COMPLY WITH THE NEW CONDITION".format(
            str(int(triples) - int(specs[St.triples]))
        )
    )

    if int(specs[St.triples] ) > 0:
        derived_from = specs[St.derivedfrom] if St.derivedfrom in specs else ""
        intermediate = "        alivocab:intermediatesTarget    <{}> ;".format(specs[St.intermediate_graph]) \
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
                   "        void:subjectsTarget             <{}> ;\n{}".format(source[St.graph], intermediate),
                   "        void:objectsTarget              <{}> ;".format(target[St.graph]),
                   "        void:linkPredicate              <{}> ;".format(specs[St.link]),
                   "        bdb:subjectsDatatype            <{}> ;".format(source[St.entity_datatype]),
                   "        bdb:objectsDatatype             <{}> ;".format(target[St.entity_datatype]),
                   "        alivocab:singletonGraph         <{}> ;".format(specs[St.singleton]),
                   "        bdb:assertionMethod             <{}> ;".format(specs[St.assertion_method]),
                   "        bdb:linksetJustification        <{}> ;".format(specs[St.justification]),
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

        return {"query": query, "message": message}
    else:
        return {"query": None, "message": message}
