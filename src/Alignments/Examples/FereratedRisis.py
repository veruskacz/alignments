
query = """
    ### 1. LOADING SOURCE AND TARGET TO A TEMPORARY GRAPH
    INSERT
    {
        GRAPH <http://risis.eu/test/load_1>
        {
            ### SOURCE DATASET AND ITS ALIGNED PREDICATE
            ?source <http://risis.eu/Eter/ontology/predicate/english_Institution_Name> ?src_value .
        }
    }
    WHERE
    {
        ### SOURCE DATASET
        service <http://sparql.sms.risis.eu>
        {
            graph <http://risis.eu/dataset/Eter>
            {
                ### SOURCE DATASET AND ITS ALIGNED PREDICATE
                ?source a <http://risis.eu/Eter/ontology/class/University> ;
                  <http://risis.eu/Eter/ontology/predicate/english_Institution_Name> ?value_1 .
                bind (lcase(str(?value_1)) as ?src_value)
            }
       }
    }
"""