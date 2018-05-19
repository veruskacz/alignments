import Alignments.Settings as St
import Alignments.UserActivities.UserRQ as Urq
from Alignments.Linksets.SPA_LinksetRefine import refine
from Alignments.Linksets.SPA_LinksetSubset import specification_2_linkset_subset
from Alignments.Linksets.SPA_Linkset import specs_2_linkset, specs_2_linkset_intermediate  # , specs_2_linkset_id

""" CREATED 6 LINKSETS BASED ON THE SPECIFICATIONS BELLOW

     1 - http://risis.eu/activity/idea_algmt_d1a022
        subjectsTarget   :	http://mytest.org/dbpedia-en
        objectsTarget    :	http://mytest.org/dbpedia-nl
        subjectsDatatype :	http://dbpedia.org/ontology/Artist
        objectsDatatype  :	http://dbpedia.org/ontology/Artist
        alignsSubjects   :	http://dbpedia.org/property/name
        alignsObjects    :	http://nl.dbpedia.org/property/naam
        >>> used         : 	http://risis.eu/linkset/en_nl_intermediate_name_P1910125924 | 3 correspondences found
        >>> created      : 	http://risis.eu/linkset/en_nl_exactStrSim_name_N467336337 | 1 correspondences found

     2 - http://risis.eu/activity/idea_algmt_b9870c
        subjectsTarget   :	http://mytest.org/dbpedia-en
        objectsTarget    :	http://mytest.org/dbpedia-nl
        subjectsDatatype :	http://dbpedia.org/ontology/Artwork
        objectsDatatype  :	http://schema.org/Painting
        alignsSubjects   :	http://www.w3.org/2000/01/rdf-schema#label
        alignsObjects    :	http://www.w3.org/2000/01/rdf-schema#label
        >>> used         : 	http://risis.eu/linkset/en_nl_exactStrSim_label_P916744941 | 27 correspondences found

     3 - http://risis.eu/activity/idea_algmt_d7fc6a
        subjectsTarget   :	http://mytest.org/dbpedia-en
        objectsTarget    :	http://mytest.org/dbpedia-en
        subjectsDatatype :	http://dbpedia.org/ontology/Artwork
        objectsDatatype  :	http://dbpedia.org/ontology/Artist
        alignsSubjects   :	http://dbpedia.org/ontology/author
        alignsObjects    :	http://risis.eu/alignment/predicate/resourceIdentifier
        >>> created      : 	http://risis.eu/linkset/subset_en_en_unknown_author_P954196570 | 61 correspondences found

     4 - http://risis.eu/activity/idea_algmt_9c5b05
        subjectsTarget   :	http://mytest.org/dbpedia-nl
        objectsTarget    :	http://mytest.org/dbpedia-nl
        subjectsDatatype :	http://schema.org/Painting
        objectsDatatype  :	http://dbpedia.org/ontology/Artist
        alignsSubjects   :	http://dbpedia.org/ontology/painter
        alignsObjects    :	http://risis.eu/alignment/predicate/resourceIdentifier
        >>> created      : 	http://risis.eu/linkset/subset_nl_nl_unknown_painter_P946887441 | 73 correspondences found

     5 - http://risis.eu/activity/idea_algmt_cb1476
        subjectsTarget   :	http://mytest.org/dbpedia-en
        objectsTarget    :	http://mytest.org/dbpedia-nl
        subjectsDatatype :	http://dbpedia.org/ontology/Artwork
        objectsDatatype  :	http://schema.org/Painting
        alignsSubjects   :	<http://dbpedia.org/ontology/author>/<http://dbpedia.org/property/name>
        alignsObjects    :	<http://dbpedia.org/ontology/painter>/<http://nl.dbpedia.org/property/naam>
        >>> used         : 	http://risis.eu/linkset/refined_en_nl_exactStrSim_label_P916744941_intermediate_author_name | 27 correspondences found
        >>> used         : 	http://risis.eu/linkset/en_nl_exactStrSim_author_name_P435378798 | 4380 correspondences found
        evolution        :	;
    [Subjects=<http://www.w3.org/2000/01/rdf-schema#label> | Objects=<http://www.w3.org/2000/01/rdf-schema#label> | Mechanism=<http://risis.eu/mechanism/exactStrSim>]

     6 - http://risis.eu/activity/idea_algmt_a2602a
        subjectsTarget   :	http://mytest.org/dbpedia-en
        objectsTarget    :	http://mytest.org/dbpedia-nl
        subjectsDatatype :	http://dbpedia.org/ontology/Artwork
        objectsDatatype  :	http://schema.org/Painting
        alignsSubjects   :	<http://dbpedia.org/ontology/author>/<http://www.w3.org/2000/01/rdf-schema#label>
        alignsObjects    :	<http://dbpedia.org/ontology/painter>/<http://nl.dbpedia.org/property/naam>
        >>> created      : 	http://risis.eu/linkset/en_nl_exactStrSim_author_label_P566692296 | 4380 correspondences found
"""

################################################################################################
""" RESEARCH QUESTIONS: 1 - What paintings did Rembrandt paint? """
################################################################################################
exact_mechanism = "exactStrSim"
identity_mechanism = "identity"
subset_mechanism = "unknown"
intermediate_exact_mechanism = "intermediate"
dataset_nl = "http://mytest.org/dbpedia-nl"
dataset_en = "http://mytest.org/dbpedia-en"
dataset_intermediate = "http://mytest.org/viaf"
artwork = "http://dbpedia.org/ontology/Artwork"
artist = "http://dbpedia.org/ontology/Artist"
painting = "http://schema.org/Painting"

""" 1: COMPOSE YOUR DATASETS of INTEREST """

dbpEnArtist = {
    St.graph: dataset_en,
    St.entity_datatype: artist,
    St.aligns: "http://dbpedia.org/property/name"}

dbpNlArtist = {
    St.graph: dataset_nl,
    St.entity_datatype: artist,
    St.aligns: "http://nl.dbpedia.org/property/naam"}

dbpEnArtwork = {
    St.graph: dataset_en,
    St.entity_datatype: artwork,
    St.aligns: "http://www.w3.org/2000/01/rdf-schema#label"}

dbpNlPainting = {
    St.graph: dataset_nl,
    St.entity_datatype: painting,
    St.aligns: "http://www.w3.org/2000/01/rdf-schema#label"}

dbpEnSub_Artwork2Artist_scr = {
        St.graph: dataset_en,
        St.entity_datatype: "http://dbpedia.org/ontology/Artwork",
        St.link_old: "http://dbpedia.org/ontology/author"}

dbpEnSub_Artwork2Artist_trg = {
        St.graph:  dataset_en,
        St.entity_datatype: artist}

dbpNlSub_Painting2Artist_scr = {
        St.graph: dataset_nl,
        St.entity_datatype: painting,
        St.link_old: "http://dbpedia.org/ontology/painter"}

dbpNlSub_Painting2Artist_trg = {
        St.graph:  dataset_nl,
        St.entity_datatype: artist}

dbpEnArtwork_ProPath = {
    St.graph: dataset_en,
    St.entity_datatype: artwork,
    St.aligns: "<http://dbpedia.org/ontology/author>/<http://dbpedia.org/property/name>"}

dbpNlPainting_ProPath = {
    St.graph: dataset_nl,
    St.entity_datatype: painting,
    St.aligns: "<http://dbpedia.org/ontology/painter>/<http://nl.dbpedia.org/property/naam>"}

dbpEnArtwork_ProPath_2 = {
    St.graph: dataset_en,
    St.entity_datatype: artwork,
    St.aligns: "<http://dbpedia.org/ontology/author>/<http://www.w3.org/2000/01/rdf-schema#label>"}


################################################################################################
""" 1: REGISTER YOUR RESEARCH QUESTION """
################################################################################################
question = "1 - What paintings did Rembrandt paint?"
research_qst = Urq.register_research_question(question)
research_uri = research_qst[St.result]
# research_uri = "http://risis.eu/activity/idea_030dae]"


################################################################################################
""" 2: REGISTER A DATASET MAPPING: A PAIR OF [DATASET|ENTITY TYPE] """
################################################################################################
ds_mapping = {
    "http://mytest.org/dbpedia-en": ["http://dbpedia.org/ontology/Artist", "http://dbpedia.org/ontology/Artwork"],
    "http://mytest.org/dbpedia-nl": ["http://dbpedia.org/ontology/Artist", "http://schema.org/Painting"]}
Urq.register_dataset_mapping(question_uri=research_uri, mapping=ds_mapping, activated=False)


################################################################################################
""" SPECS FOR GENERATING STANDARD LINKSETS """
################################################################################################

# SPECS FOR LINKING [ARTISTS] IN BDP ENGLISH TO THOSE IN DBP NETHERLANDS
ls_specs_1 = {
    St.researchQ_URI: research_uri,
    St.source: dbpEnArtist,
    St.target: dbpNlArtist,
    St.mechanism: exact_mechanism}

print "\n\n>>> LINKSET 1: LINKING [ARTIST] IN BDP ENGLISH TO [ARTIST] IN DBP NETHERLANDS "
linkset_1 = specs_2_linkset(ls_specs_1, display=False, activated=False)
# print "RESULT:", linkset_1
# linkset_1 = ""
# alignment_1 = ""

# SPECS FOR LINKING [ARTWORK] IN BDP ENGLISH TO [PAINTING] IN DBP NETHERLANDS
ls_specs_2 = {
    St.researchQ_URI: research_uri,
    St.source: dbpEnArtwork,
    St.target: dbpNlPainting,
    St.mechanism: exact_mechanism}


print "\n\n>>> LINKSET 2: LINKING [ARTWORK] IN BDP ENGLISH TO [PAINTING] IN DBP NETHERLANDS "
linkset_2 = specs_2_linkset(ls_specs_2, display=False, activated=True)
# linkset_2 = ""
# alignment_2 = ""

################################################################################################
""" SPECS FOR GENERATING A REFINED LINKSETS WITH PROPERTY PATH """
################################################################################################

ls_refined_specs = {

    St.researchQ_URI: research_uri,

    St.mechanism: intermediate_exact_mechanism,

    # THE LINKSET 2 NEEDS TO BE ACTIVATED FOR THIS
    St.linkset: linkset_2[St.result],

    St.intermediate_graph: dataset_intermediate,

    St.source: {
        St.graph: dataset_en,
        St.entity_datatype: artwork,
        St.aligns: "<http://dbpedia.org/ontology/author>/<http://dbpedia.org/property/name>"
    },

    St.target: {
        St.graph: dataset_nl,
        St.entity_datatype: painting,
        St.aligns: "<http://dbpedia.org/ontology/painter>/<http://nl.dbpedia.org/property/naam>"
    }
}

print "\n\n>>> LINKSET 3: REFINING LINKSET 1"
linkset_3 = refine(ls_refined_specs, exact=False, exact_intermediate=True, activated=True)
# linkset_3 = ""
# alignment_3 = ""


################################################################################################
""" SPECS FOR GENERATING STANDARD LINKSETS WITH INTERMEDIATE DATASET """
################################################################################################

# SPECS FOR LINKING [ARTISTS] IN BDP ENGLISH TO THOSE IN DBP NETHERLANDS
ls_specs_4 = {
    St.researchQ_URI: research_uri,
    St.source: dbpEnArtist,
    St.target: dbpNlArtist,
    St.intermediate_graph: dataset_intermediate,
    St.mechanism: intermediate_exact_mechanism}

print "\n\n>>> LINKSET 4: LINKING [ARTWORK] IN BDP ENGLISH TO [PAINTING] IN DBP NETHERLANDS "
linkset_4 = specs_2_linkset_intermediate(ls_specs_4, display=False, activated=False)
# linkset_4 = ""
# alignment_4 = ""


################################################################################################
""" SPECS FOR GENERATING STANDARD LINKSETS WITH PROPERTY PATH """
################################################################################################

# SPECS FOR LINKING [ARTWORK] IN BDP ENGLISH TO [PAINTING] IN DBP NETHERLANDS
ls_specs_5 = {
    St.researchQ_URI: research_uri,
    St.source: dbpEnArtwork_ProPath,
    St.target: dbpNlPainting_ProPath,
    St.mechanism: exact_mechanism}

# SPECS FOR LINKING [ARTWORK] IN BDP ENGLISH TO [PAINTING] IN DBP NETHERLANDS
ls_specs_6 = {
    St.researchQ_URI: research_uri,
    St.source: dbpEnArtwork_ProPath_2,
    St.target: dbpNlPainting_ProPath,
    St.mechanism: exact_mechanism}

print "\n\n>>> LINKSET 5: LINKING [ARTWORK] IN BDP ENGLISH TO [PAINTING] IN DBP NETHERLANDS "
linkset_5 = specs_2_linkset(ls_specs_5, display=False, activated=False)
# linkset_5 = "http://risis.eu/linkset/en_nl_exactStrSim_author_name_P435378798"
# alignment_5 = "http://risis.eu/activity/idea_algmt_b9870c"

print "\n\n>>> LINKSET 6: LINKING [ARTWORK] IN BDP ENGLISH TO [PAINTING] IN DBP NETHERLANDS "
linkset_6 = specs_2_linkset(ls_specs_6, display=False, activated=False)
# linkset_6 = "http://risis.eu/linkset/en_nl_exactStrSim_author_label_P566692296"
# alignment_6 = "http://risis.eu/activity/idea_algmt_a2602a"

################################################################################################
""" SPECS FOR GENERATING SUBSET LINKSETS """
################################################################################################

# SPECS FOR LINKING [ARTWORK] TO [ARTIST] WITHIN [THE SAME DATABASE] BDP ENGLISH
ls_sub_specs_1 = {
    St.researchQ_URI: research_uri,
    St.source: dbpEnSub_Artwork2Artist_scr,
    St.target: dbpEnSub_Artwork2Artist_trg,
    St.mechanism: subset_mechanism}

print "\n\n>>> LINKSET 7: LINKING [ARTWORK] TO [ARTIST] WITHIN [THE SAME DATABASE] BDP ENGLISH "
linkset_subset_1 = specification_2_linkset_subset(ls_sub_specs_1, activated=True)
# linkset_subset_1 = "http://risis.eu/linkset/subset_en_en_unknown_author_P954196570"
# alignment_subset_1 = "http://risis.eu/activity/idea_algmt_d7fc6a"

# SPECS FOR LINKING [PAINTING] TO [ARTIST] WITHIN [THE SAME DATABASE] BDP netherlands
ls_sub_specs_2 = {
    St.researchQ_URI: research_uri,
    St.source: dbpNlSub_Painting2Artist_scr,
    St.target: dbpNlSub_Painting2Artist_trg,
    St.mechanism: subset_mechanism}

print "\n\n>>> LINKSET 8: LINKING [PAINTING] TO [ARTIST] WITHIN [THE SAME DATABASE] BDP NETHERLANDS "
linkset_subset_2 = specification_2_linkset_subset(ls_sub_specs_2, activated=True)
# linkset_subset_2 = "http://risis.eu/linkset/subset_nl_nl_unknown_painter_P946887441"
# alignment_subset_2 = "http://risis.eu/activity/idea_algmt_9c5b05"
exit(0)
