import logging

import Linkset as Ls
import src.Alignments.ErrorCodes as Ec
import src.Alignments.GenericMetadata as Gn
import src.Alignments.NameSpace as Ns
import src.Alignments.Query as Qry
import src.Alignments.Settings as St
import src.Alignments.UserActivities.UserRQ as Urq
import src.Alignments.Utility as Ut
from Linkset import writelinkset
from src.Alignments.Utility import write_to_path, update_specification

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)
handler = logging.StreamHandler()
logger.addHandler(handler)

"""
SINGLE PREDICATE ALIGNMENT
    - THE NAME OF A LINKSET SHOULD BE FORMATTED AS [SRC DATASET]_[TARGET DATASET]_[SRC ALIGNS]_[MECHANISM]
    - spa_linksets ONY HANDLES THE EXACT STRING SIMILARITY MECHANISM
    - BECAUSE IDENTITY IS ABOUT MATCHING EXACT SUBJECT WITH THE SAME URI IDENTIFIER, THIS FUNCTION IS ALSO USED BY
      PLUGGING DIFFERENT INSERT QUERIES
    - THE "sameAsCount" VARIABLE HELPS CREATING TASK SPECIFIC PREDICATE BY APPENDING AN INTEGER TO THE PARENT PREDICATE.
      WHEN EVER THE "sameAsCount" VARIABLE IS NULL, AN ERROR-CODE 1 IS RETURNED
"""


def spa_linksets(specs, id=False, display=False, activated=False):

    if activated is False:
        print "THE FUNCTION IS NOT ACTIVATED." \
              "\n======================================================" \
              "========================================================"
        return {St.message: "THE FUNCTION IS NOT ACTIVATED.", St.error_code: 1, St.result: None}

    source = specs[St.source]
    target = specs[St.target]

    """
    # CHECK WHETHER A METADATA DESCRIBING THIS LINKSET EXIST
    """
    # THE NAME OF A LINKSET SHOULD BE FORMATTED AS FOLLOW:
    #   [SRC DATASET]_[TARGET DATASET]_[SRC ALIGNS]_[MECHANISM]
    if St.linkset not in specs:
        # GENERATE THE NAME OF THE LINKSET
        Ls.set_linkset_name(specs)

    # This function is designed for EXACT NAME SIMILARITY RUN AS SPARQL QUERIES
    # if True:
    try:

        if activated is True:
            # print "NAME: " + specs[St.linkset]
            # CHECK WHETHER OR NOT THE LINKSET WAS ALREADY CREATED

            if id is False:
                check = Ls.run_checks(specs)
            else:
                check = Ls.run_checks_id(specs)

            if check[St.result] != "GOOD TO GO":
                return check

            # print "NAME: " + specs[St.linkset]


            # THE LINKSET DOES NOT EXIT, LETS CREATE IT NOW
            print Ls.linkset_info(specs, specs[St.sameAsCount])

            # Generating insert quarries
            insertqueries = specs[St.linkset_insert_queries]

            # LINKSET insert Query
            specs[St.insert_query] = "{}\n{}\n{}".format(insertqueries[1], insertqueries[2], insertqueries[3])
            # print insertqueries[0], '\n', insertqueries[1], '\n', insertqueries[2], '\n', insertqueries[3]

            # print time.time()
            ########################################################################
            """ 1. SAFETY GRAPHS DROPS                                           """
            ########################################################################
            Qry.boolean_endpoint_response(insertqueries[0])

            ########################################################################
            """ 2. TEMPORARY GRAPHS                                              """
            ########################################################################
            Qry.boolean_endpoint_response(insertqueries[1])

            ########################################################################
            """ 3. LINKSET & METADATA                                            """
            ########################################################################
            Qry.boolean_endpoint_response(insertqueries[2])

            ########################################################################
            """ 4. DROPPING TEMPORARY GRAPHS                                     """
            ########################################################################
            Qry.boolean_endpoint_response(insertqueries[3])

            ########################################################################
            """ 5. GENERATING LINKSET METADATA                                   """
            ########################################################################
            metadata = Gn.linkset_metadata(specs)

            # NO POINT TO CREATE ANY FILE WHEN NO TRIPLE WAS INSERTED
            if int(specs[St.triples]) > 0:

                Qry.boolean_endpoint_response(metadata)

                ########################################################################
                """ 6. WRITING TO FILE                                               """
                ########################################################################
                src = [source[St.graph_name], "", source[St.entity_ns]]
                trg = [target[St.graph_name], "", target[St.entity_ns]]

                print "\t>>> WRITING TO FILE"
                # linkset_path = "D:\datasets\Linksets\ExactName"
                linkset_path = write_to_path
                writelinkset(src, trg, specs[St.linkset_name], linkset_path, metadata)
                server_message = "Linksets created as: {}".format(specs[St.linkset])
                message = "The linkset was created!<br/>URI = {}".format(specs[St.linkset])
                print "\t", server_message
                print "\t*** JOB DONE! ***"

                if display is True:
                    # Generating insert quarries
                    insertqueries = spa_linkset_ess_query(specs)
                    # LINKSET insert Query
                    specs[St.insert_query] = "{}\n{}\n{}".format(insertqueries[1], insertqueries[2], insertqueries[3])
                    # print insertqueries[0], '\n', insertqueries[1], '\n', insertqueries[2], '\n', insertqueries[3]
                    metadata = Gn.linkset_metadata(specs)
                    print metadata

                return {St.message: message, St.error_code: 0, St.result: specs[St.linkset]}

            else:
                return {St.message: Ec.ERROR_CODE_4.replace('\n', "<br/>"), St.error_code: 4, St.result: None}

    except Exception as err:
        # logger.warning(err)
        print "ERROR IN SPA_LINKSET", err
        return {St.message: Ec.ERROR_CODE_4.replace('\n', "<br/>"), St.error_code: 4, St.result: None}


########################################################################################
# SINGLE PREDICATE ALIGNMENT
########################################################################################


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

    drop_ls = "DROP SILENT GRAPH linkset:{}".format(specs[St.linkset_name])
    drop_metadata = "DROP SILENT GRAPH singleton:{}".format(specs[St.linkset_name])

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
               "\t  GRAPH linkset:{}".format(specs[St.linkset_name]),
               "\t  {",
               "\t    ### Correspondence triple with singleton",
               "\t    ?source ?singPre ?target.",
               "\t  }",

               "\t  GRAPH singleton:{}".format(specs[St.linkset_name]),
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

    # print query01, query02, query03, query04

    return queries


def specs_2_linkset(specs, display=False, activated=False):

    # if activated is True:
    heading = "\nEXECUTING LINKSET SPECS" \
              "\n======================================================" \
              "========================================================"

    inserted_mapping = None
    inserted_linkset = None

    # ACCESS THE TASK SPECIFIC PREDICATE COUNT BEFORE YOU DO ANYTHING
    specs[St.sameAsCount] = Qry.get_same_as_count(specs[St.mechanism])

    if specs[St.sameAsCount]:

        # UPDATE THE SPECS OF SOURCE AND TARGETS
        update_specification(specs[St.source])
        update_specification(specs[St.target])

        # GENERATE THE NAME OF THE LINKSET
        Ls.set_linkset_name(specs)

        # SET THE INSERT QUERY
        specs[St.linkset_insert_queries] = spa_linkset_ess_query(specs)

        # GENERATE THE LINKSET
        inserted_linkset = spa_linksets(specs, display, activated)

        # REGISTER THE ALIGNMENT
        if inserted_linkset[St.message].__contains__("ALREADY EXISTS"):
            Urq.register_alignment_mapping(specs, created=False)
        else:
            Urq.register_alignment_mapping(specs, created=True)

        # SPA_LINKSET returns
        # {St.message: message, St.error_code: 0, St.result: specs[St.linkset]}
        return inserted_linkset

    else:
        print "HERE!!!!!!!!!!!!!"
        print Ec.ERROR_CODE_1
        return {St.message: Ec.ERROR_CODE_1, St.error_code: 5, St.result: None}


########################################################################################
# SINGLE PREDICATE ALIGNMENT IDENTITY
# ALIGNING SUBJECTS FROM DIFFERENT GRAPHS THAT HAVE THE SAME RESOURCE URI IDENTIFIER
########################################################################################


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

    drop_ls = "DROP SILENT GRAPH linkset:{}".format(specs[St.linkset_name])
    drop_metadata = "DROP SILENT GRAPH singleton:{}".format(specs[St.linkset_name])

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
            GRAPH linkset:{0}
            {{
                ### Correspondence triple with singleton
                ?source ?singPre ?target .
            }}

            GRAPH singleton:{0}
            {{
                ### ### Singleton metadata
                ?singPre
                    rdf:singletonPropertyOf     alivocab:exactStrSim{1} ;
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
                BIND( replace("{2}{3}{4}_#", "#", STRAFTER(str(UUID()),"uuid:")) as ?pre )
                BIND( iri(?pre) as ?singPre )
            }}
        }}""".format(specs[St.linkset_name], specs[St.sameAsCount],
                     Ns.alivocab, specs[St.mechanism],  specs[St.sameAsCount])

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
    # print query01
    # print query02
    # print query03

    return queries


def specs_2_linkset_id(specs, display=False, activated=False):

    print "\nEXECUTING LINKSET SPECS" \
          "\n======================================================" \
          "========================================================"

    # ACCESS THE TASK SPECIFIC PREDICATE COUNT
    specs[St.sameAsCount] = Qry.get_same_as_count(specs[St.mechanism])

    # UPDATE THE QUERY THAT IS GOING TO BE EXECUTED
    if specs[St.sameAsCount]:

        specs[St.source][St.aligns] = "{}type".format(Ns.rdf)
        specs[St.target][St.aligns] = "{}type".format(Ns.rdf)

        # UPDATE THE SPECS OF SOURCE AND TARGETS
        update_specification(specs[St.source])
        update_specification(specs[St.target])

        # GENERATE THE NAME OF THE LINKSET
        # GENERATE THE NAME OF THE LINKSET
        Ls.set_linkset_identity_name(specs)

        # SET THE INSERT QUERY
        specs[St.linkset_insert_queries] = spa_linkset_identity_query(specs)
        # print specs[St.linkset_insert_queries]

        # GENERATE THE LINKSET
        inserted_linkset = spa_linksets(specs, id=True, display=display, activated=activated)

        # REGISTER THE ALIGNMENT
        if inserted_linkset[St.message].__contains__("ALREADY EXISTS"):
            Urq.register_alignment_mapping(specs, created=False)
        else:
            Urq.register_alignment_mapping(specs, created=True)

        # SPA_LINKSET returns
        # {St.message: message, St.error_code: 0, St.result: specs[St.linkset]}
        return inserted_linkset

    else:
        print Ec.ERROR_CODE_1
        return {St.message: Ec.ERROR_CODE_1, St.error_code: 5, St.result: None}


########################################################################################
# See if this makes sens or is necessary
########################################################################################


def pred_match(dataset_list):

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
            predicates = Qry.get_properties(dataset)
            # Load it into the dictionary
            if predicates is not None:
                # going through the predicates
                for i in range(1, len(predicates)):
                    if predicates[i][0] != "http://www.w3.org/1999/02/22-rdf-syntax-ns#type":
                        local_name = Ut.get_uri_local_name(predicates[i][0])

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
                dataset_name = Ut.get_uri_local_name(dataset)

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
    response = Qry.sparql_xml_to_matrix(query)
    print query
    if response is None:
        print "No match"
