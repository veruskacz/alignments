from Alignments.UserActivities.Import_Data import download_data as download
import Alignments.NameSpace as Ns

entity_type ="organization"
directory = "D:/datasets/OpenAire"
endpoint="http://lod.openaire.eu/sparql"
graph = "{}openAire_20170816".format(Ns.dataset)

count_query = """
    PREFIX foaf: <http://xmlns.com/foaf/0.1/>
    SELECT (COUNT (?subj) as ?triples)
    WHERE {?subj a foaf:Organization ; ?pred ?object }"""

main_query = """
    PREFIX foaf: <http://xmlns.com/foaf/0.1/>
    CONSTRUCT {?subj ?pred ?object }
    WHERE {?subj a foaf:Organization ; ?pred ?object }"""


download(endpoint=endpoint, entity_type=entity_type, graph=graph, directory=directory,
         limit=10000, main_query=main_query, count_query=count_query, activated=True)