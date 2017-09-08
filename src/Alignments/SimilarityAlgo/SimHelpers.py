# encoding=utf-8


import re
import Alignments.Query as Qry
from operator import itemgetter
import Alignments.Utility as Ut
import Alignments.Settings as St
import Alignments.NameSpace as Ns
from kitchen.text.converters import to_unicode, to_bytes
import Alignments.Server_Settings as Ss
DIRECTORY = Ss.settings[St.linkset_Approx_dir]

LIMIT = ""
# LIMIT = "LIMIT 20000"
prefix = "@prefix alivocab:\t<{}> .\n" \
         "@prefix linkset:\t<{}> .\n" \
         "@prefix singletons:\t<{}> .\n".format(Ns.alivocab, Ns.linkset, Ns.singletons)

#################################################################
# HELPER FUNCTIONS
#################################################################

writers = None
stop_word = dict()
stop_words_string = ""
stop_symbols_string = ""
remove_term_in_bracket = False

data = {
    'biggest_freq': 0,
    'biggest_freq_token': "",
    'delta': 0}


def term_2_remove(universe_tf):
    t2r_dict = dict()
    for key, value in universe_tf.items():
        if value >= data['delta']:
            t2r_dict[key] = value
    return t2r_dict


def set_writers(specs):
    # SET THE PATH WHERE THE LINKSET WILL BE SAVED AND GET THE WRITERS
    print DIRECTORY
    writers = Ut.get_writers(specs[St.linkset_name], directory=DIRECTORY)
    for key, writer in writers.items():
        # BECAUSE THE DICTIONARY ALSO CONTAINS OUTPUT PATH
        if type(writer) is not str:
            if key is not St.batch_writer and key is not St.meta_writer:
                writer.write(prefix)
            if key is St.crpdce_writer:
                writer.write("\nlinkset:{}\n{{\n".format(specs[St.linkset_name]))
            elif key is St.singletons_writer:
                writer.write("\nsingletons:{}\n{{".format(specs[St.linkset_name]))
    return writers


def set_stop_word_dic():
    # STOP WORD DICTIONARY

    if stop_words_string is not None and len(stop_words_string) > 0:
        _stop_words_string = stop_words_string.lower()
        stw_split = str(_stop_words_string).split(' ')
        for stop in stw_split:
            if stop not in stop_word:
                stop_word[stop] = stop


# HELPER FOR EXTRACTING SPA VALUES FROM A GRAPH
def get_table(dataset_specs, reducer=None):
    # ADD THE REDUCER IF SET. THE REDUCER OR (DATASET REDUCER) HELPS ELIMINATING
    # THE COMPUTATION OF SIMILARITY FOR INSTANCES THAT WHERE ALREADY MATCHED
    print "LOADING: {}".format(dataset_specs[St.graph])
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


# HELPER FOR CREATING A CORRESPONDENCE
def correspondence(description, in_writers, counter):

    # GENERATE CORRESPONDENCE
    in_crpdce = "\n\t### Instance [{5}]\n\t<{0}> \t\t{1}_{2}_{3} \t\t<{4}> .\n".format(
        description[St.src_resource], description[St.link],
        description[St.row], description[St.inv_index], description[St.trg_resource], counter)
    # WRITE CORRESPONDENCE TO FILE
    # print in_crpdce
    in_writers[St.crpdce_writer].write(to_unicode(in_crpdce))

    # GENERATE SINGLETONS METADATA
    singleton = "\n\t### Instance [{8}]\n\t{1}_{2}_{3}\n\t\t" \
                "alivocab:hasStrength \t\t{5} ;" \
                "\n\t\talivocab:hasEvidence  \t\t\"\"\"[{6}] was compared to [{7}]\"\"\" .\n". \
        format(description[St.src_resource], description[St.link], description[St.row],
               description[St.inv_index], description[St.trg_resource], description[St.sim],
               description[St.src_value], description[St.trg_value], counter)
    in_writers[St.singletons_writer].write(to_unicode(singleton))
    # WRITE SINGLETON EVIDENCE TO FILE
    return in_crpdce + singleton


def get_tf(datasets):
    print "COMPUTING TERM FREQUENCY"
    # Qry.display_matrix(matrix, is_activated=True)
    # print matrix
    # datasets = [matrix_src, matrix_trg]
    term_frequency = dict()
    for matrix in datasets:
        # print "DATASETS:", matrix
        for r in range(1, len(matrix)):
            # print "matrix[row]:", matrix[row]

            # REMOVE DATA IN BRACKETS, STOP WORDS, AND STOP SYMBOLS
            in_tokens = process_input((matrix[r][1]))

            # TOKENIZE
            in_tokens = in_tokens.split(" ")

            # COMPUTE FREQUENCY
            for t in in_tokens:
                if t not in term_frequency:
                    term_frequency[t] = 1
                else:
                    term_frequency[t] += 1
                    if term_frequency[t] > data['biggest_freq']:
                        data['biggest_freq'] = term_frequency[t]
                        data['biggest_freq_token'] = t

    return term_frequency


def get_inverted_index(matrix, tf, threshold):

    # INVERTED INDEX DICTIONARY
    inv_index = dict()

    for in_row in range(1, len(matrix)):

        # GET THE VALUE
        value = str(matrix[in_row][1])

        # REMOVE DATA IN BRACKETS, STOP WORDS, AND STOP SYMBOLS
        value = process_input(value)

        # GET THE TOKENS
        in_tokens = value.split(" ")

        # COMPUTE THE NUMBER OF TOKENS TO INCLUDE
        included = len(in_tokens) - (int(threshold * len(in_tokens)) - 1)

        # UPDATE THE TOKENS WITH THEIR FREQUENCY
        # print "1", in_tokens
        for n in range(len(in_tokens)):
            # print value + " | +" + tokens[i]
            in_tokens[n] = [in_tokens[n], tf[in_tokens[n]]]

        # SORT THE TOKENS BASED ON THEIR FREQUENCY OF OCCURRENCES
        in_tokens = sorted(in_tokens, key=itemgetter(1))
        # print "{} {}".format(in_row, in_tokens)
        # print "2", in_tokens

        # INSERTING included TOKENS IN THE INVERTED INDEX
        for t in in_tokens[:included]:
            if t[0] not in inv_index:
                # THE INVERTED INDEX DICTIONARY HAS A TUPLE OF AN [ARRAY OF INDEXES] AND A [TERM FREQUENCY]
                inv_index[t[0]] = [in_row]
            elif in_row not in inv_index[t[0]]:
                # UPDATE THE INDEX ARRAY AND INCREMENT THE TERM FREQUENCY
                inv_index[t[0]] += [in_row]

    return inv_index


def get_tokens_to_include(string, threshold, tf):

    # GET THE TOKENS
    stg = str(string).lower()
    # print stg

    # REMOVE DATA IN BRACKETS, STOP WORDS, AND STOP SYMBOLS
    stg = process_input(stg)

    # if stg != to_unicode(string):
    #     print stg + "!!!!!!!!!"

    in_tokens = stg.split(" ")
    # COMPUTE THE NUMBER OF TOKENS TO INCLUDE
    included = len(in_tokens) - (int(threshold * len(in_tokens)) - 1) \
        if int(threshold * len(in_tokens)) > 1 else len(in_tokens)
    # included = len(in_tokens)

    # UPDATE THE TOKENS WITH THEIR FREQUENCY
    for k in range(len(in_tokens)):
        in_tokens[k] = [in_tokens[k], tf[in_tokens[k]]]

    # SORT THE TOKENS BASED ON THEIR FREQUENCY OF OCCURRENCES
    in_tokens = sorted(in_tokens, key=itemgetter(1))
    return in_tokens[:included]


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


def remove_stop_words(text):
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


def process_input(text):

    try:
        temp = to_bytes(text.lower())

        # temp = str(temp).decode(encoding="utf-8")

        # REMOVE DATA IN BRACKETS
        # REMOVE (....) FROM THE VALUE
        if remove_term_in_bracket is True:
            temp = remove_info_in_bracket(temp)

        # REMOVE STOP WORLD
        if len(stop_word) > 0:
            temp = remove_stop_words(temp)

        # REMOVE SYMBOLS OR CHARACTER
        if stop_symbols_string is not None and len(stop_symbols_string) > 0:
            pattern = str("[{}]".format(str(stop_symbols_string).strip())).replace(" ", "")
            temp = re.sub(pattern, "", temp)

        return temp.strip()

    except Exception as error:
        print "!!!!!!!!!!!!! PROBLEM !!!!!!!!!!!!!!!!!!!"
        print str(error.message)
        return text


def get_corr_reducer(graph):
    query = """
    SELECT ?uri1 ?uri2
    {{
        GRAPH <{}>
        {{
            ?uri1    ?p    ?uri2 .
        }}
    }}""".format(graph)
    alignment = Qry.sparql_xml_to_matrix(query)
    table_matrix = alignment[St.result]
    reducer_dict = {}
    if len(table_matrix) > 0:
        for row in table_matrix[1:]:
            src_uri = row[0].strip()
            trg_uri = row[1].strip()
            if len(row) == 2 and (src_uri, trg_uri) not in reducer_dict:
                reducer_dict[(src_uri, trg_uri)] = 1
    return reducer_dict
