from Alignments.Query import sparql_xml_to_csv as query2csv
from Alignments.Query import virtuoso_request as endpoint
from Alignments.Query import remote_endpoint_request as remote

query = """
prefix lens: <http://risis.eu/lens/>
prefix ds: <http://risis.eu/dataset/>
prefix grid: <http://www.grid.ac/ontology/>
select(count(distinct ?open) as ?Total) ?countryName ?countryCount
{
	graph lens:union_Grid_20170712_OpenAire_20170816_P4943421715394164828
    #graph lens:union_Grid_20170712_Eter_2014_N8987762074610654084
  	#graph lens:union_Grid_20170712_Orgreg_20170718_N7875946677548047942
    {
    	?open	?pred ?grid .
    }

    graph ds:grid_20170712
    {
    	?grid a grid:Education.
        {
          select ?countryName  (count(distinct ?open) as ?countryCount)
          {
              graph lens:union_Grid_20170712_OpenAire_20170816_P4943421715394164828 { ?open	?pred ?grid . }
              graph ds:grid_20170712
              {
                  ?grid a grid:Education ;
                      <http://www.grid.ac/ontology/hasAddress>/<http://www.grid.ac/ontology/countryName> ?countryName .
              }
          } GROUP BY ?countryName
        }
    }
}
group by ?countryName ?countryCount
ORDER BY DESC(?countryCount)
"""
print query2csv(query)["result"].getvalue()

print endpoint(query)["result"]

print remote("""select * {?x ?y ?z} limit 10""", "http://stardog.risis.d2s.labs.vu.nl/risis#!/query/")["result"]