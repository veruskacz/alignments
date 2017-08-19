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
         limit=10000, main_query=main_query, count_query=count_query, activated=False)



entity_type ="project"
directory = "D:/datasets/OpenAireProject"
endpoint="http://lod.openaire.eu/sparql"
graph = "{}openAire_20170816".format(Ns.dataset)

count_query = """
    PREFIX foaf: <http://xmlns.com/foaf/0.1/>
    SELECT (COUNT (?subj) as ?triples)
    WHERE {?subj a <http://www.eurocris.org/ontologies/cerif/1.3#Project> ; ?pred ?object }"""

main_query = """
    PREFIX foaf: <http://xmlns.com/foaf/0.1/>
    CONSTRUCT {?subj ?pred ?object }
    WHERE {?subj a <http://www.eurocris.org/ontologies/cerif/1.3#Project> ; ?pred ?object }"""


download(endpoint=endpoint, entity_type=entity_type, graph=graph, directory=directory,
         limit=10000, main_query=main_query, count_query=count_query, activated=True)




# dDOWNLOAD BIND(LCASE(?label2) as ?name2)

entity_type = "location"
directory = "D:/datasets/Countries"
endpoint= "http://sparql.sms.risis.eu/"
graph = "{}countries".format(Ns.dataset)

"http://rdf.risis.eu/datasets/countries/vocab/Country"

count_query = """
    SELECT (COUNT (?subj) as ?triples)
    WHERE { graph <http://rdf.risis.eu/countries> { ?subj ?pred ?object } }"""

main_query = """
    CONSTRUCT { ?subj ?pred ?object }
    WHERE { graph <http://rdf.risis.eu/countries> { ?subj ?pred ?object } }"""


download(endpoint=endpoint, entity_type=entity_type, graph=graph, directory=directory,
         limit=10000, main_query=main_query, count_query=count_query, activated=False)