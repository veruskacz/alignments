import rdflib

ttl_rdf_file = "C:\Users\Al\Documents\Tobias\Test-OneLinkset\GenericGraph.ttl"
trig_rdf_file = "C:\Users\Al\Documents\Tobias\Test-OneLinkset\LinksetGraph.trig"

# GenericGraph.ttl
# LinksetGraph.trig

g = rdflib.Graph()
g.parse(location=trig_rdf_file, format="turtle")
# print len(g)