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
         limit=10000, main_query=main_query, count_query=count_query, activated=False)


# dDOWNLOAD BIND(LCASE(?lab326el2) as ?name2)

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

# DOWNLOADING DBPEDIA ORGANIZATION
dbo = "http://dbpedia.org/ontology/Organisation"
dbo_directory = "D:/datasets/dbpedia/dbpediaOntologyOrganisation"
edbo_ntity_type = "organisation"

foaf = "<http://xmlns.com/foaf/0.1/Organization>"
directory = "D:/datasets/dbpedia/organisation"
entity_type = "organization"

endpoint= "http://dbpedia.org/sparql"
graph = "{}dbpedia_organisation_20170823".format(Ns.dataset)
count_q = "SELECT (COUNT(?subj) as ?total) WHERE {{?subj a <{}> ; ?pred ?object .}}".format(dbo)
main_q = "CONSTRUCT {{ ?subj ?pred ?object }} WHERE {{ ?subj a <{}> ; ?pred ?object .}}".format(dbo)
download(endpoint=endpoint, entity_type=edbo_ntity_type, graph=graph, directory=dbo_directory,
         limit=10000, start_at=2448, main_query=main_q, count_query=count_q, activated=False)

# DOWNLOADING DBPEDIA ORGANIZATION TYPE AND LABEL ONLY
label_count_q = """
SELECT (COUNT(?subj) as ?total)
WHERE {{ ?subj a <{}> ; <http://www.w3.org/2000/01/rdf-schema#label> ?object . }}""".format(dbo)

label_main_q = """
CONSTRUCT {{ ?subj a <{0}> ; <http://www.w3.org/2000/01/rdf-schema#label> ?object . }}
WHERE {{ ?subj a <{0}> ; <http://www.w3.org/2000/01/rdf-schema#label> ?object . }}""".format(dbo)
dbp_endpoint = "http://dbpedia.org/sparql"
dbo_label_directory = "D:/datasets/dbpedia/dbpediaOntologyOrganisationLabel"

download(endpoint=dbp_endpoint, entity_type=edbo_ntity_type, graph=graph, directory=dbo_label_directory,
         limit=10000, start_at=0, main_query=label_main_q, count_query=label_count_q, activated=True)



