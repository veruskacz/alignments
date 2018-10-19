# encoding=utf-8

import networkx as nx
import Alignments.Utility as Ut
from Alignments.Examples.GoldenAgent.Validation import \
    generate_sheet, extract_eval, shortest_paths, nodes_in_cycle, shortest_path_nodes
from Alignments.UserActivities.Clustering import links_clustering
from Alignments.UserActivities.Plots import draw_graph

# ********************************************************************************
# CLUSTERING THE RE=SuLT OF AN ALIGNMENT
# ********************************************************************************
clustering = False
if clustering:
    clusters = links_clustering(
        graph="http://risis.eu/lens/union_Orgreg_20170718_Amadeus"
              "_Eter_2014_Grid_20180625_H2020_2017_LeidenRanking_2015_Orgref_20180301_P1951854249",
        serialisation_dir="C:\Productivity\\1 - GA - VALIDATION")


# ********************************************************************************
# GENERATE MACHINE VALIDATION SHEET SHEET
# ********************************************************************************
info = {
        'dataset-1': {
            'mandatory': [('property-1', 'name'), ('property-10', ""), ('property-15', '')],
            'optional': [('property-00', 'country')]
        },
        'dataset-2': {
            'mandatory': [('property-2', 'name'), ('property-23', ""), ('property-30', "")],
            'optional': []
        },
        'dataset-3': {
            'mandatory': [('property-3', 'name'), ('property-36', ""), ('property-33', "")],
            'optional': []
        }
    }
info_2 = {
        'http://risis.eu/dataset/grid_20180625': {
            'mandatory': [
                ('http://www.w3.org/2000/01/rdf-schema#label', 'name')],
            'optional': [('<http://www.grid.ac/ontology/hasAddress>/<http://www.grid.ac/ontology/countryCode>',
                          'Country'),
                         ('http://www.w3.org/2004/02/skos/core#altLabel', "Alternative")]
        },
        'http://risis.eu/dataset/orgref_20180301': {
            'mandatory': [
                ('http://risis.eu/orgref_20180301/ontology/predicate/Name', 'name'),
                ('http://risis.eu/orgref_20180301/ontology/predicate/Country', "Country")],
            'optional': []
        },
        'http://risis.eu/dataset/orgreg_20170718': {
            'mandatory': [('http://risis.eu/orgreg_20170718/ontology/predicate/Name_of_entity', 'name')],
            'optional': [("http://risis.eu/orgreg_20170718/ontology/predicate/English_name_of_entity", "Alternative"),
                         ("http://risis.eu/orgreg_20170718/ontology/predicate/Country_of_establishment", "Country")]
        },

        'http://risis.eu/dataset/eter_2014': {
            'mandatory': [('http://risis.eu/eter_2014/ontology/predicate/Institution_Name', 'name')],
            'optional': [("http://risis.eu/eter_2014/ontology/predicate/English_Institution_Name", "Alternative")]
        },
    }
rscs = ['http://risis.eu/orgref_20180301/resource/10039929',
        'http://risis.eu/orgref_20180301/resource/13967334',
        'http://www.grid.ac/institutes/grid.1001.0', 'http://www.grid.ac/institutes/grid.413314.0']
directory = "C:\Productivity\\1 - GA - VALIDATION"
graph = "http://risis.eu/lens/union_Orgreg_20170718_Amadeus_Eter_2014_Grid" \
        "_20180625_H2020_2017_LeidenRanking_2015_Orgref_20180301_P1951854249"

generate_sheet(data=info_2, directory=directory, graph=graph,
               serialisation_dir=directory, related_alignment=graph, separator_size=50, size=30,  activated=False)


# ********************************************************************************
# EVALUATE THE SHEET AFTER HUMAN EVALUATION
# ********************************************************************************
METRICS = False
save_in = "C:\Productivity\\1 - GA - VALIDATION\N1689818117"
sheet = "C:\Productivity\\1 - GA - VALIDATION\N1689818117\\EvalSheet_N1689818117_20181018-075016_noCycle.txt"
extract_eval(sheet, 3, save_in, print_stats=False, zero_rule=False)
if METRICS:
    for i in range(1, 5):
        extract_eval(sheet, i, save_in, zero_rule=False)


# ********************************************************************************
# LAMBDA FILTER TEST
# ********************************************************************************
LAMBDA = False
if LAMBDA:
    matching = ["good", "bad", "good", "bad", "bad", "bad", "bad"]
    eccentricity = {'<http://risis.eu/eter_2014/resource/EE0006>': 2,
                    '<http://risis.eu/leidenRanking_2015/resource/115>': 3,
                    '<http://risis.eu/orgref_20180301/resource/787614>': 3,
                    '<http://risis.eu/orgreg_20170718/resource/CHAREE0006-1>': 3,
                    '<http://www.grid.ac/institutes/grid.6988.f>': 2,
                    '<http://risis.eu/orgreg_20170718/resource/CHAREE0006-2>': 3,
                    '<http://risis.eu/orgreg_20170718/resource/CHAREE0002-2>': 2,
                    '<http://risis.eu/cordisH2020/resource/participant_999842536>': 2,
                    '<http://risis.eu/eter_2014/resource/EE0002>': 2,
                    '<http://risis.eu/orgreg_20170718/resource/CHAREE0002-1>': 3}
    print filter(lambda x: x.upper() == "GOOD", matching)
    result = filter(lambda x: int(x[1]) == 3, eccentricity.items())
    Ut.print_list(result)


# ********************************************************************************
# TESTING GRAPH CREATION
# ********************************************************************************
# process_cluster(info_2, rscs, "C:\Productivity\\1 - GA - VALIDATION", cluster_id="ad15fdc8")

PLOTES = False
if PLOTES:
    file_path = "C:\Productivity\\2 - MatchingTools\\image_{}.pdf"
    nodes_al = ["Al", "Koudouss", "Koudous", "oladele", "Idrissou"]
    nodes = ["Veruska", "Carretta", "Zamborlini",  "Al", "Koudouss", "Koudous", "oladele", "Idrissou", "Kamila", "Mila"]
    links_ve = [("Veruska", "Carretta"), ("Carretta", "Zamborlini"), ("Zamborlini", "Veruska")]
    links_al = [("Al", "Koudouss"), ("Koudouss", "Idrissou"), ("oladele", "Koudouss"),
                ("Idrissou", "oladele"), ("oladele", "Koudous"), ("Koudous", "Al")]
    links_ka = [("Kamila", "Mila")]
    links_all = links_ve + links_al + links_ka + [
        ("Veruska", 'Kamila'), ("Veruska", "Mila"), ("Carretta", "Al"), ("Zamborlini", "oladele")]

    draw_graph(links_ve, file_path=file_path.format("ve"), show_image=True)
    draw_graph(links_al, file_path=file_path.format("Al"), show_image=True)
    draw_graph(links_ka, file_path=file_path.format("Ka"), show_image=True)
    draw_graph(links_all, file_path=file_path.format("All"), show_image=True)

    print nx.shortest_path(links_al, source="Al", target="oladele")
    print shortest_paths(links_all, start_node="Al", end_node="oladele")

    specs = {

        'investigated_cluster': {"network": links_ve, "start": "Carretta", 'end': "Zamborlini"},
        'extended_cluster': {"network": links_al, "start": "Al", 'end': "oladele"}}

    specs_2 = {

        'investigated_cluster': {
            "network": links_al,
            "start": "Al",
            'end': "oladele"
        },
        'extended_cluster': {"network": links_ve, "start": "Carretta", 'end': "Zamborlini"}}

    specs_3 = {

        'investigated_cluster': {
            "network": links_al,
            "start": "Koudouss",
            'end': "Idrissou"
        },
        'extended_cluster': {"network": links_ka, "start": "Kamila", 'end': "Mila"}}

    nodes_in_cycle(specs)
    nodes_in_cycle(specs_2)
    print shortest_paths(links_al, "Al", "oladele")
    print shortest_path_nodes(links_al, "Al", "oladele")
    nodes_in_cycle(specs_3)
    print shortest_paths(links_al, "Koudouss", "Idrissou")
    print shortest_path_nodes(links_al, "Koudouss", "Idrissou")


# ********************************************************************************
# TESTING SAMPLE SIZE
# ********************************************************************************

POPULATION = 3000000
SAMPLING = False
if SAMPLING:
    print "\nSAMPLE SIZE FOR POPULATION OF {} IS: {}".format(POPULATION,
        Ut.sample_size(POPULATION, confidence_level=0.02, degree_freedom=1))

diameter = 3
weighted_sum = 3- 0.3
reconciled_strength = (100 - 10 * (2*diameter - weighted_sum - 1)) / float(100)
# print "RECONCILIATION STRENGTH: ", reconciled_strength

# from scipy.stats import chi2
# chi = chi2.isf(q=0.05, df=1)
# print chi



import pickle

pickle_file = "C:\Productivity\\2 - MatchingTools\\pickle.txt"
# data = open(pickle_file, "wb")
# data.write(str(pickle.dumps(info_2)))

myopen = open(pickle_file, "rb")
# print "data:", myopen.read()
Ut.print_dict(pickle.loads(myopen.read()))

# print pickle.loads(myopen.read())