import src.Alignments.Settings as St
import src.Alignments.NameSpace as Ns
import src.Alignments.Query as Qry
from Linkset import writelinkset, write_to_path, update_specification
import logging
import Linkset as Ls
import src.Alignments.GenericMetadata as Gn

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)
handler = logging.StreamHandler()
logger.addHandler(handler)


def linkset_info(specs, same_as_count):
    info = "{}{}{}{}{}{}". \
        format("======================================================="
               "=======================================================\n",
               "Results for creating the linkset between {} and {}.\n".format(
                   specs[St.source][St.graph_name], specs[St.target][St.graph_name],
                   specs[St.context_code], specs[St.mechanism]),

               "\t   Linksets GRAPH            : linkset:{}_{}_C{}_{}\n".format(
                   specs[St.source][St.graph_name], specs[St.target][St.graph_name],
                   specs[St.context_code], specs[St.mechanism]),

               "\t   Metadata GRAPH            : lsMetadata:{}_{}_C{}_{}\n".format(
                   specs[St.source][St.graph_name], specs[St.target][St.graph_name],
                   specs[St.context_code], specs[St.mechanism]),

               "\t   Singleton Metadata GRAPH  : GRAPH singMetadata:{}_{}_C{}_{}\n".format(
                   specs[St.source][St.graph_name], specs[St.target][St.graph_name],
                   specs[St.context_code], specs[St.mechanism]),

               "\t   LINKTYPE                  : alivocab:{}{}\n".format(specs[St.mechanism], same_as_count))
    return info


def spa_linksets(specs, database_name, host, display=False, activated=False):

    source = specs[St.source]
    target = specs[St.target]
    # The name of the linkset
    linkset_name = "{}_{}_C{}_{}".format(
        source[St.graph_name], target[St.graph_name], specs[St.context_code], specs[St.mechanism])
    linkset = "{}{}".format(Ns.linkset, linkset_name)

    # This function is designed for EXACT NAME SIMILARITY RUN AS SPARQL QUERIES
    try:

        if activated is False:
            print "THE FUNCTION IS NOT ACTIVATED." \
                  "\n======================================================" \
                  "========================================================"
            return {"message": "THE FUNCTION IS NOT ACTIVATED.", 'error_code': 1, 'linkset': None}

        if activated is True:

            if specs[St.sameAsCount] is None:
                print "PROBLEM"
                return {"message": "PROBLEM", 'error_code': 1, 'linkset': None}

            # Check whether this linkset was already generated. If yes, delete it or change the context code
            ask_query = "ASK {{ <{}> ?p ?o . }}".format(linkset)
            ask = Qry.boolean_endpoint_response(ask_query, database_name, host)
            if ask == "true":
                # logger.warning("\n{} ALREADY EXISTS. \nTO PROCEED ANYWAY, PLEASE DELETE "
                #                "THE LINKSET FIRST OR CHANGE THE CONTEXT CODE\n".format(linkset))

                server_message = ("LINKSET <{}> ALREADY EXISTS. \nTO PROCEED ANYWAY, PLEASE DELETE "
                           "THE LINKSET FIRST OR CHANGE THE CONTEXT CODE\n".format(linkset))
                message = ("LINKSET \"{}\" ALREADY EXISTS.<br/>TO PROCEED ANYWAY, PLEASE DELETE "
                           "THE LINKSET FIRST OR CHANGE THE CONTEXT CODE".format(linkset))
                print server_message

                return {"message": message, 'error_code': 1, 'linkset': linkset}

            print linkset_info(specs, specs[St.sameAsCount])

            # Generating insert quarries
            insertqueries = specs[St.linkset_insert_queries]

            # LINKSET insert Query
            specs[St.insert_query] = "{}\n{}\n{}".format(insertqueries[1], insertqueries[2], insertqueries[3])
            # print insertqueries[0], '\n', insertqueries[1], '\n', insertqueries[2], '\n', insertqueries[3]

            # print time.time()
            #########################################################################
            """ 1. SAFETY GRAPHS DROPS                                            """
            ########################################################################
            Qry.boolean_endpoint_response(insertqueries[0], database_name, host)

            ########################################################################
            """ 2. TEMPORARY GRAPHS                                              """
            ########################################################################
            Qry.boolean_endpoint_response(insertqueries[1], database_name, host)

            ########################################################################
            """ 3. LINKSET & METADATA                                            """
            ########################################################################
            Qry.boolean_endpoint_response(insertqueries[2], database_name, host)

            ########################################################################
            """ 4. DROPPING TEMPORARY GRAPHS                                     """
            ########################################################################
            Qry.boolean_endpoint_response(insertqueries[3], database_name, host)

            ########################################################################
            """ 5. GENERATING LINKSET METADATA                                   """
            ########################################################################
            metadata = Gn.linkset_metadata(specs, database_name, host)
            if int(specs[St.triples]) > 0:
                Qry.boolean_endpoint_response(metadata, database_name, host)

                ########################################################################
                """ 6. WRITING TO FILE                                               """
                ########################################################################
                src = [source[St.graph_name], "", source[St.entity_ns]]
                trg = [target[St.graph_name], "", target[St.entity_ns]]

                print "\t>>> WRITING TO FILE"
                # linkset_path = "D:\datasets\Linksets\ExactName"
                linkset_path = write_to_path
                writelinkset(src, trg, linkset_name, linkset_path, metadata, database_name, host)
                server_message = "Linksets created as: {}".format(linkset)
                message = "The linkset was created!<br/>URI = {}".format(linkset)
                print "\t", server_message
                print "\t*** JOB DONE! ***"
                return { "message": message, 'error_code': 0, 'linkset': linkset}

            else:
                print metadata

        elif display is True:

            # Generating insert quarries
            insertqueries = spa_linkset_ess_query(specs)
            # LINKSET insert Query
            specs[St.insert_query] = "{}\n{}\n{}".format(insertqueries[1], insertqueries[2], insertqueries[3])
            # print insertqueries[0], '\n', insertqueries[1], '\n', insertqueries[2], '\n', insertqueries[3]
            metadata = Gn.linkset_metadata(specs, database_name, host)
            print metadata
            return None

    except Exception as err:
        # logger.warning(err)
        print err


def spa_linkset_ess_query(specs):
    # Single Predicate Alignment with Exact String Similarity
    source = specs[St.source]
    target = specs[St.target]

    """
        NAMESPACE
    """
    prefix = "\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}".format(
        "##################################################################",
        "### Linking {{{}}} to {{{}}} based on exact name".format(source[St.graph_name], target[St.graph_name]),
        "##################################################################",
        "prefix dataset:    <{}>".format(Ns.dataset),
        "prefix linkset:    <{}>".format(Ns.linkset),
        "prefix singleton:  <{}>".format(Ns.singletons),
        "prefix alivocab:   <{}>".format(Ns.alivocab),
        "prefix tmpgraph:   <{}>".format(Ns.tmpgraph),
        "prefix tmpvocab:   <{}>".format(Ns.tmpvocab))
    '''
        DROPPING GRAPHS
    '''
    drop_tmp = "DROP SILENT GRAPH tmpgraph:load"
    drop_tmp00 = "DROP SILENT GRAPH tmpgraph:load00"
    drop_tmp01 = "DROP SILENT GRAPH tmpgraph:load01"
    # drop_ls = "DROP SILENT GRAPH linkset:{}_{}_ExactName".format(src_dataset_name, trg_dataset_name)
    # drop_metadata = "DROP SILENT GRAPH lsMetadata:{}_{}_ExactName_metadata".format(src_dataset_name, trg_dataset_name)

    drop_ls = "DROP SILENT GRAPH linkset:{}_{}_C{}_{}".format(
        source[St.graph_name], target[St.graph_name], specs[St.context_code], specs[St.mechanism])
    drop_metadata = "DROP SILENT GRAPH singleton:{}_{}_C{}_{}".format(
        source[St.graph_name], target[St.graph_name], specs[St.context_code], specs[St.mechanism])

    '''
        LOADING SOURCE TO TEMPORARY GRAPH tmpgraph:load00
    '''
    load_temp00 = "{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}". \
        format("\tINSERT",
               "\t{",
               "\t  GRAPH tmpgraph:load00",
               "\t  {",
               "\t    ?source <{}> ?label .".format(source[St.aligns]),
               "\t  }",
               "\t}",

               "\tWHERE",
               "\t{",
               "\t  ### Selecting source data instances based on name",
               "\t  GRAPH <{}>".format(source[St.graph]),
               "\t  {",
               "\t    ?source <{}> ?aLabel .".format(source[St.aligns]),
               "\t    BIND(lcase(str(?aLabel)) as ?label)",
               "\t  }",
               "\t}")

    '''
        LOADING TARGET TO TEMPORARY GRAPH tmpgraph:load01
    '''
    load_temp01 = "{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}". \
        format("\tINSERT",
               "\t{",
               "\t  GRAPH tmpgraph:load01",
               "\t  {",
               "\t    ?target <{}>  ?label .".format(target[St.aligns]),
               "\t  }",
               "\t}",

               "\tWHERE",
               "\t{",
               "\t  ### Selecting target data instances based on exact name",
               "\t  graph <{}>".format(target[St.graph]),
               "\t  {",
               "\t    ?target <{}>  ?bLabel .".format(target[St.aligns]),
               "\t    BIND(lcase(str(?bLabel)) as ?label)",
               "\t  }",
               "\t}")

    '''
        LOADING CORRESPONDENCE TO TEMPORARY GRAPH tmpgraph:load
    '''
    load_temp = "{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}". \
        format("\tINSERT",
               "\t{",
               "\t  GRAPH tmpgraph:load",
               "\t  {",
               "\t    ?source tmpvocab:exactName ?target ;",
               "\t            tmpvocab:evidence  ?label .",
               "\t  }",
               "\t}",
               # Load
               "\tWHERE",
               "\t{",
               "\t  ### Selecting source data instances based on name",
               "\t  GRAPH tmpgraph:load00",
               "\t  {",
               "\t    ?source <{}> ?label .".format(source[St.aligns]),
               "\t  }",

               "\t  ### Selecting target data instances based on exact name",
               "\t  graph tmpgraph:load01",
               "\t  {",
               "\t    ?target <{}>  ?label .".format(target[St.aligns]),
               "\t  }",

               "\t}", )

    '''
        CREATING THE LINKSET & METADATA GRAPHS lsMetadata
    '''
    load_linkset = "{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}" \
                   "\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}". \
        format("\tINSERT",
               "\t{",
               "\t  GRAPH linkset:{}_{}_C{}_{}".
               format(source[St.graph_name], target[St.graph_name], specs[St.context_code], specs[St.mechanism]),
               "\t  {",
               "\t    ### Correspondence triple with singleton",
               "\t    ?source ?singPre ?target.",
               "\t  }",

               "\t  GRAPH singleton:{}_{}_C{}_{}".format(
                   source[St.graph_name], target[St.graph_name], specs[St.context_code], specs[St.mechanism]),
               "\t  {",
               "\t    ### Singleton metadata",
               "\t    ?singPre rdf:singletonPropertyOf     alivocab:exactStrSim{} ;".format(specs[St.sameAsCount]),
               "\t             alivocab:hasEvidence        ?label .",
               "\t  }",

               "\t}",
               "\tWHERE",
               "\t{",
               "\t  ### Selecting from tmpgraph:load",
               "\t  GRAPH tmpgraph:load",
               "\t  {",
               "\t    ?source tmpvocab:exactName ?target ;",
               "\t            tmpvocab:evidence  ?label .",
               "\t            ",
               "\t    ### Create A SINGLETON URI",
               "\t    BIND( replace(\"{}{}{}_#\",\"#\",".format(
                   Ns.alivocab, specs[St.mechanism], specs[St.sameAsCount]),
               "\t        STRAFTER(str(UUID()),\"uuid:\")) as ?pre )",
               "\t    BIND(iri(?pre) as ?singPre)",
               "\t  }",
               "\t}")

    '''
        PUTTING IT ALL TOGETHER
    '''
    query01 = "{}\n\n{}\n\t{} ;\n\n{}\n\t{} ;\n\n{}\n\t{} ;\n\n{}\n{} ;\n\n{}\n\t{}".format(
        prefix,
        "### 1.0 DROP temporary graph",
        drop_tmp,
        "### 1.1 DROP SOURCE temporary graph 00",
        drop_tmp00,
        "### 1.2 DROP TARGET temporary graph 01",
        drop_tmp01,
        "### 1.3 DROP LINKSET graph",
        drop_ls,
        "### 1.4 DROP METADATA graph",
        drop_metadata
    )

    query02 = "{}\n\n{}\n{} ;\n\n{}\n{} ;\n\n{}\n{} ".format(
        prefix,
        "### 2.0 INSERT SOURCE into tmpgraph:load00",
        load_temp00,
        "### 2.1 INSERT TARGET into tmpgraph:load01",
        load_temp01,
        "### 2.3 INSERT CORRESPONDENCE [match] into tmpgraph:load",
        load_temp,
    )

    query03 = "{}\n\n{}\n{}".format(
        prefix,
        "### 3.0 CREATING AND LOADING THE LINKSET AND ITS METADATA",
        load_linkset,
    )

    query04 = "{}\n\n{}\n\t{} ;\n\t{} ;\n\t{}".format(
        prefix,
        "### 4.0 DROP temporary graphs",
        drop_tmp00,
        drop_tmp01,
        drop_tmp
    )

    queries = [query01, query02, query03, query04]

    return queries


def spa_linkset_identity_query(specs):
    # Single Predicate Alignment with Exact String Similarity

    source = specs[St.source]
    target = specs[St.target]
    """
        NAMESPACE
    """
    prefix = "\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}".format(
        "##################################################################",
        "### Linking {{{}}} to {{{}}} based on exact name".format(source[St.graph_name], target[St.graph_name]),
        "##################################################################",
        "prefix dataset:    <{}>".format(Ns.dataset),
        "prefix linkset:    <{}>".format(Ns.linkset),
        "prefix singleton:  <{}>".format(Ns.singletons),
        "prefix alivocab:   <{}>".format(Ns.alivocab),
        "prefix tmpgraph:   <{}>".format(Ns.tmpgraph),
        "prefix tmpvocab:   <{}>".format(Ns.tmpvocab))

    ''' DROPPING GRAPHS '''
    drop_tmp = "DROP SILENT GRAPH tmpgraph:load"
    drop_tmp00 = "DROP SILENT GRAPH tmpgraph:load00"
    drop_tmp01 = "DROP SILENT GRAPH tmpgraph:load01"

    drop_ls = "DROP SILENT GRAPH linkset:{}_{}_C{}_{}".format(
        source[St.graph_name], target[St.graph_name], specs[St.context_code], specs[St.mechanism])
    drop_metadata = "DROP SILENT GRAPH singleton:{}_{}_C{}_{}".format(
        source[St.graph_name], target[St.graph_name], specs[St.context_code], specs[St.mechanism])

    ''' LOADING SOURCE TO TEMPORARY GRAPH tmpgraph:load00 '''
    load_temp00 = """
    INSERT
    {{
        GRAPH tmpgraph:load00 {{ ?source <{0}> <{1}> . }}
    }}
    WHERE
    {{
        ### Selecting source data instances based on name
        GRAPH <{2}> {{ ?source <{0}> <{1}> . }}
    }}""".format(source[St.aligns], source[St.entity_datatype], source[St.graph])

    ''' LOADING TARGET TO TEMPORARY GRAPH tmpgraph:load01 '''
    load_temp01 = """
    INSERT
    {{
       GRAPH tmpgraph:load01 {{ ?target <{0}> <{1}> . }}
    }}
    WHERE
    {{
       ### Selecting target data instances based on name
       GRAPH <{2}> {{ ?target <{0}> <{1}> . }}
    }}""".format(target[St.aligns], target[St.entity_datatype], target[St.graph])

    ''' LOADING CORRESPONDENCE TO TEMPORARY GRAPH tmpgraph:load '''
    load_temp = """
    INSERT
    {{
        GRAPH tmpgraph:load
        {{
            ?subject tmpvocab:identical ?subject ;
                     tmpvocab:evidence  "Identical resource URI ." .
        }}
    }}
    WHERE
    {{
        GRAPH tmpgraph:load00 {{ ?subject <{}> <{}> . }}
        GRAPH tmpgraph:load01 {{ ?subject <{}> <{}> . }}
    }}""".format(source[St.aligns], source[St.entity_datatype],
                 target[St.aligns], target[St.entity_datatype])

    ''' CREATING THE LINKSET & METADATA GRAPHS lsMetadata '''
    load_linkset = """
        INSERT
        {{
            GRAPH linkset:{0}_{1}_C{2}_{3}
            {{
                ### Correspondence triple with singleton
                ?source ?singPre ?target .
            }}

            GRAPH singleton:{0}_{1}_C{2}_{3}
            {{
                ### ### Singleton metadata
                ?singPre
                    rdf:singletonPropertyOf     alivocab:exactStrSim{4} ;
                    alivocab:hasEvidence        ?label .
            }}
        }}
        WHERE
        {{
            ### Selecting from tmpgraph:load
            GRAPH tmpgraph:load
            {{
                ?source
                    tmpvocab:identical ?target ;
                    tmpvocab:evidence  ?label .

                ### Create A SINGLETON URI"
                BIND( replace("{5}{3}{6}_#", "#", STRAFTER(str(UUID()),"uuid:")) as ?pre )
                BIND( iri(?pre) as ?singPre )
            }}
        }}""".format(source[St.graph_name], target[St.graph_name], specs[St.context_code], specs[St.mechanism], "",
                     Ns.alivocab, specs[St.sameAsCount])

    '''
        PUTTING IT ALL TOGETHER
    '''
    query01 = "{}\n\n{}\n\t{} ;\n\n{}\n\t{} ;\n\n{}\n\t{} ;\n\n{}\n{} ;\n\n{}\n\t{}".format(
        prefix,
        "### 1.0 DROP temporary graph",
        drop_tmp,
        "### 1.1 DROP SOURCE temporary graph 00",
        drop_tmp00,
        "### 1.2 DROP TARGET temporary graph 01",
        drop_tmp01,
        "### 1.3 DROP LINKSET graph",
        drop_ls,
        "### 1.4 DROP METADATA graph",
        drop_metadata
    )

    query02 = "{}\n\n{}\n{} ;\n\n{}\n{} ;\n\n{}\n{} ".format(
        prefix,
        "### 2.0 INSERT SOURCE into tmpgraph:load00",
        load_temp00,
        "### 2.1 INSERT TARGET into tmpgraph:load01",
        load_temp01,
        "### 2.3 INSERT CORRESPONDENCE [match] into tmpgraph:load",
        load_temp,
    )

    query03 = "{}\n\n{}\n{}".format(
        prefix,
        "### 3.0 CREATING AND LOADING THE LINKSET AND ITS METADATA",
        load_linkset,
    )

    query04 = "{}\n\n{}\n\t{} ;\n\t{} ;\n\t{}".format(
        prefix,
        "### 4.0 DROP temporary graphs",
        drop_tmp00,
        drop_tmp01,
        drop_tmp
    )

    queries = [query01, query02, query03, query04]

    return queries


def specs_2_linkset(specs, database_name, host, display=False, activated=False):

    # if activated is False:
    #     logger.warning("THE FUNCTION IS NOT ACTIVATED."
    #                    "\n======================================================"
    #                    "========================================================")

    # if activated is True:
    print "\nEXECUTING LINKSET SPECS"

    update_specification(specs[St.source])
    update_specification(specs[St.target])
    specs[St.sameAsCount] = Qry.get_same_as_count(specs[St.mechanism], database_name, host)
    specs[St.linkset_insert_queries] = spa_linkset_ess_query(specs)
    return spa_linksets(specs, database_name, host, display, activated)


def specs_2_linkset_id(specs, database_name, host, display=False, activated=False):

    # if activated is False:
    #     logger.warning("THE FUNCTION IS NOT ACTIVATED."
    #                    "\n======================================================"
    #                    "========================================================")

    # if activated is True:
    print "\nEXECUTING LINKSET SPECS"

    update_specification(specs[St.source])
    update_specification(specs[St.target])
    specs[St.sameAsCount] = Qry.get_same_as_count(specs[St.mechanism], database_name, host)
    specs[St.linkset_insert_queries] = spa_linkset_identity_query(specs)
    return spa_linksets(specs, database_name, host, display, activated)


########################################################################################
# See if this makes sens or is necessary
########################################################################################


def pred_match(dataset_list, database_name, host):

    def helper1(index, predicate, obj):
        sparql_query = "?{} <{}> ?{} .".format(index, predicate, obj)
        return [" ?{}".format(obj), sparql_query, ]

    def helper2(graph_uri, triple_lines):
        sparql_query = """
    GRAPH <{}>
    {{
        {}
    }}""".format(graph_uri, triple_lines)
        return sparql_query

    pred_count = 0
    dataset_dict = dict()
    if type(dataset_list) is list:
        # For each dataset, gather its predicates
        for dataset in dataset_list:
            predicates = Qry.get_properties(dataset, database_name, host)
            # Load it into the dictionary
            if predicates is not None:
                # going through the predicates
                for i in range(1, len(predicates)):
                    if predicates[i][0] != "http://www.w3.org/1999/02/22-rdf-syntax-ns#type":
                        local_name = Ls.get_URI_local_name(predicates[i][0])

                        # Insert a new key
                        if local_name not in dataset_dict:
                            pred_count += 1
                            temp_dict = dict()
                            temp_dict[pred_count] = [dataset, predicates[i][0]]
                            dataset_dict[local_name] = temp_dict

                        # we found a match in property name
                        else:
                            pred_count += 1
                            curr_dict = dataset_dict[local_name]
                            curr_dict[pred_count] = [dataset, predicates[i][0]]

    # Write the SPARQL query for checking whether there is an actual match
    query = "SELECT DISTINCT"
    sub_query = ""
    group = dict()
    pre_dict = dict()
    for pred, data in dataset_dict.items():

        if len(data) > 1:
            for key, value in data.items():
                dataset = value[0]
                prd = value[1]
                dataset_name = Ls.get_URI_local_name(dataset)

                if dataset not in group:
                    line = helper1(dataset_name, prd, pred)
                    group[dataset] = line[1]
                    if line[0] not in pre_dict:
                        pre_dict[line[0]] = pred

                else:
                    line = helper1(dataset_name, prd, pred)
                    group[dataset] += "\n\t\t{}".format(line[1])
                    if line[0] not in pre_dict:
                        pre_dict[line[0]] = pred

                # print group[dataset]
    for key in pre_dict:
        query += " {}".format(key)
    for graph, triples in group.items():
        sub_query += helper2(graph, triples)
    #             result = helper(key, value[0], value[1])
    #             sub_query += result[1]
    #             query += result[0]

    query = "{}\n{{{}\n}}".format(query, sub_query)
    response = Qry.sparql_xml_to_matrix(query, database_name, host)
    print query
    if response is None:
        print "No match"

# "http://risis.eu/dataset/orgref"
# "http://risis.eu/dataset/grid"
# dt_base = "risis"
# hst = "localhost:5820"
# print pred_match(["http://risis.eu/dataset/orgref", "http://risis.eu/dataset/grid",
#                   "http://risis.eu/dataset/eter", "http://risis.eu/dataset/leidenRanking",
#                   "http://risis.eu/dataset/gridStats"],
#                  dt_base, hst)
