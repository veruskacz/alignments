from Alignments.Examples.GoldenAgent.Validation import generate_sheet

# TESTING
info = {
        'dataset-1': {
            'mandatory':[('property-1', 'name'), ('property-10', ""), ('property-15', '')],
            'optional': [('property-00', 'country'),]
        },
        'dataset-2': {
            'mandatory':[('property-2', 'name'), ('property-23', ""), ('property-30', "")],
            'optional': []
        },
        'dataset-3': {
            'mandatory':[('property-3', 'name'), ('property-36', ""), ('property-33', "")],
            'optional': []
        }
    }

info_2 = {
        'http://risis.eu/dataset/grid_20180625': {
            'mandatory':[
                ('http://www.w3.org/2000/01/rdf-schema#label', 'name')],
            'optional': [('<http://www.grid.ac/ontology/hasAddress>/<http://www.grid.ac/ontology/countryCode>', 'Country'),
                         ('http://www.w3.org/2004/02/skos/core#altLabel', "Alternative")]
        },
        'http://risis.eu/dataset/orgref_20180301': {
            'mandatory':[
                ('http://risis.eu/orgref_20180301/ontology/predicate/Name', 'name'),
                ('http://risis.eu/orgref_20180301/ontology/predicate/Country', "Country")],
            'optional': []
        },
        'http://risis.eu/dataset/orgreg_20170718': {
            'mandatory':[('http://risis.eu/orgreg_20170718/ontology/predicate/Name_of_entity', 'name')],
            'optional': [("http://risis.eu/orgreg_20170718/ontology/predicate/English_name_of_entity", "Alternative"),
                         ("http://risis.eu/orgreg_20170718/ontology/predicate/Country_of_establishment", "Country")]
        },

        'http://risis.eu/dataset/eter_2014': {
            'mandatory':[('http://risis.eu/eter_2014/ontology/predicate/Institution_Name', 'name')],
            'optional': [("http://risis.eu/eter_2014/ontology/predicate/English_Institution_Name", "Alternative")]
        },
    }

rscs = ['http://risis.eu/orgref_20180301/resource/10039929',
       'http://risis.eu/orgref_20180301/resource/13967334',
       'http://www.grid.ac/institutes/grid.1001.0', 'http://www.grid.ac/institutes/grid.413314.0']


# clusters = links_clustering(
#     graph="http://risis.eu/lens/union_Orgreg_20170718_Amadeus"
#           "_Eter_2014_Grid_20180625_H2020_2017_LeidenRanking_2015_Orgref_20180301_P1951854249",
#     serialisation_dir="C:\Productivity\\1 - GA - VALIDATION")

directory = "C:\Productivity\\1 - GA - VALIDATION"
graph="http://risis.eu/lens/union_Orgreg_20170718_Amadeus_Eter_2014_Grid_20180625_H2020_2017_LeidenRanking_2015_Orgref_20180301_P1951854249"
generate_sheet(data=info_2, directory=directory, graph=graph,
               serialisation_dir=directory, related_alignment=graph, separator_size=50)



# process_cluster(info_2, rscs, "C:\Productivity\\1 - GA - VALIDATION", cluster_id="ad15fdc8")