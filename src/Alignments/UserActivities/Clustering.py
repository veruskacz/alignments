import datetime
import rdflib
import Alignments.Settings as St
import Alignments.NameSpace as Ns
import Alignments.UserActivities.ExportAlignment as Exp
# from Alignments.Utility import get_uri_local_name as local_name
from Alignments.Query import sparql_xml_to_matrix as sparql2matrix
import Alignments.Query as Qry

_format = "%a %b %d %H:%M:%S:%f %Y"


def cluster(graph):

    count = 0
    clusters = dict()
    root = dict()

    for pair in graph:

        count += 1
        child_1 = pair[0]
        child_2 = pair[1]
        parent = ""

        # DATE CREATION
        date = "{}".format(datetime.datetime.today().strftime(_format))

        # CHECK WHETHER A CHILD HAS A PARENT
        has_parent_1 = True if child_1 in root else False
        has_parent_2 = True if child_2 in root else False
        print "{} Has Parents {}|{}".format(pair, has_parent_1, has_parent_2)

        if has_parent_1 is False and has_parent_2 is False:

            # GENERATE THE PARENT
            hash_value = hash(date + str(count) + graph)
            parent = "{}".format(str(hash_value).replace("-", "N")) if str(hash_value).startswith("-") \
                else "P{}".format(hash_value)

            # ASSIGN A PARENT TO BOTH CHILD
            root[child_1] = parent
            root[child_2] = parent

            # CREATE A CLUSTER
            if parent not in clusters:
                clusters[parent] = [child_1, child_2]

        elif has_parent_1 is True and has_parent_2 is True:

            # IF BOTH CHILD HAVE THE SAME PARENT, DO NOTHING
            if clusters[root[child_1]] == clusters[root[child_2]]:
                print "{} NOTHING TO DO\n".format(len(clusters))
                continue

            # THE PARENT WITH THE MOST CHILD GET THE CHILD OF THE OTHER PARENT
            if len(clusters[root[child_1]]) >= len(clusters[root[child_2]]):
                parent = root[child_1]
                pop_parent = root[child_2]
                root[child_2] = parent

            else:
                parent = root[child_2]
                pop_parent = root[child_1]
                root[child_1] = parent

            # ALL CHILD OF PARENT (SMALL) ARE REASSIGNED A NEW PARENT
            for child in clusters[pop_parent]:
                root[child] = parent
                clusters[parent] += [child]

            # POP THE PARENT WITH THE LESSER CHILD
            clusters.pop(pop_parent)

        elif has_parent_1 is True:

            # THE CHILD WITH NO PARENT IS ASSIGNED TO THE PARENT OF THE CHILD WITH PARENT
            parent = root[child_1]
            root[child_2] = parent
            clusters[parent] += [child_2]

        elif has_parent_2 is True:

            # THE CHILD WITH NO PARENT IS ASSIGNED TO THE PARENT OF THE CHILD WITH PARENT
            parent = root[child_2]
            root[child_1] = parent
            clusters[parent] += [child_1]

        print "{} Clusters but the current is: {}\n".format(len(clusters), clusters[parent])

    return clusters


def cluster_triples(graph):

    count = 0
    clusters = dict()
    root = dict()

    # DOWNLOAD THE GRAPH
    print "\n0. DOWNLOADING THE GRAPH"
    response = Exp.export_alignment(graph)
    links = response['result']
    # print links

    # LOAD THE GRAPH
    print "1. LOADING THE GRAPH"
    g = rdflib.Graph()
    g.parse(data=links, format="turtle")

    print "2. ITERATING THROUGH THE GRAPH OF SIZE {}".format(len(g))
    for subject, predicate, obj in g:

        count += 1
        child_1 = subject
        child_2 = obj
        # parent = ""

        # DATE CREATION
        date = "{}".format(datetime.datetime.today().strftime(_format))

        # CHECK WHETHER A CHILD HAS A PARENT
        has_parent_1 = True if child_1 in root else False
        has_parent_2 = True if child_2 in root else False

        # print "{}|{} Has Parents {}|{}".format(child_1, child_2, has_parent_1, has_parent_2)

        if has_parent_1 is False and has_parent_2 is False:

            # GENERATE THE PARENT
            hash_value = hash(date + str(count) + graph)
            parent = "{}".format(str(hash_value).replace("-", "N")) if str(hash_value).startswith("-") \
                else "P{}".format(hash_value)

            # ASSIGN A PARENT TO BOTH CHILD
            root[child_1] = parent
            root[child_2] = parent

            # CREATE A CLUSTER
            if parent not in clusters:
                clusters[parent] = [child_1, child_2]

        elif has_parent_1 is True and has_parent_2 is True:

            # IF BOTH CHILD HAVE THE SAME PARENT, DO NOTHING
            if clusters[root[child_1]] == clusters[root[child_2]]:
                # print "CLUSTER SIZE IS {} BUT THERE IS NOTHING TO DO\n".format(len(clusters))
                continue

            # THE PARENT WITH THE MOST CHILD GET THE CHILD OF THE OTHER PARENT
            if len(clusters[root[child_1]]) >= len(clusters[root[child_2]]):
                parent = root[child_1]
                pop_parent = root[child_2]
                root[child_2] = parent

            else:
                parent = root[child_2]
                pop_parent = root[child_1]
                root[child_1] = parent

            # ALL CHILD OF PARENT (SMALL) ARE REASSIGNED A NEW PARENT
            for child in clusters[pop_parent]:
                root[child] = parent
                clusters[parent] += [child]

            # POP THE PARENT WITH THE LESSER CHILD
            clusters.pop(pop_parent)

        elif has_parent_1 is True:

            # THE CHILD WITH NO PARENT IS ASSIGNED TO THE PARENT OF THE CHILD WITH PARENT
            parent = root[child_1]
            root[child_2] = parent
            clusters[parent] += [child_2]

        elif has_parent_2 is True:

            # THE CHILD WITH NO PARENT IS ASSIGNED TO THE PARENT OF THE CHILD WITH PARENT
            parent = root[child_2]
            root[child_1] = parent
            clusters[parent] += [child_1]

        # print "{} Clusters but the current is: {}\n".format(len(clusters), clusters[parent])
    print "3. NUMBER OF CLUSTER FOND: {}".format(len(clusters))
    return clusters


def cluster_triples2(graph, limit=0):

    count = 0
    clusters = dict()
    root = dict()

    # DOWNLOAD THE GRAPH
    print "\n0. DOWNLOADING THE GRAPH"
    response = Exp.export_alignment(graph)
    links = response['result']
    # print links

    # LOAD THE GRAPH
    print "1. LOADING THE GRAPH"
    g = rdflib.Graph()
    g.parse(data=links, format="turtle")

    print "2. ITERATING THROUGH THE GRAPH OF SIZE {}".format(len(g))
    for subject, predicate, obj in g:

        count += 1
        child_1 = subject
        child_2 = obj
        # parent = ""

        # DATE CREATION
        date = "{}".format(datetime.datetime.today().strftime(_format))

        # CHECK WHETHER A CHILD HAS A PARENT
        has_parent_1 = True if child_1 in root else False
        has_parent_2 = True if child_2 in root else False

        # print "{}|{} Has Parents {}|{}".format(child_1, child_2, has_parent_1, has_parent_2)

        if has_parent_1 is False and has_parent_2 is False:

            if limit != 0 and len(clusters) > limit:
                continue
                # Do not add new clusters

            # GENERATE THE PARENT
            hash_value = hash(date + str(count) + graph)
            parent = "{}".format(str(hash_value).replace("-", "N")) if str(hash_value).startswith("-") \
                else "P{}".format(hash_value)

            # ASSIGN A PARENT TO BOTH CHILD
            root[child_1] = parent
            root[child_2] = parent

            # CREATE A CLUSTER
            if parent not in clusters:
                clusters[parent] = [child_1, child_2]

        elif has_parent_1 is True and has_parent_2 is True:

            # IF BOTH CHILD HAVE THE SAME PARENT, DO NOTHING
            if clusters[root[child_1]] == clusters[root[child_2]]:
                # print "CLUSTER SIZE IS {} BUT THERE IS NOTHING TO DO\n".format(len(clusters))
                continue

            # THE PARENT WITH THE MOST CHILD GET THE CHILD OF THE OTHER PARENT
            if len(clusters[root[child_1]]) >= len(clusters[root[child_2]]):
                parent = root[child_1]
                pop_parent = root[child_2]
                root[child_2] = parent

            else:
                parent = root[child_2]
                pop_parent = root[child_1]
                root[child_1] = parent

            # ALL CHILD OF PARENT (SMALL) ARE REASSIGNED A NEW PARENT
            for child in clusters[pop_parent]:
                root[child] = parent
                clusters[parent] += [child]

            # POP THE PARENT WITH THE LESSER CHILD
            clusters.pop(pop_parent)

        elif has_parent_1 is True:

            # THE CHILD WITH NO PARENT IS ASSIGNED TO THE PARENT OF THE CHILD WITH PARENT
            parent = root[child_1]
            root[child_2] = parent
            clusters[parent] += [child_2]

        elif has_parent_2 is True:

            # THE CHILD WITH NO PARENT IS ASSIGNED TO THE PARENT OF THE CHILD WITH PARENT
            parent = root[child_2]
            root[child_1] = parent
            clusters[parent] += [child_1]

        # print "{} Clusters but the current is: {}\n".format(len(clusters), clusters[parent])
    print "3. NUMBER OF CLUSTER FOND: {}".format(len(clusters))

    result = []
    for parent, in_cluster in clusters.items():
        query = Qry.linkset_aligns_prop(graph)
        response = sparql2matrix(query)
        # print response
        # get one value per cluster in order to exemplify it
        sample = ''
        if response['result'] and len(response['result']) >= 2:  # header and one line
            # print response['result']
            properties = response['result'][1][:2]
            sample_response = cluster_values2(in_cluster, properties, limit_resources=1)
            if sample_response['result'] and len(sample_response['result']) >= 2:  # header and one line
                # print sample_response['result']
                sample = sample_response['result'][1][0]
        result += [{'parent': parent, 'cluster': in_cluster, 'sample': sample}]

    return result


def cluster_dataset(dataset_uri, datatype_uri, graph_list=None):

    append = "#" if graph_list is None else ""
    values = ""

    # LIST OF GRAPHS
    if graph_list is not None:
        for alignment in graph_list:
            values += " <{}>".format(alignment)

    # QUERY FOR LINKSETS INVOLVE AND THEIR RESPECTIVE DATA SOURCE
    query = """
    PREFIX void:    <{}>
    PREFIX bdb:     <{}>
    PREFIX dataset: <{}>
    PREFIX foaf:    <{}>
    PREFIX ll:      <{}>
    PREFIX skos:    <{}>

    SELECT DISTINCT  ?linkset ?src_dataset ?trg_dataset
    {{
        bind(<{}> as ?input_dataset)
        bind(<{}> as ?input_datatype)
        {}VALUES ?linkset {{ {} }}

        graph ?input_dataset
        {{
            ?RESOURCE a ?input_datatype .
        }}

        ?linkset
            void:subjectsTarget							?src_dataset  ;
            void:objectsTarget 							?trg_dataset  ;
            void:subjectsTarget|void:objectsTarget		?input_dataset  ;
            bdb:subjectsDatatype|bdb:objectsDatatype	?input_datatype .
    }}""".format(Ns.void, Ns.bdb, Ns.dataset, Ns.foaf, Ns.alivocab, Ns.skos, dataset_uri, datatype_uri, append, values)
    response = sparql2matrix(query)

    count = 0
    clusters = dict()
    root = dict()

    if response[St.message] == "OK":

        # response = sparql_xml_to_matrix(query)
        matrix = response[St.result]

        for row in range(1, len(matrix)):

            graph = matrix[row][0]
            # src_dataset = matrix[row][1]
            # trg_dataset = matrix[row][2]

            # DOWNLOAD THE GRAPH
            print "\n0. DOWNLOADING THE GRAPH"
            response = Exp.export_alignment(graph)
            links = response['result']
            # print links

            # LOAD THE GRAPH
            print "1. LOADING THE GRAPH"
            g = rdflib.Graph()
            g.parse(data=links, format="turtle")

            print "2. ITERATING THROUGH THE GRAPH OF SIZE {}".format(len(g))
            for subject, predicate, obj in g:

                count += 1
                child_1 = subject
                child_2 = obj
                # parent = ""

                # DATE CREATION
                date = "{}".format(datetime.datetime.today().strftime(_format))

                # CHECK WHETHER A CHILD HAS A PARENT
                has_parent_1 = True if child_1 in root else False
                has_parent_2 = True if child_2 in root else False

                # print "{}|{} Has Parents {}|{}".format(child_1, child_2, has_parent_1, has_parent_2)

                if has_parent_1 is False and has_parent_2 is False:

                    # GENERATE THE PARENT
                    hash_value = hash(date + str(count) + dataset_uri)
                    parent = "{}".format(str(hash_value).replace("-", "N")) if str(hash_value).startswith("-") \
                        else "P{}".format(hash_value)

                    # ASSIGN A PARENT TO BOTH CHILD
                    root[child_1] = parent
                    root[child_2] = parent

                    # CREATE A CLUSTER
                    if parent not in clusters:
                        clusters[parent] = [child_1, child_2]

                elif has_parent_1 is True and has_parent_2 is True:

                    # IF BOTH CHILD HAVE THE SAME PARENT, DO NOTHING
                    if clusters[root[child_1]] == clusters[root[child_2]]:
                        # print "CLUSTER SIZE IS {} BUT THERE IS NOTHING TO DO\n".format(len(clusters))
                        continue

                    # THE PARENT WITH THE MOST CHILD GET THE CHILD OF THE OTHER PARENT
                    if len(clusters[root[child_1]]) >= len(clusters[root[child_2]]):
                        parent = root[child_1]
                        pop_parent = root[child_2]
                        root[child_2] = parent

                    else:
                        parent = root[child_2]
                        pop_parent = root[child_1]
                        root[child_1] = parent

                    # ALL CHILD OF PARENT (SMALL) ARE REASSIGNED A NEW PARENT
                    for child in clusters[pop_parent]:
                        root[child] = parent
                        clusters[parent] += [child]

                    # POP THE PARENT WITH THE LESSER CHILD
                    clusters.pop(pop_parent)

                elif has_parent_1 is True:

                    # THE CHILD WITH NO PARENT IS ASSIGNED TO THE PARENT OF THE CHILD WITH PARENT
                    parent = root[child_1]
                    root[child_2] = parent
                    clusters[parent] += [child_2]

                elif has_parent_2 is True:

                    # THE CHILD WITH NO PARENT IS ASSIGNED TO THE PARENT OF THE CHILD WITH PARENT
                    parent = root[child_2]
                    root[child_1] = parent
                    clusters[parent] += [child_1]

            # print "{} Clusters but the current is: {}\n".format(len(clusters), clusters[parent])
            print "3. NUMBER OF CLUSTER FOND: {}".format(len(clusters))
    return clusters


def cluster_values(g_cluster, properties, display=False):

    """
    :param g_cluster: A LIST OF CLUSTERED RESOURCES
    :param properties: A LIST OF PROPERTIES OF INTEREST
    :param display: if True, display the matrix as a table
    :return: A DICTIONARY WHERE THE RESULT OF THE QUERY IS OBTAINED USING THE KEY: result
    """
    prop = ""
    union = ""
    for uri in properties:
        prop += " <{}>".format(uri.strip())

    for i in range(0, len(g_cluster)):
        if i > 0:
            append = "UNION"
        else:
            append = ""
        union += """ {}
        {{
            bind(<{}> as ?resource)
            graph ?input_dataset {{ ?resource ?property ?obj . }}
        }}""".format(append, g_cluster[i])

    query = """
    PREFIX void: <http://rdfs.org/ns/void#>
    PREFIX bdb: <http://vocabularies.bridgedb.org/ops#>
    PREFIX dataset: <http://risis.eu/dataset/>
    PREFIX foaf: <http://xmlns.com/foaf/0.1/>
    PREFIX ll: <http://risis.eu/alignment/predicate/>
    PREFIX skos:        <http://www.w3.org/2004/02/skos/core#>

    SELECT DISTINCT  *
    {{
        values ?property {{{} }}
        {}
    }}""".format(prop, union)

    # print query
    response = sparql2matrix(query)
    if display is True:
        Qry.display_matrix(response, spacing=100, is_activated=True)
    return response


def cluster_values2(g_cluster, properties, distinct_values=True, display=False, limit_resources=100):

    """
    :param g_cluster: A LIST OF CLUSTERED RESOURCES
    :param properties: A LIST OF PROPERTIES OF INTEREST
    :param distinct_values: return distinct resources
    :param display: display the matrix as a table
    :param limit_resources: limit the number of resources to include in the cluster
    :return: A DICTIONARY WHERE THE RESULT OF THE QUERY IS OBTAINED USING THE KEY: result
    """
    prop = ""
    union = ""
    # print "\nCLUSTER SIZE: {}".format(len(g_cluster))

    for uri in properties:
        prop += " <{}>".format(uri.strip())

    for i in range(0, len(g_cluster)):
        if limit_resources != 0 and i > limit_resources:
            break
        if i > 0:
            append = "UNION"
        else:
            append = ""
        union += """ {}
        {{
            bind(<{}> as ?resource)
            graph ?dataset {{ ?resource ?property ?value . }}
        }}""".format(append, g_cluster[i])

    if distinct_values is True:
        select = '?dataset ?value (count(distinct ?resource) as ?count)'
        group_by = 'group by ?value ?dataset order by desc(?count)'
    else:
        select = '*'
        group_by = ''

    query = """
    PREFIX void: <http://rdfs.org/ns/void#>
    PREFIX bdb: <http://vocabularies.bridgedb.org/ops#>
    PREFIX dataset: <http://risis.eu/dataset/>
    PREFIX foaf: <http://xmlns.com/foaf/0.1/>
    PREFIX ll: <http://risis.eu/alignment/predicate/>
    PREFIX skos:        <http://www.w3.org/2004/02/skos/core#>

    SELECT DISTINCT {}
    {{
        values ?property {{{} }}
        {}
    }} {} """.format(select, prop, union, group_by)

    # print query
    response = sparql2matrix(query)
    if display is True:
        Qry.display_matrix(response, spacing=50, is_activated=True)
    return response


def linkset_from_cluster():

    query = """
    # DATASETS
    {{
        # CLUSTER
        GRAPH <{}>
        {{
            
        }}
    }}
    """


" >>> CLUSTERING RESOURCES BASED ON COUNTRY CODE"
# groups0 = cluster_triples("http://risis.eu/dataset/grid_country")
# count = 0
# print ""
# for cluster1 in groups0.items():
#
#     count += 1
#     country = None
#     for instance in cluster1[1]:
#         if str(instance).__contains__("http://") is False:
#             country = instance
#     if country is not None:
#         print "{} in {} {}".format(cluster1[0], country, len(cluster1[1]))
# exit(0)

" >>> COMPARE LINKSET FOR MERGED CLUSTERS"
# groups1 = cluster_triples(
#     "http://risis.eu/linkset/orgref_20170703_grid_20170712_approxStrSim_Organisation_Name_N221339442")
# groups2 = cluster_triples(
#     "http://risis.eu/linkset/orgref_20170703_grid_20170712_approxStrSim_Organisation_Name_N212339613")
# counter = 0
# print ""
# for cluster1 in groups1.items():
#     counter += 1
#     stop = False
#     outer = "CLUSTER {} of size {}".format(cluster1[0], len(cluster1[1]))
#
#     # for instance in cluster1[1]:
#     #     print "\t{}".format(instance)
#
#     for instance in cluster1[1]:
#         for other_cluster in groups2.items():
#             if instance in other_cluster[1]:
#                 stop = True
#                 inner = "LINKED TO CLUSTER {} OF SIZE {}".format(other_cluster[0], len(other_cluster[1]))
#                 if len(cluster1[1]) != len(other_cluster[1]):
#                     print "{} {}".format(outer, inner)
#                 # for o_cluster in other_cluster[1]:
#                 #     print "\t\t\t{}".format(o_cluster)
#             if stop:
#                 break
#     if counter == 5000:
#         break


    # if len(item['cluster']) > 1:
    #     print "\n{:10}\t{:3}\t{}".format(item['parent'], len(item['cluster']), item['sample'])

# test = [('x','y'), ('x','B'), ('w','B'), ('x','w'), ('e','d'), ('e','y'),
# ('s', 'w'),('a','b'),('h','j'),('k','h'),('k','s'),('s','a')]
# clus= cluster(test)
# for key, value in clus.items():
#     print "{} {}".format(key, value)

# test = cluster_triples("http://risis.eu/linkset/subset_openAire_20170816_openAire_20170816_"
#                        "embededAlignment_Organization_sameAs_P541043043")

# groups = cluster_dataset("http://risis.eu/dataset/grid_20170712", "http://xmlns.com/foaf/0.1/Organization")
# properties = ["http://www.w3.org/2004/02/skos/core#prefLabel", "{}label".format(Ns.rdfs)]
# for key, value in groups.items():
#     if len(value) > 15:
#         print "\n{:10}\t{:3}".format(key, len(value))
#         response = cluster_values(value, properties)
#         exit(0)

# groups = cluster_dataset("http://goldenagents.org/datasets/Ecartico", "http://ecartico.org/ontology/Person")
# # print groups
# properties = ["http://ecartico.org/ontology/full_name", "http://goldenagents.org/uva/SAA/ontology/full_name"]
# counter = 0
# for key, value in groups.items():
#     if len(value) > 15:
#         print "\n{:10}\t{:3}".format(key, len(value))
#         response = cluster_values(value, properties, display=True)
#         if counter > 5:
#             exit(0)
#         counter +=1

# groups = cluster_triples2("http://risis.eu/linkset/refined_003MarriageRegistries_Ecartico_exactStrSim_Person_full_"
#                           "name_N3531703432838097870_approxNbrSim_isInRecord_registration_date_P0")
# counter = 0
# for item in groups:
#     if len(item['cluster']) > 1:
#         print "\n{:10}\t{:3}\t{}".format(item['parent'], len(item['cluster']), item['sample'])
