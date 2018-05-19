import time
import os
import re
import datetime
import subprocess
import Alignments.Query as Qr
import Alignments.Utility as Ut
import cStringIO as Builder
import Alignments.Examples.LinkValidation.Data as Data
_format = "%a %b %d %H:%M:%S %Y"
date = datetime.datetime.today()
begining = time.time()
_line = "------------------------------------------------------------------------------------------------------"
print "\n{}\n{:>90}\n{}\n".format(_line, date.strftime(_format), _line)
from os.path import join


# RESEARCH QUESTION LABEL       : Link Validation Reprocess 0.75
# RESEARCH QUESTION ID          : http://risis.eu/activity/idea_3944ec
# ORGREG CONTAINS               : 3201 UNIVERSITIES
# COVERAGE USING NAME           : 1922 UNIVERSITIES
# COVERAGE USING GEO SIM        : 1450 UNIVERSITIES
# OVERALL COVERAGE NAME + GEO   : |2512 - 3201| = 689

# THE LENS TO USE FOR NETWORK EXTRACTION
lens = "union_Eter_2014_LeidenRanking_2015_Grid_20170712_H2020_Orgref_20170703_Orgreg_20170718_P1768695787"
name_lens = "http://risis.eu/lens/{}".format(lens)

lens = "union_Eter_2014_Grid_20170712_Orgreg_20170718_P2045540655"
geo_lens = "http://risis.eu/lens/{}".format(lens)


lens_name = "union_Eter_2014_Grid_20170712_Orgreg_20170718_H2020_LeidenRanking_2015_Orgref_20170703_N248196449"
union_name = "http://risis.eu/lens/{}".format(lens_name)

lens_geo = "union_Orgreg_20170718_Eter_2014_Grid_20170712_N1471387312"
union_geo = "http://risis.eu/lens/{}".format(lens_geo)





# FOR SOME REASONS, STARDOG IS UNABLE TO RUN THE QUERY BELOW.
# THE ALTERNATIVE WAS TO CREATE THE UNION FIRST AND THEN RUN
# THE MINUS OVER THAT UNION. THIS IS QUERY-2
query_1 = """
PREFIX lens:<http://risis.eu/lens/>
PREFIX dataset:<http://risis.eu/dataset/>
# SELECT DISTINCT ?subj
SELECT (count(DISTINCT ?entity) as ?total)
{{
    BIND(<{0}> AS ?nameData)
    BIND(<{1}> AS ?geoData)

    {{
        # ORGREG UNIVERSITIES THAT ARE FOUND IN EITHER THE
        # NAME SIMILARITY LENS OR THE GEO SIMILARITY LENS
        GRAPH <{2}>
        {{
            # ?entity ?predicate ?value .
            ?entity a <http://risis.eu/orgreg_20170718/ontology/class/University> .
        }}
    }}
    MINUS
    {{
        # LENS FROM NAME SIMILARITY
        {{ GRAPH ?nameData {{ ?entity ?pred ?obj . }}}}
        UNION
        {{ GRAPH ?nameData {{ ?subj ?pred ?entity . }}}}
        UNION

        # LENS FROM GEO SIMILARITY
        {{ GRAPH ?geoData {{ ?entity ?pred ?obj . }}}}
        UNION
        {{ GRAPH ?geoData {{ ?subj ?pred ?entity . }}}}
    }}
}}
""".format(name_lens, geo_lens, Data.orgreg_GRAPH)
# print query_1

query_2 = """
PREFIX lens:<http://risis.eu/lens/>
PREFIX dataset:<http://risis.eu/dataset/>
# SELECT DISTINCT ?entity
SELECT (count(DISTINCT ?entity) as ?total)
{{
    BIND(<{0}> AS ?lens)
    {{
        GRAPH <{1}>
        {{
            ?entity a <http://risis.eu/orgreg_20170718/ontology/class/University> .
        }}
    }}
    MINUS
    {{
        {{ GRAPH ?lens {{ ?entity ?pred ?obj . }}}}
        UNION
        {{ GRAPH ?lens {{ ?subj ?pred ?entity . }}}}
    }}
}}
""".format(union_name, Data.orgreg_GRAPH)

# print query_2
# Qr.display_result(query=query_2, spacing=80, limit=10, is_activated=True)


query_3 = """
PREFIX lens:<http://risis.eu/lens/>
PREFIX dataset:<http://risis.eu/dataset/>
PREFIX property:<http://risis.eu/orgreg_20170718/ontology/predicate/>
#SELECT DISTINCT ?entity ?value
# SELECT ?entity (count(DISTINCT ?value) as ?total)
SELECT  ?value (count( ?value) as ?total)
{{

    {{
        BIND(<{0}> AS ?lens)
        {{
            GRAPH <{1}>
            {{
                ?entity a <http://risis.eu/orgreg_20170718/ontology/class/University> .
            }}
        }}
        MINUS
        {{
            {{ GRAPH ?lens {{ ?entity ?pred ?obj . }}}}
            UNION
            {{ GRAPH ?lens {{ ?subj ?pred ?entity . }}}}
        }}
    }}

    GRAPH {1}
    {{
        ?entity property:locationOf/property:Country_of_location ?value.
    }}
}} GROUP BY ?value ORDER BY ?value
""".format(union_name, Data.orgreg_GRAPH)
# print query_3
# Qr.display_result(query=query_3, spacing=50, limit=50, is_activated=True)


"""
PETER:

    For D25 I need a series of screen-shots of the disambiguation tool, plus some
    text explaining the steps and guiding the reader through the screen-shots

    For D8 we need still the description of the organisations we have in the data store:
    - What from OrgReg wo we cover? (number of organisations by type and country)
    - What from OrgRed do we miss in the open data? (number of organisations by type and country)
    - What do we additionally have in the open datasets (number of organisations by type and country)

    ORGREG CONTAINS               : 3201 UNIVERSITIES
    COVERAGE USING NAME           : 1922 UNIVERSITIES
    COVERAGE USING GEO SIM        : 1450 UNIVERSITIES
    OVERALL COVERAGE NAME + GEO   : |2512 - 3201| = 689

        ####################################################################################
        TABLE OF 12 Row(S) AND 1 Columns
        LIMIT IS SET TO 50 BUT COULD BE CHANGED WITH THE LIMIT PARAMETER.
        ####################################################################################

pred
##################################################
http://www.w3.org/1999/02/22-rdf-syntax-ns#type.................................
http://risis.eu/orgreg_20170718/ontology/predicate/Entity_ID....................
http://risis.eu/orgreg_20170718/ontology/predicate/Entity_current_name_English..
http://risis.eu/orgreg_20170718/ontology/predicate/Entity_foundation_year.......
http://risis.eu/orgreg_20170718/ontology/predicate/Remarks_on_foundation_year...
http://risis.eu/orgreg_20170718/ontology/predicate/Entity_closure_year..........
http://risis.eu/orgreg_20170718/ontology/predicate/Website_of_entity............
http://risis.eu/orgreg_20170718/ontology/predicate/Remarks_on_closure_year......
http://risis.eu/orgreg_20170718/ontology/predicate/characteristicsOf............
http://risis.eu/orgreg_20170718/ontology/predicate/parentOf.....................
http://risis.eu/orgreg_20170718/ontology/predicate/childOf......................
http://risis.eu/orgreg_20170718/ontology/predicate/locationOf...................


        UNIVERSITY DISTRIBUTION IN ORGREF
        ####################################################################################
        TABLE OF 29 Row(S) AND 2 Columns
        LIMIT IS SET TO 50 BUT COULD BE CHANGED WITH THE LIMIT PARAMETER.
        ####################################################################################

value                                              total
################################################## ##################################################
AT................................................ 104...............................................
BE................................................ 141...............................................
BG................................................ 63................................................
CH................................................ 66................................................
CY................................................ 59................................................
CZ................................................ 171...............................................
DE................................................ 576...............................................
DK................................................ 80................................................
EE................................................ 47................................................
ES................................................ 237...............................................
FI................................................ 88................................................
HR................................................ 64................................................
HU................................................ 150...............................................
IE................................................ 51................................................
IL................................................ 67................................................
IS................................................ 14................................................
IT................................................ 308...............................................
LI................................................ 2.................................................
LT................................................ 61................................................
LU................................................ 9.................................................
LV................................................ 55................................................
MT................................................ 3.................................................
NL................................................ 114...............................................
NO................................................ 128...............................................
PT................................................ 146...............................................
RO................................................ 121...............................................
SE................................................ 83................................................
SI................................................ 57................................................
SK................................................ 52................................................


        UNIVERSITY NOT COVERED BY GRID - ORGREF - ETER - H202 - LEIDEN
        ####################################################################################
        TABLE OF 26 Row(S) AND 2 Columns
        LIMIT IS SET TO 50 BUT COULD BE CHANGED WITH THE LIMIT PARAMETER.
        ####################################################################################

value                                              total
################################################## ##################################################
AT................................................ 13................................................
BE................................................ 29................................................
BG................................................ 1.................................................
CH................................................ 9.................................................
CY................................................ 4.................................................
CZ................................................ 11................................................
DE................................................ 203...............................................
DK................................................ 25................................................
EE................................................ 11................................................
ES................................................ 80................................................
FI................................................ 9.................................................
HR................................................ 1.................................................
HU................................................ 29................................................
IE................................................ 3.................................................
IL................................................ 13................................................
IS................................................ 1.................................................
IT................................................ 114...............................................
LT................................................ 9.................................................
LV................................................ 3.................................................
MT................................................ 1.................................................
NL................................................ 21................................................
NO................................................ 13................................................
PT................................................ 15................................................
RO................................................ 17................................................
SE................................................ 19................................................
SK................................................ 5.................................................

"""


# """ FUNCTION RETURNING GENERAL STATS ON ORGREG COVERAGE """
def coverage_query(merged_lens, dataset, distribution=True, minus=False, datasets_involve=False, activated=False):

    if activated is False:
        print "THE FUNCTION [coverage_query] IS NOT ACTIVATED."
        return None

    # FETCH ALL DATASETS INVOLVED IN THE LENS
    if datasets_involve is True:
        datasets_q = """
        SELECT DISTINCT ?datasets
        {{
            {}  void:target*/(void:subjectsTarget|void:objectsTarget) ?datasets.
        }}
        """.format(Ut.to_nt_format(merged_lens))
        # print datasets_q
        Qr.display_result(query=datasets_q, spacing=50, limit=50, is_activated=True)

    if distribution is False:
        distribution_str = ""
    else:
        print "\n>>> COMPUTING THE ORIGINAL DISTRIBUTION OF : {}".format(dataset)
        distribution_str = "# "

    if minus is True:
        if distribution is True:
            print ">>> WARNING: DISTRIBUTION MUST BE SET TO [FALSE] IF MINUS IS SET TO [TRUE]"
        minus_str = ""
    else:
        if distribution is True:
            print ">>> WARNING: FOR COVERAGE DISTRIBUTION, DISTRIBUTION MUST BE SET TO FALSE"
        else:
            print "\n>>> COVERAGE OF {}".format(dataset)
        minus_str = "# "

    query = """
PREFIX lens:<http://risis.eu/lens/>
PREFIX dataset:<http://risis.eu/dataset/>
PREFIX property:<http://risis.eu/orgreg_20170718/ontology/predicate/>
# SELECT DISTINCT ?entity ?country
SELECT ?country (count(DISTINCT ?entity) as ?total)
# SELECT  ?country (count( ?country) as ?total)
{{
    {{
        SELECT  DISTINCT  ?entity
        {{
            {{
                # ALL UNIVERSITIES IN ORGREG
                GRAPH <{1}>
                {{
                    ?entity a <http://risis.eu/orgreg_20170718/ontology/class/University> .
                }}
            }}
            {2}{3}MINUS # ==> FETCH ALL UNIVERSITIES IN THE ORGREG DATASET THAT ARE NOT FOUND
            {2}{{
            {2}     # LINKS (ENTITIES) FOUND FOR THE SIX DATASETS
            {2}     BIND(<{0}> AS ?lens)
            {2}     {{ GRAPH ?lens {{ ?entity ?pred ?obj . }}}}
            {2}     UNION
            {2}     {{ GRAPH ?lens {{ ?subj ?pred ?entity . }}}}
            {2}}}
        }}
    }}

    # FETCHING THE COUNTRY FOR EACH ORGANIZATION
    GRAPH <{1}>
    {{
        ?entity a <http://risis.eu/orgreg_20170718/ontology/class/University> .
        OPTIONAL {{ ?entity property:locationOf/property:Country_of_location ?_country. }}
        BIND (IF(bound(?_country), ?_country , "NONE") AS ?country)
    }}
}} GROUP BY ?country ORDER BY ?country
""".format(merged_lens, dataset, distribution_str, minus_str)
    # print query
    Qr.display_result(query=query, spacing=50, limit=50, is_activated=True)


# """ FUNCTION FOR UNIVERSITIES IN EACH OF THE DATASETS BUT IN A SPECIFIC COUNTRY """
def universities_in(file_path, country, activated=False):

    if activated is False:
        print "THE FUNCTION [universities_in] IS NOT ACTIVATED."
        return None

    query_filter = ""
    for i in range(0, len(country)):
        query_filter += "ucase(?country) = ucase(\"{}\")".format(country[i]) if i == 0 \
            else "|| ucase(?country) = ucase(\"{}\")".format(country[i])

    netherlands = """
    SELECT DISTINCT ?subj ?university
    {{
        VALUES ?name_pred
        {{
            <http://www.w3.org/2000/01/rdf-schema#label>
            <http://risis.eu/eter_2014/ontology/predicate/Institution_Name>
            <http://risis.eu/orgreg_20170718/ontology/predicate/Entity_current_name_English>
            <http://risis.eu/orgref_20170703/ontology/predicate/Name>
            <http://risis.eu/leidenRanking_2015/ontology/predicate/actor>
            <http://xmlns.com/foaf/0.1/name>
        }}

        GRAPH <{}>
        {{
            ?subj ?name_pred ?university .
            ?subj {} ?country .
            FILTER ({})
        }}
    }} ORDER BY ?university
    """

    # VARIABLES
    grid = "<http://www.grid.ac/ontology/hasAddress>/<http://www.grid.ac/ontology/countryCode>"
    eter = "<http://risis.eu/eter_2014/ontology/predicate/Country_Code>"
    orgreg = "<http://risis.eu/orgreg_20170718/ontology/predicate/characteristicsOf>" \
             "/<http://risis.eu/orgreg_20170718/ontology/predicate/Country_of_establishment>"
    orgref = "<http://risis.eu/orgref_20170703/ontology/predicate/Country>"
    leiden = "<http://risis.eu/leidenRanking_2015/ontology/predicate/country>"
    h2020 = "<http://risis.eu/cordisH2020/vocab/country>"

    countries = [leiden, eter, orgreg, orgref, h2020, grid]
    graphs = [Data.leiden_GRAPH, Data.eter_GRAPH,
              Data.orgreg_GRAPH, Data.orgref_GRAPH, Data.h2020_GRAPH, Data.grid_GRAPH]
    names = ["\n>>> LEIDEN", "\n>>> ETER", "\n>>> ORGREG", "\n>>> ORGREG", "\n>>> H2020", "\n>>> GRID"]
    results = ["", "", "", "", "", ""]
    size = 0
    excel = Builder.StringIO()

    # QUERY LOOP
    for i in range(0, 6):
        start = time.time()
        query = netherlands.format(graphs[i], countries[i], query_filter)
        # print query
        # Qr.display_result(query=query, spacing=50, limit=5, is_activated=True)
        results[i] = Qr.sparql_xml_to_matrix(query)
        temp_size = dict(results[i])["result"].__len__() - 1
        elapsed = str(datetime.timedelta(seconds=time.time() - start))
        sofar = str(datetime.timedelta(seconds=time.time() - begining))
        print "{} {} in {} and so far in [{}]".format(names[i], temp_size, elapsed, sofar)

        if temp_size > size:
            size = temp_size

    print "\n>>> MAX SIZE {}".format(size)

    for row in range(1, size + 1):
        excel.write(str(row) + "\t")

        # GO THROUGH EATCH RESULT
        for i in range(0, 6):
            query_results = dict(results[i])["result"]
            if row < len(query_results):
                elt = "{}\t{}".format(query_results[row][0], (query_results[row][1]).replace("\t", ""))
                excel.write(elt + "\t") if i < 5 else excel.write(elt + "\n")
            else:
                excel.write("\t\t") if i < 5 else excel.write("\t\t\n")

        # SAMPLE
        if row == 100:
            print "\n", excel.getvalue()
        #     break

    with open(name=file_path, mode="wb") as writer:
        writer.write(excel.getvalue())


# """ FUNCTION FOR EXTRACTING ENTITIES THAT CONNECT WITH ORGTEG FROM ALL OTHER DATASETS """
def university_connected(file_path, merged_lens, country_constraint, activated=False):

    if activated is False:
        print "THE FUNCTION [university_connected] IS NOT ACTIVATED."
        return None

    # VARIABLES
    grid = "<http://www.grid.ac/ontology/hasAddress>/<http://www.grid.ac/ontology/countryCode>"
    eter = "<http://risis.eu/eter_2014/ontology/predicate/Country_Code>"
    # orgreg = "<http://risis.eu/orgreg_20170718/ontology/predicate/characteristicsOf>" \
    #          "/<http://risis.eu/orgreg_20170718/ontology/predicate/Country_of_establishment>"
    orgref = "<http://risis.eu/orgref_20170703/ontology/predicate/Country>"
    leiden = "<http://risis.eu/leidenRanking_2015/ontology/predicate/country>"
    h2020 = "<http://risis.eu/cordisH2020/vocab/country>"

    country_predicates = [leiden, eter, orgref, h2020, grid]
    graphs = [Data.leiden_GRAPH, Data.eter_GRAPH, Data.orgref_GRAPH, Data.h2020_GRAPH, Data.grid_GRAPH]
    names = [">>> LEIDEN", ">>> ETER", ">>> ORGREF", ">>> H2020", ">>> GRID"]
    results = [{"result": None}, {"result": None}, {"result": None}, {"result": None}, {"result": None}]
    size = 0
    excel = Builder.StringIO()

    # 1. THE QUERY CONSTRAINT FILTER
    query_filter = ""
    for i in range(0, len(country_constraint)):
        query_filter += "ucase(?country) = ucase(\"{}\")".format(country_constraint[i]) if i == 0 \
            else " || ucase(?country) = ucase(\"{}\")".format(country_constraint[i])

    # 2. MAIN QUERY
    query = """
    PREFIX lens:<http://risis.eu/lens/>
    PREFIX dataset:<http://risis.eu/dataset/>
    PREFIX property:<http://risis.eu/orgreg_20170718/ontology/predicate/>
    PREFIX rsc:<http://risis.eu/orgreg_20170718/ontology/class/>
    SELECT DISTINCT ?entity ?university ?name
    {{
        {{
            SELECT  DISTINCT  ?entity ?university ?name
            {{

                # UNIVERSITIES IN ORGREG
                GRAPH <{4}>
                {{
                    ?orgreg_entity a rsc:University .
                    ?orgreg_entity  property:Entity_current_name_English ?name .
                }}

                # UNIVERSITIES CONNECTED
                GRAPH <{1}>
                {{
                    ?entity a ?type .
                }}

                # ALL UNIVERSITIES CONNECTED IN THE LENS
                BIND(<{0}> AS ?lens)
                {{ GRAPH ?lens {{ ?entity ?pred ?orgreg_entity . }}}}
                UNION
                {{ GRAPH ?lens {{ ?orgreg_entity ?pred ?entity . }}}}
            }}
        }}

        VALUES ?name_pred
        {{
            <http://www.w3.org/2000/01/rdf-schema#label>
            <http://risis.eu/eter_2014/ontology/predicate/Institution_Name>
            <http://risis.eu/orgreg_20170718/ontology/predicate/Entity_current_name_English>
            <http://risis.eu/orgref_20170703/ontology/predicate/Name>
            <http://risis.eu/leidenRanking_2015/ontology/predicate/actor>
            <http://xmlns.com/foaf/0.1/name>
        }}

        # FETCH ORGANIZATION URI AND NAME
        GRAPH <{1}>
        {{
            ?entity ?name_pred ?university .
            OPTIONAL {{ ?entity {2} ?_country . }}
            BIND (IF(bound(?_country), ?_country , "NONE") AS ?country)
            FILTER ({3})
        }}
    }} ORDER BY ?university
    """

    # QUERY LOOP
    for i in range(0, 5):

        # if i > 1:
        #     continue

        start = time.time()
        cur_query = query.format(merged_lens, graphs[i], country_predicates[i], query_filter, Data.orgreg_GRAPH)
        # print cur_query
        results[i] = Qr.sparql_xml_to_matrix(cur_query)
        # Qr.display_result(query=cur_query, spacing=50, limit=5, is_activated=True)
        temp_size = dict(results[i])["result"].__len__() - 1
        elapsed = str(datetime.timedelta(seconds=time.time() - start))
        sofar = str(datetime.timedelta(seconds=time.time() - begining))
        print "\n {} in {} and so far in [{}]".format(names[i], elapsed, sofar)
        if temp_size > size:
            size = temp_size
            # print cur_query
            # exit(0)

    print "\n >>> MAX SIZE {}".format(size)

    # GOING THROUGH THE SIX DATASETS
    for row in range(1, size + 1):

        excel.write(str(row) + "\t")

        # GO THROUGH EATCH RESULT
        for i in range(0, 5):

            query_results = dict(results[i])["result"]
            if query_results is not None and row < len(query_results):
                elt = "{}\t{}\t{}".format(query_results[row][0],
                                          query_results[row][1].replace("\t", ""),
                                          query_results[row][2].replace("\t", ""))
                excel.write(elt + "\t") if i < 4 else excel.write(elt + "\n")
            else:
                excel.write("\t\t\t") if i < 4 else excel.write("\t\t\n")

        # SAMPLE
        if row == 100:
            print "\n", excel.getvalue()
        #          break

    # SAMPLE
    # print "\n", excel.getvalue()

    with open(name=file_path, mode="wb") as writer:
        writer.write(excel.getvalue())


# """ FUNCTION FOR EXTRACTING ENTITIES THAT CONNECT WITH ORGTEG FROM ALL OTHER DATASETS """
def university_connected_geo(file_path, merged_lens, country_constraint, activated=False):

        if activated is False:
            print "THE FUNCTION [university_connected] IS NOT ACTIVATED."
            return None

        # VARIABLES
        grid = "<http://www.grid.ac/ontology/hasAddress>/<http://www.grid.ac/ontology/countryCode>"
        eter = "<http://risis.eu/eter_2014/ontology/predicate/Country_Code>"
        country_predicates = [eter, grid]
        graphs = [Data.eter_GRAPH, Data.grid_GRAPH]
        names = [">>> ETER", ">>> GRID"]
        results = [{"result": None}, {"result": None}]
        size = 0
        excel = Builder.StringIO()

        # 1. THE QUERY CONSTRAINT FILTER
        query_filter = ""
        for i in range(0, len(country_constraint)):
            query_filter += "ucase(?country) = ucase(\"{}\")".format(country_constraint[i]) if i == 0 \
                else " || ucase(?country) = ucase(\"{}\")".format(country_constraint[i])

        # 2. MAIN QUERY
        query = """
        PREFIX lens:<http://risis.eu/lens/>
        PREFIX dataset:<http://risis.eu/dataset/>
        PREFIX property:<http://risis.eu/orgreg_20170718/ontology/predicate/>
        PREFIX rsc:<http://risis.eu/orgreg_20170718/ontology/class/>
        SELECT DISTINCT ?entity ?university ?name
        {{
            {{
                SELECT  DISTINCT  ?entity ?university ?name
                {{

                    # UNIVERSITIES IN ORGREG
                    GRAPH <{4}>
                    {{
                        ?orgreg_entity a rsc:University .
                        ?orgreg_entity  property:Entity_current_name_English ?name .
                    }}

                    # UNIVERSITIES CONNECTED
                    GRAPH <{1}>
                    {{
                        ?entity a ?type .
                    }}

                    # ALL UNIVERSITIES CONNECTED IN THE LENS
                    BIND(<{0}> AS ?lens)
                    {{ GRAPH ?lens {{ ?entity ?pred ?orgreg_entity . }}}}
                    UNION
                    {{ GRAPH ?lens {{ ?orgreg_entity ?pred ?entity . }}}}
                }}
            }}

            VALUES ?name_pred
            {{
                <http://www.w3.org/2000/01/rdf-schema#label>
                <http://risis.eu/eter_2014/ontology/predicate/Institution_Name>
                <http://risis.eu/orgreg_20170718/ontology/predicate/Entity_current_name_English>
                <http://risis.eu/orgref_20170703/ontology/predicate/Name>
                <http://risis.eu/leidenRanking_2015/ontology/predicate/actor>
                <http://xmlns.com/foaf/0.1/name>
            }}

            # FETCH ORGANIZATION URI AND NAME
            GRAPH <{1}>
            {{
                ?entity ?name_pred ?university .
                OPTIONAL {{ ?entity {2} ?_country . }}
                BIND (IF(bound(?_country), ?_country , "NONE") AS ?country)
                FILTER ({3})
            }}
        }} ORDER BY ?university
        """

        # QUERY LOOP
        for i in range(0, 2):

            if i > 2:
                continue

            start = time.time()
            cur_query = query.format(merged_lens, graphs[i], country_predicates[i], query_filter, Data.orgreg_GRAPH)
            # print cur_query
            results[i] = Qr.sparql_xml_to_matrix(cur_query)
            # Qr.display_result(query=cur_query, spacing=50, limit=5, is_activated=True)
            temp_size = dict(results[i])["result"].__len__() - 1
            elapsed = str(datetime.timedelta(seconds=time.time() - start))
            sofar = str(datetime.timedelta(seconds=time.time() - begining))
            print "\n {} in {} and so far in [{}]".format(names[i], elapsed, sofar)
            if temp_size > size:
                size = temp_size
                # print cur_query
                # exit(0)

        print "\n >>> MAX SIZE {}".format(size)

        # GOING THROUGH THE SIX DATASETS
        for row in range(1, size + 1):

            excel.write(str(row) + "\t")

            # GO THROUGH EATCH RESULT
            for i in range(0, 2):

                query_results = dict(results[i])["result"]
                if query_results is not None and row < len(query_results):
                    elt = "{}\t{}\t{}".format(query_results[row][0],
                                              query_results[row][1].replace("\t", ""),
                                              query_results[row][2].replace("\t", ""))
                    excel.write(elt + "\t") if i < 1 else excel.write(elt + "\n")
                else:
                    excel.write("\t\t\t") if i < 1 else excel.write("\t\t\n")

            # SAMPLE
            if row == 100:
                print "\n", excel.getvalue()
                #          break

        # SAMPLE
        # print "\n", excel.getvalue()

        with open(name=file_path, mode="wb") as writer:
            writer.write(excel.getvalue())


# """ DISPLAYING PROPERTIES FROM A PARTICULAR GRAPH """
def properties(graph, datatype=None):

    comment = "# " if datatype is None else ""
    datatype = datatype if Ut.is_nt_format(datatype) is True else "<{}>".format(datatype)
    graph = graph if Ut.is_nt_format(graph) is True else "<{}>".format(graph)
    properties = """
    # <http://www.w3.org/1999/02/22-rdf-syntax-ns#type>
    SELECT DISTINCT ?predicate
    WHERE
    {{
        GRAPH {}
        {{
            {}?subj {} ?type .
            ?subj ?predicate ?obj .
        }}
    }}
    """.format(graph, comment, datatype)
    print properties
    Qr.display_result(query=properties, spacing=50, limit=0, is_activated=True)


overall_q = """
PREFIX dataset:<http://risis.eu/dataset/>
# SELECT DISTINCT ?entity
SELECT ( count(DISTINCT ?entity) as ?Total)
{{
    {{
        SELECT  DISTINCT ?entity
        {{
            VALUES ?datasets{{
                dataset:leidenRanking_2015
                dataset:h2020
                dataset:eter_2014
                dataset:orgreg_20170718
                dataset:orgref_20170703
                dataset:grid_20170712
            }}

            GRAPH ?datasets {{ ?entity ?subject ?values .}}
        }}
    }}


    BIND(<{0}> AS ?lens)
    {{
         {{ GRAPH ?lens {{ ?entity ?pred ?obj . }}}}
         UNION
        {{ GRAPH ?lens {{ ?subj ?pred ?entity . }}}}
    }}
    MINUS
    {{
        GRAPH <{1}>
        {{
            ?entity a <http://risis.eu/orgreg_20170718/ontology/class/University> .
        }}
    }}


}}
# """.format(union_name, Data.orgreg_GRAPH)
# print overall_q
# Qr.display_result(query=overall_q, spacing=50, limit=50, is_activated=True)



# properties(Data.grid_GRAPH, datatype="<http://www.w3.org/1999/02/22-rdf-syntax-ns#type>")


data = """
SELECT DISTINCT ?obj ?graph ?name
WHERE{{

    VALUES ?country
    {{
        <http://www.grid.ac/ontology/countryCode>
        <http://risis.eu/eter_2014/ontology/predicate/Country_Code>
        <http://risis.eu/orgref_20170703/ontology/predicate/Country>
        <http://risis.eu/cordisH2020/vocab/country>
        <http://risis.eu/leidenRanking_2015/ontology/predicate/country>
    }}

    VALUES ?graph
    {{
        <http://risis.eu/dataset/grid_20170712>
        <http://risis.eu/dataset/eter_2014>
        <http://risis.eu/dataset/orgreg_20170718>
        <http://risis.eu/dataset/orgref_20170703>
        <http://risis.eu/dataset/leidenRanking_2015>
        <http://risis.eu/dataset/h2020>
    }}

    VALUES ?name_pred
    {{
        <http://www.w3.org/2000/01/rdf-schema#label>
        <http://risis.eu/eter_2014/ontology/predicate/Institution_Name>
        <http://risis.eu/orgreg_20170718/ontology/predicate/Entity_current_name_English>
        <http://risis.eu/orgref_20170703/ontology/predicate/Name>
        <http://risis.eu/leidenRanking_2015/ontology/predicate/actor>
        <http://xmlns.com/foaf/0.1/name>
    }}

    {{
        GRAPH ?graph
        {{
            ?subj ?country ?obj .
            # ?subj ?name_pred ?name .
            # FILTER (?obj = "NL" || ?obj = "Netherlands")
        }}
    }}
    UNION
    {{
        GRAPH ?graph
        {{
            ?subj <http://risis.eu/orgreg_20170718/ontology/predicate/locationOf>/
            <http://risis.eu/orgreg_20170718/ontology/predicate/Country_of_location> ?obj .
            # ?subj ?name_pred ?name .
            # FILTER (?obj = "NL" || ?obj = "Netherlands")
        }}
    }}

    FILTER (?obj = "BE" || ?obj = "Belgium")
}}
"""
# Qr.display_result(query=data.format(Data.grid_GRAPH), spacing=50, limit=800, is_activated=True)


########################################################################
print "\n>>> GENERAL STATS"
########################################################################
coverage_query(union_name, Data.orgreg_GRAPH, distribution=True, minus=False, datasets_involve=True, activated=False)
coverage_query(union_name, Data.orgreg_GRAPH, distribution=False, minus=False, datasets_involve=False, activated=False)
coverage_query(union_name, Data.orgreg_GRAPH, distribution=False, minus=True, datasets_involve=False, activated=False)


########################################################################
print "\n>>> EXISTING ENTITIES"
# GENERATE UNIVERSITIES FILE FOR SPECIFIC COUNTRIES
########################################################################
f_path_1 = "C:\Productivity\LinkAnalysis\Coverage\coverageExisting-4-NETHERLANDS.csv"
f_path_2 = "C:\Productivity\LinkAnalysis\Coverage\coverageExisting-4-BELGIUM.csv"
universities_in(file_path=f_path_1, country=["NL", "Netherlands"], activated=False)
universities_in(file_path=f_path_2, country=["BE", "BELGIUM"], activated=False)


########################################################################
print "\n>>> MATCHED ENTITIES BY NAME SIMILARITY"
# GENERATE CONNECTED UNIVERSITIES FILES FOR SPECIFIC COUNTRIES
########################################################################
f_path_3 = "C:\Productivity\LinkAnalysis\Coverage\coverageNameConnected-4-NETHERLANDS.csv"
f_path_4 = "C:\Productivity\LinkAnalysis\Coverage\coverageNameConnected-4-BELGIUM.csv"
orgreg_pred = "<http://risis.eu/orgreg_20170718/ontology/predicate/characteristicsOf>" \
             "/<http://risis.eu/orgreg_20170718/ontology/predicate/Country_of_establishment>"
grid_pred = "<http://www.grid.ac/ontology/hasAddress>/<http://www.grid.ac/ontology/countryCode>"
university_connected(f_path_3, union_name, country_constraint=["NL", "Netherlands"], activated=False)
university_connected(f_path_4, union_name, country_constraint=["BE", "BELGIUM"], activated=False)


########################################################################
print "\n>>> MATCHED ENTITIES BY GEO SIMILARITY"
# GENERATE CONNECTED UNIVERSITIES FILES FOR SPECIFIC COUNTRIES
########################################################################
f_path_5 = "C:\Productivity\LinkAnalysis\Coverage\coverageGeoConnected-4-NETHERLANDS.csv"
f_path_6 = "C:\Productivity\LinkAnalysis\Coverage\coverageGeoConnected-4-BELGIUM.csv"
university_connected_geo(f_path_5, union_geo, country_constraint=["NL", "Netherlands"], activated=False)
university_connected_geo(f_path_6, union_geo, country_constraint=["BE", "BELGIUM"], activated=False)


"""
>>> COVERAGE

        ####################################################################################
        TABLE OF 19 Row(S) AND 2 Columns
        LIMIT IS SET TO 5 BUT COULD BE CHANGED WITH THE LIMIT PARAMETER.
        ####################################################################################

entity                                             university
################################################## ##################################################
http://risis.eu/leidenRanking_2015/resource/482... Delft University of Technology....................
http://risis.eu/leidenRanking_2015/resource/7307.. Deltares..........................................
http://risis.eu/leidenRanking_2015/resource/483... Eindhoven University of Technology................
http://risis.eu/leidenRanking_2015/resource/490... Erasmus University Rotterdam......................
http://risis.eu/leidenRanking_2015/resource/487... Leiden University.................................
0:01:21.824000

        ####################################################################################
        TABLE OF 56 Row(S) AND 2 Columns
        LIMIT IS SET TO 5 BUT COULD BE CHANGED WITH THE LIMIT PARAMETER.
        ####################################################################################

entity                                             university
################################################## ##################################################
http://risis.eu/eter_2014/resource/NL0021......... Amsterdamse Hogeschool voor de Kunsten............
http://risis.eu/eter_2014/resource/NL0022......... ArtEZ Hogeschool voor de Kunsten..................
http://risis.eu/eter_2014/resource/NL0023......... Avans Hogeschool..................................
http://risis.eu/eter_2014/resource/NL0026......... Christelijke Hogeschool Ede.......................
http://risis.eu/eter_2014/resource/NL0028......... Christelijke Hogeschool Windesheim................
0:01:01.251000

        ####################################################################################
        TABLE OF 8 Row(S) AND 2 Columns
        LIMIT IS SET TO 5 BUT COULD BE CHANGED WITH THE LIMIT PARAMETER.
        ####################################################################################

entity                                             university
################################################## ##################################################
http://risis.eu/orgreg_20170718/resource/NL0046... Amsterdam University of Applied Sciences..........
http://risis.eu/orgreg_20170718/resource/NL0047... HAN University of Applied Sciences................
http://risis.eu/orgreg_20170718/resource/NL0035... HAS University of Applied Sciences................
http://risis.eu/orgreg_20170718/resource/NL1032... Netherlands Organisation for Applied Scientific Research
http://risis.eu/orgreg_20170718/resource/NL1021... Netherlands Organisation for Scientific Research..
0:16:44.016000

        ####################################################################################
        TABLE OF 46 Row(S) AND 2 Columns
        LIMIT IS SET TO 5 BUT COULD BE CHANGED WITH THE LIMIT PARAMETER.
        ####################################################################################

entity                                             university
################################################## ##################################################
http://risis.eu/orgref_20170703/resource/8986821.. Academic Medical Center...........................
http://risis.eu/orgref_20170703/resource/648454... Avans University of Applied Sciences..............
http://risis.eu/orgref_20170703/resource/506063... Centrum Wiskunde & Informatica....................
http://risis.eu/orgref_20170703/resource/103244... Delft University of Technology....................
http://risis.eu/orgref_20170703/resource/3166402.. Design Academy Eindhoven..........................
0:53:47.251000

        ####################################################################################
        TABLE OF 9 Row(S) AND 2 Columns
        LIMIT IS SET TO 5 BUT COULD BE CHANGED WITH THE LIMIT PARAMETER.
        ####################################################################################

entity                                             university
################################################## ##################################################
http://risis.eu/cordisH2020/resource/participant_999839335 ERASMUS UNIVERSITEIT ROTTERDAM....................
http://risis.eu/cordisH2020/resource/participant_998530417 LOUIS BOLK INSTITUUT..............................
http://risis.eu/cordisH2020/resource/participant_998203527 Netherlands Forensic Institute....................
http://risis.eu/cordisH2020/resource/participant_999473936 ROESSINGH RESEARCH AND DEVELOPMENT BV.............
http://risis.eu/cordisH2020/resource/participant_990414039 STICHTING WETSUS, EUROPEAN CENTRE OF EXCELLENCE FOR
SUSTAINABLE WATER TECHNOLOGY
1:14:09.047000

        ####################################################################################
        TABLE OF 429 Row(S) AND 2 Columns
        LIMIT IS SET TO 5 BUT COULD BE CHANGED WITH THE LIMIT PARAMETER.
        ####################################################################################

entity                                             university
################################################## ##################################################
http://www.grid.ac/institutes/grid.450088.1....... AMN (Netherlands).................................
http://www.grid.ac/institutes/grid.482296.3....... AOMB Intellectual Property (Netherlands)..........
http://www.grid.ac/institutes/grid.482390.4....... AbbVie (Netherlands)..............................
http://www.grid.ac/institutes/grid.424087.d....... Academic Center for Dentistry Amsterdam...........
http://www.grid.ac/institutes/grid.5650.6......... Academic Medical Center...........................
4:24:27.697000
"""


def visit_data():

    # ETER
    eter_query = """
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX pred: <http://risis.eu/eter_2014/ontology/predicate/>
    SELECT *
    {{
        GRAPH <http://risis.eu/dataset/eter_2014>
        {{
            ?entity rdf:type                                            ?type ;
                    pred:ETER_ID_Year                                   ?year ;
                    pred:Institution_Name                               ?name ;

                    pred:Geographic_coordinates__latitude    ?lat ;
                    pred:Geographic_coordinates__longitude  ?long .
            OPTIONAL {{ ?entity pred:Total_number_of_full_professors    ?professors .}}
            OPTIONAL {{ ?entity pred:Total_academic_staff_FTE           ?academic_staff_FTE . }}
            OPTIONAL {{ ?entity pred:Total_academic_staff_HC            ?academic_staff_HC }}
            OPTIONAL {{ ?entity pred:Total_students_enrolled_at_ISCED_5 ?ISCED_5. }}
            OPTIONAL {{ ?entity pred:Total_students_enrolled_at_ISCED_6 ?ISCED_6. }}
            OPTIONAL {{ ?entity pred:Total_students_enrolled_at_ISCED_7 ?ISCED_7. }}
            OPTIONAL {{ ?entity pred:Total_students_enrolled_at_ISCED_8 ?ISCED_8. }}
        }}
    }} LIMIT 50
    """.format()
    print eter_query
    Qr.display_result(query=eter_query, spacing=50, limit=0, is_activated=True)

    grid_query = """
    PREFIX coord: <http://www.w3.org/2003/01/geo/wgs84_pos#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX pred: <http://www.grid.ac/ontology/>
    SELECT *
    {{
        GRAPH <http://risis.eu/dataset/grid_20180208>
        {{
            ?entity     rdf:type                    ?type ;
                        rdfs:label                  ?name .
            ?entity     pred:hasAddress/coord:long  ?long .
            ?entity     pred:hasAddress/coord:lat   ?lat .
        }}
    }} LIMIT 50
    """.format()
    print grid_query
    # Qr.display_result(query=grid_query, spacing=50, limit=0, is_activated=True)


    orgreg_query = """
    PREFIX pred: <http://risis.eu/orgreg_20170718/ontology/predicate/>
    SELECT *
    {{
        GRAPH <http://risis.eu/dataset/orgreg_20170718>
        {{
            ?entity     pred:characteristicsOf/pred:Type_of_entity                  ?type ;
                        pred:Entity_current_name_English                            ?name .
            ?entity     pred:locationOf/pred:Geographical_coordinates__latitude     ?long .
            ?entity     pred:locationOf/pred:Geographical_coordinates__longitude    ?lat .
        }}
    }} LIMIT 500
    """.format()
    # print orgreg_query
    # Qr.display_result(query=orgreg_query, spacing=50, limit=0, is_activated=True)

dbpedia_q0 = """
PREFIX prop:<http://dbpedia.org/property/>
PREFIX rdfs:<http://www.w3.org/2000/01/rdf-schema#>
SELECT DISTINCT ?name ?employees
{
    SERVICE <http://sparql.sms.risis.eu/>
    {
        select  *
        {
              GRAPH <http://risis.eu/dataset/dbpedia_organisation_20170823>
              {
                    ?subj rdfs:label ?value.

                    # EMPLOYEES DATA
                    { OPTIONAL { ?subj prop:numemployees        ?employees . } } UNION
                    { OPTIONAL { ?subj prop:numEmployee         ?employees . } }
                    OPTIONAL { ?subj prop:numEmployees        ?employees . }
                    OPTIONAL { ?subj prop:numberEmployees     ?employees . }
                    OPTIONAL { ?subj prop:num.OfEmployees     ?employees . }
                    OPTIONAL { ?subj prop:no.OfEmployees      ?employees . }
                    OPTIONAL { ?subj prop:numberOfEmployees   ?employees . }
                    OPTIONAL { ?subj prop:employees           ?employees . }
                    OPTIONAL { ?subj prop:totalEmployees      ?employees . }
                    OPTIONAL { ?subj prop:employee            ?employees . }
                    BIND(str(?value) as ?name )
              }
        } limit 10
    }
}
"""


dbpedia_q2 = """
PREFIX prop:<http://dbpedia.org/property/>
PREFIX rdfs:<http://www.w3.org/2000/01/rdf-schema#>
SELECT DISTINCT ?name ?employees
{
    SERVICE <http://sparql.sms.risis.eu/>
    {
        select  *
        {
              GRAPH <http://risis.eu/dataset/dbpedia_organisation_20170823>
              {
                    { ?subj rdfs:label         ?value. } union
                    { OPTIONAL { ?subj prop:numemployees        ?employees . } } union
                    { OPTIONAL { ?subj prop:numEmployee         ?employees . } } union
                    { OPTIONAL { ?subj prop:numEmployees        ?employees . } } union
                    { OPTIONAL { ?subj prop:numberEmployees     ?employees . } } union
                    { OPTIONAL { ?subj prop:num.OfEmployees     ?employees . } } union
                    { OPTIONAL { ?subj prop:no.OfEmployees      ?employees . } } union
                    { OPTIONAL { ?subj prop:numberOfEmployees   ?employees . } } union
                    { OPTIONAL { ?subj prop:employees           ?employees . } } union
                    { OPTIONAL { ?subj prop:totalEmployees      ?employees . } } union
                    { OPTIONAL { ?subj prop:employee            ?employees . } }

                BIND(str(?value) as ?name )
              }
        } limit 10
    }
}
"""

#
# "less than 10


dbpedia_q = """
PREFIX prop:<http://dbpedia.org/property/>
PREFIX rdfs:<http://www.w3.org/2000/01/rdf-schema#>
SELECT DISTINCT ?name ?employees
{
    SERVICE <http://sparql.sms.risis.eu/>
    {
        select  *
        {
            GRAPH <http://km.aifb.kit.edu/services/crunchbase>
            {
                ?subj ?prop        ?value.
            }
        } limit 10
    }
}
"""


crunch_base = """
PREFIX prop:<http://dbpedia.org/property/>
PREFIX rdfs:<http://www.w3.org/2000/01/rdf-schema#>
SELECT DISTINCT ?name ?employees
{
    SERVICE <http://sparql.sms.risis.eu/>
    {
        SELECT  DISTINCT ?name ?employees
        {
            { GRAPH <http://risis.eu/dataset/dbpedia_organisation_20170823>
                {
                    ?subj rdfs:label ?value.
                    BIND(str(?value) as ?name ) }} UNION

            { GRAPH <http://risis.eu/dataset/dbpedia_organisation_20170823>
                { ?subj prop:numemployees ?employees . } } UNION

            { GRAPH <http://risis.eu/dataset/dbpedia_organisation_20170823>
                { ?subj prop:numEmployees ?employees . } } UNION

            { GRAPH <http://risis.eu/dataset/dbpedia_organisation_20170823>
                { ?subj prop:numberEmployees ?employees . } } union

            { GRAPH <http://risis.eu/dataset/dbpedia_organisation_20170823>
                { ?subj prop:numberEmployees ?employees . } } UNION

            { GRAPH <http://risis.eu/dataset/dbpedia_organisation_20170823>
                { ?subj prop:num.OfEmployees ?employees . } } UNION

            { GRAPH <http://risis.eu/dataset/dbpedia_organisation_20170823>
                { ?subj prop:no.OfEmployees ?employees . } } UNION

            { GRAPH <http://risis.eu/dataset/dbpedia_organisation_20170823>
                { ?subj prop:numberOfEmployees ?employees . } } UNION

            { GRAPH <http://risis.eu/dataset/dbpedia_organisation_20170823>
                { ?subj prop:employees  ?employees . } } UNION

            { GRAPH <http://risis.eu/dataset/dbpedia_organisation_20170823>
                { ?subj prop:totalEmployees ?employees . } } UNION

            { GRAPH <http://risis.eu/dataset/dbpedia_organisation_20170823>
                { ?subj prop:employee ?employees . } }

        }  LIMIT 10
    }
}
"""



# print dbpedia_q0
# Qr.remote_endpoint_request(query=dbpedia_q0, endpoint_url="http://sparql.sms.risis.eu/")
#

print "\n{}\n{:>90}\n{}\n".format(_line, date.strftime(_format), _line)


# INSTALL PYTHON 2.7.12
# INSTALL GIT
# INSTALL STARDOG
# INSTALL VIRTUAL ENVIRONMENT
# INSTALL PIP
# CLONED DIRECTORY




# max_v = divmod(python_version, 10)[0] + 1
# temp_max = str(max_v)
# for i in range(0, len(str(max_v))):
#     temp_max += "0"
# max_v = int(temp_max)
# print python, pip, env
# pip install --upgrade pip (MAC)
# exit(0)
#

