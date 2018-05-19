import Alignments.Query as Qr
import Alignments.Settings as St


predicate = """
SELECT DISTINCT ?pred
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
"""

subject = """
SELECT DISTINCT ?subj
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
}}
"""

modified_value = """
SELECT DISTINCT ?subj ?pred ?obj_1 ?obj_2
{{
    {{ GRAPH <{}>
        {{
            ?subj ?pred ?obj_1 .
        }}
    }}

    {{ GRAPH <{}>
        {{
            ?subj ?pred ?obj_2  .
        }}
    }}
}}
"""


modified_predicate = """
SELECT DISTINCT ?pred_1 ?pred_2
{{
    {{ GRAPH <{}>
        {{
            ?subj ?pred_1 ?obj .
        }}
    }}

    {{ GRAPH <{}>
        {{
            ?subj ?pred_2 ?obj  .
        }}
    }}
}}
"""


def removed(early_version, late_version, display=True, activated=False):

    if activated is False:
        print "\nTHE FUNCTION [removed] IS NOT ACTIVATED"
        return {St.subject: None, St.predicate: None, St.triples: None}

    status = False

    # TRIPLES REMOVED
    subj_rem = subject.format(early_version, late_version)
    prop_rem = predicate.format(early_version, late_version)

    # RESPONSE FOR TRIPLES REMOVED
    resp_subj_rem = Qr.sparql_xml_to_matrix(subj_rem)
    resp_prop_rem = Qr.sparql_xml_to_matrix(prop_rem)

    status = (resp_subj_rem[St.result] and len(resp_subj_rem[St.result]) > 1) and \
             (resp_prop_rem[St.result] and len(resp_prop_rem[St.result]) > 1)

    if display is True:

        # DISPLAY THE RESULTS FOR SUBJECT REMOVED
        print "\n>>> DISPLAY THE RESULTS FOR SUBJECT REMOVED"
        Qr.display_matrix(resp_subj_rem, limit=10, is_activated=True)

        # DISPLAY THE RESULTS FOR PREDICATE REMOVED
        print "\n>>> DISPLAY THE RESULTS FOR PREDICATE REMOVED"
        Qr.display_matrix(resp_prop_rem, limit=10, is_activated=True)

        # DISPLAY THE RESULTS FOR VALUE REMOVED
        # print "\n>>> DISPLAY THE RESULTS FOR VALUE REMOVED"
        # Qr.display_matrix(resp_val_rem, spacing=90, limit=10, is_activated=True)

    return {"status":status, St.subject: resp_subj_rem, St.predicate: resp_prop_rem}




    # return delta_q

def added(early_version, late_version, display=True, activated=False):

    if activated is False:
        print "\nTHE FUNCTION [added] IS NOT ACTIVATED"
        return {St.subject: None, St.predicate: None, St.triples: None}

    # TRIPLES ADDED
    subj_added = subject.format(late_version, early_version)
    prop_added = predicate.format(late_version, early_version)

    # RESPONSE FOR TRIPLES ADDED
    resp_subj_added = Qr.sparql_xml_to_matrix(subj_added)
    resp_prop_added = Qr.sparql_xml_to_matrix(prop_added)

    status = (resp_subj_added[St.result] and len(resp_subj_added[St.result]) > 1) and \
             (resp_prop_added[St.result] and len(resp_prop_added[St.result]) > 1)

    if display is True:

        # DISPLAY THE RESULTS FOR SUBJECT ADDED
        print "\n>>> DISPLAY THE RESULTS FOR SUBJECT ADDED"
        Qr.display_matrix(resp_subj_added, limit=10, is_activated=True)

        # DISPLAY THE RESULTS FOR PREDICATE ADDED
        print "\n>>> DISPLAY THE RESULTS FOR PREDICATE ADDED"
        Qr.display_matrix(resp_prop_added, limit=10, is_activated=True)

    return {"status":status, St.subject: subj_added, St.predicate: prop_added}

def modified(early_version, late_version, display=True, activated=False):

    if activated is False:
        print "\nTHE FUNCTION [removed] IS NOT ACTIVATED"
        return {St.subject: None, St.predicate: None, St.triples: None}

    # TRIPLES REMOVED
    mod_val = modified_value.format(early_version, late_version)
    mod_pred = modified_predicate.format(early_version, late_version)

    # RESPONSE FOR TRIPLES REMOVED
    resp_mod_val = Qr.sparql_xml_to_matrix(mod_val)
    resp_mod_pred = Qr.sparql_xml_to_matrix(mod_pred)

    status = (resp_mod_val[St.result] and len(resp_mod_val[St.result]) > 1) and \
             (resp_mod_pred[St.result] and len(resp_mod_pred[St.result]) > 1)

    if display is True:

        # DISPLAY THE RESULTS FOR VALUE REMOVED
        print "\n>>> DISPLAY THE RESULTS FOR VALUE MODIFIED"
        Qr.display_matrix(resp_mod_val, spacing=90, limit=10, is_activated=True)

        # DISPLAY THE RESULTS FOR VALUE REMOVED
        print "\n>>> DISPLAY THE RESULTS FOR PREDICATE MODIFIED"
        Qr.display_matrix(resp_mod_pred, spacing=90, limit=10, is_activated=True)

    return {"status":status, St.predicate: resp_mod_pred, St.triples: resp_mod_val}




    # return delta_q

def all(early_version, late_version):

    # TRIPLES REMOVED
    subj_rem = subject.format(early_version, late_version)
    prop_rem = predicate.format(early_version, late_version)
    val_rem = value.format(early_version, late_version)

    # TRIPLES ADDED
    prop_added = predicate.format(late_version, early_version)
    subj_added = subject.format(late_version, early_version)
    val_added = value.format(late_version, early_version)
    # print val_added

    # RESPONSE FOR TRIPLES REMOVED
    resp_subj_rem = Qr.sparql_xml_to_matrix(subj_rem)
    resp_prop_rem = Qr.sparql_xml_to_matrix(prop_rem)
    resp_val_rem = Qr.sparql_xml_to_matrix(val_rem)

    # RESPONSE FOR TRIPLES ADDED
    resp_subj_added = Qr.sparql_xml_to_matrix(subj_added)
    resp_prop_added = Qr.sparql_xml_to_matrix(prop_added)
    resp_val_added = Qr.sparql_xml_to_matrix(val_added)

    # DISPLAY THE RESULTS FOR SUBJECT REMOVED
    Qr.display_matrix(resp_subj_rem, limit=10, is_activated=True)

    # DISPLAY THE RESULTS FOR PREDICATE REMOVED
    Qr.display_matrix(resp_prop_rem, limit=10, is_activated=True)

    # DISPLAY THE RESULTS FOR VALUE REMOVED
    Qr.display_matrix(resp_val_rem, spacing=90, limit=10, is_activated=True)


    # DISPLAY THE RESULTS FOR SUBJECT ADDED
    Qr.display_matrix(resp_subj_added, limit=10, is_activated=True)

    # DISPLAY THE RESULTS FOR PREDICATE ADDED
    Qr.display_matrix(resp_prop_added, limit=10, is_activated=True)

    # DISPLAY THE RESULTS FOR VALUE ADDED
    Qr.display_matrix(resp_val_added, limit=90, is_activated=True)

    # return delta_q


# removed("http://risis.eu/dataset/orgreg_V0", "http://risis.eu/dataset/orgreg_V3", display=True, activated=True)
# added("http://risis.eu/dataset/orgreg_V0", "http://risis.eu/dataset/orgreg_V3", display=True, activated=True)
# removed("http://risis.eu/dataset/openAire_20170816", "http://risis.eu/dataset/openAire_20180219")


# removed("http://risis.eu/dataset/orgreg_V0", "http://risis.eu/dataset/orgreg_V3", display=True, activated=True)
i_added = added("http://risis.eu/dataset/Test.v1", "http://risis.eu/dataset/Test.v2", display=False, activated=True)
i_removed = removed("http://risis.eu/dataset/Test.v1", "http://risis.eu/dataset/Test.v2", display=False, activated=True)
i_modifed = modified("http://risis.eu/dataset/Test.v1", "http://risis.eu/dataset/Test.v2", display=False, activated=True)

print i_added["status"]
print i_removed["status"]
print i_modifed["status"]
