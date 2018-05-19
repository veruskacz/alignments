import time
import Alignments.Query as Qr
# import Alignments.Settings as St
import cStringIO as Builder
# import Alignments.Examples.EvolvingSemanticWebData.GraphData as data
# import urllib
import urllib2
import Alignments.Settings as St
import Alignments.Utility as Ut
# from kitchen.text.converters import to_bytes
_format = "%a %b %d %H:%M:%S %Y"
_line = "------------------------------------------------------------------------------------------------------"
import datetime


def subject(early_version, late_version, count=False):

    count_c = "" if count is True else "# "
    select_c = "# " if count is True else ""

    subject_q = """
    # SUBJECT ADDED OR REMOVED
    {}SELECT (COUNT(DISTINCT ?subj) AS ?TOTAL)
    {}SELECT DISTINCT ?subj
    {{
        {{ GRAPH <{}>
            {{
                ?subj ?pred ?obj .
            }}
        }}
        MINUS
        {{ GRAPH <{}>
            {{
                ?subj ?pred_1 ?obj_1  .
            }}
        }}
    }}""".format(count_c, select_c, early_version, late_version)
    # print subject_q
    return subject_q


def predicate(early_version, late_version, count=False):

    count_c = "" if count is True else "# "
    select_c = "# " if count is True else ""

    predicate_q = """
    # PREDICATE ADDED OR REMOVED
    {}SELECT (COUNT(DISTINCT ?pred) AS ?TOTAL)
    {}SELECT DISTINCT ?pred
    {{
        {{ GRAPH <{}>
            {{
                ?subj ?pred ?obj .
            }}
        }}
        MINUS
        {{ GRAPH <{}>
            {{
                ?subj_1 ?pred ?obj_1  .
            }}
        }}
    }}
    """.format(count_c, select_c, early_version, late_version)
    # print predicate_q
    return predicate_q


def modified_value2(early_version, late_version, count=False):

    count_c = "" if count is True else "# "
    select_c = "# " if count is True else ""
    modified_value_q = """
    {}SELECT (COUNT(?obj_1) AS ?TOTAL)
    {}SELECT DISTINCT ?subj ?pred ?obj_1 ?obj_2
    {{
        {{
            GRAPH <{}>
            {{
                ?subj ?pred ?obj_1 .
            }}
        }}
        FILTER EXISTS
        {{
            GRAPH <{}>
            {{
                ?subj ?pred ?obj_2  .
            }}
        }}
    }}""".format(count_c, select_c, early_version, late_version)
    return modified_value_q


def modified_value(early_version, late_version, count=False):
    count_c = "" if count is True else "# "
    select_c = "# " if count is True else ""
    modified_value_q_load = """
    DROP SILENT GRAPH <{2}_TEMP>;
    DROP SILENT GRAPH <{3}_TEMP>;

    INSERT
    {{
        GRAPH <{2}_TEMP>
        {{
            ?subj ?pred ?obj_1 .
        }}

        GRAPH <{3}_TEMP>
        {{
            ?subj ?pred ?obj_2  .
        }}
    }}

    WHERE
    {{
        {{
            GRAPH <{2}>
            {{
                ?subj ?pred ?obj_1 .
            }}

            GRAPH <{3}>
            {{
                ?subj ?pred ?obj_2  .
            }}

            FILTER(?obj_1 != ?obj_2)
        }}
    }} """.format(count_c, select_c, early_version, late_version)

    if count is False:
        print "\nLOADING VALUES TEMP GRAPH..."
        start = time.time()
        Qr.endpoint(modified_value_q_load)
        diff = str(datetime.timedelta(seconds=time.time() - start))
        print "\t{:50} [{}]".format("... values temp graph loaded in", diff)

    modified_value_q = """
    # PREDICATE MODIFIED
    {0}SELECT (COUNT(?obj_1) AS ?TOTAL)
    {1}SELECT DISTINCT ?subj ?pred ?obj_1 ?obj_2
    {{
        GRAPH <{2}_TEMP>
        {{
            ?subj ?pred ?obj_1 .
            FILTER NOT EXISTS {{ GRAPH <{3}_TEMP> {{?subj ?pred ?obj_1 .  }} }}
        }}

        GRAPH <{3}_TEMP>
        {{
            ?subj ?pred ?obj_2  .
            FILTER NOT EXISTS {{  GRAPH <{2}_TEMP> {{?subj ?pred ?obj_2 . }} }}
        }}

        #  FILTER NOT EXISTS {{
        #     GRAPH <{3}_TEMP> {{?subj ?pred ?obj_1 . }}
        #     GRAPH <{2}_TEMP> {{?subj ?pred ?obj_2 . }}
        # }}
    }}
    """.format(count_c, select_c, early_version, late_version)
    # print modified_predicate_q
    # if count is False:
    #     print "MATCHING TEMPS..."
    return modified_value_q


def modified_predicate2(early_version, late_version, count=False):

    count_c = "" if count is True else "# "
    select_c = "# " if count is True else ""
    modified_predicate_q = """
    # PREDICATE MODIFIED
    {0}SELECT (COUNT (?pred_1) AS ?TOTAL)
    {1}SELECT DISTINCT ?pred_1 ?pred_2
    {{
        GRAPH <{2}>
        {{
            ?subj ?pred_1 ?obj .
            FILTER NOT EXISTS {{  GRAPH <{3}> {{?subj ?pred_1 ?obj . }} }}
        }}

        GRAPH <{3}>
        {{
            ?subj ?pred_2 ?obj  .
            FILTER NOT EXISTS {{  GRAPH <{2}> {{?subj ?pred_2 ?obj . }} }}
        }}

        FILTER(?pred_1 != ?pred_2)

        # FILTER EXISTS
        # {{
        #     GRAPH <{3}>
        #     {{
        #         ?subj ?pred_2 ?obj  .
        #     }}
        # }}

        # FILTER NOT EXISTS {{
        #     GRAPH <{3}> {{?subj ?pred_1 ?obj . }}
        #     GRAPH <{2}> {{?subj ?pred_2 ?obj . }}
        # }}

        # # PREDICATE REMOVED
        # FILTER NOT EXISTS
        # {{
        #     {{ GRAPH <{2}>
        #         {{
        #             ?subj ?pred_1 ?obj .
        #         }}
        #     }}
        #     MINUS
        #     {{ GRAPH <{3}>
        #         {{
        #             ?subj_1 ?pred_1 ?obj_1  .
        #         }}
        #     }}
        # }}

        # # PREDICATE ADDED
        # FILTER NOT EXISTS
        # {{
        #     {{ GRAPH <{3}>
        #         {{
        #             ?subj ?pred_1 ?obj .
        #         }}
        #     }}
        #     MINUS
        #     {{ GRAPH <{2}>
        #         {{
        #             ?subj_1 ?pred_1 ?obj_1  .
        #         }}
        #     }}
        # }}

    }}""".format(count_c, select_c, early_version, late_version)
    # print modified_predicate_q
    return modified_predicate_q


def modified_predicate(early_version, late_version, count=False):
    count_c = "" if count is True else "# "
    select_c = "# " if count is True else ""
    modified_predicate_q_load = """
    DROP SILENT GRAPH <{2}_TEMP>;
    DROP SILENT GRAPH <{3}_TEMP>;

    INSERT
    {{
        GRAPH <{2}_TEMP>
        {{
            ?subj ?pred_1 ?obj .
        }}

        GRAPH <{3}_TEMP>
        {{
            ?subj ?pred_2 ?obj  .
        }}
    }}

    WHERE
    {{
        {{
            GRAPH <{2}>
            {{
                ?subj ?pred_1 ?obj .
            }}

            GRAPH <{3}>
            {{
                ?subj ?pred_2 ?obj  .
            }}

            #FILTER(?pred_1 != ?pred_2)
        }}
    }} """.format(count_c, select_c, early_version, late_version)

    if count is False:
        print "\nLOADING PREDICATE TEMP GRAPH..."
        start = time.time()
        Qr.endpoint(modified_predicate_q_load)
        diff = str(datetime.timedelta(seconds=time.time() - start))
        print "\t{:50} [{}]".format("... predicate temp GRAPH loaded in ", diff)

    modified_predicate_q = """
    # PREDICATE MODIFIED
    {0}SELECT (COUNT (?pred_1) AS ?TOTAL)
    {1}SELECT DISTINCT ?pred_1 ?pred_2
    {{
        GRAPH <{2}_TEMP>
        {{
            ?subj ?pred_1 ?obj .
            FILTER NOT EXISTS {{  GRAPH <{3}> {{?subj ?pred_1 ?obj . }} }}
        }}

        GRAPH <{3}_TEMP>
        {{
            ?subj ?pred_2 ?obj  .
            FILTER NOT EXISTS {{  GRAPH <{2}> {{?subj ?pred_2 ?obj . }} }}
        }}
    }}
    """.format(count_c, select_c, early_version, late_version)
    # print modified_predicate_q
    # if count is False:
    #     print "MATCHING TEMPS..."
    return modified_predicate_q


def added(early_version, late_version, stat=False, display=True, activated=False):

    if activated is False:
        print "\nTHE FUNCTION [added] IS NOT ACTIVATED"
        return {St.subject: None, St.predicate: None, St.triples: None}

    if stat is False:

        subj_added = subject(late_version, early_version, count=stat)
        prop_added = predicate(late_version, early_version, count=stat)

        # RESPONSE FOR TRIPLES ADDED
        resp_subj_added = Qr.sparql_xml_to_matrix(subj_added)
        resp_prop_added = Qr.sparql_xml_to_matrix(prop_added)

        status = (resp_subj_added[St.result] is not None and len(resp_subj_added[St.result]) > 1) or \
                 (resp_prop_added[St.result] is not None and len(resp_prop_added[St.result]) > 1)

        if display is True:

            # DISPLAY THE RESULTS FOR SUBJECT ADDED
            print "\n>>> DISPLAY THE RESULTS FOR SUBJECT ADDED"
            Qr.display_matrix(resp_subj_added, limit=10, is_activated=True)

            # DISPLAY THE RESULTS FOR PREDICATE ADDED
            print "\n>>> DISPLAY THE RESULTS FOR PREDICATE ADDED"
            Qr.display_matrix(resp_prop_added, limit=10, is_activated=True)

        return {"status": status,
                St.subject: resp_subj_added[St.result],
                St.predicate: resp_prop_added[St.result]}

    else:

        subj_added = subject(late_version, early_version, count=stat)
        prop_added = predicate(late_version, early_version, count=stat)
        resp_subj_added = Qr.sparql_xml_to_matrix(subj_added)
        resp_prop_added = Qr.sparql_xml_to_matrix(prop_added)

        status = (resp_subj_added[St.result] is not None and int(resp_subj_added[St.result][1][0]) > 0)\
            or (resp_prop_added[St.result] is not None and int(resp_prop_added[St.result][1][0]) > 0)

        return {"status": status,
                St.subject: resp_subj_added[St.result][1][0],
                St.predicate: resp_prop_added[St.result][1][0]}


def removed(early_version, late_version, stat=False, display=True, activated=False):

    if activated is False:
        print "\nTHE FUNCTION [removed] IS NOT ACTIVATED"
        return {St.subject: None, St.predicate: None, St.triples: None}

    if stat is False:

        # TRIPLES REMOVED
        subj_rem = subject(early_version, late_version, count=stat)
        prop_rem = predicate(early_version, late_version, count=stat)

        # RESPONSE FOR TRIPLES REMOVED
        resp_subj_rem = Qr.sparql_xml_to_matrix(subj_rem)
        resp_prop_rem = Qr.sparql_xml_to_matrix(prop_rem)

        status = (resp_subj_rem[St.result] is not None and len(resp_subj_rem[St.result]) > 1) or \
                 (resp_prop_rem[St.result] is not None and len(resp_prop_rem[St.result]) > 1)

        if display is True:

            # DISPLAY THE RESULTS FOR SUBJECT REMOVED
            print "\n>>> DISPLAY THE RESULTS FOR SUBJECT REMOVED"
            Qr.display_matrix(resp_subj_rem, limit=10, is_activated=True)

            # DISPLAY THE RESULTS FOR PREDICATE REMOVED
            print "\n>>> DISPLAY THE RESULTS FOR PREDICATE REMOVED"
            Qr.display_matrix(resp_prop_rem, limit=10, is_activated=True)

        return {"status": status, St.subject: resp_subj_rem[St.result], St.predicate: resp_prop_rem[St.result]}

    else:

        subj_rem = subject(early_version, late_version, count=stat)
        prop_rem = predicate(early_version, late_version, count=stat)
        resp_subj_rem = Qr.sparql_xml_to_matrix(subj_rem)
        resp_prop_rem = Qr.sparql_xml_to_matrix(prop_rem)

        status = int(resp_subj_rem[St.result][1][0]) > 0 or int(resp_prop_rem[St.result][1][0]) > 0

        return {"status": status,
                St.subject: resp_subj_rem[St.result][1][0],
                St.predicate: resp_prop_rem[St.result][1][0]}


def modified(early_version, late_version, stat=False, display=True, activated=False):

    if activated is False:
        print "\nTHE FUNCTION [removed] IS NOT ACTIVATED"
        return {St.subject: None, St.predicate: None, St.triples: None}

    if stat is False:

        # TRIPLES REMOVED
        mod_pred = modified_predicate(early_version, late_version, count=stat)

        # EXECUTING THE PREDICATE MODIFICATION QUERY
        start = time.time()
        resp_mod_pred = Qr.sparql_xml_to_matrix(mod_pred)
        matched_time_1 = str(datetime.timedelta(seconds=time.time() - start))
        print " \t{:50} [{}]".format("... predicate matched in", matched_time_1)

        # DROPPING THE TEMP GRAPH USED FOR THE QUERY
        # print "DROPPING TEMPS..."
        drop = """
        DROP SILENT GRAPH <{}_TEMP>;
        DROP SILENT GRAPH <{}_TEMP> """.format(early_version, late_version)
        start = time.time()
        Qr.endpoint(drop)
        dropped_time_1 = str(datetime.timedelta(seconds=time.time() - start))
        print "\t{:50} [{}]".format("... predicate temp graph dropped in", dropped_time_1)
        print "\t{:50} [{}]".format("... elapse time", str(datetime.timedelta(seconds=time.time() - start)))

        mod_val = modified_value(early_version, late_version, count=stat)

        # EXECUTING THE VALUE MODIFICATION QUERY
        start_2 = time.time()
        resp_mod_val = Qr.sparql_xml_to_matrix(mod_val)
        matched_time_2 = str(datetime.timedelta(seconds=time.time() - start_2))
        print "\t{:50} [{}]".format("... value matched in", matched_time_2)

        # DROPPING THE TEMP GRAPH USED FOR THE QUERY
        # print "DROPPING TEMPS..."
        drop = """
        DROP SILENT GRAPH <{}_TEMP>;
        DROP SILENT GRAPH <{}_TEMP> """.format(early_version, late_version)
        start_2 = time.time()
        Qr.endpoint(drop)
        dropped_time_2 = str(datetime.timedelta(seconds=time.time() - start_2))
        print "\t{:50} [{}]".format("... value temp graph dropped in", dropped_time_2)
        print "\t{:50} [{}]".format("... elapse time", str(datetime.timedelta(seconds=time.time() - start)))

        status = (resp_mod_val[St.result] is not None and len(resp_mod_val[St.result]) > 1) or \
                 (resp_mod_pred[St.result] is not None and len(resp_mod_pred[St.result]) > 1)

        if display is True:

            # DISPLAY THE RESULTS FOR VALUE REMOVED
            print "\n>>> DISPLAY THE RESULTS FOR VALUE MODIFIED"
            Qr.display_matrix(resp_mod_val, spacing=90, limit=10, is_activated=True)

            # DISPLAY THE RESULTS FOR VALUE REMOVED
            print "\n>>> DISPLAY THE RESULTS FOR PREDICATE MODIFIED"
            Qr.display_matrix(resp_mod_pred, spacing=90, limit=10, is_activated=True)

        return {"status": status,
                St.predicate: resp_mod_pred[St.result],
                St.triples: resp_mod_val[St.result]}

    else:

        mod_pred = modified_predicate(early_version, late_version, count=stat)
        mod_val = modified_value(early_version, late_version, count=stat)

        resp_mod_pred = Qr.sparql_xml_to_matrix(mod_pred)
        resp_mod_val = Qr.sparql_xml_to_matrix(mod_val)

        # resp_mod_val = {St.result: None}

        resp_mod_pred_bool = resp_mod_pred[St.result] is None
        resp_mod_val_bool = resp_mod_val[St.result] is None

        status = (resp_mod_pred_bool is not True and int(resp_mod_pred[St.result][1][0]) > 0) or \
                 (resp_mod_val_bool is not None and int(resp_mod_val[St.result][1][0]) > 0)

        return {"status": status,
                St.predicate: resp_mod_pred[St.result][1][0] if resp_mod_pred_bool is not True else None,
                St.triples: resp_mod_val[St.result][1][0] if resp_mod_val_bool is not True else None}


def version_analysis(early_version, late_version, stat=True, detail=False, display=True, activated=False):

    date = datetime.datetime.today()
    started_at = time.time()
    print "\n{}\n{:>90}\n{}\n".format(_line, date.strftime(_format), _line)

    # print "COMPUTING DELTAS FOR: \n\t-{}\n\t-{}".format(early_version, late_version)
    if stat:
        print "\nPRINTING ONLY STATS OF DELTA COMPUTATIONS FOR: \n- {}\n- {}".format(early_version, late_version)
    else:
        print "\nPRINTING STATS AND SAMPLE OF DELTA COMPUTATIONS FOR: \n- {}\n- {}".format(early_version, late_version)

    limit = 25
    i_added = added(early_version, late_version, stat=stat, display=display, activated=activated)
    print "\n{:20}: {}".format("ADDED", i_added["status"])
    if i_added["status"]:
        subj = i_added[St.subject]
        pred = i_added[St.predicate]

        if stat is False:
            subj_stats = subj.__len__() if subj else None
            pred_stats = pred.__len__() if pred else None
            if subj:
                print "\t{:16}: {}".format("Subject Count", subj_stats - 1)
                if detail:
                    for i in range(1, subj_stats):
                        print "\t\t{}".format(subj[i][0])
                        if i == limit:
                            break

            if pred:
                print "\t{:16}: {}".format("Predicate Count", pred_stats - 1)
                if detail:
                    for i in range(1, pred_stats):
                        print "\t\t{}".format(pred[i][0])
                        if i == limit:
                            break
        else:
            print "\t{:16}: {}".format("Subject Count", subj)
            print "\t{:16}: {}".format("Predicate Count", pred)

    # #################################################
    # REMOVED
    # #################################################
    i_removed = removed(early_version, late_version, stat=stat, display=display, activated=activated)
    print "\n{:20}: {}".format("REMOVED", i_removed["status"])
    if i_removed["status"]:
        subj = i_removed[St.subject]
        pred = i_removed[St.predicate]

        if stat is False:
            subj_stats = subj.__len__() if subj else None
            pred_stats = pred.__len__() if pred else None
            if subj:
                print "\t{:16}: {}".format("Subject Count", subj_stats - 1)
                if detail:
                    for i in range(1, subj_stats):
                        print "\t\t{}".format(subj[i][0])
                        if i == limit:
                            break

            if pred:
                print "\t{:16}: {}".format("Predicate Count", pred_stats - 1)
                if detail:
                    for i in range(1, pred_stats):
                        print "\t\t{}".format(pred[i][0])
                        if i == limit:
                            break
        else:
            print "\t{:16}: {}".format("Subject Count", subj)
            print "\t{:16}: {}".format("Predicate Count", pred)

    # #################################################
    # MODIFIED
    # #################################################

    i_modified = modified(early_version, late_version, stat=stat, display=display, activated=activated)
    start = time.time()
    print "\n{:54} [{}]".format("Time so far...", str(datetime.timedelta(seconds=start - started_at)))
    print "\n{:20}: {}".format("MODIFIED", i_modified["status"])
    if i_modified["status"]:
        triple = i_modified[St.triples]
        pred = i_modified[St.predicate]

        if stat is False:
            triple_stats = triple.__len__() if triple else None
            pred_stats = pred.__len__() if pred else None
            if pred:
                print "\t{:16}: {}".format("Predicate Count", pred_stats - 1)
                if detail:
                    for i in range(1, pred_stats):
                        print "\t\t{} {}".format(pred[i][0], pred[i][1])
                        if i == limit:
                            break

            if triple:
                print "\t{:16}: {}".format("Value Count", triple_stats - 1)
                if detail:
                    for i in range(1, triple_stats):
                        print "\t\t{} {} {} {}".format(triple[i][0], triple[i][1], triple[i][2], triple[i][3])
                        if i == limit:
                            break

        else:
            print "\t{:16}: {}".format("Predicate Count", pred)
            print "\t{:16}: {}".format("Value Count", triple)

    return{"removed": removed, "added": added, "modified": modified}


def version_analysis_stat(early_version, late_version, display=True, activated=False):

    # ############################################
    # ADDED
    # ############################################
    i_added = added(early_version, late_version, display=display, activated=activated)
    print "\n{:9}: {}".format("ADDED", i_added["status"])

    if i_added["status"]:
        subj = i_added[St.subject]
        pred = i_added[St.predicate]

        if subj:
            print "\t{:16}: {}".format("Subject Count", subj.__len__() - 1)
            # for i in range(1, len(subj)):
            #     print "\t\t{}".format(subj[i][0])

        if pred:
            print "\t{:16}: {}".format("Predicate Count", pred.__len__() - 1)
            # for i in range(1, len(pred)):
            #     print "\t\t{}".format(pred[i][0])

    i_removed = removed(early_version, late_version, display=display, activated=activated)
    print "\n{:9}: {}".format("REMOVED", i_removed["status"])

    if i_removed["status"]:
        subj = i_removed[St.subject]
        pred = i_removed[St.predicate]

        if subj:
            print "\t{:16}: {}".format("Subject Count", subj.__len__() - 1)
            # for i in range(1, len(subj)):
            #     print "\t\t{}".format(subj[i][0])

        if pred:
            print "\t{:16}: {}".format("Predicate Count", pred.__len__() - 1)
            # for i in range(1, len(pred)):
            #     print "\t\t{}".format(pred[i][0])

    i_modified = modified(early_version, late_version, display=display, activated=activated)
    print "\n{:9}: {}".format("MODIFIED", i_modified["status"])

    if i_modified["status"]:
        triple = i_modified[St.triples]
        pred = i_modified[St.predicate]

        if pred:
            print "\t{:16}: {}".format("Predicate Count", pred.__len__() - 1)
            # for i in range(1, len(pred)):
            #     print "\t\t{} {}".format(pred[i][0], pred[i][1])

        if triple:
            print "\t{:16}: {}".format("Predicate Count", triple.__len__() - 1)
            # for i in range(1, len(triple)):
            #     print "\t\t{} {} {}".format(triple[i][1], triple[i][2], triple[i][3])

    return{"removed": removed, "added": added, "modified": modified}


# removed("http://risis.eu/dataset/orgreg_V0", "http://risis.eu/dataset/orgreg_V3", display=True, activated=True)
# added("http://risis.eu/dataset/orgreg_V0", "http://risis.eu/dataset/orgreg_V3", display=True, activated=True)
# removed("http://risis.eu/dataset/openAire_20170816", "http://risis.eu/dataset/openAire_20180219")
# removed("http://risis.eu/dataset/orgreg_V0", "http://risis.eu/dataset/orgreg_V3", display=True, activated=True)


# i_added = added("http://risis.eu/dataset/Test.v1", "http://risis.eu/dataset/Test.v2", display=False, activated=True)
# print "{:10}: {}".format("STATUS", i_added["status"])

# i_removed = removed("http://risis.eu/dataset/Test.v1",
# "http://risis.eu/dataset/Test.v2", display=False, activated=True)
# i_modified = modified(
#     "http://risis.eu/dataset/Test.v1", "http://risis.eu/dataset/Test.v2", display=False, activated=True)
#

# data.reload()
# print i_removed["status"]
# print i_modified["status"]

test_v1 = "http://risis.eu/dataset/Test.v1"
test_v2 = "http://risis.eu/dataset/Test.v2"
grid_v1 = "http://risis.eu/dataset/grid_20170712"
grid_v2 = "http://risis.eu/dataset/grid_20180208"


# print added_stats(test_v1, test_v2, display=False, activated=True)
# version_analysis(test_v1, test_v2, stat=True, detail=True, display=False, activated=True)
version_analysis(test_v1, test_v2, stat=False, detail=True, display=False, activated=True)
# version_analysis(grid_v1, grid_v2, stat=False,  detail=True, display=False, activated=True)


def my_code(inputs, encode=True):

    output = Builder.StringIO()

    # inputs = "I love you more"
    # inputs = "410516181 909161-90686171 9"
    # sample = """The Multipurpose Internet Mail Extensions (MIME) type is a standardized way to indicate the nature
    # and format of a document. It is defined and standardized in IETF RFC 6838. The Internet Assigned Numbers Authority
    # (IANA) is the official body responsible for keeping track of all official MIME types, and you can find the most
    # up-to-date and complete list at the Media Types page.
    # Browsers often use the MIME type (and not the file extension) to determine how it will process a document; it is
    # therefore important that servers are set up correctly to attach the correct MIME type to the header of the
    # response
    # object."""

    letters = {
        'a': [2, 8], 'b': [2, 9], 'c': [2, 1],
        'd': [3, 8], 'e': [' ', 9], 'f': [3, 1],
        'g': [4, 8], 'h': [4, 9], 'i': [4, 1],
        'j': [5, 8], 'k': [5, 9], 'l': [5, 1],
        'm': [6, 8], 'n': [6, 9], 'o': [6, 1],
        'p': [7, 8], 'q': [7, 9], 'r': [7, 1], 's': [7, 2],
        't': [8, 8], 'u': ['-', 9], 'v': [8, 1], ' ': [1, 0],
        'w': [9, 8], 'x': [9, 9], 'y': [9, 1], 'z': [9, 2],
        '1': [1, 7], '2': [2, 7], '3': [3, 7], '4': [4, 7], '5': [5, 7],
        '6': [6, 7], '7': [7, 7], '8': [8, 7], '9': [9, 7], '0': ['.', 7]
    }

    numbers = {
        '28': 'a', '29': 'b', '21': 'c',
        '38': 'd', ' 9': 'e', '31': 'f',
        '48': 'g', '49': 'h', '41': 'i',
        '58': 'j', '59': 'k', '51': 'l',
        '68': 'm', '69': 'n', '61': 'o',
        '78': 'p', '79': 'q', '71': 'r', '72': 's',
        '88': 't', '-9': 'u', '81': 'v', '10': ' ',
        '98': 'w', '99': 'x', '91': 'y', '92': 'z',
        '.7': '0', '17': '1', '27': '2', '37': '3', '47': '4', '57': '5',
        '67': '6', '77': '7', '87': '8', '97': '9'}

    # ENCODE
    if encode is True:
        inputs = Ut.to_alphanumeric(inputs, spacing=" ")
        inputs = inputs.replace("  ", " ")
        print inputs
        for character in inputs.lower():
            code = letters[character]
            if character == ' ':
                output.write(str(code[1]))
            else:
                output.write(str(code[0]) + str(code[1]))

        # print my_code(output.getvalue(), encode=False)

    # DECODE
    else:

        inputs = inputs.lower()
        words = inputs.split('0')
        # print words

        for word in words:
            # print word

            for i in range(0, len(word), 2):
                key = "{}{}".format(word[i], word[i + 1])
                # print key, numbers[key]
                output.write(numbers[key])
            output.write(' ')

    return output.getvalue()


def google_request(query):

    # script = """
    # <script>
    #   (function() {
    #     var cx = '003451433256106493178:ewmhkur_ov0';
    #     var gcse = document.createElement('script');
    #     gcse.type = 'text/javascript';
    #     gcse.async = true;
    #     gcse.src = 'https://cse.google.com/cse.js?cx=' + cx;
    #     var s = document.getElementsByTagName('script')[0];
    #     s.parentNode.insertBefore(gcse, s);
    #   })();
    # </script>
    # <gcse:search></gcse:search>
    # """
    # source = "https://www.google.nl/search?q=benin+size"
    # source = "view-source:http://docs.python-requests.org/en/master/api/"
    # query = "benin+size?"
    api_key = "AIzaSyBbMhZuhJD_HC-Okj0ody1kAlXYDeL5f8A"
    root = "https://www.googleapis.com/customsearch/v1?"
    engine = '003451433256106493178:ewmhkur_ov0'
    example = "{}key={}&cx={}&q={}&output=txt&type=text/html".format(root, api_key, engine, query)

    # buf = buffer.StringIO()
    # curl = pycurl.Curl()
    # curl.setopt(pycurl.CAINFO, certifi.where())
    # curl.setopt(pycurl.URL, source)
    # curl.setopt(curl.WRITEFUNCTION, buf.write)
    # curl.setopt(curl.HTTPHEADER, ['Content-Type: text/html','Accept-Charset: UTF-8'])
    # curl.perform()
    # print buf.getvalue()
    # buf.close()

    print urllib2.urlopen(example).read()
