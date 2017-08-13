# encoding=utf-8

import os
import re
import cStringIO as Buffer
# from sys import maxint
import Alignments.Query as Qry
from operator import itemgetter
import Alignments.Utility as Ut
import Alignments.Settings as St
import Alignments.NameSpace as Ns
from time import time, ctime, gmtime
import Alignments.GenericMetadata as Gn
import Alignments.Linksets.Linkset as Ls
import Alignments.UserActivities.UserRQ as Urq
from kitchen.text.converters import to_unicode, to_bytes
from Alignments.CheckRDFFile import check_rdf_file
import Alignments.Server_Settings as Svr
import Alignments.Server_Settings as Ss
DIRECTORY = Ss.settings[St.linkset_Approx_dir]


LIMIT = ""
# LIMIT = "LIMIT 2000"

# /***************************************************************************************************************
# * INDEXING TECHNIQUES (1)
# * SCALING UP STRING MATCHING : Plain Inverted Index over data table Y
# * IMPLEMENTED WITH C# built in  Dictionary
# ***************************************************************************************************************/


def inverted_index(specs, theta):
    start = time()
    count = 0
    print "Started at {}".format(start)
    source = specs[St.source]
    target = specs[St.target]
    dataset = None
    index = dict()
    """
    BACKGROUND

    This technique first converts each string y ∈ Y into a document and then builds an inverted
    index over these document. Given a term t ∈ X, we can use the index to quickly find the list
    of documents created from Y that contain X, and hence the string in Y that contain t.
    Given a string x ∈ X, the method [Find Candidates] uses the inverted index to quickly locate the set
    of strings in Y that share at least one term with x. Continuing with the example below,
    gives x = {lake, mendota}, we use the index in the table below to find and merge the ID lists
    for lake and mendota to obtain the umbrella Z = {4, 6}
                                                 -------------------------
    set X                                        | Terms in Y | ID Lists |
    --------------------------------             |------------|----------|
    1: {lake, mendota}                           | area       |  5       |
    2: {lake, monona, area}                      |------------|----------|
    3: {lake, mendota, monona, dane}             | lake       |  4.6     |
                                                 |------------|----------|
    set Y                                        | mendota    |  6       |
    --------------------------------             |------------|----------|
    4: {lake, monona, university}                | monona     |  4,5,6   |
    5: {monona, research, area}                  |------------|----------|
    6: {lake, mendota, monona, area}             | research   |  5       |
                                                 |------------|----------|
                                                 | universit  |  4       |
                                                 -------------------------
    Limitations
    1. The inverted list of some terms (e.g stop words) can be very long, so building and
    manipulating such list are quite costly. ==> this problem is reduced when the data is pre-processed

    2. The method requires enumerating all pairs of strings that share at least one term. The set
    of such pair can be very long in practice.

    ASSUMPTIONS
        1. The input data set is already pre-processed and all tokens are separated with the space
        character
        2. All cells in attributes are of type string
        3. The inverted list use the pipe character '|' as document ID separator
    """

    """ Converts each string y ∈ Y into a document and then builds an inverted index over these document. """

    #################################################################
    # HELPER FUNCTIONS
    #################################################################

    # HELPER FOR EXTRACTING SPA VALUES FROM A GRAPH
    def get_table(dataset_specs):
        query = """
        SELECT *
        {{
            GRAPH <{}>
            {{
                ?subject    <{}>    ?object .
            }}
        }} limit  {}
        """.format(dataset_specs[St.graph], dataset_specs[St.aligns], LIMIT)
        table_matrix = Qry.sparql_xml_to_matrix(query)
        # print table_matrix
        return table_matrix

    # HELPER FOR CREATING A CORRESPONDENCE
    # def correspondence(description, writers):
    #     # GENERATE CORRESPONDENCE
    #     crpdce = "\t<{0}> \t\t{1}_{2}_{3} \t\t<{4}> .\n".format(
    #         description[St.src_resource], description[St.link],
    #         description[St.row], description[St.inv_index], description[St.trg_resource])
    #     # WRITE CORRESPONDENCE TO FILE
    #     writers[St.crpdce_writer].write(to_unicode(crpdce))
    #
    #     # GENERATE SINGLETONS METADATA
    #     singleton = "\n\t{1}_{2}_{3}\n\t\t" \
    #                 "alivocab:hasStrength \t\t{5} ;" \
    #                 "\n\t\talivocab:hasEvidence  \t\t\"[{6}] was compared to [{7}]\" .\n".\
    #         format(description[St.src_resource], description[St.link], description[St.row],
    #                description[St.inv_index], description[St.trg_resource], description[St.sim],
    #                description[St.src_value], description[St.trg_value])
    #     writers[St.singletons_writer].write(to_unicode(singleton))
    #     # WRITE SINGLETON EVIDENCE TO FILE
    #     return crpdce + singleton

    #################################################################
    # CREATING THE  INVERTED INDEX
    #################################################################

    """
    1. GET PREDICATE VALUES AS PREPARATION FOR THE TABLE INPUT
    """
    src_dataset = get_table(source)
    trg_dataset = get_table(target)
    iteration = 0

    """
    2. MERGE THE DATASETS (PREDICATE VALUE GENERATED ABOVE)
    """
    if (src_dataset is not None) and (trg_dataset is not None):
        dataset = src_dataset + trg_dataset[1:]
        iteration = len(src_dataset)
        # DISPLAY THE MERGE IN ACTIVATE IS TRUE
        Qry.display_matrix(dataset, is_activated=False)
        print ""
    elif (src_dataset is not None) and (trg_dataset is None):
        print "WE COULD NOT EXTRACT PREDICATE VALUES FROM THE TARGET DATASET"
        return None
    elif (src_dataset is None) and (trg_dataset is not None):
        print "WE COULD NOT EXTRACT PREDICATE VALUES FROM THE SOURCE DATASET"
        return None

    """
    3. GENERATE THE INVERTED INDEX USING THE PREDICATE VALUE TABLE
    """
    for row in range(iteration, len(dataset)):
        value = to_unicode(dataset[row][1])
        tokens = value.split(" ")
        # INSERTING TOKENS AND INDEXES
        for token in tokens:
            if token not in index:
                index[token] = [row]
            elif row not in index[token]:
                index[token] += [row]
    # print index

    #################################################################
    # GENERATING CORRESPONDENCES USING THE SIMILARITY
    #################################################################
    """
    4. COMPUTE THE SIMILARITY BASED ON THE INVERTED INDEX
    """
    linkset_name = "approxLinkset"
    link = "alivocab:approxStrSim"
    prefix = "PREFIX alivocab:\t<{}>\n" \
             "PREFIX linkset:\t<{}>\n" \
             "PREFIX singletons:\t<{}>\n".format(Ns.alivocab, Ns.linkset, Ns.singletons)
    # SET THE PATH WHERE THE LINKSET WILL BE SAVED AND GET THE WRITERS
    Ut.write_to_path = "C:\Users\Al\Dropbox\Linksets\ApproxSim"
    writers = Ut.get_writers(linkset_name, directory=DIRECTORY)
    for key, writer in writers.items():
        # BECAUSE THE DICTIONARY ALSO CONTAINS OUTPUT PATH
        if type(writer) is not str:
            writer.write(prefix)
            if key is St.crpdce_writer:
                writer.write("\nlinkset:{}\n{{\n".format(linkset_name))
            elif key is St.singletons_writer:
                writer.write("\nsingletons:{}\n{{".format(linkset_name))

    # ITERATE THROUGH THE SOURCE DATASET
    for row in range(1, iteration):

        # TOKENS IN THE CURRENT PREDICATE VALUE
        curr_index = set()
        tokens = str(dataset[row][1]).split(" ")

        # GET THE INDEX WHERE A TOKEN IN THE CURRENT INSTANCE CAN BE FOUND
        for token in tokens:
            if token in index:
                curr_index = curr_index.union(set(index[token]))

        # COMPUTE THE SIMILARITY FOR THESE OCCURRENCES
        # print dataset[row][1], curr_index
        for idx in curr_index:

            # index needs to be greater than the current row and compared with
            # an index in the opposite table which must be greater than iteration
            if idx != row and idx > iteration:

                # COMPARE THE CURRENT TO OTHERS THAT IS NOT YOURSELF
                sim = edit_distance(dataset[row][1], dataset[idx][1])

                # PRODUCE A CORRESPONDENCE IF A MATCH GREATER THAN THETA IS FOUND
                if sim >= theta:
                    count += 1
                    crpdce = dict()
                    crpdce[St.sim] = sim
                    crpdce[St.src_value] = dataset[row][1]
                    crpdce[St.trg_value] = dataset[idx][1]
                    crpdce[St.src_resource] = dataset[row][0]
                    crpdce[St.trg_resource] = dataset[idx][0]
                    crpdce[St.link] = link
                    crpdce[St.row] = row
                    crpdce[St.inv_index] = idx
                    # print correspondence(crpdce, writers)

    for key, writer in writers.items():
        if type(writer) is not str:
            if key is St.crpdce_writer:
                writer.write("}")
            elif key is St.singletons_writer:
                writer.write("}")
            writer.close()

    t_sim = time()
    print "\t\t>>> in {}".format(t_sim - start)
    print "\t\t>>> in {} match found)".format(count)

    check_rdf_file(writers[St.crpdce_writer_path])
    check_rdf_file(writers[St.singletons_writer_path])
    print "\tLinkset created as: ", linkset_name
    print "\t*** JOB DONE! ***"
    # print index
    return index


def edit_distance(token_x, token_y):
    ln_y = len(token_y) + 1
    ln_x = len(token_x) + 1
    # https://leojiang.com/experiments/levenshtein/

    """
    ***SEQUENCE-BASED SIMILARITY MEASURES **********************************************************************
    *
    * Edit distance aka Levenshtein distance (MINIMUM DISTANCE)
    *
    * The edit distance measure d(x,y), computes the minimal cost of transforming string x to string y.
    * Transforming a string is carried out using a sequence of the following operators: delete a character,
    * insert a character, and substitute one character for another. Intuitively, the edit distance tries to
    * capture the various ways people make editing mistakes.
    * The smaller the edit distance is, the more similar the two strings are.
    * the value of d(x,y) can be computed using dynamic programming.
    *
    * DYNAMIC PROGRAMMING (Wikipedia) [http://en.wikipedia.org/wiki/Dynamic_programming]
    * Dynamic programming algorithms are used for optimization (for example, finding the shortest
    * path between two points, or the fastest way to multiply many matrices). A dynamic programming
    * algorithm will examine all possible ways to solve the problem and will pick the best solution.
    * Therefore, we can roughly think of dynamic programming as an intelligent, brute-force method
    * that enables us to go through all possible solutions to pick the best one. If the scope of the
    * problem is such that going through all possible solutions is possible and fast enough, dynamic
    * programming guarantees finding the optimal solution. The alternatives are many, such as using
    * a greedy algorithm, which picks the best possible choice "at any possible branch in the road".
    * While a greedy algorithm does not guarantee the optimal solution, it is faster. Fortunately,
    * some greedy algorithms (such as minimum spanning trees) are proven to lead to the optimal solution.
    *
    * This function does not trace back the global optimal path but returns the optimal number of edit(s)
    * action(s) necessary to transform x to y.
    *
    ************************************************************************************************************
    """

    """
    Create a matrix and set its first row and column
    """
    matrix = [[column * row * 0 for column in range(ln_x)] for row in range(ln_y)]
    for row in range(ln_y):
        matrix[row][0] = row
    for col in range(1, ln_x):
        matrix[0][col] = col
    # print matrix

    """
    Filling in the matrix by comparing each element from the strings, character by character
    """
    for row in range(1, ln_y):
        for col in range(1, ln_x):

            # If the comparison is a MATCH ==> use the value at the diagonal of the current cell
            if token_y[row - 1] == token_x[col - 1]:
                matrix[row][col] = matrix[row - 1][col - 1]

            # If the match fails, take the minimal value of 3 cells surrounding the current cell
            # [ cell on the left, cell in the diagonal and cell on the top] and add 1 to it
            else:
                # matrix[row][col] = maxint
                # Left cell to the current cell
                matrix[row][col] = min([matrix[row][col - 1], matrix[row-1][col - 1], matrix[row-1][col]]) + 1

    # print matrix
    # print "EDIT DISTANCE:", matrix[ln_y - 1][ln_x - 1]
    # print "DENOMINATOR", float(ln_x - 1 if ln_x > ln_y else ln_y - 1)
    # print "SIMILARITY [0 1]", 1 - matrix[ln_y - 1][ln_x - 1] / float(ln_x - 1 if ln_x > ln_y else ln_y - 1)

    return 1 - matrix[ln_y - 1][ln_x - 1] / float(ln_x - 1 if ln_x > ln_y else ln_y - 1)

    # return  matrix[ln_y - 1][ln_x - 1]


# edit_distance("vu university medical center", "leiden university medical center")
# edit_distance("vu center", "leiden center")
# edit_distance("landspitali, iceland", "australian national")
# stop_symbols_string = "\.\-\,\+'\?"
# test = "Al.in,the-market+veruska-albert'elle?linda"
# pattern = str("[{}]".format(str(stop_symbols_string).strip())).replace(" ", "")
# print "pattern;", pattern
# temp = re.sub(pattern, " ", test)
# print "temp2", temp

def prefixed_inverted_index(specs, theta, stop_words_string=None, stop_symbols_string=None):
    specs["specs"] = theta
    specs["stop_words_string"] = stop_words_string
    specs["stop_symbols_string"] = stop_symbols_string
    # stop_words_string = "THE FOR IN THAT AND OF ON DE LA LES"
    # stop_symbols_string = "\.\-\,\+'\?"

    debug = False
    start = time()
    print "\nStarted at {}".format(ctime(start))
    count = 0

    source = specs[St.source]
    target = specs[St.target]
    Ut.update_specification(source)
    Ut.update_specification(target)
    Ls.set_linkset_name(specs)
    print "LINKSET: {}".format(specs[St.linkset_name])

    specs[St.graph] = specs[St.linkset]
    specs[St.sameAsCount] = Qry.get_same_as_count(specs[St.mechanism])
    specs[St.insert_query] = "The generated triple file was uploaded to the server."
    specs[St.threshold] = theta

    # STOP WORD DICTIONARY
    stop_word = dict()
    stop_words_string = stop_words_string.lower()
    if stop_words_string is not None and len(stop_words_string) > 0:
        stw_split = str(stop_words_string).split(' ')
        for stop in stw_split:
            if stop not in stop_word:
                stop_word[stop] = stop

    # CHECK WHETHER OR NOT THE LINKSET WAS ALREADY CREATED
    check = Ls.run_checks(specs, check_type="linkset")
    if check[St.result] != "GOOD TO GO":
        return check
    # print "LINKSET: {}".format(specs[St.linkset_name])
    """
    BACKGROUND

    This technique first converts each string y ∈ Y into a document and then builds an inverted
    index over these document. Given a term t ∈ X, we can use the index to quickly find the list
    of documents created from Y that contain X, and hence the string in Y that contain t.
    Given a string x ∈ X, the method [Find Candidates] uses the inverted index to quickly locate the set
    of strings in Y that share at least one term with x. Continuing with the example below,
    gives x = {lake, mendota}, we use the index in the table below to find and merge the ID lists
    for lake and mendota to obtain the umbrella Z = {4, 6}
                                                 -------------------------
    set X                                        | Terms in Y | ID Lists |
    --------------------------------             |------------|----------|
    1: {lake, mendota}                           | area       |  5       |
    2: {lake, monona, area}                      |------------|----------|
    3: {lake, mendota, monona, dane}             | lake       |  4.6     |
                                                 |------------|----------|
    set Y                                        | mendota    |  6       |
    --------------------------------             |------------|----------|
    4: {lake, monona, university}                | monona     |  4,5,6   |
    5: {monona, research, area}                  |------------|----------|
    6: {lake, mendota, monona, area}             | research   |  5       |
                                                 |------------|----------|
                                                 | universit  |  4       |
                                                 -------------------------
    Limitations
    1. The inverted list of some terms (e.g stop words) can be very long, so building and
    manipulating such list are quite costly. ==> this problem is reduced when the data is pre-processed

    2. The method requires enumerating all pairs of strings that share at least one term. The set
    of such pair can be very long in practice.

    ASSUMPTIONS
        1. The input data set is already pre-processed and all tokens are separated with the space
        character
        2. All cells in attributes are of type string
        3. The inverted list use the pipe character '|' as document ID separator

    UPDATE FOR COMPUTING APPROXIMATE SIMILARITY
        use a universe of tokens: source and target datasets
        sim-1 that computes similarity of the most rare tokens (tokens to include based of a threshold)
        Sim-2 that computes similarity of ordered (based on utf) tokens if sim_1 is greater or equal to a threshold

    """

    """ Converts each string y ∈ Y into a document and then builds an inverted index over these document. """

    """
    SETTINGS PRIOR TO COMPUTE THE SIMILARITY BASED ON THE INVERTED INDEX
    """

    link = "alivocab:approxStrSim"
    prefix = "@prefix alivocab:\t<{}> .\n" \
             "@prefix linkset:\t<{}> .\n" \
             "@prefix singletons:\t<{}> .\n".format(Ns.alivocab, Ns.linkset, Ns.singletons)

    # SET THE PATH WHERE THE LINKSET WILL BE SAVED AND GET THE WRITERS
    Ut.write_to_path = "C:\Users\Al\Dropbox\Linksets\ApproxSim"
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

    #################################################################
    # HELPER FUNCTIONS
    #################################################################

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

    # HELPER FOR CREATING A CORRESPONDENCE
    def correspondence(description, in_writers, counter):

        # GENERATE CORRESPONDENCE
        in_crpdce = "\n\t### Instance [{5}]\n\t<{0}> \t\t{1}_{2}_{3} \t\t<{4}> .\n".format(
            description[St.src_resource], description[St.link],
            description[St.row], description[St.inv_index], description[St.trg_resource], counter)
        # WRITE CORRESPONDENCE TO FILE
        in_writers[St.crpdce_writer].write(to_unicode(in_crpdce))

        # GENERATE SINGLETONS METADATA
        singleton = "\n\t### Instance [{8}]\n\t{1}_{2}_{3}\n\t\t" \
                    "alivocab:hasStrength \t\t{5} ;" \
                    "\n\t\talivocab:hasEvidence  \t\t\"\"\"[{6}] was compared to [{7}]\"\"\" .\n".\
            format(description[St.src_resource], description[St.link], description[St.row],
                   description[St.inv_index], description[St.trg_resource], description[St.sim],
                   description[St.src_value], description[St.trg_value], counter)
        in_writers[St.singletons_writer].write(to_unicode(singleton))
        # WRITE SINGLETON EVIDENCE TO FILE
        return in_crpdce + singleton

    # def get_tf(matrix):
    #     # Qry.display_matrix(matrix, is_activated=True)
    #     # print matrix
    #     term_frequency = dict()
    #     for r in range(1, len(matrix)):
    #         # print "matrix[row]:", matrix[row]
    #
    #         # REMOVE DATA IN BRACKETS
    #         in_tokens = remove_info_in_bracket(to_unicode(matrix[r][1]))
    #         in_tokens = in_tokens.split(" ")
    #
    #         # COMPUTE FREQUENCY
    #         for t in in_tokens:
    #             if t not in term_frequency:
    #                 term_frequency[t] = 1
    #             else:
    #                 term_frequency[t] += 1
    #
    #     return term_frequency

    def get_tf_2(matrix_src, matrix_trg):
        # Qry.display_matrix(matrix, is_activated=True)
        # print matrix
        datasets = [matrix_src, matrix_trg]
        term_frequency = dict()
        for matrix in datasets:
            # print "DATASETS:", matrix
            for r in range(1, len(matrix)):
                # print "matrix[row]:", matrix[row]

                # REMOVE DATA IN BRACKETS
                # in_tokens = remove_info_in_bracket(to_unicode(matrix[r][1])).lower()

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

        return term_frequency

    def get_inverted_index(matrix, tf, threshold):

        # INVERTED INDEX DICTIONARY
        inv_index = dict()

        for in_row in range(1, len(matrix)):

            # GET THE VALUE
            value = str(matrix[in_row][1])

            # REMOVE DATA IN BRACKETS
            # REMOVE (....) FROM THE VALUE
            # value = remove_info_in_bracket(value)

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

        # REMOVE DATA IN BRACKETS
        # stg = remove_info_in_bracket(stg)

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
            temp = remove_info_in_bracket(temp)

            # REMOVE STOP WORLD
            if len(stop_word) > 0:
                temp = remove_stop_words(temp)

            # REMOVE SYMBOLS OR CHARACTER
            if stop_symbols_string is not None and len(stop_symbols_string) > 0:
                pattern = str("[{}]".format(str(stop_symbols_string).strip())).replace(" ", "")
                temp = re.sub(pattern, "", temp)

            return temp

        except Exception as error:
            print "!!!!!!!!!!!!! PROBLEM !!!!!!!!!!!!!!!!!!!"
            print str(error.message)
            return text

    #################################################################
    # CREATING THE  INVERTED INDEX
    #################################################################

    writer = Buffer.StringIO()
    src_dataset = get_table(source) if St.reducer not in source else get_table(source, reducer=source[St.reducer])
    trg_dataset = get_table(target) if St.reducer not in target else get_table(target, reducer=source[St.reducer])
    Ut.update_specification(specs)

    t_load = time()
    print "\n1. DATASETS LOADED.\n\t>>> IN {}".format(t_load - start)

    print "\n2. VALIDATING THE TABLES"
    if (src_dataset is not None) and (trg_dataset is None):
        print "WE COULD NOT EXTRACT PREDICATE VALUES FROM THE TARGET DATASET"
        return None

    elif (src_dataset is None) and (trg_dataset is not None):
        print "WE COULD NOT EXTRACT PREDICATE VALUES FROM THE SOURCE DATASET"
        return None

    elif (src_dataset is not None) and (trg_dataset is not None):
        # DISPLAY THE MERGE IN ACTIVATE IS TRUE
        Qry.display_matrix(src_dataset, is_activated=False)
        Qry.display_matrix(trg_dataset, is_activated=False)

    print "\tTHE SOURCES DATASET CONTAINS {} INSTANCES.".format(len(src_dataset) - 1)
    print "\tTHE TARGET DATASET CONTAINS {} INSTANCES.".format(len(trg_dataset) - 1)
    print "\tNUMBER OF STOP WORDS: {}".format(len(stop_word) - 1)

    print "\n3. GENERATE THE TERM FREQUENCY OF THE SOURCE DATASET"
    # src_tf = get_tf(src_dataset)
    # trg_tf = get_tf(trg_dataset)
    universe_tf = get_tf_2(src_dataset, trg_dataset)
    # print "\t\tTHE SOURCE DATASET CONTAINS {} POTENTIAL TERMS.".format(len(src_tf) - 1)
    print "\tTHE UNIVERSE OF TOKENS CONTAINS {} POTENTIAL TERMS.".format(len(universe_tf) - 1)
    print "\tTHE TARGET DATASET CONTAINS {} POTENTIAL CANDIDATES.".format(len(trg_dataset) - 1)
    t_tf = time()
    print "\t>>> In {}.\n\t>>> Elapse time: {}".format(t_tf - t_load, t_load - start)
    # print src_tf

    print "\n4. GENERATE THE INVERTED INDEX OF THE TARGET DATASET USING THE FILTERED PREFIX APPROACH"
    trg_inv_index = get_inverted_index(trg_dataset, universe_tf, theta)
    t_inv_ind = time()
    print "\t>>> In {}.\n\t>>> Elapse time: {}".format(t_inv_ind - t_tf, t_inv_ind - start)

    #################################################################
    # GENERATING CORRESPONDENCES USING THE SIMILARITY
    #################################################################

    print "\n5. COMPUTE THE SIMILARITY BASED ON THE INVERTED INDEX"

    # ITERATE THROUGH THE SOURCE DATASET
    for row in range(1, len(src_dataset)):

        src_input = str(src_dataset[row][1])
        src_input = process_input(src_input)

        # print row
        # TOKENS IN THE CURRENT PREDICATE VALUE
        curr_index = set()
        tokens = get_tokens_to_include(src_input, theta, universe_tf)
        # print tokens

        # GET THE INDEX WHERE A TOKEN IN THE CURRENT INSTANCE CAN BE FOUND
        for token in tokens:
            # print token
            # print trg_inv_index
            if token[0] in trg_inv_index:
                curr_index = curr_index.union(set(trg_inv_index[token[0]]))

        # COMPUTE THE SIMILARITY FOR THESE OCCURRENCES
        # print dataset[row][1], curr_index
        for idx in curr_index:

            # COMPARE THE CURRENT TO OTHERS THAT IS NOT YOURSELF
            # sim_val_1 = (remove_info_in_bracket(to_bytes(src_dataset[row][1]))).lower()
            # sim_val_2 = (remove_info_in_bracket(to_bytes(trg_dataset[idx][1]))).lower()

            # REMOVE DATA IN BRACKETS, STOP WORDS, AND STOP SYMBOLS
            # sim_val_1 = process_input(to_bytes(src_dataset[row][1]))
            trg_input = process_input(trg_dataset[idx][1])

            # sim_val_1 = str(sim_val_1).decode(encoding="utf-8")
            # print "1", src_input
            # print "2", trg_input

            # print u"SOURCE [ORIGINAL] [TEMPERED]: [{}] [{}]".format(to_unicode(src_dataset[row][1]), sim_val_1)
            # print u"TARGET [ORIGINAL] [TEMPERED]: [{}] [{}]".format(to_unicode(trg_dataset[idx][1]), sim_val_2)

            # TOKENIZE
            tokens_src = src_input.split(" ")
            tokens_trg = trg_input.split(" ")

            # small
            if len(tokens_src) < len(tokens_trg):
                tokens_1 = tokens_src
                tokens_2 = tokens_trg
                # TOKEN TO INCLUDE
                token2include = get_tokens_to_include(src_input, theta, universe_tf)
            else:
                tokens_1 = tokens_trg
                tokens_2 = tokens_src
                # TOKEN TO INCLUDE
                token2include = get_tokens_to_include(trg_input, theta, universe_tf)
            # print u"TOKEN TO INCLUDE  :", token2include

        # SORT
            # UPDATE THE TOKENS WITH THEIR FREQUENCY
            # token2tf = [i for i in range(len(tokens_2))]
            token2tf = []
            for i in range(len(tokens_2)):
                token2tf += [[tokens_2[i], universe_tf[tokens_2[i]]]]

            # token1tf = [i for i in range(len(tokens_1))]
            token1tf = []
            for i in range(len(tokens_1)):
                token1tf += [[tokens_1[i], universe_tf[tokens_1[i]]]]

            # print u"BIGGEST           :", tokens_2

            # for i in range(len(tokens_2)):
            #     tokens_2[i] = [tokens_2[i], universe_tf[tokens_2[i]]]

            # SORT THE TOKENS BASED ON THEIR FREQUENCY OF OCCURRENCES
            tokens_1_sorted = sorted(token1tf, key=itemgetter(1))
            tokens_2_sorted = sorted(token2tf, key=itemgetter(1))
            # print u"BIGGEST SORTED    :", tokens_2_sorted

            # COMPUTE SIM OF THE IMPORTANT TOKENS (TOKENS TO INCLUDE)
            value_1 = " - "
            value_2 = " - "
            for i in range(len(token2include)):
                # print token2include[i], token2include[i] in tokens_2
                to_use = tokens_2_sorted[:len(token2include)]
                # if token2include[i][0] in tokens_2:
                if token2include[i] in to_use:
                    "DO NOTHING"
                else:
                    value_1 += token2include[i][0] + " "
                    # if token2include[i] in tokens_2:
                    #     value_2 += token2include[i][0] + " "
                    # else:
                    value_2 += to_use[i][0] + " "

            value_1 = value_1.replace(" - ", "") if value_1 != " - " else value_1
            value_2 = value_2.replace(" - ", "") if value_2 != " - " else value_2

            # TODO THINK OF WHAT TO REMOVE FROM A TOKEN LIKE . - ' ,
            # TODO MAKE IT EFFICENT BY MAKING THESE CHANGES AT AN EARLY STAGE
            # TODO DO NOT FORGET TO INCLUDE IT WHEN COMPUTING THE FREQUENCY
            # value_1 = value_1.replace(".", "")
            # value_2 = value_2.replace(".", "")

            sim = edit_distance(value_1.strip(), value_2.strip())
            # print u"COMPARING         :", "{} and {} outputted: {}".format(to_bytes(value_1), to_bytes(value_2), sim)

            # if row == 560000:
            #     print u"\nSOURCE [ORIGINAL] [TEMPERED]: [{}] [{}]".format(to_unicode(src_dataset[row][1]), sim_val_1)
            #     print u"TARGET [ORIGINAL] [TEMPERED]: [{}] [{}]".format(to_unicode(trg_dataset[idx][1]), sim_val_2)
            #
            #     print u"BIGGEST           :", tokens_2
            #     print u"TOKEN TO INCLUDE  :", token2include
            #     print u"BIGGEST SORTED    :", tokens_2_sorted
            #     print u"COMPARING         :", "{} and {} outputted: {}".format(
            #         to_bytes(value_1), to_bytes(value_2), sim)

            if sim >= theta:

                if debug is True:
                    writer.write("\nSOURCE:{} TARGET:{}".format(str(row), str(idx)))
                    writer.write("\nSOURCE [ORIGINAL] [TEMPERED]: [{}] [{}]\n".format(
                        to_bytes(src_dataset[row][1]), src_input))
                    writer.write("TARGET [ORIGINAL] [TEMPERED]: [{}] [{}]\n".format(
                        to_bytes(to_bytes(trg_dataset[idx][1])), trg_input))
                    writer.write(u"BIGGEST           : {}\n".format(tokens_2))
                    writer.write(u"TOKEN TO INCLUDE  : {}\n".format(token2include))
                    writer.write(u"BIGGEST SORTED    : {}\n".format(tokens_2_sorted))
                    writer.write("COMPARING         : {} and {} ==> {}\n".format(
                        to_bytes(value_1), to_bytes(value_2), sim))

                # IF IMPORTANT BIGGER THAN THRESHOLD
                # CONTINUE
                sim_val_1 = ""
                sim_val_2 = ""
                for i in range(len(tokens_1_sorted)):
                    sim_val_1 += tokens_1_sorted[i][0] if i == 0 else " {}".format(tokens_1_sorted[i][0])

                for i in range(len(tokens_2_sorted)):
                    sim_val_2 += tokens_2_sorted[i][0] if i == 0 else " {}".format(tokens_2_sorted[i][0])

                sim = edit_distance(sim_val_1, sim_val_2)
                if debug is True:
                    writer.write("> FINAL COMPARING : {} and {} ==> {}\n".format(sim_val_1, sim_val_2, sim))

                # PRODUCE A CORRESPONDENCE IF A MATCH GREATER THAN THETA IS FOUND
                # if sim >= theta and sim < 1:
                if sim >= theta:
                    if debug is True:
                        writer.write("                   WINNER!!!!!!!!!!!")
                    count += 1
                    # print count
                    crpdce = dict()
                    crpdce[St.sim] = sim
                    crpdce[St.src_value] = src_dataset[row][1]
                    crpdce[St.trg_value] = trg_dataset[idx][1]
                    crpdce[St.src_resource] = src_dataset[row][0]
                    crpdce[St.trg_resource] = trg_dataset[idx][0]
                    crpdce[St.link] = link
                    crpdce[St.row] = row
                    crpdce[St.inv_index] = idx

                    # if gmtime(time()).tm_min % 10 == 0:
                    if gmtime(time()).tm_min % 10 == 0 and gmtime(time()).tm_sec % 60 == 0:
                        print correspondence(crpdce, writers, count)
                    else:
                        correspondence(crpdce, writers, count)
                if debug is True:
                    writer.write(u"\n")
                    print writer.getvalue()
                    writer.flush()

    t_sim = time()
    print "\t\t>>> in {} MINUTE(S).\n\t\t>>> Elapse time: {} MINUTE(S)".format(
        (t_sim - t_inv_ind)/60, (t_sim - start)/60)
    print "\t\t>>> {} match found".format(count)

    # metadata = Gn.linkset_metadata(specs, display=False).replace("INSERT DATA", "")
    # writers[St.meta_writer].write(to_unicode(metadata))

    if Ut.OPE_SYS == "windows":
        path = ''
    else:
        path = Svr.settings[St.stardog_path]

    load = """
    echo "Loading data"
    {}stardog data add {} "{}" "{}"
    """.format(
        path, Ss.DATABASE, writers[St.crpdce_writer_path],
        writers[St.singletons_writer_path]
        # writers[St.meta_writer_path],
    )

    # GENERATE THE BATCH FILE
    writers[St.batch_writer].write(to_unicode(load))

    for key, writer in writers.items():
        if type(writer) is not str:
            if key is St.crpdce_writer:
                writer.write("}")
            elif key is St.singletons_writer:
                writer.write("}")
            if key is not St.meta_writer:
                writer.close()

    # print OPE_SYS
    if Ut.OPE_SYS != 'windows':
        print "MAC BATCH: {}".format(writers[St.batch_output_path])
        os.chmod(writers[St.batch_output_path], 0o777)

    print "\n>>> STARTED ON {}".format(ctime(start))
    print ">>> FINISHED ON {}".format(ctime(t_sim))
    print ">>> MATCH WAS DONE IN {}\n".format((t_sim - start)/60)

    # print inserted
    # if int(inserted[1]) > 0:
    if count > 0:

        print "6. RUNNING THE BATCH FILE FOR LOADING THE CORRESPONDENCES INTO THE TRIPLE STORE\n\t\t{}", writers[
            St.batch_output_path]

        if Svr.settings[St.split_sys] is True:
            print "THE DATA IS BEING LOADED OVER HTTP POST."
        else:
            print "THE DATA IS BEING LOADED AT THE STARDOG LOCAL HOST FROM BATCH."
            # os.system(writers[St.batch_output_path])
            Ut.batch_load(writers[St.batch_output_path])
        # inserted = Qry.insert_size(specs[St.linkset], isdistinct=False)

        metadata = Gn.linkset_metadata(specs, display=False).replace("INSERT DATA", "")
        writers[St.meta_writer].write(to_unicode(metadata))

        if int(specs[St.triples]) > 0:
            Qry.boolean_endpoint_response(metadata)
        writers[St.meta_writer].close()

        # REGISTER THE ALIGNMENT
        if check[St.result].__contains__("ALREADY EXISTS"):
                Urq.register_alignment_mapping(specs, created=False)
        else:
            Urq.register_alignment_mapping(specs, created=True)

        # WRITE TO FILE
        check_rdf_file(writers[St.crpdce_writer_path])
        check_rdf_file(writers[St.meta_writer_path])
        check_rdf_file(writers[St.singletons_writer_path])

        print "\tLinkset created as: ", specs[St.linkset_name]
        print "\t*** JOB DONE! ***"

        message = "The linkset was created as {} with {} triples.".format(specs[St.linkset], count)
        return {St.message: message, St.error_code: 0, St.result: specs[St.linkset]}

    else:
        message = "\tLinkset was not created because no match was found: ", specs[St.linkset_name]
        print message
        print "\t*** JOB DONE! ***"
        return {St.message: message, St.error_code: 0, St.result: None}
