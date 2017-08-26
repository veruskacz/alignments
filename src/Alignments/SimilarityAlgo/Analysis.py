# encoding=utf-8


import re
from time import time, ctime, gmtime
import Alignments.NameSpace as Ns
import Alignments.Query as Qry
import Alignments.Utility as Ut
import Alignments.Settings as St
from kitchen.text.converters import to_bytes, to_unicode
import Alignments.Server_Settings as Ss
DIRECTORY = Ss.settings[St.linkset_Approx_dir]

LIMIT = ""
# LIMIT = "LIMIT 100"


def get_tf(specs, is_token=True,
           stop_words_string="THE FOR IN THAT AND OF ON DE LA LES ltd inc", stop_symbols_string = "\.\-\,\+'\?"):

    term_frequency = dict()

    # DISPLAY SPECS
    print "\n1. SPECS\n\tGRAPH     : {}\n\tTRIPLES   : {}\n\tPREDICATE : {}\n\tIS TOKEN  : {}".format(
        specs[St.graph], specs[St.entity_datatype], specs[St.aligns], str(is_token).upper())

    # LOADING DATA
    print "\n2. LOADING THE DATA..."
    start = time()
    matrix = get_table(specs, reducer=None)
    t_load = time()
    print "DATASET STATS\n\t>>> LOADED IN         : {}\n\t>>> DATASET SIZE      : {}".format(
        t_load - start, len(matrix) - 1)

    stop_word = dict()
    stop_words_string = stop_words_string.lower()
    if stop_words_string is not None and len(stop_words_string) > 0:
        stw_split = str(stop_words_string).split(' ')
        for stop in stw_split:
            if stop not in stop_word:
                stop_word[stop] = stop

    # COMPUTING THE FREQUENCIES
    for r in range(1, len(matrix)):

        # REMOVE DATA IN BRACKETS
        in_tokens = process_input((matrix[r][1]), stop_word, stop_symbols_string)
        in_tokens = in_tokens.strip()

        if is_token is True:

            # TOKENIZE
            in_tokens = in_tokens.split(" ")

            # COMPUTE FREQUENCY
            for t in in_tokens:

                if t:
                    if t not in term_frequency:
                        term_frequency[t] = 1
                    else:
                        term_frequency[t] += 1

        else:
            if in_tokens not in term_frequency:
                term_frequency[in_tokens] = 1
            else:
                term_frequency[in_tokens] += 1


    print "\n3. LOAD SAMPLE"

    list = []
    count = 0
    biggest = 0
    term = ""
    start = time()
    if term_frequency:
        for token, frequency in term_frequency.items():

            count += 1

            if frequency > biggest:
                biggest = frequency
                term = token

            if frequency > 1:
                list += [{"text":token, "freq": frequency}]

            if count < 11:
                print "\t{}".format(str({"text": to_unicode(token), "freq": frequency}))

    t_load = time()

    print "\n4. FREQUENCY STATS.\n\t>>> LOADED IN         : {}" \
          "\n\t>>> ITEM SIZE         : {}\n\t>>> BIGGEST FREQUENCY : {} | {}".format(
        t_load - start, len(term_frequency), biggest, term)

    print "\nJOB DONE!!!!"
    # return term_frequency
    return list


# HELPER FOR EXTRACTING SPA VALUES FROM A GRAPH
def get_table(dataset_specs, reducer=None):
    # ADD THE REDUCER IF SET
    if reducer is None:
        reducer_comment = "#"
        reducer = ""
    else:
        reducer_comment = ""
        reducer = reducer
    aligns = dataset_specs[St.aligns] if Ut.is_nt_format(dataset_specs[St.aligns]) \
        else "<{}>".format(dataset_specs[St.aligns])
    query = """
    SELECT DISTINCT *
    {{
        GRAPH <{0}>
        {{
            ?subject
                a       <{1}> ;
                {2}    ?object .
        }}
        {4}FILTER NOT EXISTS
        {4}{{
        {4}    GRAPH <{3}>
        {4}    {{
        {4}        {{ ?subject   ?pred   ?obj . }}
        {4}        UNION
        {4}        {{ ?obj   ?pred   ?subject. }}
        {4}    }}
        {4}}}
    }} {5}
    """.format(
        dataset_specs[St.graph], dataset_specs[St.entity_datatype], aligns,
        reducer, reducer_comment, LIMIT)
    table_matrix = Qry.sparql_xml_to_matrix(query)
    # Qry.display_matrix(table_matrix, is_activated=True)
    # print table_matrix
    # print query
    return table_matrix[St.result]


def process_input(text, stop_word, stop_symbols_string):

    try:
        temp = to_bytes(text.lower())

        # temp = str(temp).decode(encoding="utf-8")

        # REMOVE DATA IN BRACKETS
        # REMOVE (....) FROM THE VALUE
        temp = remove_info_in_bracket(temp)

        # REMOVE STOP WORLD
        if len(stop_word) > 0:
            temp = remove_stop_words(temp, stop_word)

        # REMOVE SYMBOLS OR CHARACTER
        if stop_symbols_string is not None and len(stop_symbols_string) > 0:
            pattern = str("[{}]".format(str(stop_symbols_string).strip())).replace(" ", "")
            temp = re.sub(pattern, "", temp)

        return to_unicode(temp)

    except Exception as error:
        print "!!!!!!!!!!!!! PROBLEM !!!!!!!!!!!!!!!!!!!"
        print str(error.message)
        return text


def remove_stop_words(text, stop_word):

    # print text
    if len(stop_word) > 0:
        for stop_key, value in stop_word.items():
            two = " {}".format(stop_key)
            one = "{} ".format(stop_key)
            three = " {} ".format(stop_key)
            if str(text).startswith(one):
                text = str(text).replace(one, "")
            elif str(text).endswith(two):
                text = str(text).replace(two, "")
            text = str(text).replace(three, " ")
        # print text
        return text


def remove_info_in_bracket(text):

    # text = "(Germany) 3M (United Kingdom) (Israel) in  (Canada) (France)"

    temp = str(text)

    if temp:

        pattern = re.findall('( *\(.*?\) *)', temp, re.S)

        for item in pattern:

            # print temp

            if item.endswith(" ") and item.startswith(" "):
                temp = str(temp).replace(item, " ", 1)
                # print "both sides"
                # print text

            elif item.startswith(" ") is not True and item.endswith(" "):
                temp = str(temp).replace(item, "", 1)
                # print "right side"
                # print text

            elif item.startswith(" ") is True and item.endswith(" ") is not True:
                temp = str(temp).replace(item, "", 1)
                # print "left side"
                # print text

            else:
                temp = str(temp).replace(item, "", 1)
                # print "None"
                # print text

        temp = str(temp).strip()

    return temp


# QUERY THAT COMPUTES STATISTICS OVER THE ALIGNMENTS INVOLVING A PARTICULAR DATASET
def ds_stats(dataset, datatype, display = True, optionalLabel=True):

    # QUERY THAT COMPUTES STATISTICS OVER THE ALIGNMENTS INVOLVING A PARTICULAR DATASET

    commentOptLbl = '' if optionalLabel else '#'
    query = """
    PREFIX void: <http://rdfs.org/ns/void#>
    PREFIX bdb: <http://vocabularies.bridgedb.org/ops#>
    PREFIX dataset: <http://risis.eu/dataset/>
    PREFIX foaf: <http://xmlns.com/foaf/0.1/>
    PREFIX ll: <http://risis.eu/alignment/predicate/>
    PREFIX skos:        <{2}>

    SELECT DISTINCT ?dataset ?alignsMechanism
    (COUNT(DISTINCT ?RESOURCE) as ?total) ?subTotal
    (ROUND((?subTotal / COUNT(DISTINCT ?RESOURCE) ) *10000)/100 as ?percentage) ?linkset ?linkset_uri
    {{
        graph <{0}>
        {{
            ?RESOURCE a <{1}> .
        }}

        ?linkset_uri
             void:subjectsTarget|void:objectsTarget 	<{0}>  ;
             bdb:subjectsDatatype|bdb:objectsDatatype		<{1}> .
        {3}OPTIONAL
        {{ graph ?rq
            {{
                ?linkset_uri skos:prefLabel ?lkst_label
            }}
         }}
         BIND (IF(bound(?lkst_label), ?lkst_label , ?linkset_uri) AS ?linkset)

	    {{
            SELECT (count(DISTINCT ?RESOURCE) as ?subTotal) ?linkset_uri ?dataset ?alignsMechanism
            {{
                ?linkset_uri
                    bdb:subjectsDatatype 	<{1}>  ;
                    void:subjectsTarget		<{0}> ;
                    void:objectsTarget		?dataset ;
                    ll:alignsMechanism      ?alignsMechanism .

                graph ?linkset_uri
                {{
                    {{ ?RESOURCE ?SING ?oResource. }}
                    UNION
                    {{ ?oResource ?SING ?RESOURCE . }}
                }}
                FILTER (<{0}> = ?dataset)
            }} GROUP BY ?linkset_uri ?dataset ?alignsMechanism
	    }}
	    UNION
	    {{
            SELECT (count(DISTINCT ?RESOURCE) as ?subTotal) ?linkset_uri ?dataset ?alignsMechanism
            {{
                ?linkset_uri
                    bdb:subjectsDatatype 	<{1}>  ;
                    void:subjectsTarget		<{0}> ;
                    void:objectsTarget		?dataset ;
                    ll:alignsMechanism      ?alignsMechanism .

                graph ?linkset_uri
                {{
                    ?RESOURCE ?SING ?oResource.
                }}
                FILTER (<{0}> != ?dataset)
            }} GROUP BY ?linkset_uri ?dataset ?alignsMechanism
        }}
        UNION
        {{
            SELECT (count(DISTINCT ?RESOURCE) as ?subTotal) ?linkset_uri ?dataset ?alignsMechanism
            {{
                ?linkset_uri
                    bdb:objectsDatatype 	<{1}>  ;
                    void:objectsTarget		<{0}> ;
                    void:subjectsTarget		?dataset ;
                    ll:alignsMechanism ?alignsMechanism .

                graph ?linkset_uri
                {{
                    ?oResource ?SING ?RESOURCE .
                }}
                FILTER (<{0}> != ?dataset)
            }} GROUP BY ?linkset_uri ?dataset ?alignsMechanism
        }}
    }}
    GROUP BY ?linkset ?subTotal ?dataset ?alignsMechanism ?linkset_uri having (?subTotal > 0)
    ORDER BY ?dataset ?alignsMechanism
    """.format(dataset, datatype, Ns.skos, commentOptLbl)
    # print query
    if display == True:
        Qry.display_result(query=query, spacing=100, is_activated=True)
    return query


def linkset_stats(linkset):

    query = """
    PREFIX void: <http://rdfs.org/ns/void#>
    PREFIX bdb: <http://vocabularies.bridgedb.org/ops#>
    PREFIX ll: <http://risis.eu/alignment/predicate/>
    SELECT DISTINCT ?dataset ?datatype ?alignsMechanism ?total
    (COUNT (DISTINCT ?RESOURCE) as ?subtotal)
    (ROUND((COUNT(DISTINCT ?RESOURCE) / ?total)*10000)  /100 as ?percentage)
    {{
        <{0}> ll:alignsMechanism ?alignsMechanism .
        {{
            <{0}>
                bdb:subjectsDatatype 	?datatype ;
                void:subjectsTarget		?dataset .

            graph <{0}>
            {{
                ?RESOURCE ?p ?o .
            }}
        }}
        UNION
        {{
            <{0}>
                bdb:objectsDatatype 	?datatype ;
                void:objectsTarget		?dataset .

            graph <{0}>
            {{
                ?o ?p ?RESOURCE .
            }}
        }}

        {{
            SELECT (COUNT(DISTINCT ?RESOURCE) as ?total) ?dataset  ?datatype
            {{
                graph ?dataset
                {{
                    ?RESOURCE a ?datatype .
                }}
            }} GROUP BY ?dataset ?datatype
        }}
    }} GROUP BY ?dataset ?datatype ?total ?alignsMechanism
    """.format(linkset)
    Qry.display_result(query=query, spacing=60, is_activated=True)

# ds_stats("http://risis.eu/dataset/h2020", "http://xmlns.com/foaf/0.1/Organization")
# linkset_stats("http://risis.eu/linkset/h2020_grid_20170712_exactStrSim_Organization_name_N1178738974")

# spec = {
#     St.graph: "http:risis.eu/dataset/openAire_20170816",
#     St.entity_datatype: "{}".format(Ns.foaf),
#     St.aligns: "{}prefLabel".format(Ns.skos)
# }

# result = get_tf(spec, is_token=True)

# print ds_stats("http://risis.eu/dataset/grid_20170712", datatype="http://xmlns.com/foaf/0.1/Organization")

