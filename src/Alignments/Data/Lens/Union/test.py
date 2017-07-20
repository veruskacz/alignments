import NameSpace as Ns
import Settings as St

mechanism_1 = "exactStrSim"
mechanism_2 = "unknown"
dt_base = "risis"
host = "localhost:5820"

################################################################################################
################################################################################################
# """ STEP 4: LENS (1) as a VIEW
#         UNION
#             Linksets 1
#             Linksets 2
#             Linksets 3
# """
#
# """ DEFINE LENS SPECIFICATION """
# context_code = "1"
# label_1 = "union_grid_orgref_C{}_TEST".format(context_code)
# lens_specification_1 = {
#     St.lens_name: label_1,
#     St.lens: "{}{}".format(Ns.lens, label_1),
#     St.datasets: ["{}test1_grid_orgref".format(Ns.linkset),
#                   "{}test1_orgref_grid".format(Ns.linkset)],
#     St.context_code: context_code,
#     St.lens_operation: Ns.lensOpu
# }
# lens_1 = union(lens_specification_1, dt_base, host, activated=True)
#
#
# """ DEFINE LENS SPECIFICATION """
# context_code = "1"
# label_1 = "TEST_view".format(context_code)
# lens_specification_2 = {
#     St.lens_name: label_1,
#     St.lens: "{}{}".format(Ns.lens, label_1),
#     St.datasets: ["http://risis.eu/lens/union_grid_orgref_C1_TEST"],
#     St.context_code: context_code,
#     St.lens_operation: Ns.lensOpu
# }
#
#
# """ STEP 5: DESIGN VIEW """
# pro_1 = {
#     St.graph: "http://risis.eu/dataset/grid",
#     St.properties: ["http://risis.eu/grid/ontology/predicate/links",
#                     "http://risis.eu/grid/ontology/predicate/city",
#                     "http://risis.eu/grid/ontology/predicate/country",
#                     "http://risis.eu/grid/ontology/predicate/name"]
# }
#
# pro_2 = {
#         St.graph: "http://risis.eu/dataset/orgref",
#         St.properties: ["http://risis.eu/orgref/ontology/predicate/Wikipedia",
#                         "http://risis.eu/orgref/ontology/predicate/Level"]
#
# }
# design_view = [pro_1, pro_2]
#
# """ STEP 6: EXECUTE VIEW """
# result = Lens_Intersection.view(design_view, lens_specification_2, dt_base, host)





# Lens_Intersection.intersection(lens_specification_1, dt_base, host)
# "http://risis.eu/linkset/subset_grid_orgref_C1_unknown",
# "http://risis.eu/linkset/subset_orgref_grid_C1_unknown",

""" EXECUTE A LENS BY UNION SPECIFICATIONS """

#



####################################################################
""" DROPPING LENS NAME-GRAPHS                                    """
####################################################################
# drop_lens(dt_base, host, display=False, is_activated=False)
# drop_subset(dt_base, host, display=False, activated=True)
# schema_alignment_2_spa_linkset(schema_alignment_1, "099", dt_base, host, display=False, activated=False)
# schema_alignment_2_spa_linkset_subset(schema_alignment_2, dt_base, host, activated=False)





# cur_activity = {
#     St.research_Q: research,
#     St.entity_ofInterest: entity_types,
#     St.linkset_alignments: [ls_specs_1, ls_specs_2],
#     St.lens_actions: [lens_specs_1, lens_specs_2]
# }

#     view = """        {:>10}  {:70} {}
#     {:>10}: {:70} {}
#     {:>10}  {:70} {}
#     {:>10}: {:70} {}
#     {:>10}  {:70} {}
#     {:>10}: {:70} {}
#     {:>10}  {:70} {}
# """.format("", "SOURCE", "TARGET",
#            "Graph", source[St.graph_name], target[St.graph_name],
#            "", source[St.graph], target[St.graph],
#            "Type", source[St.entity_name],target[St.entity_name],
#            "", source[St.entity_datatype], target[St.entity_datatype],
#            "Predicate", source[St.aligns_name], target[St.aligns_name],
#            "", source[St.aligns], target[St.aligns]
#            )


# schema_alignment_2_spa_linkset(schema_alignment_1, "077", dt_base, host, display=False, activated=True)
# schema_alignment_2_spa_linkset(schema_alignment_2, "088", dt_base, host, display=False, activated=True)


def view_alignments(alignments):

    linksets = ""
    count = 0
    for alignment in alignments:
        count += 1
        source = alignment[St.source]
        target = alignment[St.target]
        linkset = "{}_{}_C{}_{}".format(source[St.graph_name], target[St.graph_name],
                                        alignment[St.context_code], alignment[St.mechanism])

        source_view = """      ALIGNMENT {}: LINKSET {}
        SOURCE
            Graph       : {} <{}>
            Type        : {} <{}>
            Predicate   : {} <{}>""".format(count, linkset, source[St.graph_name], source[St.graph],
                                            source[St.entity_name], source[St.entity_datatype],
                                            source[St.aligns_name], source[St.aligns])

        target_view = """
        Target
            Graph       : {} <{}>
            Type        : {} <{}>
            Predicate   : {} <{}>""".format(target[St.graph_name], target[St.graph],
                                            target[St.entity_name], target[St.entity_datatype],
                                            target[St.aligns_name], target[St.aligns])

        linksets += source_view
        linksets += target_view + "\n"
    return linksets


def display_activity(activity):

    # RESEARCH QUESTION
    rq = """
    RESEARCH QUESTION
        {}\n""".format(activity[St.research_Q])

    # LINKSETS from alignments
    linksets = view_alignments(activity[St.linkset_alignments])

    # LENS
    lenses = "\tLens"
    for lens in activity[St.lens_actions]:

        if lens[St.lens_operation] == Ns.lensOpu:
            lenses += "\n\tWE ARE OPERATING A UNIION ON THE FOLLOWING GRAPHS\n"
            lenses += view_alignments(lens[St.alignments])
        if lens[St.lens_operation] == Ns.lensOpi:
            lenses += "\n\tWE ARE OPERATING AN INTERSECTION ON THE FOLLOWING GRAPHS\n"
            lenses += lens[St.lens_operation]

    print rq
    print linksets
    print lenses


# display_activity(cur_activity)