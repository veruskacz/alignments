PREFIX ="""
    PREFIX void: <http://rdfs.org/ns/void#>
    PREFIX alivocab: <http://risis.eu/alignment/predicate/>
"""
def get_target_datasets(singleton_list):

    sample = """
            ### LINKSET WHERE A CORRESPONDENCE MIGHT HAV HAPPENED
            graph ?g
            {
                ?sub # ?obj .
            }"""

    union = "{"
    if len(singleton_list) > 1:
        for i in range(len(singleton_list)):
            if i == 0:
                union += sample.replace('#', singleton_list[i])
            else:
                union += "\n\t     }\n\t      UNION\n\t     {" + sample.replace('#', singleton_list[i])
            if i == len(singleton_list)-1:
                union += "\n\t     }"
    else:
        union = """
        graph ?g
        {{
            ?sub <{}> ?obj .
        }}""".format(singleton_list[0])

    query = """
    {}
    select distinct ?g ?source ?trget ?alignsSubjects ?alignsObjects
    where
    {{
        ### Initially, we have A -> B via Z
        ### Z is derived from X, Y and W
        ### So we could replaced Z with X or Y or Z and find out the graph for with the assertion holds
        {}

        ### Once we find those graphs, it means that we can extract the same source
        ### and target datasets that hold details about the entities being linked
        ?g
           void:subjectsTarget 			?source ;
           void:objectsTarget  			?target .
        OPTIONAL {{ ?g	  alivocab:alignsMechanism  ?alignsMechanism }}
        OPTIONAL {{ ?g    alivocab:alignsSubjects   ?alignsSubjects }}
        OPTIONAL {{ ?g    alivocab:alignsObjects    ?alignsObjects }}

        ### Here, we could easily have the description of the entities from
        ### the source and target datasets
        ### and... VOILA!!!
        ### The only thing is that all ?g being linksets :(
        ### More to come on the mixed :-)
        graph ?source
        {{
           ?sub ?srcPre ?srcObj.
        }}

        graph ?target
        {{
           ?obj ?trgPre ?trgObj.
        }}
    }}
    """.format(PREFIX, union)

    print query


get_target_datasets(["alivocab:exactStrSim1_aaea1f82-c0a3-4e6d-b653-ff8bd1e9406d",
                     "linkset:subset_grid_orgref_C1_unknown_738f0f6f-34db-45a3-9be6-9405a16eb8f2",
                     "linkset:subset_orgref_grid_C1_unknown_64a0785b-4811-4f39-ae90-58587740cd23"])