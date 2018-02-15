
import os
from numpy import median, mean, std
import Alignments.Query as Qry
import Alignments.Utility as Ut
import Alignments.Settings as St
from time import time, gmtime  # , ctime
import Alignments.Server_Settings as Ss
import Alignments.GenericMetadata as Gn
import Alignments.Server_Settings as Svr
import Alignments.UserActivities.UserRQ as Urq
# from Alignments.CheckRDFFile import check_rdf_file
import Alignments.SimilarityAlgo.SimHelpers as Helper
from kitchen.text.converters import to_unicode  # , to_bytes

#################################################################################################
#################################################################################################

theta = 0.5
count = 0
frq_limit = 10

# gender C#######################################################################################
#################################################################################################

source_specs = {
    St.graph: "http://risis.eu/dataset/genderc",
    St.aligns: "http://risis.eu/Panellists/ontology/predicate/Name_of_home_institution",
    St.entity_datatype: "http://risis.eu/Panellists/ontology/class/Panelists"}

target_specs = {
    St.graph: "http://risis.eu/dataset/genderc",
    St.aligns: "http://risis.eu/genderc/vocab/affiliation",
    St.entity_datatype: "http://risis.eu/genderc/vocab/Applicant"}

specs = {
    St.source: source_specs,
    St.target: target_specs,
    St.linkset_name: "InvTest",
    St.sameAsCount: 1,
    St.mechanism: "approxStrSim",
    St.linkset: "http://risis.eu/linkset/InvTest",
    St.threshold: 1,
    St.insert_query: "",
    St.researchQ_URI: "http://risis.eu/activity/idea_8b78a8"}

src_dataset = Helper.get_table(source_specs)
trg_dataset = Helper.get_table(target_specs)
universe_tf = Helper.get_tf([src_dataset, trg_dataset])
trg_inv_index = Helper.get_inverted_index(trg_dataset, universe_tf, theta)
Helper.data['delta'] = int(Helper.data['mode']/10)
t2r_dict = Helper.term_2_remove(universe_tf)
exit(0)


# AMADEUS #######################################################################################
#################################################################################################

# source_specs = {
#     St.graph: "http://risis.eu/dataset/amadeus",
#     St.aligns: "http://risis.eu/amadeus/ontology/predicate/Companyname",
#     St.entity_datatype: "http://risis.eu/amadeus/ontology/class/Organisation"}
#
# target_specs = {
#     St.graph: "http://risis.eu/dataset/grid_20170712",
#     St.aligns: "http://www.w3.org/2000/01/rdf-schema#label",
#     St.entity_datatype: "http://xmlns.com/foaf/0.1/Organization"}
#
# specs = {
#     St.source: source_specs,
#     St.target: target_specs,
#     St.sameAsCount: frq_limit,
#     St.mechanism: "approxStrSim",
#     St.linkset_name: "InvTestAmadeus{}".format(frq_limit),
#     St.linkset: "http://risis.eu/linkset/InvTestAmadeus{}".format(frq_limit),
#     St.threshold: 1,
#     St.insert_query: "",
#     St.researchQ_URI: "http://risis.eu/activity/idea_13e5bc"}

# GRID - ORGREF #################################################################################
#################################################################################################

# research_question = "http://risis.eu/activity/idea_341982"
#
# source_specs = {
#     St.graph: "http://risis.eu/dataset/orgref_20170703",
#     St.aligns: "http://risis.eu/orgref_20170703/ontology/predicate/Name",
#     St.entity_datatype: "http://risis.eu/orgref_20170703/ontology/class/Organisation"}
#
# target_specs = {
#     St.graph: "http://risis.eu/dataset/grid_20170712",
#     St.aligns: "http://www.w3.org/2000/01/rdf-schema#label",
#     St.entity_datatype: "http://xmlns.com/foaf/0.1/Organization"}
#
# specs = {
#     St.source: source_specs,
#     St.target: target_specs,
#     St.sameAsCount: frq_limit,
#     St.mechanism: "approxStrSim",
#     St.linkset_name: "InvTestAmadeus{}".format(frq_limit),
#     St.linkset: "http://risis.eu/linkset/InvTestAmadeus{}".format(frq_limit),
#     St.threshold: 1,
#     St.insert_query: "",
#     St.researchQ_URI: research_question}

# Helper.stop_words_string =  "THE FOR IN THAT AND OF ON DE LA LES INC"
Helper.stop_symbols_string = "\.\-\,\+'\?;()"
Helper.set_stop_word_dic()
writers = Helper.set_writers(specs)
Helper.remove_term_in_bracket = False

# DOWNLOAD THE DATA
src_dataset = Helper.get_table(source_specs)
trg_dataset = Helper.get_table(target_specs)

# COMPUTE THE UNIVERSE OF FREQUENCY
universe_tf = Helper.get_tf([src_dataset, trg_dataset])
sorted_universe_tf = sorted(universe_tf.values())

# TERMS WITH FREQUENCY GREATER THAN DELTA ARE NOT CONSIDERED
Helper.data['delta'] = int(Helper.data['mode'] / frq_limit)

# if (len(sorted_universe_tf)/2) % 2 > 0:
#     median = sorted_universe_tf[len(sorted_universe_tf)/2]
# else:
#     middle = len(sorted_universe_tf)/2
#     left = sorted_universe_tf[middle]
#     right = sorted_universe_tf[middle + 1]
#     print left, "|", right
#     median = (sorted_universe_tf[middle] + sorted_universe_tf[middle + 1])/2

i_median = median(sorted_universe_tf)
i_mean = mean(sorted_universe_tf)
i_std = std(sorted_universe_tf)
mode = sorted_universe_tf[len(sorted_universe_tf) - 1]

ic_median = ic_mean = ic_std = 0
ic_std_plus = c_frq_limit = ic_std_minus = 0

for i in range(0, len(sorted_universe_tf)):

    if sorted_universe_tf[i] <= i_median:
        ic_median += 1
    if sorted_universe_tf[i] <= i_mean:
        ic_mean += 1
    if sorted_universe_tf[i] <= i_std:
        ic_std += 1
    if sorted_universe_tf[i] <= i_std - i_mean:
        ic_std_minus += 1
    if sorted_universe_tf[i] <= i_std + i_mean:
        ic_std_plus += 1
    if sorted_universe_tf[i] <= Helper.data['delta']:
        c_frq_limit += 1

print "SIZE      : {:>28}".format(str(len(sorted_universe_tf)))
print "MODE      : {:>28}".format(mode)
print "MEDIAN    : {:13} includes {} instances".format(median(sorted_universe_tf), str(ic_median))
print "MEAN      : {:13} includes {} instances".format(mean(sorted_universe_tf), str(ic_mean))
print "STD-      : {:13} includes {} instances".format(std(sorted_universe_tf) - i_mean, str(ic_std_minus))
print "STD       : {:13} includes {} instances".format(std(sorted_universe_tf), str(ic_std))
print "STD+      : {:13} includes {} instances".format(std(sorted_universe_tf) + i_mean, str(ic_std_plus))
print "LIMIT     : {:>13} includes {} instances".format(Helper.data['delta'], str(c_frq_limit))

exit(0)
# COMPUTE THE INVERTED INDEX
trg_inv_index = Helper.get_inverted_index(trg_dataset, universe_tf, theta)


t2r_dict = Helper.term_2_remove(universe_tf)

# target_specs = {
#     St.graph: "http://risis.eu/dataset/grid_20170712",
#     St.aligns: "http://www.w3.org/2004/02/skos/core#altLabel",
#     St.entity_datatype: "http://xmlns.com/foaf/0.1/Organization"
# }


link = "alivocab:invertedIndexStrSim"

# print writers[St.batch_output_path]
# exit(0)
# print "test", universe_tf["rollsroyce"]
print "TARGET INVERTED INDEX SIZE          : {}".format(len(universe_tf))
print "TARGET INVERTED INDEX MODE          : {}".format(Helper.data['mode'])
print "TARGET INVERTED INDEX MODE TERM     : {}".format(Helper.data['mode_token'])
print "TARGET INVERTED MAX DELTA FREQUENCY : {}".format(Helper.data['delta'])
print "TARGET INVERTED INDEX TERM 2 REMOVE : {}".format(len(t2r_dict))
for key, value in t2r_dict.items():
    print "\t", key, value

# for key, value in universe_tf.items():
#     if value >=  Helper.data['delta'] :
#         count2 += 1
#         if len(key) > 3:
#             print "\t", key, value
#     if value > mode:
#         mode = value
#     sum_up +=  value
# print count2
# exit(0)
# ITERATE THROUGH THE SOURCE
for row in range(1, len(src_dataset)):

    src_uri = src_dataset[row][0].strip()
    src_input = Helper.process_input(str(src_dataset[row][1]))

    # TOKENIZE SOURCE INPUT
    tokens_src = src_input.split(" ")

    # TOKENS IN THE CURRENT PREDICATE VALUE
    curr_index = set()
    tokens = Helper.get_tokens_to_include(src_input, theta, universe_tf)

    # GET THE INDEX WHERE A TOKEN IN THE CURRENT INSTANCE CAN BE FOUND
    for token in tokens:
        # print token
        # print trg_inv_index
        if token[0] in trg_inv_index and token[0] not in t2r_dict:
            curr_index = curr_index.union(set(trg_inv_index[token[0]]))

    # COMPUTE THE SIMILARITY FOR THESE OCCURRENCES
    # print dataset[row][1], curr_index
    for idx in curr_index:

        trg_uri = trg_dataset[idx][0].strip()

        # TOKENIZE TARGET INPUT AND PROCESS IT ACCORDINGLY
        trg_input = Helper.process_input(trg_dataset[idx][1])

        count += 1
        crpdce = dict()
        crpdce[St.sim] = 0
        crpdce[St.src_value] = src_dataset[row][1]
        crpdce[St.trg_value] = trg_dataset[idx][1]
        crpdce[St.src_resource] = src_uri
        crpdce[St.trg_resource] = trg_uri
        crpdce[St.link] = link
        crpdce[St.row] = row
        crpdce[St.inv_index] = idx

        # print >> sys.stderr, count, crpdce[St.src_value], "\r",

        if gmtime(time()).tm_min % 10 == 0 and gmtime(time()).tm_sec % 60 == 0:
            print Helper.correspondence(crpdce, writers, count)
            # Helper.correspondence(crpdce, writers, count)
        else:
            Helper.correspondence(crpdce, writers, count)

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

if count > 0:

    print "\n{} INSTANCES FOUND.".format(count)
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
        # if check[St.result].__contains__("ALREADY EXISTS"):
        #     Urq.register_alignment_mapping(specs, created=False)
        # else:
        #     Urq.register_alignment_mapping(specs, created=True)
        Urq.register_alignment_mapping(specs, created=False)
        # WRITE TO FILE
        # check_rdf_file(writers[St.crpdce_writer_path])
        # check_rdf_file(writers[St.meta_writer_path])
        # check_rdf_file(writers[St.singletons_writer_path])
    else:
        writers[St.meta_writer].close()

    print "\tLinkset created as: ", specs[St.linkset_name]
    print "\t*** JOB DONE! ***"

    message = "The linkset was created as {} with {} triples.".format(specs[St.linkset], count)

else:
    print "NO LINK WAS CREATED"

# print "\n>>> STARTED ON {}".format(ctime(start))
# print ">>> FINISHED ON {}".format(ctime(t_sim))
# print ">>> MATCH WAS DONE IN {}\n".format((t_sim - start) / 60)
# print writers[St.crpdce_writer_path]

# print len(trg_dataset)

# for key, val in trg_inv_index.items():
#     print key, val
