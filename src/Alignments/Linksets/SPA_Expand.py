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
from Alignments.SimilarityAlgo.ApproximateSim import prefixed_inverted_index


def first():
    c = 1
    """
    THE TRICK HERE IS IN TWO FORDS

    LINKSET-1 LINKS ENTITIES OF DATASET-1 TO THOSE OF DATASET-2
    IN OTHER SCENARIOS, WE RUN ONLY ONCE MATCHING ALGORITHM.
    THE TRICK HERE, IS THAT WE WILL HAVE TO RUN THE ALGORITHM TWICE
        ON THE SOURCE, WE RUN A

    1. RELIES ON ADDING A RETHE DOWNLOAD
    2. RELIES ON RUNNING THE ALGORITHM TWICE
    """


def load_temp_query(specs, is_source, is_expand=True):

    # UPDATE THE SPECS OF SOURCE AND TARGETS
    if is_expand is False:
        comment_exp = "# "
    else:
        comment_exp = ""

    if is_source is True:
        info = specs[St.source]
        load = "_{}_1".format(specs[St.linkset_name])
        linkset_triple = "\t\t\t?{}  ?predicate ?target".format(info[St.graph_name])
    else:
        info = specs[St.target]
        load = "_{}_2".format(specs[St.linkset_name])
        linkset_triple = "\t\t\t?source  ?predicate ?{}".format(info[St.graph_name])

    # REPLACE RDF TYPE "a" IN CASE ANOTHER TYPE IS PROVIDED
    if St.rdf_predicate in info and info[St.rdf_predicate] is not None:
        rdf_pred = info[St.rdf_predicate] \
            if Ls.nt_format(info[St.rdf_predicate]) else "<{}>".format(info[St.rdf_predicate])
    else:
        rdf_pred = "a"

    # FORMATTING THE ALIGNS PROPERTY
    aligns = info[St.aligns] \
        if Ls.nt_format(info[St.aligns]) else "<{}>".format(info[St.aligns])

    name = info[St.graph_name]
    uri = info[St.graph]

    # ADD THE REDUCER IF SET
    if St.reducer not in info:
        reducer_comment = "#"
        reducer = ""
    else:
        reducer_comment = ""
        reducer = info[St.reducer]

    # EXTRACTION QUERY
    query = """
    INSERT
    {{
        GRAPH <{0}load{8}>
        {{
            ?{5}  alivocab:hasProperty  ?trimmed .
        }}
    }}
    WHERE
    {{

        # THE LINKSET TO EXPAND
        {12}GRAPH <{9}{10}>
        {12}{{
        {12}    {11} .
        {12}}}

        GRAPH <{1}>
        {{
            # RESOURCE IS OF A CERTAIN TYPE
            ?{5}  {2}  <{7}> .

            # EXTRACT THE PROPERTY-VALUE TO ALIGN
            ?{5}  {3}  ?object .

            # LOWER CASE OF THE VALUE
            BIND(lcase(str(?object)) as ?label)

            # VALUE TRIMMING
            BIND('^\\\\s+(.*?)\\\\s*$|^(.*?)\\\\s+$' AS ?regexp)
            BIND(REPLACE(?label, ?regexp, '$1$2') AS ?trimmed)
        }}

        {6}FILTER NOT EXISTS
        {6}{{
        {6}    GRAPH <{4}>
        {6}    {{
        {6}        {{ ?{5}   ?pred   ?obj . }}
        {6}        UNION
        {6}        {{ ?obj   ?pred   ?{5}. }}
        {6}    }}
        {6}}}
    }}
    """.format(
        # 0          1    2         3       4 `      5     6                7                         8
        Ns.tmpgraph, uri, rdf_pred, aligns, reducer, name, reducer_comment, info[St.entity_datatype], load,
        # 9         10                        11             12
        Ns.linkset, specs[St.expanded_name], linkset_triple, comment_exp
    )
    return query


def expand_approx(specs, theta, stop_words_string, stop_symbols_string, linkset2expand, reorder=True):

    data = None
    inserted_1 = 0
    inserted_2 = 0
    total = 0
    count= 0
    abort = False
    for is_source in [True, False]:

        count += 1
        print Ut.headings("********* PASS {} *********").format(count)

        # if is_source is False:
        #     specs[St.corr_reducer] = data[St.result]
            # print data[St.result]

        data = prefixed_inverted_index( specs, theta=theta, reorder=reorder, stop_words_string=stop_words_string,
                             stop_symbols_string=stop_symbols_string, expands=True, is_source=is_source,
                             linkset2expand=linkset2expand, check_file=False)

        if count == 1:
            inserted_1 += data['inserted']
            total += inserted_1

        else:
            inserted_2 += data['inserted']
            total += inserted_2

        if data[St.message].__contains__('ALREADY EXISTS'):
            abort = True
            print "\n>>> THE PROCESS IS BEING ABORTED AS THE FIRST " \
                  "PASS REVEALS THE EXISTENCE OF AN EXPANSION OF THE GRAPH."
            break

    if abort is False:
        # REMOVE DUPLICATES
        print "REMOVING REPETITION"
        if data is not None and data[St.result] is not None:
            print "\t", Qry.remove_repetition_same_direction(data[St.result])

        # PRINT THE FINAL TRIPLE COUNT
        final_inserted = Qry.get_triples_count(data[St.result])
        if final_inserted is None:
            final_inserted = 0
        else:
            final_inserted = int(final_inserted)
        print "\nOVERALL STATS:\n\tCORRESPONDENCES DISCOVERED AT PASS 1   : {}\n\tCORRESPONDENCES DISCOVERED AT PASS 2   : {}".format(
            inserted_1, inserted_2)
        print "\tOVERALL CORRESPONDENCES DISCOVERED     : {}".format(total)
        print "\tTOTAL REPEATED CORRESPONDENCES REMOVED : {}".format(total - final_inserted)
        print "\tTOTAL CORRESPONDENCES INSERTED         : {}".format(final_inserted)
        # print data

        return data


# spec = {
#     'target':
#         {'aligns': u'<http://www.w3.org/2000/01/rdf-schema#label>',
#          'graph': u'http://risis.eu/dataset/grid_20170712',
#          'entity_datatype': u'http://xmlns.com/foaf/0.1/Organization'},
#     'researchQ_URI': u'http://risis.eu/activity/idea_9cc1e7',
#     'stop_symbols_string': u"\\.\\-\\,\\+'\\?;()\u2013",
#     'mechanism': u'approxStrSim',
#
#     'source': {'aligns': u'<http://risis.eu/INDRecognisedSponsors/ontology/predicate/Organisation>',
#                'graph': u'http://risis.eu/dataset/INDRecognisedSponsors',
#                'link_old': u'<http://risis.eu/INDRecognisedSponsors/ontology/predicate/Organisation>',
#                'entity_datatype': u'http://risis.eu/INDRecognisedSponsors/ontology/class/Organigasion'},
#     'threshold': 0.8, 'specs': 0.8,
#     'stop_words_string': u'THE FOR IN THAT AT AND OF ON DE DES LA LES INC. LTD. B.V. INC LTD BV'}

# spec_2 = {
#     'target':
#         {'aligns': u'<http://www.w3.org/2000/01/rdf-schema#label>',
#          'graph': u'http://risis.eu/dataset/grid_20170712',
#          'entity_datatype': u'http://xmlns.com/foaf/0.1/Organization'},
#     'researchQ_URI': u'http://risis.eu/activity/idea_9cc1e7',
#     'stop_symbols_string': u"\\.\\-\\,\\+'\\?;()\u2013",
#     'mechanism': u'approxStrSim',
#     'source':
#         {'aligns': u'<http://risis.eu/INDRecognisedSponsors/ontology/predicate/Organisation>',
#          'graph': u'http://risis.eu/dataset/INDRecognisedSponsors',
#          'link_old': u'<http://risis.eu/INDRecognisedSponsors/ontology/predicate/Organisation>',
#          'entity_datatype': u'http://risis.eu/INDRecognisedSponsors/ontology/class/Organigasion'},
#     'threshold': 0.8,
#     'specs': 0.8,
#     'stop_words_string': u'THE FOR IN THAT AT AND OF ON DE DES LA LES INC. LTD. B.V. INC LTD BV'}
#
#
# linkset = "http://risis.eu/linkset/INDRecognisedSponsors_grid_20170712_exactStrSim_Organigasion_Organisation_N1231646853"
# expand_approx(spec_2, theta=0.8, stop_words_string=spec_2['stop_words_string'],
#               stop_symbols_string=spec_2['stop_symbols_string'], linkset2expand=linkset, reorder=True)

spec_2 = {
    'target':
        {'aligns': u'<http://goldenagents.org/uva/SAA/ontology/full_name>',
         'graph': u'http://goldenagents.org/datasets/BaptismRegistries002_0to5',
         'entity_datatype': u'http://goldenagents.org/uva/SAA/ontology/Person',
          #'reducer': u'http://risis.eu/linkset/refined_approxNbrSim_N2843981611761022069'
         },
    'researchQ_URI': u'http://risis.eu/activity/idea_e89d9c',
    'stop_symbols_string': u"\\.\\-\\,\\+'\\?;()\u2013",
    'mechanism': u'approxStrSim',
    'source':
        {'aligns': u'<http://goldenagents.org/uva/SAA/ontology/full_name>',
         'graph': u'http://goldenagents.org/datasets/BaptismRegistries002_0to5',
         'entity_datatype': u'http://goldenagents.org/uva/SAA/ontology/Person',
         # 'reducer': u'http://risis.eu/linkset/refined_approxNbrSim_N2843981611761022069'
         },
    #'corr_reducer': u'http://risis.eu/linkset/refined_approxNbrSim_N2843981611761022069',
    'threshold': 0.9,
    'specs': 0.9,
    'stop_words_string': u''}

linkset = "http://risis.eu/linkset/refined_approxNbrSim_N1447745871626231026"
# expand_approx(spec_2, theta=0.9, stop_words_string=spec_2['stop_words_string'],
#               stop_symbols_string=spec_2['stop_symbols_string'], linkset2expand=linkset, reorder=True)
