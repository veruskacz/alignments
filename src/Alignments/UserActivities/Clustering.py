import datetime
import rdflib
import Alignments.Settings as St
import Alignments.NameSpace as Ns
import Alignments.UserActivities.ExportAlignment as Exp
from Alignments.Query import sparql_xml_to_matrix as sparql2matrix
import Alignments.Query as Qry
import Alignments.Utility as Ut
# import Alignments.UserActivities.Plots as Plt


_format = "%a %b %d %H:%M:%S:%f %Y"


def matrix(row, column, init=0):
    # row, column = 8, 5;
    return [[init for x in range(row)] for y in range(column)]


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
            for offspring in clusters[pop_parent]:
                root[offspring] = parent
                clusters[parent] += [offspring]

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


# LINKSET CLUSTERING
def cluster_triples(graph):

    count = 0
    clusters = dict()
    root = dict()

    # DOWNLOAD THE GRAPH
    print "0. DOWNLOADING THE GRAPH"
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
        child_1 = subject.n3()
        child_2 = obj.n3()
        # parent = ""

        # DATE CREATION
        date = "{}".format(datetime.datetime.today().strftime(_format))

        # CHECK WHETHER A CHILD HAS A PARENT
        has_parent_1 = True if child_1 in root else False
        has_parent_2 = True if child_2 in root else False
        # print "{}|{} Has Parents {}|{}".format(child_1, child_2, has_parent_1, has_parent_2)

        # BOTH CHILD ARE ORPHANS
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

                # MATRIX
                mx = matrix(10, 10)
                # ROW
                mx[0][1] = child_1
                mx[0][2] = child_2
                # COLUMNS
                mx[1][0] = child_1
                mx[2][0] = child_2
                # RELATION
                mx[1][2] = 1
                mx[2][1] = 1

                clusters["{}_M".format(parent)] = mx

        # BOTH CHILD HAVE A PARENT OF THEIR OWN
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
            for offspring in clusters[pop_parent]:
                root[offspring] = parent
                clusters[parent] += [offspring]

            # POP THE PARENT WITH THE LESSER CHILD
            clusters.pop(pop_parent)
            # print clusters["{}_M".format(pop_parent)]
            # print clusters["{}_M".format(parent)]

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
            for offspring in clusters[pop_parent]:
                root[offspring] = parent
                clusters[parent] += [offspring]

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
        mx = response[St.result]

        for row in range(1, len(mx)):

            graph = mx[row][0]
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
                    for offspring in clusters[pop_parent]:
                        root[offspring] = parent
                        clusters[parent] += [offspring]

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

    for x in range(0, len(g_cluster)):
        if x > 0:
            append = "UNION"
        else:
            append = ""
        union += """ {}
        {{
            bind(<{}> as ?resource)
            graph ?input_dataset {{ ?resource ?property ?obj . }}
        }}""".format(append, g_cluster[x])

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

    for x in range(0, len(g_cluster)):
        if limit_resources != 0 and x > limit_resources:
            break
        if x > 0:
            append = "UNION"
        else:
            append = ""
        union += """ {}
        {{
            bind({} as ?resource)
            graph ?dataset {{ ?resource ?property ?value . }}
        }}""".format(append, g_cluster[x])

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
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>

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


def cluster_values_plus(rq_uri, g_cluster, properties, distinct_values=True, display=False, limit_resources=100):

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

    for x in range(0, len(g_cluster)):
        if limit_resources != 0 and x > limit_resources:
            break
        if x > 0:
            append = "UNION"
        else:
            append = ""
        union += """ {}
        {{
            bind({} as ?resource)
            graph ?dataset {{ ?resource ?property ?value . }}
        }}""".format(append, g_cluster[x])

    if distinct_values is True:
        select = '?dataset ?value (count(distinct ?resource) as ?count)'
        group_by = 'group by ?value ?dataset order by desc(?count)'
    else:
        select = '?dataset ?resource (GROUP_CONCAT(?property; SEPARATOR=" | ") ' \
                 'as ?properties) (concat("[", ?temp ,"]") as ?values) (GROUP_CONCAT(?value; SEPARATOR="] [") as ?temp)'
        group_by = 'group by ?dataset ?resource order by ?dataset ?resource '

    query = """
    PREFIX void: <http://rdfs.org/ns/void#>
    PREFIX bdb: <http://vocabularies.bridgedb.org/ops#>
    PREFIX dataset: <http://risis.eu/dataset/>
    PREFIX foaf: <http://xmlns.com/foaf/0.1/>
    PREFIX ll: <http://risis.eu/alignment/predicate/>
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>

    SELECT DISTINCT {}
    {{
        values ?property {{{} }}
        {}
        {{
            graph <{}>
            {{
                ?idea   ll:selected ?dataset .
                ?dataset a <http://risis.eu/class/Dataset> ;
            }}
        }}
    }} {} """.format(select, prop, union, rq_uri, group_by)

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
    print query


# WORKING ONE
def cluster_links(graph, limit=1000):

    count = 0
    matrix_size = 240
    clusters = dict()
    root = dict()

    # DOWNLOAD THE GRAPH
    print "\n0. DOWNLOADING THE GRAPH"
    response = Exp.export_alignment(graph, limit=limit)
    links = response['result']
    # print links

    # LOAD THE GRAPH3
    print "1. LOADING THE GRAPH"
    g = rdflib.Graph()
    g.parse(data=links, format="turtle")
    # g = [
    #     ("<http://grid.2>", "<http://risis.eu/alignment/predicate/sameAs>", "<http://orgref.2>"),
    #     ("<http://leiden.2>", "<http://risis.eu/alignment/predicate/sameAs>", "<http://grid.2>"),
    #     ("<http://orgref.2>", "<http://risis.eu/alignment/predicate/sameAs>", "<http://orgreg.2>"),
    #     ("<http://orgreg.2> ", "<http://risis.eu/alignment/predicate/sameAs>", "<http://h2020.2> "),
    #     ("<http://h2020.2>", "<http://risis.eu/alignment/predicate/sameAs>", "<http://eter.2>"),
    #     ("<http://eter.2>", "<http://risis.eu/alignment/predicate/sameAs>", "<http://leiden.2>"),
    # ]
    #
    g = [
        ("<http://grid.2>", "<http://risis.eu/alignment/predicate/sameAs>", "<http://orgref.2>"),
        ("<http://eter.2>", "<http://risis.eu/alignment/predicate/sameAs>", "<http://leiden.2>"),
        ("<http://orgreg.2> ", "<http://risis.eu/alignment/predicate/sameAs>", "<http://h2020.2> "),
        ("<http://leiden.2>", "<http://risis.eu/alignment/predicate/sameAs>", "<http://grid.2>"),
        ("<http://orgref.2>", "<http://risis.eu/alignment/predicate/sameAs>", "<http://orgreg.2>"),
        ("<http://h2020.2>", "<http://risis.eu/alignment/predicate/sameAs>", "<http://eter.2>")]

    # g = [
    #     ("<http://risis.eu/leidenRanking_2015/resource/884>", "<http://risis.eu/alignment/predicate/sameAs>",
    #      "<http://www.grid.ac/institutes/grid.10493.3f>"),
    #     ("<http://risis.eu/leidenRanking_2015/resource/884>", "<http://risis.eu/alignment/predicate/sameAs>",
    #      "<http://risis.eu/eter_2014/resource/DE0056>"),
    #     ("<http://www.grid.ac/institutes/grid.10493.3f> ", "<http://risis.eu/alignment/predicate/sameAs>",
    #      "<http://risis.eu/eter_2014/resource/DE0056> ") ]

    def merge_matrices(parent, pop_parent):

        # COPYING LESSER MATRIX TO BIGGER MATRIX

        index = parent[St.row]
        pop_row = pop_parent[St.row]
        cur_mx = parent[St.matrix]
        pop_mx = pop_parent[St.matrix]

        # print "\tPOSITION: {} | POSITION POP: {}".format(index, pop_row)
        # print "\tADD VALUE: {}".format(position_add)

        # COPY MATRIX
        # print "\tPOP HEADER: {}".format(pop_mx[0][:])
        for row in range(1, pop_row):

            # ADD HEADER IF NOT ALREADY IN
            # print "\tCURRENT HEADER ADDED: {}".format(cur_mx[0:])
            if pop_mx[row][0] not in cur_mx[0:]:
                pop_item_row = pop_mx[row][0]
                cur_mx[index][0] = pop_item_row
                cur_mx[0][index] = pop_item_row
                index += 1
                parent[St.row] = index
                # print "\tHEADER ADDED: {}".format(pop_item_row)

                # FOR THAT HEADER, COPY THE SUB-MATRIX
                for col in range(1, pop_row):

                    # THE HEADER ARE ALREADY IN THERE
                    if pop_mx[row][col] != 0:
                        # find header in current matrix
                        for col_item in range(1, len(cur_mx[1:-1])):
                            if cur_mx[0][col_item] == pop_mx[0][col]:
                                # print "\tIN2 ({}, {})".format(index - 1, col_item)
                                cur_mx[index - 1][col_item] = 1

    def cluster_helper(counter):

        counter += 1
        # parent = None
        # child_1 = subject.n3().strip()
        # child_2 = obj.n3().strip()
        child_1 = subject.strip()
        child_2 = obj.strip()

        # DATE CREATION
        date = "{}".format(datetime.datetime.today().strftime(_format))

        # CHECK WHETHER A CHILD HAS A PARENT
        has_parent_1 = True if child_1 in root else False
        has_parent_2 = True if child_2 in root else False
        # print "\n{}|{} Has Parents {}|{}".format(child_1, child_2, has_parent_1, has_parent_2)

        # 1. START BOTH CHILD ARE ORPHANS
        if has_parent_1 is False and has_parent_2 is False:

            # print "\nSTART {}:{} | {}:{}".format(child_1, has_parent_1, child_2, has_parent_2)

            # GENERATE THE PARENT
            hash_value = hash(date + str(count) + graph)
            parent = "{}".format(str(hash_value).replace("-", "N")) if str(
                hash_value).startswith("-") \
                else "P{}".format(hash_value)

            # ASSIGN A PARENT TO BOTH CHILD
            root[child_1] = parent
            root[child_2] = parent

            # CREATE A CLUSTER
            if parent not in clusters:
                # MATRIX
                mx = matrix(matrix_size, matrix_size)
                # ROW
                mx[0][1] = child_1
                mx[0][2] = child_2

                # COLUMNS
                mx[1][0] = child_1
                mx[2][0] = child_2

                # RELATION
                # mx[1][2] = 1
                mx[2][1] = 1
                # mxd[(2, 1)] = 1

                clusters[parent] = {St.children: [child_1, child_2], St.matrix: mx, St.row: 3}
                clusters[parent][St.annotate] = "\n\tSTART {} | {}".format(child_1, child_2)

            # print "\tPOSITION: {}".format(3)
            # print "\tIT WILL BE PRINTED AT: ({}, {})".format(2, 1)

        # 2. BOTH CHILD HAVE A PARENT OF THEIR OWN
        elif has_parent_1 is True and has_parent_2 is True:

            # 2.1 BOTH CHILD HAVE THE SAME PARENT, DO NOTHING
            if root[child_1] == root[child_2]:
                # print "CLUSTER SIZE IS {} BUT THERE IS NOTHING TO DO\n".format(len(clusters))
                # print "\nSAME PARENTS {}:{} | {}:{}".format(child_1, has_parent_1, child_2, has_parent_2)
                cur_mx = clusters[root[child_1]][St.matrix]

                row_1 = 0
                row_2 = 0

                # FIND ROW
                # row_1 = clusters[root[child_1]][St.row]
                for row in range(1, clusters[root[child_1]][St.row]):
                    if cur_mx[row][0] == child_1:
                        row_1 = row

                for col in range(1, clusters[root[child_1]][St.row]):
                    if cur_mx[0][col] == child_2:
                        row_2 = col

                # row_2 = clusters[root[child_2]][St.row]

                # print "\tPOSITIONS: {} | {}".format(row_2, row_1)
                cur_mx[row_2][row_1] = 1
                clusters[root[child_1]][St.annotate] += "\n\tSAME PARENTS {} | {}".format(child_1, child_2)

                # COPY THE SUB-MATRIX

                # for col in range(1, row_1):
                #     if cur_mx[0][col] == child_2:
                #         print "\tFOUND: {} AT POSITION: {}".format(cur_mx[0][col], col)
                #         print "\tIT WILL BE PRINTED AT: ({}, {})".format(row_1 - 1, col)
                #         cur_mx[row_1 - 1][col] = 1

                # continue
                return counter

            # THE PARENT WITH THE MOST CHILD GET THE CHILD OF THE OTHER PARENT
            # fFETCHING THE RESOURCES IN THE CLUSTER (CHILDREN)
            # print "\n{}:{} | {}:{}".format(child_1, has_parent_1, child_2, has_parent_2)

            children_1 = (clusters[root[child_1]])[St.children]
            children_2 = (clusters[root[child_2]])[St.children]

            # 2.2 CHOOSE A PARENT
            if len(children_1) >= len(children_2):
                # print "\tPARENT 1"
                parent = root[child_1]
                pop_parent = root[child_2]
                # root[child_2] = parent

            else:
                # print "\tPARENT 2"
                parent = root[child_2]
                pop_parent = root[child_1]
                # root[child_1] = parent

            # ALL CHILD OF PARENT (SMALL) ARE REASSIGNED A NEW PARENT
            for offspring in clusters[pop_parent][St.children]:
                root[offspring] = parent
                clusters[parent][St.children] += [offspring]

            # MERGE CURRENT WITH LESSER (CHILDREN) MATRICES, ANNOTATE AND POOP LESSER (CHILDREN) MATRICES
            # print '1\n', clusters[parent]
            merge_matrices(clusters[parent], clusters[pop_parent])
            # print '2\n', clusters[parent]
            clusters[parent][St.annotate] += "\n\tCHOOSE A PARENT {} | {}".format(child_1, child_2)
            cluster_helper(count)
            # cluster_helper(count)

            # COPYING LESSER MATRIX TO BIGGER MATRIX
            # index = clusters[parent][St.row]
            # pop_row = clusters[pop_parent][St.row]
            # cur_mx = clusters[parent][St.matrix]
            # pop_mx = clusters[pop_parent][St.matrix]
            # # position_add = clusters[parent][St.row] - 1
            #
            # print "\tPOSITION: {} | POSITION POP: {}".format(index, pop_row)
            # # print "\tADD VALUE: {}".format(position_add)
            #
            # # # ADD HEADER
            # # for x in range(1, pop_index):
            # #     cur_mx[0][index - 1 + x] = pop_mx[0][x]
            # #     cur_mx[index - 1 + x][0] = pop_mx[0][x]
            # #     clusters[parent][St.row] += 1
            #
            # # COPY MATRIX
            # print "\tPOP HEADER: {}".format(pop_mx[0][:])
            # for row in range(1, pop_row):
            #
            #     # ADD HEADER IF NOT ALREADY IN
            #     # print "\tCURREENT HEADER ADDED: {}".format(cur_mx[0:])
            #     if pop_mx[row][0] not in cur_mx[0:]:
            #         pop_item_row = pop_mx[row][0]
            #         cur_mx[index][0] = pop_item_row
            #         cur_mx[0][index] = pop_item_row
            #         index += 1
            #         clusters[parent][St.row] = index
            #         print "\tHEADER ADDED: {}".format(pop_item_row)
            #
            #
            #         # FOR THAT HEADER, COPY THE SUB-MATRIX
            #         for col in range(1, pop_row):
            #
            #             # THE HEADER IS NOT IN
            #             if pop_mx[row][col] != 0 and pop_mx[row][0] not in cur_mx[1:-1]:
            #                 print "\tIN ({}, {})".format(index-1, col )
            #                 # index += 1
            #                 # clusters[parent][St.row] = index
            #
            #             # THE HEADER ARE ALREADY IN THERE
            #             if pop_mx[row][col] != 0:
            #                 # find header in current matrix
            #                 for col_item in range(1, len(cur_mx[1:-1])):
            #                     if cur_mx[0][col_item] == pop_mx[0][col]:
            #                         print "\tIN2 ({}, {})".format(index-1, col_item)
            # cur_mx[row + position_add][col + position_add] = pop_mx[row][col]

            # cur_mx[0][position_add+ row] = pop_mx[row][0]

            # cur_mx[y + position_add][x + position_add] = pop_mx[y][x]

            # POP THE PARENT WITH THE LESSER CHILD

            clusters[parent][St.annotate] += clusters[pop_parent][St.annotate]
            clusters.pop(pop_parent)

        elif has_parent_1 is True:

            # THE CHILD WITH NO PARENT IS ASSIGNED TO THE PARENT OF THE CHILD WITH PARENT
            # print "\n{}:{} | {}:{}".format(child_1, has_parent_1, child_2, has_parent_2)

            parent = root[child_1]
            root[child_2] = parent
            clusters[parent][St.children] += [child_2]
            # print "\t>>> {} is in root {}".format(child_2, child_2 in root)

            cur_mx = clusters[parent][St.matrix]
            row_1 = clusters[parent][St.row]

            # ADD HEADER
            cur_mx[row_1][0] = child_2
            cur_mx[0][row_1] = child_2

            # INCREMENT POSITION
            row_1 += 1
            # print "\tPOSITION: {}".format(row_1)
            clusters[parent][St.row] = row_1

            # COPY MATRIX
            for col in range(1, row_1):
                # print cur_mx[0][x], child_1
                if cur_mx[0][col] == child_1:
                    # print "\tFOUND: {} AT POSITION: {}".format(cur_mx[0][col], col)
                    # print "\tIT WILL BE PRINTED AT: ({}, {})".format(row_1 - 1, col)
                    # cur_mx[position_1 - 1][x] = 1
                    cur_mx[row_1 - 1][col] = 1
                    clusters[root[child_1]][St.annotate] += "\n\tONLY 1 {} HAS A PARENT COMPARED TO {}".format(
                        child_1, child_2)

        elif has_parent_2 is True:

            # THE CHILD WITH NO PARENT IS ASSIGNED TO THE PARENT OF THE CHILD WITH PARENT
            # print "\n{}:{} | {}:{}".format(child_1, has_parent_1, child_2, has_parent_2)

            parent = root[child_2]
            root[child_1] = parent
            clusters[parent][St.children] += [child_1]
            # print "\t>>> {} is in root {}".format(child_1, child_1 in root)

            cur_mx = clusters[parent][St.matrix]
            row_2 = clusters[parent][St.row]

            # ADD HEADER
            # print row_2
            cur_mx[row_2][0] = child_1
            cur_mx[0][row_2] = child_1

            # INCREMENT POSITION
            row_2 += 1
            # print "\tPOSITION: {}".format(row_2)
            clusters[parent][St.row] = row_2

            # COPY MATRIX
            for col in range(1, row_2):
                # print cur_mx[0][x], child_1
                if cur_mx[0][col] == child_2:
                    # print "\tFOUND: {} AT POSITION: {}".format(cur_mx[0][col], col)
                    # print "\tIT WILL BE PRINTED AT: ({}, {})".format(row_2 - 1, col)
                    # cur_mx[position_2 - 1][x] = 1
                    cur_mx[row_2 - 1][col] = 1
                    clusters[root[child_1]][St.annotate] += "\n\tONLY 2 {} HAS A PARENT COMPARED TO {}".format(
                        child_2, child_1)

        return counter

    print "2. ITERATING THROUGH THE GRAPH OF SIZE {}".format(len(g))

    standard = 10
    check = 1
    iteration = 1
    for subject, predicate, obj in g:
        print "\tRESOURCE {:>4}: {} {}".format(count, subject.n3() , obj)

        count = cluster_helper(count)
        if iteration == check:
            print "1- ", count
            check = check + standard
        iteration += 1

    print "3. NUMBER OF CLUSTER FOUND: {}".format(len(clusters))
    return clusters


# QUERY TO HELP DISAMBIGUATING A NETWORK OF RESOURCES
def disambiguate_network(linkset, resource_list, output=True):

    # GATHER SOME DATA ABOUT THE LINKSET
    metadata_query = """
    PREFIX ll:  <{1}>
    SELECT ?target ?aligns
    {{
        <{0}> ll:hasAlignmentTarget ?alignmentTarget .
        ?alignmentTarget
            ll:hasTarget 	?target ;
            ll:aligns		?aligns .
    }} order by ?alignmentTarget
    """.format(linkset, Ns.alivocab)
    # print metadata_query
    uri_size = 0

    response = Qry.sparql_xml_to_matrix(metadata_query)
    result = response[St.result]
    # print result

    if result:
        dataset = ""
        bind = ""
        property_or = ""
        dataset_count = 0
        resources = ""
        for resource in resource_list:
            use = "<{}>".format(resource) if Ut.is_nt_format(resource) is not True else resource
            resources += "\n\t\t{}".format(use)
            if len(resource) > uri_size:
                uri_size = len(resource)

        for i in range(1, len(result)):
            if dataset != result[i][0]:
                dataset_count += 1
                union = "UNION " if dataset_count > 1 else ""
                dataset = result[i][0]
                bind += """\n\tBIND(IRI("{}") as ?dataset_{})""".format(
                    dataset, str(dataset_count))

                prop_1 = "<{}>".format(result[i][1]) if Ut.is_nt_format(result[i][1]) is not True else result[i][1]
                property_or += "\n\t{}{{\n\t\tGRAPH ?dataset_{}\n\t\t{{\n\t\t\t?subject {}".format(
                    union, dataset_count, prop_1)
                for j in range(i + 1, len(result)):
                    if dataset == result[i][0]:
                        prop_2 = "<{}>".format(result[i][1]) if Ut.is_nt_format(result[i][1]) is not True \
                            else result[i][1]
                        property_or += "\n\t\t\t\t| {}".format(prop_2)
                        i = j
                property_or += "  ?object .\n\t\t}\n\t}"

        final_query = "SELECT DISTINCT ?subject ?object\n{{\n\tVALUES ?subject {{{}\n\t}}{}{}\n}}".format(
            resources, bind, property_or)
        # print final_query
        response = Qry.sparql_xml_to_matrix(final_query)

        if output is False:
            return response[St.result]

        return Qry.display_matrix(response, spacing=uri_size, output=output, line_feed='.', is_activated=True)

    print "\t>>> NO RESULT FOR THE QUERY BECAUSE NO METADATA COULD BE EXTRACTED FOR THE PROVIDED LINKSET..."
    print metadata_query
    return "NO RESULT FOR THE QUERY..."


# QUERY TO HELP DISAMBIGUATING A NETWORK OF RESOURCES
def disambiguate_network_2(lookup_resource_list, targets, output=True):

    # GATHER SOME DATA ABOUT THE LINKSET

    # print metadata_query
    uri_size = 0
    dataset = ""
    bind = ""
    property_or = ""
    dataset_count = 0
    resources = ""

    for resource in lookup_resource_list:
        use = "<{}>".format(resource) if Ut.is_nt_format(resource) is not True else resource
        resources += "\n\t\t{}".format(use)
        if len(resource) > uri_size:
            uri_size = len(resource)

    for i in range(len(targets)):
        if dataset != targets[i][St.graph]:
            dataset_count += 1
            union = "UNION " if dataset_count > 1 else ""
            dataset = targets[i][St.graph]
            bind += """\n\tBIND(IRI("{}") as ?dataset_{})""".format(
                dataset, str(dataset_count))
            data = targets[i][St.data]

            for dt_dic in data:
                properties = dt_dic[St.properties]
                for index in range(len(properties)):
                    if index == 0:
                        prop_1 = "<{}>".format(properties[index]) if Ut.is_nt_format(properties[index]) is not True \
                            else properties[index]
                        property_or += "\n\t{}{{\n\t\tGRAPH ?dataset_{}\n\t\t{{\n\t\t\t?subject {}".format(
                            union, dataset_count, prop_1)
                    else:

                        prop_2 = "<{}>".format(properties[index]) if Ut.is_nt_format(properties[index]) is not True \
                            else properties[index]
                        property_or += "\n\t\t\t\t| {}".format(prop_2)

            property_or += "  ?object .\n\t\t}\n\t}"

    final_query = "SELECT DISTINCT ?subject ?object\n{{\n\tVALUES ?subject {{{}\n\t}}{}{}\n}}".format(
        resources, bind, property_or)
    # print final_query
    response = Qry.sparql_xml_to_matrix(final_query)
    # print "RESPONSE", response
    if output is False:
        return response[St.result]

    return Qry.display_matrix(response, spacing=uri_size, output=output, line_feed='.', is_activated=True)

    # print "\t>>> NO RESULT FOR THE QUERY BECAUSE NO METADATA COULD BE EXTRACTED FOR THE PROVIDED LINKSET..."
    # print metadata_query
    # return "NO RESULT FOR THE QUERY..."


# TESTING THE CLUSTER ANALYSIS
# def cluster_test(linkset, network_size=3, greater_equal=True, limit=5000):
#
#     count_1 = 0
#     count_2 = 0
#
#     print ""
#
#     linkset = linkset.strip()
#
#     # RUN THE CLUSTER
#     clusters_0 = cluster_links(linkset, limit)
#
#     for i_cluster in clusters_0.items():
#
#         network = []
#         count_1 += 1
#         children = i_cluster[1][St.children]
#         # if "<http://www.grid.ac/institutes/grid.10493.3f>" not in children:
#         #     continue
#
#         check = len(children) >= network_size if greater_equal else len(children) == network_size
#
#         if check:
#             count_2 += 1
#
#             print "\nCLUSTER {:>3}: {}: with size: {}".format(count_1, i_cluster[0], len(children))
#             for child in children:
#                 print "\t{}".format(child)
#
#             print "\nDISAMBIGUATION HELPER"
#             disambiguate_network(linkset, children)
#
#             position = i_cluster[1][St.row]
#             print "\nANNOTATED CLUSTER PROCESS"
#             print i_cluster[1][St.annotate]
#
#             # THE CLUSTER
#             # print "POSITION: {}".format(position)
#             print "\nMATRIX DISPLAY\n"
#             for i in range(0, position):
#                 resource = (i_cluster[1][St.matrix])[i]
#                 print "\t{}".format(resource[:position])
#                 # print "\t{}".format(resource)
#
#             # THE MATRIX
#             for i in range(1, position):
#                 for j in range(1, position):
#                     if (i_cluster[1][St.matrix])[i][j] != 0:
#                         r = (i_cluster[1][St.matrix])[i][0]
#                         c = (i_cluster[1][St.matrix])[0][j]
#                         # r_name = r[-25:]
#                         # c_name = c[-25:]
#                         r_name = "{}:{}".format(i, Ut.get_uri_local_name(r))
#                         c_name = "{}:{}".format(j, Ut.get_uri_local_name(c))
#                         # r_smart = {"key": i, "name": r_name}
#                         # c_smart = {"key": j, "name": c_name}
#                         network += [(r_name, c_name)]
#                         # network += [(r_smart, c_smart)]
#
#             print ""
#             # print "\tNETWORK", network
#             Plt.draw_graph(network)
#
#     print "FOUND: {}".format(count_2)


# WORKING ONE
def links_clustering_matrix(graph, limit=1000):

    count = 0
    clusters = dict()

    # ROOT = KEY:CHILD VALUE:PARENT
    root = dict()

    # DOWNLOAD THE GRAPH
    print "\n0. DOWNLOADING THE GRAPH FROM THE TRIPLE STORE"
    response = Exp.export_alignment(graph, limit=limit)
    links = response['result']

    # LOAD THE GRAPH
    print "1. LOADING THE GRAPH USING RDFLIB"
    g = rdflib.Graph()
    g.parse(data=links, format="turtle")

    # g = [
    #     ("<http://grid.2>", "<http://risis.eu/alignment/predicate/SAMEAS>", "<http://orgref.2>"),
    #     ("<http://leiden.2>", "<http://risis.eu/alignment/predicate/SAMEAS>", "<http://grid.2>"),
    #     ("<http://orgref.2>", "<http://risis.eu/alignment/predicate/SAMEAS>", "<http://orgreg.2>"),
    #     ("<http://orgreg.2> ", "<http://risis.eu/alignment/predicate/SAMEAS>", "<http://h2020.2> "),
    #     ("<http://h2020.2>", "<http://risis.eu/alignment/predicate/SAMEAS>", "<http://eter.2>"),
    #     ("<http://eter.2>", "<http://risis.eu/alignment/predicate/SAMEAS>", "<http://leiden.2>"),
    # ]

    # g = [
    #     ( "<http://grid.2>", "<http://risis.eu/alignment/predicate/SAMEAS>", "<http://orgref.2>"),
    #     ( "<http://eter.2>", "<http://risis.eu/alignment/predicate/SAMEAS>", "<http://leiden.2>"),
    #     ("<http://orgreg.2> ", "<http://risis.eu/alignment/predicate/SAMEAS>", "<http://h2020.2> "),
    #     ( "<http://leiden.2>", "<http://risis.eu/alignment/predicate/SAMEAS>", "<http://grid.2>"),
    #     ("<http://orgref.2>", "<http://risis.eu/alignment/predicate/SAMEAS>", "<http://orgreg.2>"),
    #     ("<http://h2020.2>", "<http://risis.eu/alignment/predicate/SAMEAS>", "<http://eter.2>"),
    # ]

    # g = [
    #     ("<http://risis.eu/leidenRanking_2015/resource/884>", "<http://risis.eu/alignment/predicate/SAMEAS>",
    #      "<http://www.grid.ac/institutes/grid.10493.3f>"),
    #     ("<http://risis.eu/leidenRanking_2015/resource/884>", "<http://risis.eu/alignment/predicate/SAMEAS>",
    #      "<http://risis.eu/eter_2014/resource/DE0056>"),
    #     ("<http://www.grid.ac/institutes/grid.10493.3f> ", "<http://risis.eu/alignment/predicate/SAMEAS>",
    #      "<http://risis.eu/eter_2014/resource/DE0056> ") ]

    def merge_d_matrices(parent, pop_parent):

        # COPYING LESSER MATRIX TO BIGGER MATRIX

        index = parent[St.row]
        pop_row = pop_parent[St.row]
        cur_mxd = parent[St.matrix_d]
        pop_mxd = pop_parent[St.matrix_d]
        # position_add = clusters[parent][St.row] - 1

        # print "\tPOSITION: {} | POSITION POP: {}".format(index, pop_row)
        # print "\tADD VALUE: {}".format(position_add)

        # COPY MATRIX
        # print "\tPOP HEADER: {}".format(pop_mx[0][:])
        for row in range(1, pop_row):

            # ADD HEADER IF NOT ALREADY IN
            # print "\tCURRENT HEADER ADDED: {}".format(cur_mx[0:])
            if pop_mxd[(row, 0)] not in cur_mxd:
                pop_item_row = pop_mxd[(row, 0)]
                cur_mxd[(index, 0)] = pop_item_row
                cur_mxd[(0, index)] = pop_item_row
                index += 1
                parent[St.row] = index
                # print "\tHEADER ADDED: {}".format(pop_item_row)

                # FOR THAT HEADER, COPY THE SUB-MATRIX
                for col in range(1, pop_row):

                    # THE HEADER ARE ALREADY IN THERE
                    if (row, col) in pop_mxd and pop_mxd[(row, col)] != 0:
                        # find header in current matrix
                        for col_item in range(1, len(cur_mxd)):
                            if (0, col_item) in cur_mxd and (0, col) in pop_mxd and \
                                            cur_mxd[(0, col_item)] == pop_mxd[(0, col)]:
                                # print "\tIN2 ({}, {})".format(index - 1, col_item)
                                cur_mxd[(index - 1, col_item)] = 1

    def cluster_helper(counter, annotate=False):

        counter += 1
        child_1 = subject.n3().strip()
        child_2 = obj.n3().strip()
        # child_1 = subject.strip()
        # child_2 = obj.strip()

        # DATE CREATION
        # date = "{}".format(datetime.datetime.today().strftime(_format))

        # CHECK WHETHER A CHILD HAS A PARENT
        has_parent_1 = True if child_1 in root else False
        has_parent_2 = True if child_2 in root else False
        # print "\n{}|{} Has Parents {}|{}".format(child_1, child_2, has_parent_1, has_parent_2)

        # 1. START BOTH CHILD ARE ORPHANS
        if has_parent_1 is False and has_parent_2 is False:

            # print "\nSTART {}:{} | {}:{}".format(child_1, has_parent_1, child_2, has_parent_2)

            # GENERATE THE PARENT
            # hash_value = hash(date + str(count) + graph)
            hash_value = hash(child_1 + child_2 + graph)
            parent = "{}".format(str(hash_value).replace("-", "N")) if str(
                hash_value).startswith("-") \
                else "P{}".format(hash_value)

            # ASSIGN A PARENT TO BOTH CHILD
            root[child_1] = parent
            root[child_2] = parent

            # CREATE A CLUSTER
            if parent not in clusters:
                # MATRIX
                # mx = matrix(matrix_size, matrix_size)
                mxd = dict()
                # ROW
                # mx[0][1] = child_1
                # mx[0][2] = child_2

                mxd[(0, 1)] = child_1
                mxd[(0, 2)] = child_2

                # COLUMNS
                # mx[1][0] = child_1
                # mx[2][0] = child_2

                mxd[(1, 0)] = child_1
                mxd[(2, 0)] = child_2

                # RELATION
                # mx[1][2] = 1
                # mx[2][1] = 1
                mxd[(2, 1)] = 1

                clusters[parent] = {St.children: [child_1, child_2], St.matrix: None, St.row: 3, St.matrix_d: mxd}
                if annotate:
                    clusters[parent][St.annotate] = "\n\tSTART {} | {}".format(child_1, child_2)

            # print "\tPOSITION: {}".format(3)
            # print "\tIT WILL BE PRINTED AT: ({}, {})".format(2, 1)

        # 2. BOTH CHILD HAVE A PARENT OF THEIR OWN
        elif has_parent_1 is True and has_parent_2 is True:

            # 2.1 BOTH CHILD HAVE THE SAME PARENT, DO NOTHING
            if root[child_1] == root[child_2]:
                # print "CLUSTER SIZE IS {} BUT THERE IS NOTHING TO DO\n".format(len(clusters))
                # print "\nSAME PARENTS {}:{} | {}:{}".format(child_1, has_parent_1, child_2, has_parent_2)
                # cur_mx = clusters[root[child_1]][St.matrix]
                cur_mxd = clusters[root[child_1]][St.matrix_d]

                row_1 = 0
                row_2 = 0

                # FIND ROW
                # row_1 = clusters[root[child_1]][St.row]
                # for row in range(1, clusters[root[child_1]][St.row]):
                #     if cur_mx[row][0] == child_1:
                #         row_1 = row
                #
                # for col in range(1, clusters[root[child_1]][St.row]):
                #     if cur_mx[0][col] == child_2:
                #         row_2 = col

                for row in range(1, clusters[root[child_1]][St.row]):
                    if (row, 0) in cur_mxd and cur_mxd[(row, 0)] == child_1:
                        row_1 = row

                for col in range(1, clusters[root[child_1]][St.row]):
                    if (0, col) in cur_mxd and cur_mxd[(0, col)] == child_2:
                        row_2 = col

                # row_2 = clusters[root[child_2]][St.row]

                # print "\tPOSITIONS: {} | {}".format(row_2, row_1)
                # cur_mx[row_2][row_1] = 1
                cur_mxd[(row_2, row_1)] = 1

                if annotate:
                    clusters[root[child_1]][St.annotate] += "\n\tSAME PARENTS {} | {}".format(child_1, child_2)

                # COPY THE SUB-MATRIX
                # for col in range(1, row_1):
                #     if cur_mx[0][col] == child_2:
                #         print "\tFOUND: {} AT POSITION: {}".format(cur_mx[0][col], col)
                #         print "\tIT WILL BE PRINTED AT: ({}, {})".format(row_1 - 1, col)
                #         cur_mx[row_1 - 1][col] = 1

                # continue
                return counter

            # THE PARENT WITH THE MOST CHILD GET THE CHILD OF THE OTHER PARENT
            # fFETCHING THE RESOURCES IN THE CLUSTER (CHILDREN)
            # print "\n{}:{} | {}:{}".format(child_1, has_parent_1, child_2, has_parent_2)

            children_1 = (clusters[root[child_1]])[St.children]
            children_2 = (clusters[root[child_2]])[St.children]

            # 2.2 CHOOSE A PARENT
            if len(children_1) >= len(children_2):
                # print "\tPARENT 1"
                parent = root[child_1]
                pop_parent = root[child_2]
                # root[child_2] = parent

            else:
                # print "\tPARENT 2"
                parent = root[child_2]
                pop_parent = root[child_1]
                # root[child_1] = parent

            # ALL CHILD OF PARENT (SMALL) ARE REASSIGNED A NEW PARENT
            for offspring in clusters[pop_parent][St.children]:
                root[offspring] = parent
                clusters[parent][St.children] += [offspring]

            # MERGE CURRENT WITH LESSER (CHILDREN) MATRICES, ANNOTATE AND POOP LESSER (CHILDREN) MATRICES
            merge_d_matrices(clusters[parent], clusters[pop_parent])

            if annotate:
                clusters[parent][St.annotate] += "\n\tCHOOSE A PARENT {} | {}".format(child_1, child_2)
            cluster_helper(count)
            # cluster_helper(count)

            # COPYING LESSER MATRIX TO BIGGER MATRIX
            # index = clusters[parent][St.row]
            # pop_row = clusters[pop_parent][St.row]
            # cur_mx = clusters[parent][St.matrix]
            # pop_mx = clusters[pop_parent][St.matrix]
            # # position_add = clusters[parent][St.row] - 1
            #
            # print "\tPOSITION: {} | POSITION POP: {}".format(index, pop_row)
            # # print "\tADD VALUE: {}".format(position_add)
            #
            # # # ADD HEADER
            # # for x in range(1, pop_index):
            # #     cur_mx[0][index - 1 + x] = pop_mx[0][x]
            # #     cur_mx[index - 1 + x][0] = pop_mx[0][x]
            # #     clusters[parent][St.row] += 1
            #
            # # COPY MATRIX
            # print "\tPOP HEADER: {}".format(pop_mx[0][:])
            # for row in range(1, pop_row):
            #
            #     # ADD HEADER IF NOT ALREADY IN
            #     # print "\tCURREENT HEADER ADDED: {}".format(cur_mx[0:])
            #     if pop_mx[row][0] not in cur_mx[0:]:
            #         pop_item_row = pop_mx[row][0]
            #         cur_mx[index][0] = pop_item_row
            #         cur_mx[0][index] = pop_item_row
            #         index += 1
            #         clusters[parent][St.row] = index
            #         print "\tHEADER ADDED: {}".format(pop_item_row)
            #
            #
            #         # FOR THAT HEADER, COPY THE SUB-MATRIX
            #         for col in range(1, pop_row):
            #
            #             # THE HEADER IS NOT IN
            #             if pop_mx[row][col] != 0 and pop_mx[row][0] not in cur_mx[1:-1]:
            #                 print "\tIN ({}, {})".format(index-1, col )
            #                 # index += 1
            #                 # clusters[parent][St.row] = index
            #
            #             # THE HEADER ARE ALREADY IN THERE
            #             if pop_mx[row][col] != 0:
            #                 # find header in current matrix
            #                 for col_item in range(1, len(cur_mx[1:-1])):
            #                     if cur_mx[0][col_item] == pop_mx[0][col]:
            #                         print "\tIN2 ({}, {})".format(index-1, col_item)
            # cur_mx[row + position_add][col + position_add] = pop_mx[row][col]

            # cur_mx[0][position_add+ row] = pop_mx[row][0]

            # cur_mx[y + position_add][x + position_add] = pop_mx[y][x]

            # POP THE PARENT WITH THE LESSER CHILD

            if annotate:
                clusters[parent][St.annotate] += clusters[pop_parent][St.annotate]
            clusters.pop(pop_parent)

        # 3. ONE CHILD [CHILD 1] HAVE A PARENT OF HIS OWN
        elif has_parent_1 is True:

            # THE CHILD WITH NO PARENT IS ASSIGNED TO THE PARENT OF THE CHILD WITH PARENT
            # print "\n{}:{} | {}:{}".format(child_1, has_parent_1, child_2, has_parent_2)

            parent = root[child_1]
            root[child_2] = parent
            clusters[parent][St.children] += [child_2]
            # print "\t>>> {} is in root {}".format(child_2, child_2 in root)

            # cur_mx = clusters[parent][St.matrix]
            cur_mxd = clusters[parent][St.matrix_d]
            row_1 = clusters[parent][St.row]

            # ADD HEADER
            # cur_mx[row_1][0] = child_2
            # cur_mx[0][row_1] = child_2

            cur_mxd[(row_1, 0)] = child_2
            cur_mxd[(0, row_1)] = child_2

            # INCREMENT POSITION
            row_1 += 1
            # print "\tPOSITION: {}".format(row_1)
            clusters[parent][St.row] = row_1

            # COPY MATRIX
            # for col in range(1, row_1):
            #     # print cur_mx[0][x], child_1
            #     if cur_mx[0][col] == child_1:
            #         # print "\tFOUND: {} AT POSITION: {}".format(cur_mx[0][col], col)
            #         # print "\tIT WILL BE PRINTED AT: ({}, {})".format(row_1 - 1, col)
            #         # cur_mx[position_1 - 1][x] = 1
            #         cur_mx[row_1 - 1][col] = 1
            #         clusters[root[child_1]][St.annotate] += "\n\tONLY 1 {} HAS A PARENT COMPARED TO {}".format(
            #             child_1, child_2)

            for col in range(1, row_1):
                if (0, col) in cur_mxd and cur_mxd[(0, col)] == child_1:
                    cur_mxd[(row_1 - 1, col)] = 1
                    if annotate:
                        clusters[root[child_1]][St.annotate] += "\n\tONLY 1 {} HAS A PARENT COMPARED TO {}".format(
                            child_1, child_2)

        # 4. ONE CHILD [CHILD 2] HAVE A PARENT OF HIS OWN
        elif has_parent_2 is True:

            # THE CHILD WITH NO PARENT IS ASSIGNED TO THE PARENT OF THE CHILD WITH PARENT
            # print "\n{}:{} | {}:{}".format(child_1, has_parent_1, child_2, has_parent_2)

            parent = root[child_2]
            root[child_1] = parent
            clusters[parent][St.children] += [child_1]
            # print "\t>>> {} is in root {}".format(child_1, child_1 in root)

            # cur_mx = clusters[parent][St.matrix]
            cur_mxd = clusters[parent][St.matrix_d]
            row_2 = clusters[parent][St.row]

            # ADD HEADER
            # print row_2
            # cur_mx[row_2][0] = child_1
            # cur_mx[0][row_2] = child_1

            cur_mxd[(row_2, 0)] = child_1
            cur_mxd[(0, row_2)] = child_1

            # INCREMENT POSITION
            row_2 += 1
            # print "\tPOSITION: {}".format(row_2)
            clusters[parent][St.row] = row_2

            # COPY MATRIX
            # for col in range(1, row_2):
            #     # print cur_mx[0][x], child_1
            #     if cur_mx[0][col] == child_2:
            #         # print "\tFOUND: {} AT POSITION: {}".format(cur_mx[0][col], col)
            #         # print "\tIT WILL BE PRINTED AT: ({}, {})".format(row_2 - 1, col)
            #         # cur_mx[position_2 - 1][x] = 1
            #         cur_mx[row_2 - 1][col] = 1
            #         clusters[root[child_1]][St.annotate] += "\n\tONLY 2 {} HAS A PARENT COMPARED TO {}".format(
            #             child_2, child_1)

            for col in range(1, row_2):
                if (0, col) in cur_mxd and cur_mxd[(0, col)] == child_2:
                    cur_mxd[(row_2 - 1, col)] = 1
                    if annotate:
                        clusters[root[child_1]][St.annotate] += "\n\tONLY 2 {} HAS A PARENT COMPARED TO {}".format(
                            child_2, child_1)

        return counter

    print "2. ITERATING THROUGH THE GRAPH OF SIZE {}".format(len(g))

    standard = 50000
    check = 1
    iteration = 1

    for subject, predicate, obj in g:

        count = cluster_helper(count, annotate=False)
        if iteration == check:
            print "\tRESOURCE {:>10}:   {} {}".format(count, subject.n3(), obj)
            check = check + standard
        iteration += 1

    print "3. NUMBER OF CLUSTER FOUND: {}".format(len(clusters))
    return clusters


def resource_stat(alignment, dataset, resource_type=None, output=True, activated=False):

    # OUTPUT FALSE RETURNS THE MATRIX WHILE OUTPUT TRUE RETURNS THE DISPLAY MATRIX IN A TABLE FORMAT

    print "\nCOMPUTING STATISTICS ON ALIGNMENT"
    if activated is False:
        print "\tTHE FUNCTION I NOT ACTIVATED"
        return [None, None]
    print "\tSTATISTICS FOR {}".format(alignment)
    message = "\tSTATISTICS FOR {}\n".format(alignment)


    # STATS ON DISCOVERED RESOURCES
    matched = dict()
    matched_resp = resources_matched(alignment, dataset, resource_type=resource_type, matched=True, stat=True)
    matched_res = matched_resp["result"]
    for r in range(1, len(matched_res)):
        for c in range(len(matched_res[r])):
            matched[matched_res[0][c]] = matched_res[r][c]

    print ">>> DISCOVERED"
    message += ">>> DISCOVERED\n"
    for key, value in matched.items():
        print "\t{:21} : {}".format(key, value)
        message += "\t{:21} : {}\n".format(key, value)

    # STATS ON RESOURCES NOT DISCOVERED
    lost = dict()
    lost_rep = resources_matched(alignment, dataset, resource_type=resource_type, matched=False, stat=True)
    lost_res = lost_rep["result"]
    for r in range(1, len(lost_res)):
        for c in range(len(lost_res[r])):
            lost[lost_res[0][c]] = lost_res[r][c]

    lost_resources = resources_matched(alignment, dataset, resource_type=resource_type, matched=False, stat=False)
    lost_result = []
    for i in range(1, len(lost_resources["result"])):
        lost_result += [lost_resources["result"][i][0]]

    lost["Resources not matched"] = disambiguate_network(alignment, lost_result, output=output)
    # print matched
    # print lost
    # print [matched, lost]

    print ">>> NOT DISCOVERED"
    message += ">>> NOT DISCOVERED\n"
    for key, value in lost.items():
        print "\t{:21} : {}".format(key, value)
        message += "\t{:21} : {}\n".format(key, value)

    return [matched, lost, message]


def resources_matched(alignment, dataset, resource_type=None, matched=True, stat=True):

    # ALIGNMENT                 : IS THE SET OF CORRESPONDENCES
    # DATASET                   : THE DATASET UNDER SCRUTINY
    # RESOURCE TYPE             : IF NOT PROVIDED, THEN THE ANALYSIS APPLIED TO ALL RESOURCES MATCHED/NO FOUND
    # STAT SET TO [TRUE]        : PROVIDES STATISTICS ON THE RESOURCES
    # MATCHED SET TO [TRUE]     : ANY DISPLAYED DATA APPLIES TO THE MATCHED RESOURCES
    # MATCHED SET TO [FALSE]    : ANY DISPLAYED DATA APPLIES TO THE NOT FOUND RESOURCES

    if resource_type:
        comment_type = ""
        comment_type_opp = "#"
    else:
        comment_type = "#"
        comment_type_opp = ""

    matched_comment = ""
    term = "lost"
    if matched:
        matched_comment = "#"
        term = 'matched'

    stat_comment = ""
    stat_comment_opp = "#"
    if stat is not True:
        stat_comment = "#"
        stat_comment_opp = ""

    query = """
    {6}select (count (distinct ?subject) as ?{8}) ?total ( (?{8}/?total)*100 as ?percentage_{8})
    {7}select distinct ?subject
    {{

        {{
            select (count (distinct ?s) as ?total)
            {{
                GRAPH <{1}>
                {{
                    {2}?s a <{3}>.

                    ### ANY TRIPLE
                    {4}?s ?pred ?obj.
                }}
            }}
        }}

        {5}{{
        {5}    GRAPH <{1}>
        {5}    {{
        {5}        ### SPECIFIC TYPE OF TRIPLE
        {5}        {2}?subject a <{3}>.

        {5}        ### ANY TRIPLE
        {5}        {4}?subject ?pred ?obj.
        {5}    }}
        {5}}} MINUS

        {{
            GRAPH <{0}>
            {{
                {{ ?subject ?predicate ?object . }} UNION
                {{ ?object ?predicate ?subject . }}

                GRAPH <{1}>
                {{
                    ### SPECIFIC TYPE OF TRIPLE
                    {2}?subject a <{3}>.

                    ### ANY TRIPLE
                    {4}?subject ?pred ?obj.
                }}
            }}
        }}
    }} {6}GROUP BY ?total

    """.format(alignment, dataset, comment_type, resource_type, comment_type_opp,
               matched_comment, stat_comment, stat_comment_opp, term)
    # print query
    # print Qry.sparql_xml_to_matrix(query)
    return Qry.sparql_xml_to_matrix(query)


# # LINKSET CLUSTERING
# def cluster_links(graph):
#
#     count = 0
#     clusters = dict()
#     root = dict()
#
#     # DOWNLOAD THE GRAPH
#     print "\n0. DOWNLOADING THE GRAPH"
#     response = Exp.export_alignment(graph)
#     links = response['result']
#     # print links
#
#     # LOAD THE GRAPH
#     print "1. LOADING THE GRAPH"
#     g = rdflib.Graph()
#     g.parse(data=links, format="turtle")
#     # g = [
#     #     ("<http://grid.2>", "<http://risis.eu/alignment/predicate/SAMEAS>", "<http://orgref.2>"),
#     #     ("<http://leiden.2>", "<http://risis.eu/alignment/predicate/SAMEAS>", "<http://grid.2>"),
#     #     ("<http://orgref.2>", "<http://risis.eu/alignment/predicate/SAMEAS>", "<http://orgreg.2>"),
#     #     ("<http://orgreg.2> ", "<http://risis.eu/alignment/predicate/SAMEAS>", "<http://h2020.2> "),
#     #     ("<http://h2020.2>", "<http://risis.eu/alignment/predicate/SAMEAS>", "<http://eter.2>"),
#     #     ("<http://eter.2>", "<http://risis.eu/alignment/predicate/SAMEAS>", "<http://leiden.2>"),
#     # ]
#
#     g = [
#         ("<http://grid.2>", "<http://risis.eu/alignment/predicate/SAMEAS>", "<http://orgref.2>"),
#         ("<http://eter.2>", "<http://risis.eu/alignment/predicate/SAMEAS>", "<http://leiden.2>"),
#         ("<http://orgreg.2> ", "<http://risis.eu/alignment/predicate/SAMEAS>", "<http://h2020.2> "),
#         ("<http://leiden.2>", "<http://risis.eu/alignment/predicate/SAMEAS>", "<http://grid.2>"),
#         ("<http://orgref.2>", "<http://risis.eu/alignment/predicate/SAMEAS>", "<http://orgreg.2>"),
#         ("<http://h2020.2>", "<http://risis.eu/alignment/predicate/SAMEAS>", "<http://eter.2>"),
#     ]
#
#     print "2. ITERATING THROUGH THE GRAPH OF SIZE {}".format(len(g))
#     for subject, predicate, obj in g:
#
#         count += 1
#         # child_1 = subject.n3().strip()
#         # child_2 = obj.n3().strip()
#
#         child_1 = subject.strip()
#         child_2 = obj.strip()
#         # parent = ""
#
#         # DATE CREATION
#         date = "{}".format(datetime.datetime.today().strftime(_format))
#
#         # CHECK WHETHER A CHILD HAS A PARENT
#         has_parent_1 = True if child_1 in root else False
#         has_parent_2 = True if child_2 in root else False
#         # print "\n{}|{} Has Parents {}|{}".format(child_1, child_2, has_parent_1, has_parent_2)
#
#         # BOTH CHILD ARE ORPHANS
#         if has_parent_1 is False and has_parent_2 is False:
#
#             print "\nSTART {}:{} | {}:{}".format(child_1, has_parent_1, child_2, has_parent_2)
#
#             # GENERATE THE PARENT
#             hash_value = hash(date + str(count) + graph)
#             parent = "{}".format(str(hash_value).replace("-", "N")) if str(hash_value).startswith("-") \
#                 else "P{}".format(hash_value)
#
#             # ASSIGN A PARENT TO BOTH CHILD
#             root[child_1] = parent
#             root[child_2] = parent
#
#             # CREATE A CLUSTER
#             if parent not in clusters:
#
#                 # MATRIX
#                 mx = matrix(150, 150)
#                 # ROW
#                 mx[0][1] = child_1
#                 mx[0][2] = child_2
#                 # COLUMNS
#                 mx[1][0] = child_1
#                 mx[2][0] = child_2
#                 # RELATION
#                 # mx[1][2] = 1
#                 mx[2][1] = 1
#
#                 clusters[parent] = {St.children: [child_1, child_2], St.matrix: mx, St.row: 3}
#
#             print "\tPOSITION: {}".format(3)
#             print "\tIT WILL BE PRINTED AT: ({}, {})".format(2, 1)
#
#         # BOTH CHILD HAVE A PARENT OF THEIR OWN
#         elif has_parent_1 is True and has_parent_2 is True:
#
#             # IF BOTH CHILD HAVE THE SAME PARENT, DO NOTHING
#             if root[child_1] == root[child_2]:
#                 # print "CLUSTER SIZE IS {} BUT THERE IS NOTHING TO DO\n".format(len(clusters))
#                 print "\n{}:{} | {}:{}".format(child_1, has_parent_1, child_2, has_parent_2)
#
#                 print "\n{}:{} | {}:{}".format(child_1, has_parent_1, child_2, has_parent_2)
#                 cur_mx = clusters[root[child_1]][St.matrix]
#
#                 row_1 = 0
#                 row_2 = 0
#
#                 # FIND ROW
#                 # row_1 = clusters[root[child_1]][St.row]
#                 for row in range(1, clusters[root[child_1]][St.row]):
#                     if cur_mx[row][0] == child_1:
#                         row_1 = row
#
#                 for col in range(1, clusters[root[child_1]][St.row]):
#                     if cur_mx[0][col] == child_2:
#                         row_2 = col
#
#                 # row_2 = clusters[root[child_2]][St.row]
#
#                 print "\tPOSITIONS: {} | {}".format(row_2, row_1)
#                 cur_mx[row_2][row_1] = 1
#
#
#                 # row_1 = clusters[root[child_1]][St.row]
#                 # row_2 = clusters[root[child_2]][St.row]
#                 #
#                 # print "\tPOSITION: {}".format(row_1)
#                 # print "\tPOSITION: {}".format(row_2)
#                 #
#                 # # COPY THE SUB-MATRIX
#                 # cur_mx = clusters[root[child_1]][St.matrix]
#                 # for col in range(1, row_1):
#                 #     if cur_mx[0][col] == child_2:
#                 #         print "\tFOUND: {} AT POSITION: {}".format(cur_mx[0][col], col)
#                 #         print "\tIT WILL BE PRINTED AT: ({}, {})".format(row_1 - 1, col)
#                 #         cur_mx[row_1 - 1][col] = 1
#
#                 continue
#
#             # THE PARENT WITH THE MOST CHILD GET THE CHILD OF THE OTHER PARENT
#             # fFETCHING THE RESOURCES IN THE CLUSTER (CHILDREN)
#             print "\n{}:{} | {}:{}".format(child_1, has_parent_1, child_2, has_parent_2)
#
#             children_1 = (clusters[root[child_1]])[St.children]
#             children_2 = (clusters[root[child_2]])[St.children]
#
#             # CHOOSE A PARENT
#             if len(children_1) >= len(children_2):
#                 print "\tPARENT 1"
#                 parent = root[child_1]
#                 pop_parent = root[child_2]
#                 # root[child_2] = parent
#
#             else:
#                 print "\tPARENT 2"
#                 parent = root[child_2]
#                 pop_parent = root[child_1]
#                 # root[child_1] = parent
#
#             # ALL CHILD OF PARENT (SMALL) ARE REASSIGNED A NEW PARENT
#             for offspring in clusters[pop_parent][St.children]:
#                 root[offspring] = parent
#                 clusters[parent][St.children] += [offspring]
#
#             merge_matrices(clusters, parent, pop_parent)
#
#             # COPYING LESSER MATRIX TO BIGGER MATRIX
#             # index = clusters[parent][St.row]
#             # pop_row = clusters[pop_parent][St.row]
#             # cur_mx = clusters[parent][St.matrix]
#             # pop_mx = clusters[pop_parent][St.matrix]
#             # # position_add = clusters[parent][St.row] - 1
#             #
#             # print "\tPOSITION: {} | POSITION POP: {}".format(index, pop_row)
#             # # print "\tADD VALUE: {}".format(position_add)
#             #
#             # # # ADD HEADER
#             # # for x in range(1, pop_index):
#             # #     cur_mx[0][index - 1 + x] = pop_mx[0][x]
#             # #     cur_mx[index - 1 + x][0] = pop_mx[0][x]
#             # #     clusters[parent][St.row] += 1
#             #
#             # # COPY MATRIX
#             # print "\tPOP HEADER: {}".format(pop_mx[0][:])
#             # for row in range(1, pop_row):
#             #
#             #     # ADD HEADER IF NOT ALREADY IN
#             #     # print "\tCURREENT HEADER ADDED: {}".format(cur_mx[0:])
#             #     if pop_mx[row][0] not in cur_mx[0:]:
#             #         pop_item_row = pop_mx[row][0]
#             #         cur_mx[index][0] = pop_item_row
#             #         cur_mx[0][index] = pop_item_row
#             #         index += 1
#             #         clusters[parent][St.row] = index
#             #         print "\tHEADER ADDED: {}".format(pop_item_row)
#             #
#             #
#             #         # FOR THAT HEADER, COPY THE SUB-MATRIX
#             #         for col in range(1, pop_row):
#             #
#             #             # THE HEADER IS NOT IN
#             #             if pop_mx[row][col] != 0 and pop_mx[row][0] not in cur_mx[1:-1]:
#             #                 print "\tIN ({}, {})".format(index-1, col )
#             #                 # index += 1
#             #                 # clusters[parent][St.row] = index
#             #
#             #             # THE HEADER ARE ALREADY IN THERE
#             #             if pop_mx[row][col] != 0:
#             #                 # find header in current matrix
#             #                 for col_item in range(1, len(cur_mx[1:-1])):
#             #                     if cur_mx[0][col_item] == pop_mx[0][col]:
#             #                         print "\tIN2 ({}, {})".format(index-1, col_item)
#                             # cur_mx[row + position_add][col + position_add] = pop_mx[row][col]
#
#
#                             # cur_mx[0][position_add+ row] = pop_mx[row][0]
#
#                             # cur_mx[y + position_add][x + position_add] = pop_mx[y][x]
#
#             # POP THE PARENT WITH THE LESSER CHILD
#             clusters.pop(pop_parent)
#
#         elif has_parent_1 is True:
#
#             # THE CHILD WITH NO PARENT IS ASSIGNED TO THE PARENT OF THE CHILD WITH PARENT
#             print "\n{}:{} | {}:{}".format(child_1, has_parent_1, child_2, has_parent_2)
#
#             parent = root[child_1]
#             root[child_2] = parent
#             clusters[parent][St.children] += [child_2]
#             print "\t>>> {} is in root {}".format(child_2, child_2 in root)
#
#             cur_mx = clusters[parent][St.matrix]
#             row_1 = clusters[parent][St.row]
#
#             # ADD HEADER
#             cur_mx[row_1][0] = child_2
#             cur_mx[0][row_1] = child_2
#
#             # INCREMENT POSITION
#             row_1 += 1
#             print "\tPOSITION: {}".format(row_1)
#             clusters[parent][St.row] = row_1
#
#             # COPY MATRIX
#             for col in range(1, row_1):
#                 # print cur_mx[0][x], child_1
#                 if cur_mx[0][col] == child_1:
#                     print "\tFOUND: {} AT POSITION: {}".format(cur_mx[0][col], col)
#                     print "\tIT WILL BE PRINTED AT: ({}, {})".format(row_1 - 1, col)
#                     # cur_mx[position_1 - 1][x] = 1
#                     cur_mx[row_1 - 1][col] = 1
#
#         elif has_parent_2 is True:
#
#             # THE CHILD WITH NO PARENT IS ASSIGNED TO THE PARENT OF THE CHILD WITH PARENT
#             print "\n{}:{} | {}:{}".format(child_1, has_parent_1, child_2, has_parent_2)
#
#             parent = root[child_2]
#             root[child_1] = parent
#             clusters[parent][St.children] += [child_1]
#             print "\t>>> {} is in root {}".format(child_1, child_1 in root)
#
#             cur_mx = clusters[parent][St.matrix]
#             row_2 = clusters[parent][St.row]
#
#             # ADD HEADER
#             cur_mx[row_2][0] = child_1
#             cur_mx[0][row_2] = child_1
#
#
#             # INCREMENT POSITION
#             row_2 += 1
#             print "\tPOSITION: {}".format(row_2)
#             clusters[parent][St.row] = row_2
#
#             # COPY MATRIX
#             for col in range(1, row_2):
#                 # print cur_mx[0][x], child_1
#                 if cur_mx[0][col] == child_2:
#                     print "\tFOUND: {} AT POSITION: {}".format(cur_mx[0][col], col)
#                     print "\tIT WILL BE PRINTED AT: ({}, {})".format(row_2 - 1, col)
#                     # cur_mx[position_2 - 1][x] = 1
#                     cur_mx[row_2 - 1][col] = 1
#
#         # print "{} Clusters but the current is: {}\n".format(len(clusters), clusters[parent])
#     print "\n3. NUMBER OF CLUSTER FOND: {}".format(len(clusters))
#     return clusters


# linkset_1 = "http://risis.eu/linkset/clustered_exactStrSim_N167245093"
# linkset_2 = "http://risis.eu/linkset/clustered_exactStrSim_N1245679810818748702"
# linkset_3 = "http://risis.eu/linkset/clustered_test"
#
# rsrd_list = ["<http://risis.eu/orgref_20170703/resource/1389122>",
#              "<http://risis.eu/cordisH2020/resource/participant_993809912>",
#              "<http://www.grid.ac/institutes/grid.1034.6>"]
#
# # print disambiguate_network(linkset_1, rsrd_list)
# cluster_test(linkset_2, network_size=4, limit=1000)

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

#     if len(item['cluster']) > 1:
#         print "\n{:10}\t{:3}\t{}".format(item['parent'], len(item['cluster']), item['sample'])

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


# links_clustering("", limit=1000)


def links_clustering_BUG(graph, limit=1000):

    count = 0
    clusters = dict()

    # ROOT = KEY:CHILD VALUE:PARENT
    root = dict()

    # DOWNLOAD THE GRAPH
    print "\n0. DOWNLOADING THE GRAPH FROM THE TRIPLE STORE"
    # response = Exp.export_alignment(graph, limit=limit)
    # links = response['result']
    # # print links
    #
    # # LOAD THE GRAPH
    # print "1. LOADING THE GRAPH USING RDFLIB"
    # g = rdflib.Graph()
    # g.parse(data=links, format="turtle")
    # g = [
    #     ("<http://grid.2>", "<http://risis.eu/alignment/predicate/SAMEAS>", "<http://orgref.2>"),
    #     ("<http://leiden.2>", "<http://risis.eu/alignment/predicate/SAMEAS>", "<http://grid.2>"),
    #     ("<http://orgref.2>", "<http://risis.eu/alignment/predicate/SAMEAS>", "<http://orgreg.2>"),
    #     ("<http://orgreg.2> ", "<http://risis.eu/alignment/predicate/SAMEAS>", "<http://h2020.2> "),
    #     ("<http://h2020.2>", "<http://risis.eu/alignment/predicate/SAMEAS>", "<http://eter.2>"),
    #     ("<http://eter.2>", "<http://risis.eu/alignment/predicate/SAMEAS>", "<http://leiden.2>"),
    # ]

    g = [
        ( "<http://grid.2>", "<http://risis.eu/alignment/predicate/SAMEAS>", "<http://orgref.2>"),
        ( "<http://eter.2>", "<http://risis.eu/alignment/predicate/SAMEAS>", "<http://leiden.2>"),
        ("<http://orgreg.2> ", "<http://risis.eu/alignment/predicate/SAMEAS>", "<http://h2020.2> "),
        ( "<http://leiden.2>", "<http://risis.eu/alignment/predicate/SAMEAS>", "<http://grid.2>"),
        ("<http://orgref.2>", "<http://risis.eu/alignment/predicate/SAMEAS>", "<http://orgreg.2>"),
        ("<http://h2020.2>", "<http://risis.eu/alignment/predicate/SAMEAS>", "<http://eter.2>"),
    ]

    # g = [
    #     ("<http://risis.eu/leidenRanking_2015/resource/884>", "<http://risis.eu/alignment/predicate/SAMEAS>",
    #      "<http://www.grid.ac/institutes/grid.10493.3f>"),
    #     ("<http://risis.eu/leidenRanking_2015/resource/884>", "<http://risis.eu/alignment/predicate/SAMEAS>",
    #      "<http://risis.eu/eter_2014/resource/DE0056>"),
    #     ("<http://www.grid.ac/institutes/grid.10493.3f> ", "<http://risis.eu/alignment/predicate/SAMEAS>",
    #      "<http://risis.eu/eter_2014/resource/DE0056> ") ]

    def merge_d_matrices(parent, pop_parent):

        print "\t\t\tMERGING"

        # COPYING LESSER MATRIX TO BIGGER MATRIX

        index = parent[St.row]
        pop_row = pop_parent[St.row]
        cur_mxd = parent[St.matrix_d]
        pop_mxd = pop_parent[St.matrix_d]
        # position_add = clusters[parent][St.row] - 1

        # print "\tPOSITION: {} | POSITION POP: {}".format(index, pop_row)
        # print "\tADD VALUE: {}".format(position_add)

        # COPY MATRIX
        # print "\tPOP HEADER: {}".format(pop_mx[0][:])
        for row in range(1, pop_row):

            # ADD HEADER IF NOT ALREADY IN
            # print "\tCURRENT HEADER ADDED: {}".format(cur_mx[0:])
            if pop_mxd[(row, 0)] not in cur_mxd:
                pop_item_row = pop_mxd[(row, 0)]
                cur_mxd[(index, 0)] = pop_item_row
                cur_mxd[(0, index)] = pop_item_row
                index += 1
                parent[St.row] = index
                # print "\tHEADER ADDED: {}".format(pop_item_row)

                # FOR THAT HEADER, COPY THE SUB-MATRIX
                for col in range(1, pop_row):

                    # THE HEADER ARE ALREADY IN THERE
                    if (row, col) in pop_mxd and pop_mxd[(row, col)] != 0:
                        # find header in current matrix
                        for col_item in range(1, len(cur_mxd)):
                            if (0, col_item) in cur_mxd and (0, col) in pop_mxd and \
                                            cur_mxd[(0, col_item)] == pop_mxd[(0, col)]:
                                # print "\tIN2 ({}, {})".format(index - 1, col_item)
                                cur_mxd[(index - 1, col_item)] = 1

    def cluster_helper(counter, annotate=False):

        counter += 1
        # child_1 = subject.n3().strip()
        # child_2 = obj.n3().strip()
        child_1 = subject.strip()
        child_2 = obj.strip()

        # DATE CREATION
        # date = "{}".format(datetime.datetime.today().strftime(_format))

        # CHECK WHETHER A CHILD HAS A PARENT
        has_parent_1 = True if child_1 in root else False
        has_parent_2 = True if child_2 in root else False
        # print "\n{}|{} Has Parents {}|{}".format(child_1, child_2, has_parent_1, has_parent_2)

        # 1. START BOTH CHILD ARE ORPHANS
        if has_parent_1 is False and has_parent_2 is False:

            # print "\nSTART {}:{} | {}:{}".format(child_1, has_parent_1, child_2, has_parent_2)

            # GENERATE THE PARENT
            # hash_value = hash(date + str(count) + graph)
            hash_value = hash(child_1 + child_2 + graph)
            parent = "{}".format(str(hash_value).replace("-", "N")) if str(
                hash_value).startswith("-") \
                else "P{}".format(hash_value)

            # ASSIGN A PARENT TO BOTH CHILD
            root[child_1] = parent
            root[child_2] = parent

            # CREATE A CLUSTER
            if parent not in clusters:
                # MATRIX
                # mx = matrix(matrix_size, matrix_size)
                mxd = dict()
                # ROW
                # mx[0][1] = child_1
                # mx[0][2] = child_2

                mxd[(0, 1)] = child_1
                mxd[(0, 2)] = child_2

                # COLUMNS
                # mx[1][0] = child_1
                # mx[2][0] = child_2

                mxd[(1, 0)] = child_1
                mxd[(2, 0)] = child_2

                # RELATION
                # mx[1][2] = 1
                # mx[2][1] = 1
                mxd[(2, 1)] = 1

                clusters[parent] = {St.children: [child_1, child_2], St.matrix: None, St.row: 3, St.matrix_d: mxd}
                if annotate:
                    clusters[parent][St.annotate] = "\n\tSTART {} | {}".format(child_1, child_2)

            # print "\tPOSITION: {}".format(3)
            # print "\tIT WILL BE PRINTED AT: ({}, {})".format(2, 1)

        # 2. BOTH CHILD HAVE A PARENT OF THEIR OWN
        elif has_parent_1 is True and has_parent_2 is True:

            # 2.1 BOTH CHILD HAVE THE SAME PARENT, DO NOTHING
            if root[child_1] == root[child_2]:
                # print "CLUSTER SIZE IS {} BUT THERE IS NOTHING TO DO\n".format(len(clusters))
                # print "\nSAME PARENTS {}:{} | {}:{}".format(child_1, has_parent_1, child_2, has_parent_2)
                # cur_mx = clusters[root[child_1]][St.matrix]
                cur_mxd = clusters[root[child_1]][St.matrix_d]

                row_1 = 0
                row_2 = 0

                # FIND ROW
                # row_1 = clusters[root[child_1]][St.row]
                # for row in range(1, clusters[root[child_1]][St.row]):
                #     if cur_mx[row][0] == child_1:
                #         row_1 = row
                #
                # for col in range(1, clusters[root[child_1]][St.row]):
                #     if cur_mx[0][col] == child_2:
                #         row_2 = col

                for row in range(1, clusters[root[child_1]][St.row]):
                    if (row, 0) in cur_mxd and cur_mxd[(row, 0)] == child_1:
                        row_1 = row

                for col in range(1, clusters[root[child_1]][St.row]):
                    if (0, col) in cur_mxd and cur_mxd[(0, col)] == child_2:
                        row_2 = col

                # row_2 = clusters[root[child_2]][St.row]

                # print "\tPOSITIONS: {} | {}".format(row_2, row_1)
                # cur_mx[row_2][row_1] = 1
                cur_mxd[(row_2, row_1)] = 1

                if annotate:
                    clusters[root[child_1]][St.annotate] += "\n\tSAME PARENTS {} | {}".format(child_1, child_2)

                # COPY THE SUB-MATRIX
                # for col in range(1, row_1):
                #     if cur_mx[0][col] == child_2:
                #         print "\tFOUND: {} AT POSITION: {}".format(cur_mx[0][col], col)
                #         print "\tIT WILL BE PRINTED AT: ({}, {})".format(row_1 - 1, col)
                #         cur_mx[row_1 - 1][col] = 1

                # continue
                return counter

            # THE PARENT WITH THE MOST CHILD GET THE CHILD OF THE OTHER PARENT
            # fFETCHING THE RESOURCES IN THE CLUSTER (CHILDREN)
            # print "\n{}:{} | {}:{}".format(child_1, has_parent_1, child_2, has_parent_2)

            children_1 = (clusters[root[child_1]])[St.children]
            children_2 = (clusters[root[child_2]])[St.children]

            # 2.2 CHOOSE A PARENT
            if len(children_1) >= len(children_2):
                # print "\tPARENT 1"
                parent = root[child_1]
                pop_parent = root[child_2]
                # root[child_2] = parent

            else:
                # print "\tPARENT 2"
                parent = root[child_2]
                pop_parent = root[child_1]
                # root[child_1] = parent

            # ALL CHILD OF PARENT (SMALL) ARE REASSIGNED A NEW PARENT
            for offspring in clusters[pop_parent][St.children]:
                root[offspring] = parent
                clusters[parent][St.children] += [offspring]

            # MERGE CURRENT WITH LESSER (CHILDREN) MATRICES, ANNOTATE AND POOP LESSER (CHILDREN) MATRICES
            merge_d_matrices(clusters[parent], clusters[pop_parent])

            if annotate:
                clusters[parent][St.annotate] += "\n\tCHOOSE A PARENT {} | {}".format(child_1, child_2)
            cluster_helper(count)
            # cluster_helper(count)

            # COPYING LESSER MATRIX TO BIGGER MATRIX
            # index = clusters[parent][St.row]
            # pop_row = clusters[pop_parent][St.row]
            # cur_mx = clusters[parent][St.matrix]
            # pop_mx = clusters[pop_parent][St.matrix]
            # # position_add = clusters[parent][St.row] - 1
            #
            # print "\tPOSITION: {} | POSITION POP: {}".format(index, pop_row)
            # # print "\tADD VALUE: {}".format(position_add)
            #
            # # # ADD HEADER
            # # for x in range(1, pop_index):
            # #     cur_mx[0][index - 1 + x] = pop_mx[0][x]
            # #     cur_mx[index - 1 + x][0] = pop_mx[0][x]
            # #     clusters[parent][St.row] += 1
            #
            # # COPY MATRIX
            # print "\tPOP HEADER: {}".format(pop_mx[0][:])
            # for row in range(1, pop_row):
            #
            #     # ADD HEADER IF NOT ALREADY IN
            #     # print "\tCURREENT HEADER ADDED: {}".format(cur_mx[0:])
            #     if pop_mx[row][0] not in cur_mx[0:]:
            #         pop_item_row = pop_mx[row][0]
            #         cur_mx[index][0] = pop_item_row
            #         cur_mx[0][index] = pop_item_row
            #         index += 1
            #         clusters[parent][St.row] = index
            #         print "\tHEADER ADDED: {}".format(pop_item_row)
            #
            #
            #         # FOR THAT HEADER, COPY THE SUB-MATRIX
            #         for col in range(1, pop_row):
            #
            #             # THE HEADER IS NOT IN
            #             if pop_mx[row][col] != 0 and pop_mx[row][0] not in cur_mx[1:-1]:
            #                 print "\tIN ({}, {})".format(index-1, col )
            #                 # index += 1
            #                 # clusters[parent][St.row] = index
            #
            #             # THE HEADER ARE ALREADY IN THERE
            #             if pop_mx[row][col] != 0:
            #                 # find header in current matrix
            #                 for col_item in range(1, len(cur_mx[1:-1])):
            #                     if cur_mx[0][col_item] == pop_mx[0][col]:
            #                         print "\tIN2 ({}, {})".format(index-1, col_item)
            # cur_mx[row + position_add][col + position_add] = pop_mx[row][col]

            # cur_mx[0][position_add+ row] = pop_mx[row][0]

            # cur_mx[y + position_add][x + position_add] = pop_mx[y][x]

            # POP THE PARENT WITH THE LESSER CHILD

            if annotate:
                clusters[parent][St.annotate] += clusters[pop_parent][St.annotate]
            clusters.pop(pop_parent)

        # 3. ONE CHILD [CHILD 1] HAVE A PARENT OF HIS OWN
        elif has_parent_1 is True:

            # THE CHILD WITH NO PARENT IS ASSIGNED TO THE PARENT OF THE CHILD WITH PARENT
            # print "\n{}:{} | {}:{}".format(child_1, has_parent_1, child_2, has_parent_2)

            parent = root[child_1]
            root[child_2] = parent
            clusters[parent][St.children] += [child_2]
            # print "\t>>> {} is in root {}".format(child_2, child_2 in root)

            # cur_mx = clusters[parent][St.matrix]
            cur_mxd = clusters[parent][St.matrix_d]
            row_1 = clusters[parent][St.row]

            # ADD HEADER
            # cur_mx[row_1][0] = child_2
            # cur_mx[0][row_1] = child_2

            cur_mxd[(row_1, 0)] = child_2
            cur_mxd[(0, row_1)] = child_2

            # INCREMENT POSITION
            row_1 += 1
            # print "\tPOSITION: {}".format(row_1)
            clusters[parent][St.row] = row_1

            # COPY MATRIX
            # for col in range(1, row_1):
            #     # print cur_mx[0][x], child_1
            #     if cur_mx[0][col] == child_1:
            #         # print "\tFOUND: {} AT POSITION: {}".format(cur_mx[0][col], col)
            #         # print "\tIT WILL BE PRINTED AT: ({}, {})".format(row_1 - 1, col)
            #         # cur_mx[position_1 - 1][x] = 1
            #         cur_mx[row_1 - 1][col] = 1
            #         clusters[root[child_1]][St.annotate] += "\n\tONLY 1 {} HAS A PARENT COMPARED TO {}".format(
            #             child_1, child_2)

            for col in range(1, row_1):
                if (0, col) in cur_mxd and cur_mxd[(0, col)] == child_1:
                    cur_mxd[(row_1 - 1, col)] = 1
                    if annotate:
                        clusters[root[child_1]][St.annotate] += "\n\tONLY 1 {} HAS A PARENT COMPARED TO {}".format(
                            child_1, child_2)

        # 4. ONE CHILD [CHILD 2] HAVE A PARENT OF HIS OWN
        elif has_parent_2 is True:

            # THE CHILD WITH NO PARENT IS ASSIGNED TO THE PARENT OF THE CHILD WITH PARENT
            # print "\n{}:{} | {}:{}".format(child_1, has_parent_1, child_2, has_parent_2)

            parent = root[child_2]
            root[child_1] = parent
            clusters[parent][St.children] += [child_1]
            # print "\t>>> {} is in root {}".format(child_1, child_1 in root)

            # cur_mx = clusters[parent][St.matrix]
            cur_mxd = clusters[parent][St.matrix_d]
            row_2 = clusters[parent][St.row]

            # ADD HEADER
            # print row_2
            # cur_mx[row_2][0] = child_1
            # cur_mx[0][row_2] = child_1

            cur_mxd[(row_2, 0)] = child_1
            cur_mxd[(0, row_2)] = child_1

            # INCREMENT POSITION
            row_2 += 1
            # print "\tPOSITION: {}".format(row_2)
            clusters[parent][St.row] = row_2

            # COPY MATRIX
            # for col in range(1, row_2):
            #     # print cur_mx[0][x], child_1
            #     if cur_mx[0][col] == child_2:
            #         # print "\tFOUND: {} AT POSITION: {}".format(cur_mx[0][col], col)
            #         # print "\tIT WILL BE PRINTED AT: ({}, {})".format(row_2 - 1, col)
            #         # cur_mx[position_2 - 1][x] = 1
            #         cur_mx[row_2 - 1][col] = 1
            #         clusters[root[child_1]][St.annotate] += "\n\tONLY 2 {} HAS A PARENT COMPARED TO {}".format(
            #             child_2, child_1)

            for col in range(1, row_2):
                if (0, col) in cur_mxd and cur_mxd[(0, col)] == child_2:
                    cur_mxd[(row_2 - 1, col)] = 1
                    if annotate:
                        clusters[root[child_1]][St.annotate] += "\n\tONLY 2 {} HAS A PARENT COMPARED TO {}".format(
                            child_2, child_1)

        return counter

    print "2. ITERATING THROUGH THE GRAPH OF SIZE {}".format(len(g))

    standard = 50000
    check = 1
    iteration = 1

    for subject, predicate, obj in g:

        print "\tRESOURCE {:>7}:   {} {}".format(count, subject, obj)
        count = cluster_helper(count, annotate=False)
        # data = "\tRESOURCE {:>7}:   {} {}".format(count, subject.n3(), obj)

        for key, value in clusters.items():
            print "\t\t", key
            print "\t\t", value
        if iteration == check:
            # print "\tRESOURCE {:>10}:   {} {}".format(count, subject.n3(), obj)
            check = check + standard
        iteration += 1

    print "3. NUMBER OF CLUSTER FOUND: {}".format(len(clusters))
    return clusters


# USING SET
def links_clustering_improved(graph, limit=1000):


    # ROOT = KEY:CHILD VALUE:PARENT
    root = dict()
    count = 0
    clusters = dict()

    root_mtx = {}
    # count_mtx = 0
    clusters_mtx = {}

    # DOWNLOAD THE GRAPH
    print "\n0. DOWNLOADING THE GRAPH FROM THE TRIPLE STORE"
    response = Exp.export_alignment(graph, limit=limit)
    links = response['result']

    # LOAD THE GRAPH
    print "1. LOADING THE GRAPH USING RDFLIB"
    g = rdflib.Graph()
    g.parse(data=links, format="turtle")

    # g = [
    #     ("<http://grid.2>", "<http://risis.eu/alignment/predicate/SAMEAS>", "<http://orgref.2>"),
    #     ("<http://leiden.2>", "<http://risis.eu/alignment/predicate/SAMEAS>", "<http://grid.2>"),
    #     ("<http://orgref.2>", "<http://risis.eu/alignment/predicate/SAMEAS>", "<http://orgreg.2>"),
    #     ("<http://orgreg.2> ", "<http://risis.eu/alignment/predicate/SAMEAS>", "<http://h2020.2> "),
    #     ("<http://h2020.2>", "<http://risis.eu/alignment/predicate/SAMEAS>", "<http://eter.2>"),
    #     ("<http://eter.2>", "<http://risis.eu/alignment/predicate/SAMEAS>", "<http://leiden.2>"),
    # ]

    # g = [
    #     ( "<http://grid.2>", "<http://risis.eu/alignment/predicate/SAMEAS>", "<http://orgref.2>"),
    #     ( "<http://eter.2>", "<http://risis.eu/alignment/predicate/SAMEAS>", "<http://leiden.2>"),
    #     ("<http://orgreg.2> ", "<http://risis.eu/alignment/predicate/SAMEAS>", "<http://h2020.2> "),
    #     ( "<http://leiden.2>", "<http://risis.eu/alignment/predicate/SAMEAS>", "<http://grid.2>"),
    #     ("<http://orgref.2>", "<http://risis.eu/alignment/predicate/SAMEAS>", "<http://orgreg.2>"),
    #     ("<http://h2020.2>", "<http://risis.eu/alignment/predicate/SAMEAS>", "<http://eter.2>"),
    # ]

    # g = [
    #     ("<http://risis.eu/leidenRanking_2015/resource/884>", "<http://risis.eu/alignment/predicate/SAMEAS>",
    #      "<http://www.grid.ac/institutes/grid.10493.3f>"),
    #     ("<http://risis.eu/leidenRanking_2015/resource/884>", "<http://risis.eu/alignment/predicate/SAMEAS>",
    #      "<http://risis.eu/eter_2014/resource/DE0056>"),
    #     ("<http://www.grid.ac/institutes/grid.10493.3f> ", "<http://risis.eu/alignment/predicate/SAMEAS>",
    #      "<http://risis.eu/eter_2014/resource/DE0056> ") ]

    def merge_d_matrices(parent, pop_parent):

        # COPYING LESSER MATRIX TO BIGGER MATRIX

        index = parent[St.row]
        pop_row = pop_parent[St.row]
        cur_mxd = parent[St.matrix_d]
        pop_mxd = pop_parent[St.matrix_d]
        # position_add = clusters[parent][St.row] - 1

        # print "\tPOSITION: {} | POSITION POP: {}".format(index, pop_row)
        # print "\tADD VALUE: {}".format(position_add)

        # COPY MATRIX
        # print "\tPOP HEADER: {}".format(pop_mx[0][:])
        for row in range(1, pop_row):

            # ADD HEADER IF NOT ALREADY IN
            # print "\tCURRENT HEADER ADDED: {}".format(cur_mx[0:])
            if pop_mxd[(row, 0)] not in cur_mxd:
                pop_item_row = pop_mxd[(row, 0)]
                cur_mxd[(index, 0)] = pop_item_row
                cur_mxd[(0, index)] = pop_item_row
                index += 1
                parent[St.row] = index
                # print "\tHEADER ADDED: {}".format(pop_item_row)

                # FOR THAT HEADER, COPY THE SUB-MATRIX
                for col in range(1, pop_row):

                    # THE HEADER ARE ALREADY IN THERE
                    if (row, col) in pop_mxd and pop_mxd[(row, col)] != 0:
                        # find header in current matrix
                        for col_item in range(1, len(cur_mxd)):
                            if (0, col_item) in cur_mxd and (0, col) in pop_mxd and \
                                            cur_mxd[(0, col_item)] == pop_mxd[(0, col)]:
                                # print "\tIN2 ({}, {})".format(index - 1, col_item)
                                cur_mxd[(index - 1, col_item)] = 1

    def cluster_helper_mtx(counter, annotate=False):

        counter += 1
        child_1 = subject.n3().strip()
        child_2 = obj.n3().strip()
        # child_1 = subject.strip()
        # child_2 = obj.strip()

        # DATE CREATION
        # date = "{}".format(datetime.datetime.today().strftime(_format))

        # CHECK WHETHER A CHILD HAS A PARENT
        has_parent_1 = True if child_1 in root_mtx else False
        has_parent_2 = True if child_2 in root_mtx else False
        # print "\n{}|{} Has Parents {}|{}".format(child_1, child_2, has_parent_1, has_parent_2)

        # 1. START BOTH CHILD ARE ORPHANS
        if has_parent_1 is False and has_parent_2 is False:

            # print "\nSTART {}:{} | {}:{}".format(child_1, has_parent_1, child_2, has_parent_2)

            # GENERATE THE PARENT
            # hash_value = hash(date + str(count) + graph)
            hash_value = hash(child_1 + child_2 + graph)
            parent = "{}".format(str(hash_value).replace("-", "N")) if str(
                hash_value).startswith("-") \
                else "P{}".format(hash_value)

            # ASSIGN A PARENT TO BOTH CHILD
            root[child_1] = parent
            root[child_2] = parent

            # CREATE A CLUSTER
            if parent not in clusters:
                # MATRIX
                # mx = matrix(matrix_size, matrix_size)
                mxd = dict()
                # ROW
                # mx[0][1] = child_1
                # mx[0][2] = child_2

                mxd[(0, 1)] = child_1
                mxd[(0, 2)] = child_2

                # COLUMNS
                # mx[1][0] = child_1
                # mx[2][0] = child_2

                mxd[(1, 0)] = child_1
                mxd[(2, 0)] = child_2

                # RELATION
                # mx[1][2] = 1
                # mx[2][1] = 1
                mxd[(2, 1)] = 1

                clusters[parent] = {St.children: [child_1, child_2], St.matrix: None, St.row: 3, St.matrix_d: mxd}
                if annotate:
                    clusters[parent][St.annotate] = "\n\tSTART {} | {}".format(child_1, child_2)

            # print "\tPOSITION: {}".format(3)
            # print "\tIT WILL BE PRINTED AT: ({}, {})".format(2, 1)

        # 2. BOTH CHILD HAVE A PARENT OF THEIR OWN
        elif has_parent_1 is True and has_parent_2 is True:

            # 2.1 BOTH CHILD HAVE THE SAME PARENT, DO NOTHING
            if root_mtx[child_1] == root_mtx[child_2]:
                # print "CLUSTER SIZE IS {} BUT THERE IS NOTHING TO DO\n".format(len(clusters))
                # print "\nSAME PARENTS {}:{} | {}:{}".format(child_1, has_parent_1, child_2, has_parent_2)
                # cur_mx = clusters[root[child_1]][St.matrix]
                cur_mxd = clusters[root[child_1]][St.matrix_d]

                row_1 = 0
                row_2 = 0

                # FIND ROW
                # row_1 = clusters[root[child_1]][St.row]
                # for row in range(1, clusters[root[child_1]][St.row]):
                #     if cur_mx[row][0] == child_1:
                #         row_1 = row
                #
                # for col in range(1, clusters[root[child_1]][St.row]):
                #     if cur_mx[0][col] == child_2:
                #         row_2 = col

                for row in range(1, clusters[root[child_1]][St.row]):
                    if (row, 0) in cur_mxd and cur_mxd[(row, 0)] == child_1:
                        row_1 = row

                for col in range(1, clusters[root[child_1]][St.row]):
                    if (0, col) in cur_mxd and cur_mxd[(0, col)] == child_2:
                        row_2 = col

                # row_2 = clusters[root[child_2]][St.row]

                # print "\tPOSITIONS: {} | {}".format(row_2, row_1)
                # cur_mx[row_2][row_1] = 1
                cur_mxd[(row_2, row_1)] = 1

                if annotate:
                    clusters[root[child_1]][St.annotate] += "\n\tSAME PARENTS {} | {}".format(child_1, child_2)

                # COPY THE SUB-MATRIX
                # for col in range(1, row_1):
                #     if cur_mx[0][col] == child_2:
                #         print "\tFOUND: {} AT POSITION: {}".format(cur_mx[0][col], col)
                #         print "\tIT WILL BE PRINTED AT: ({}, {})".format(row_1 - 1, col)
                #         cur_mx[row_1 - 1][col] = 1

                # continue
                return counter

            # THE PARENT WITH THE MOST CHILD GET THE CHILD OF THE OTHER PARENT
            # fFETCHING THE RESOURCES IN THE CLUSTER (CHILDREN)
            # print "\n{}:{} | {}:{}".format(child_1, has_parent_1, child_2, has_parent_2)

            children_1 = (clusters_mtx[root_mtx[child_1]])[St.children]
            children_2 = (clusters_mtx[root_mtx[child_2]])[St.children]

            # 2.2 CHOOSE A PARENT
            if len(children_1) >= len(children_2):
                # print "\tPARENT 1"
                parent = root_mtx[child_1]
                pop_parent = root_mtx[child_2]
                # root[child_2] = parent

            else:
                # print "\tPARENT 2"
                parent = root_mtx[child_2]
                pop_parent = root_mtx[child_1]
                # root[child_1] = parent

            # ALL CHILD OF PARENT (SMALL) ARE REASSIGNED A NEW PARENT
            for offspring in clusters_mtx[pop_parent][St.children]:
                root_mtx[offspring] = parent
                clusters_mtx[parent][St.children] += [offspring]

            # MERGE CURRENT WITH LESSER (CHILDREN) MATRICES, ANNOTATE AND POOP LESSER (CHILDREN) MATRICES
            merge_d_matrices(clusters_mtx[parent], clusters_mtx[pop_parent])

            if annotate:
                clusters_mtx[parent][St.annotate] += "\n\tCHOOSE A PARENT {} | {}".format(child_1, child_2)
            cluster_helper_mtx(count)
            # cluster_helper(count)

            # COPYING LESSER MATRIX TO BIGGER MATRIX
            # index = clusters[parent][St.row]
            # pop_row = clusters[pop_parent][St.row]
            # cur_mx = clusters[parent][St.matrix]
            # pop_mx = clusters[pop_parent][St.matrix]
            # # position_add = clusters[parent][St.row] - 1
            #
            # print "\tPOSITION: {} | POSITION POP: {}".format(index, pop_row)
            # # print "\tADD VALUE: {}".format(position_add)
            #
            # # # ADD HEADER
            # # for x in range(1, pop_index):
            # #     cur_mx[0][index - 1 + x] = pop_mx[0][x]
            # #     cur_mx[index - 1 + x][0] = pop_mx[0][x]
            # #     clusters[parent][St.row] += 1
            #
            # # COPY MATRIX
            # print "\tPOP HEADER: {}".format(pop_mx[0][:])
            # for row in range(1, pop_row):
            #
            #     # ADD HEADER IF NOT ALREADY IN
            #     # print "\tCURREENT HEADER ADDED: {}".format(cur_mx[0:])
            #     if pop_mx[row][0] not in cur_mx[0:]:
            #         pop_item_row = pop_mx[row][0]
            #         cur_mx[index][0] = pop_item_row
            #         cur_mx[0][index] = pop_item_row
            #         index += 1
            #         clusters[parent][St.row] = index
            #         print "\tHEADER ADDED: {}".format(pop_item_row)
            #
            #
            #         # FOR THAT HEADER, COPY THE SUB-MATRIX
            #         for col in range(1, pop_row):
            #
            #             # THE HEADER IS NOT IN
            #             if pop_mx[row][col] != 0 and pop_mx[row][0] not in cur_mx[1:-1]:
            #                 print "\tIN ({}, {})".format(index-1, col )
            #                 # index += 1
            #                 # clusters[parent][St.row] = index
            #
            #             # THE HEADER ARE ALREADY IN THERE
            #             if pop_mx[row][col] != 0:
            #                 # find header in current matrix
            #                 for col_item in range(1, len(cur_mx[1:-1])):
            #                     if cur_mx[0][col_item] == pop_mx[0][col]:
            #                         print "\tIN2 ({}, {})".format(index-1, col_item)
            # cur_mx[row + position_add][col + position_add] = pop_mx[row][col]

            # cur_mx[0][position_add+ row] = pop_mx[row][0]

            # cur_mx[y + position_add][x + position_add] = pop_mx[y][x]

            # POP THE PARENT WITH THE LESSER CHILD

            if annotate:
                clusters_mtx[parent][St.annotate] += clusters_mtx[pop_parent][St.annotate]
            clusters_mtx.pop(pop_parent)

        # 3. ONE CHILD [CHILD 1] HAVE A PARENT OF HIS OWN
        elif has_parent_1 is True:

            # THE CHILD WITH NO PARENT IS ASSIGNED TO THE PARENT OF THE CHILD WITH PARENT
            # print "\n{}:{} | {}:{}".format(child_1, has_parent_1, child_2, has_parent_2)

            parent = root[child_1]
            root[child_2] = parent
            clusters[parent][St.children] += [child_2]
            # print "\t>>> {} is in root {}".format(child_2, child_2 in root)

            # cur_mx = clusters[parent][St.matrix]
            cur_mxd = clusters[parent][St.matrix_d]
            row_1 = clusters[parent][St.row]

            # ADD HEADER
            # cur_mx[row_1][0] = child_2
            # cur_mx[0][row_1] = child_2

            cur_mxd[(row_1, 0)] = child_2
            cur_mxd[(0, row_1)] = child_2

            # INCREMENT POSITION
            row_1 += 1
            # print "\tPOSITION: {}".format(row_1)
            clusters[parent][St.row] = row_1

            # COPY MATRIX
            # for col in range(1, row_1):
            #     # print cur_mx[0][x], child_1
            #     if cur_mx[0][col] == child_1:
            #         # print "\tFOUND: {} AT POSITION: {}".format(cur_mx[0][col], col)
            #         # print "\tIT WILL BE PRINTED AT: ({}, {})".format(row_1 - 1, col)
            #         # cur_mx[position_1 - 1][x] = 1
            #         cur_mx[row_1 - 1][col] = 1
            #         clusters[root[child_1]][St.annotate] += "\n\tONLY 1 {} HAS A PARENT COMPARED TO {}".format(
            #             child_1, child_2)

            for col in range(1, row_1):
                if (0, col) in cur_mxd and cur_mxd[(0, col)] == child_1:
                    cur_mxd[(row_1 - 1, col)] = 1
                    if annotate:
                        clusters[root[child_1]][St.annotate] += "\n\tONLY 1 {} HAS A PARENT COMPARED TO {}".format(
                            child_1, child_2)

        # 4. ONE CHILD [CHILD 2] HAVE A PARENT OF HIS OWN
        elif has_parent_2 is True:

            # THE CHILD WITH NO PARENT IS ASSIGNED TO THE PARENT OF THE CHILD WITH PARENT
            # print "\n{}:{} | {}:{}".format(child_1, has_parent_1, child_2, has_parent_2)

            parent = root[child_2]
            root[child_1] = parent
            clusters[parent][St.children] += [child_1]
            # print "\t>>> {} is in root {}".format(child_1, child_1 in root)

            # cur_mx = clusters[parent][St.matrix]
            cur_mxd = clusters[parent][St.matrix_d]
            row_2 = clusters[parent][St.row]

            # ADD HEADER
            # print row_2
            # cur_mx[row_2][0] = child_1
            # cur_mx[0][row_2] = child_1

            cur_mxd[(row_2, 0)] = child_1
            cur_mxd[(0, row_2)] = child_1

            # INCREMENT POSITION
            row_2 += 1
            # print "\tPOSITION: {}".format(row_2)
            clusters[parent][St.row] = row_2

            # COPY MATRIX
            # for col in range(1, row_2):
            #     # print cur_mx[0][x], child_1
            #     if cur_mx[0][col] == child_2:
            #         # print "\tFOUND: {} AT POSITION: {}".format(cur_mx[0][col], col)
            #         # print "\tIT WILL BE PRINTED AT: ({}, {})".format(row_2 - 1, col)
            #         # cur_mx[position_2 - 1][x] = 1
            #         cur_mx[row_2 - 1][col] = 1
            #         clusters[root[child_1]][St.annotate] += "\n\tONLY 2 {} HAS A PARENT COMPARED TO {}".format(
            #             child_2, child_1)

            for col in range(1, row_2):
                if (0, col) in cur_mxd and cur_mxd[(0, col)] == child_2:
                    cur_mxd[(row_2 - 1, col)] = 1
                    if annotate:
                        clusters[root[child_1]][St.annotate] += "\n\tONLY 2 {} HAS A PARENT COMPARED TO {}".format(
                            child_2, child_1)

        return counter

    def cluster_helper_set(counter, annotate=False):

        counter += 1
        # child_1 = subject.strip()
        # child_2 = obj.strip()

        child_1 = subject.n3().strip()
        child_2 = obj.n3().strip()

        # DATE CREATION
        date = "{}".format(datetime.datetime.today().strftime(_format))

        # CHECK WHETHER A CHILD HAS A PARENT
        has_parent_1 = True if child_1 in root else False
        has_parent_2 = True if child_2 in root else False
        # print "\n{}|{} Has Parents {}|{}".format(child_1, child_2, has_parent_1, has_parent_2)

        # 1. START BOTH CHILD ARE ORPHANS
        if has_parent_1 is False and has_parent_2 is False:

            # print "\nSTART {}:{} | {}:{}".format(child_1, has_parent_1, child_2, has_parent_2)

            # GENERATE THE PARENT
            hash_value = hash(date + str(count) + graph)
            parent = "{}".format(str(hash_value).replace("-", "N")) if str(
                hash_value).startswith("-") \
                else "P{}".format(hash_value)

            # ASSIGN A PARENT TO BOTH CHILD
            root[child_1] = parent
            root[child_2] = parent


            link = (child_1, child_2) if child_1 < child_2 else (child_2, child_1)
            clusters[parent] = {'nodes': set([child_1, child_2]), 'links': set([link])}

            # print parent, child_1, child_2
            if annotate:
                clusters[parent][St.annotate] = "\n\tSTART {} | {}".format(child_1, child_2)

        # 2. BOTH CHILD HAVE A PARENT OF THEIR OWN
        elif has_parent_1 is True and has_parent_2 is True:

            # 2.1 BOTH CHILD HAVE THE SAME PARENT, DO NOTHING
            if root[child_1] != root[child_2]:

                parent1 = root[child_1]
                parent2 = root[child_2]
                # root2[child_2] = parent1

                if annotate:
                    clusters[parent1][St.annotate] += "\n\tCHOOSE A PARENT {} | {}".format(child_1, child_2)
                # print parent1, parent2

                if parent2 in clusters:
                    # ALL CHILD OF PARENT (SMALL) ARE REASSIGNED A NEW PARENT
                    for child in clusters[parent2]['nodes']: ### check this
                        root[child] = parent1

                    # print 'before', clusters2[parent1]['nodes']
                    clusters[parent1]['nodes'] = clusters[parent1]['nodes'].union(clusters[parent2]['nodes'])
                    clusters[parent1]['links'] = clusters[parent1]['links'].union(clusters[parent2]['links'])
                    # print 'after', clusters2[parent1]['nodes']

                    #add the current link (child_1, child_2)  ### check this
                    link = (child_1, child_2) if child_1 < child_2 else (child_2, child_1)
                    clusters[parent1]['links'].add(link)

                    clusters.pop(parent2)
            else:
                parent = root[child_1]
                link = (child_1, child_2) if child_1 < child_2 else (child_2, child_1)
                clusters[parent]['links'].add(link)
                if annotate:
                    clusters[root[child_1]][St.annotate] += "\n\tSAME PARENTS {} | {}".format(child_1, child_2)

        elif has_parent_1 is True:

            # THE CHILD WITH NO PARENT IS ASSIGNED TO THE PARENT OF THE CHILD WITH PARENT
            # print "\n{}:{} | {}:{}".format(child_1, has_parent_1, child_2, has_parent_2)

            parent = root[child_1]
            root[child_2] = parent

            link = (child_1, child_2) if child_1 < child_2 else (child_2, child_1)
            clusters[parent]['links'].add(link)
            clusters[parent]['nodes'].add(child_2)

            if annotate:
                clusters[parent][St.annotate] += "\n\tONLY 1 {} HAS A PARENT COMPARED TO {}".format(
                            child_1, child_2)

        elif has_parent_2 is True:

            # THE CHILD WITH NO PARENT IS ASSIGNED TO THE PARENT OF THE CHILD WITH PARENT
            # print "\n{}:{} | {}:{}".format(child_1, has_parent_1, child_2, has_parent_2)

            parent = root[child_2]
            root[child_1] = parent

            link = (child_1, child_2) if child_1 < child_2 else (child_2, child_1)
            clusters[parent]['links'].add(link)
            clusters[parent]['nodes'].add(child_1)

            if annotate:
                clusters[parent][St.annotate] += "\n\tONLY 2 {} HAS A PARENT COMPARED TO {}".format(
                            child_2, child_1)

        return counter

    print "2. ITERATING THROUGH THE GRAPH OF SIZE {}".format(len(g))

    standard = 50000
    check = 1
    iteration = 1

    # COMPARING HELPERS
    for subject, predicate, obj in g:

        count = cluster_helper_set(count, annotate=False)
        # count_mtx = cluster_helper_mtx(count_mtx)
        if iteration == check:
            print "\tRESOURCE {:>10}:   {} {}".format(count, subject.n3(), obj)
            check = check + standard
        iteration += 1

    # sizes = set()
    # sizes2 = set()
    # for p, c in clusters.items():
    #     # {St.children: [child_1, child_2], St.matrix: None, St.row: 3, St.matrix_d: mxd}
    #     # print c
    #     mdx = c[St.matrix_d]
    #     countLinks = 0
    #     for x, y in mdx.items():
    #         if y == 1:
    #             countLinks += 1
    #     sizes.add((len(c[St.children]), countLinks))
    # for p, c in clusters2.items():
    #     sizes2.add((len(c['nodes']), len(c['links'])))
    #
    # sizes = sorted(sizes)
    # sizes2 = sorted(sizes2)
    # print 'Clusters sizes:', '\n', sizes, '\n', sizes2

    print "3. NUMBER OF CLUSTER FOUND: {}".format(len(clusters))
    return clusters



# USING SET AND THE TABLE OF RESOURCES AND THEIR STRENGTHS
def links_clustering(graph, limit=1000):

    # ***************************************************************************
    # USING SET OPERATOR FOR GENERATING THE LINK CLUSTERS OF RESOURCES AND ALSO
    # USING TABLE AND NOT TRIPLES AS THE TABLE OF RESOURCES AND THEIR STRENGTHS
    # ***************************************************************************

    # g = [
    #     ("<http://grid.2>", "<http://risis.eu/alignment/predicate/SAMEAS>", "<http://orgref.2>"),
    #     ("<http://leiden.2>", "<http://risis.eu/alignment/predicate/SAMEAS>", "<http://grid.2>"),
    #     ("<http://orgref.2>", "<http://risis.eu/alignment/predicate/SAMEAS>", "<http://orgreg.2>"),
    #     ("<http://orgreg.2> ", "<http://risis.eu/alignment/predicate/SAMEAS>", "<http://h2020.2> "),
    #     ("<http://h2020.2>", "<http://risis.eu/alignment/predicate/SAMEAS>", "<http://eter.2>"),
    #     ("<http://eter.2>", "<http://risis.eu/alignment/predicate/SAMEAS>", "<http://leiden.2>"),
    # ]

    # g = [
    #     ( "<http://grid.2>", "<http://risis.eu/alignment/predicate/SAMEAS>", "<http://orgref.2>"),
    #     ( "<http://eter.2>", "<http://risis.eu/alignment/predicate/SAMEAS>", "<http://leiden.2>"),
    #     ("<http://orgreg.2> ", "<http://risis.eu/alignment/predicate/SAMEAS>", "<http://h2020.2> "),
    #     ( "<http://leiden.2>", "<http://risis.eu/alignment/predicate/SAMEAS>", "<http://grid.2>"),
    #     ("<http://orgref.2>", "<http://risis.eu/alignment/predicate/SAMEAS>", "<http://orgreg.2>"),
    #     ("<http://h2020.2>", "<http://risis.eu/alignment/predicate/SAMEAS>", "<http://eter.2>"),
    # ]

    # g = [
    #     ("<http://risis.eu/leidenRanking_2015/resource/884>", "<http://risis.eu/alignment/predicate/SAMEAS>",
    #      "<http://www.grid.ac/institutes/grid.10493.3f>"),
    #     ("<http://risis.eu/leidenRanking_2015/resource/884>", "<http://risis.eu/alignment/predicate/SAMEAS>",
    #      "<http://risis.eu/eter_2014/resource/DE0056>"),
    #     ("<http://www.grid.ac/institutes/grid.10493.3f> ", "<http://risis.eu/alignment/predicate/SAMEAS>",
    #      "<http://risis.eu/eter_2014/resource/DE0056> ") ]


    # DOWNLOAD THE GRAPH


    # ROOT = KEY:CHILD VALUE:PARENT
    root = dict()
    count = 0
    clusters = dict()

    root_mtx = {}
    # count_mtx = 0
    clusters_mtx = {}

    def merge_d_matrices(parent, pop_parent):

        # COPYING LESSER MATRIX TO BIGGER MATRIX

        index = parent[St.row]
        pop_row = pop_parent[St.row]
        cur_mxd = parent[St.matrix_d]
        pop_mxd = pop_parent[St.matrix_d]
        # position_add = clusters[parent][St.row] - 1

        # print "\tPOSITION: {} | POSITION POP: {}".format(index, pop_row)
        # print "\tADD VALUE: {}".format(position_add)

        # COPY MATRIX
        # print "\tPOP HEADER: {}".format(pop_mx[0][:])
        for row in range(1, pop_row):

            # ADD HEADER IF NOT ALREADY IN
            # print "\tCURRENT HEADER ADDED: {}".format(cur_mx[0:])
            if pop_mxd[(row, 0)] not in cur_mxd:
                pop_item_row = pop_mxd[(row, 0)]
                cur_mxd[(index, 0)] = pop_item_row
                cur_mxd[(0, index)] = pop_item_row
                index += 1
                parent[St.row] = index
                # print "\tHEADER ADDED: {}".format(pop_item_row)

                # FOR THAT HEADER, COPY THE SUB-MATRIX
                for col in range(1, pop_row):

                    # THE HEADER ARE ALREADY IN THERE
                    if (row, col) in pop_mxd and pop_mxd[(row, col)] != 0:
                        # find header in current matrix
                        for col_item in range(1, len(cur_mxd)):
                            if (0, col_item) in cur_mxd and (0, col) in pop_mxd and \
                                            cur_mxd[(0, col_item)] == pop_mxd[(0, col)]:
                                # print "\tIN2 ({}, {})".format(index - 1, col_item)
                                cur_mxd[(index - 1, col_item)] = 1

    def cluster_helper_mtx(counter, annotate=False):

        counter += 1
        child_1 = subject.n3().strip()
        child_2 = obj.n3().strip()
        # child_1 = subject.strip()
        # child_2 = obj.strip()

        # DATE CREATION
        # date = "{}".format(datetime.datetime.today().strftime(_format))

        # CHECK WHETHER A CHILD HAS A PARENT
        has_parent_1 = True if child_1 in root_mtx else False
        has_parent_2 = True if child_2 in root_mtx else False
        # print "\n{}|{} Has Parents {}|{}".format(child_1, child_2, has_parent_1, has_parent_2)

        # 1. START BOTH CHILD ARE ORPHANS
        if has_parent_1 is False and has_parent_2 is False:

            # print "\nSTART {}:{} | {}:{}".format(child_1, has_parent_1, child_2, has_parent_2)

            # GENERATE THE PARENT
            # hash_value = hash(date + str(count) + graph)
            hash_value = hash(child_1 + child_2 + graph)
            parent = "{}".format(str(hash_value).replace("-", "N")) if str(
                hash_value).startswith("-") \
                else "P{}".format(hash_value)

            # ASSIGN A PARENT TO BOTH CHILD
            root[child_1] = parent
            root[child_2] = parent

            # CREATE A CLUSTER
            if parent not in clusters:
                # MATRIX
                # mx = matrix(matrix_size, matrix_size)
                mxd = dict()
                # ROW
                # mx[0][1] = child_1
                # mx[0][2] = child_2

                mxd[(0, 1)] = child_1
                mxd[(0, 2)] = child_2

                # COLUMNS
                # mx[1][0] = child_1
                # mx[2][0] = child_2

                mxd[(1, 0)] = child_1
                mxd[(2, 0)] = child_2

                # RELATION
                # mx[1][2] = 1
                # mx[2][1] = 1
                mxd[(2, 1)] = 1

                clusters[parent] = {St.children: [child_1, child_2], St.matrix: None, St.row: 3, St.matrix_d: mxd}
                if annotate:
                    clusters[parent][St.annotate] = "\n\tSTART {} | {}".format(child_1, child_2)

            # print "\tPOSITION: {}".format(3)
            # print "\tIT WILL BE PRINTED AT: ({}, {})".format(2, 1)

        # 2. BOTH CHILD HAVE A PARENT OF THEIR OWN
        elif has_parent_1 is True and has_parent_2 is True:

            # 2.1 BOTH CHILD HAVE THE SAME PARENT, DO NOTHING
            if root_mtx[child_1] == root_mtx[child_2]:
                # print "CLUSTER SIZE IS {} BUT THERE IS NOTHING TO DO\n".format(len(clusters))
                # print "\nSAME PARENTS {}:{} | {}:{}".format(child_1, has_parent_1, child_2, has_parent_2)
                # cur_mx = clusters[root[child_1]][St.matrix]
                cur_mxd = clusters[root[child_1]][St.matrix_d]

                row_1 = 0
                row_2 = 0

                # FIND ROW
                # row_1 = clusters[root[child_1]][St.row]
                # for row in range(1, clusters[root[child_1]][St.row]):
                #     if cur_mx[row][0] == child_1:
                #         row_1 = row
                #
                # for col in range(1, clusters[root[child_1]][St.row]):
                #     if cur_mx[0][col] == child_2:
                #         row_2 = col

                for row in range(1, clusters[root[child_1]][St.row]):
                    if (row, 0) in cur_mxd and cur_mxd[(row, 0)] == child_1:
                        row_1 = row

                for col in range(1, clusters[root[child_1]][St.row]):
                    if (0, col) in cur_mxd and cur_mxd[(0, col)] == child_2:
                        row_2 = col

                # row_2 = clusters[root[child_2]][St.row]

                # print "\tPOSITIONS: {} | {}".format(row_2, row_1)
                # cur_mx[row_2][row_1] = 1
                cur_mxd[(row_2, row_1)] = 1

                if annotate:
                    clusters[root[child_1]][St.annotate] += "\n\tSAME PARENTS {} | {}".format(child_1, child_2)

                # COPY THE SUB-MATRIX
                # for col in range(1, row_1):
                #     if cur_mx[0][col] == child_2:
                #         print "\tFOUND: {} AT POSITION: {}".format(cur_mx[0][col], col)
                #         print "\tIT WILL BE PRINTED AT: ({}, {})".format(row_1 - 1, col)
                #         cur_mx[row_1 - 1][col] = 1

                # continue
                return counter

            # THE PARENT WITH THE MOST CHILD GET THE CHILD OF THE OTHER PARENT
            # fFETCHING THE RESOURCES IN THE CLUSTER (CHILDREN)
            # print "\n{}:{} | {}:{}".format(child_1, has_parent_1, child_2, has_parent_2)

            children_1 = (clusters_mtx[root_mtx[child_1]])[St.children]
            children_2 = (clusters_mtx[root_mtx[child_2]])[St.children]

            # 2.2 CHOOSE A PARENT
            if len(children_1) >= len(children_2):
                # print "\tPARENT 1"
                parent = root_mtx[child_1]
                pop_parent = root_mtx[child_2]
                # root[child_2] = parent

            else:
                # print "\tPARENT 2"
                parent = root_mtx[child_2]
                pop_parent = root_mtx[child_1]
                # root[child_1] = parent

            # ALL CHILD OF PARENT (SMALL) ARE REASSIGNED A NEW PARENT
            for offspring in clusters_mtx[pop_parent][St.children]:
                root_mtx[offspring] = parent
                clusters_mtx[parent][St.children] += [offspring]

            # MERGE CURRENT WITH LESSER (CHILDREN) MATRICES, ANNOTATE AND POOP LESSER (CHILDREN) MATRICES
            merge_d_matrices(clusters_mtx[parent], clusters_mtx[pop_parent])

            if annotate:
                clusters_mtx[parent][St.annotate] += "\n\tCHOOSE A PARENT {} | {}".format(child_1, child_2)
            cluster_helper_mtx(count)
            # cluster_helper(count)

            # COPYING LESSER MATRIX TO BIGGER MATRIX
            # index = clusters[parent][St.row]
            # pop_row = clusters[pop_parent][St.row]
            # cur_mx = clusters[parent][St.matrix]
            # pop_mx = clusters[pop_parent][St.matrix]
            # # position_add = clusters[parent][St.row] - 1
            #
            # print "\tPOSITION: {} | POSITION POP: {}".format(index, pop_row)
            # # print "\tADD VALUE: {}".format(position_add)
            #
            # # # ADD HEADER
            # # for x in range(1, pop_index):
            # #     cur_mx[0][index - 1 + x] = pop_mx[0][x]
            # #     cur_mx[index - 1 + x][0] = pop_mx[0][x]
            # #     clusters[parent][St.row] += 1
            #
            # # COPY MATRIX
            # print "\tPOP HEADER: {}".format(pop_mx[0][:])
            # for row in range(1, pop_row):
            #
            #     # ADD HEADER IF NOT ALREADY IN
            #     # print "\tCURREENT HEADER ADDED: {}".format(cur_mx[0:])
            #     if pop_mx[row][0] not in cur_mx[0:]:
            #         pop_item_row = pop_mx[row][0]
            #         cur_mx[index][0] = pop_item_row
            #         cur_mx[0][index] = pop_item_row
            #         index += 1
            #         clusters[parent][St.row] = index
            #         print "\tHEADER ADDED: {}".format(pop_item_row)
            #
            #
            #         # FOR THAT HEADER, COPY THE SUB-MATRIX
            #         for col in range(1, pop_row):
            #
            #             # THE HEADER IS NOT IN
            #             if pop_mx[row][col] != 0 and pop_mx[row][0] not in cur_mx[1:-1]:
            #                 print "\tIN ({}, {})".format(index-1, col )
            #                 # index += 1
            #                 # clusters[parent][St.row] = index
            #
            #             # THE HEADER ARE ALREADY IN THERE
            #             if pop_mx[row][col] != 0:
            #                 # find header in current matrix
            #                 for col_item in range(1, len(cur_mx[1:-1])):
            #                     if cur_mx[0][col_item] == pop_mx[0][col]:
            #                         print "\tIN2 ({}, {})".format(index-1, col_item)
            # cur_mx[row + position_add][col + position_add] = pop_mx[row][col]

            # cur_mx[0][position_add+ row] = pop_mx[row][0]

            # cur_mx[y + position_add][x + position_add] = pop_mx[y][x]

            # POP THE PARENT WITH THE LESSER CHILD

            if annotate:
                clusters_mtx[parent][St.annotate] += clusters_mtx[pop_parent][St.annotate]
            clusters_mtx.pop(pop_parent)

        # 3. ONE CHILD [CHILD 1] HAVE A PARENT OF HIS OWN
        elif has_parent_1 is True:

            # THE CHILD WITH NO PARENT IS ASSIGNED TO THE PARENT OF THE CHILD WITH PARENT
            # print "\n{}:{} | {}:{}".format(child_1, has_parent_1, child_2, has_parent_2)

            parent = root[child_1]
            root[child_2] = parent
            clusters[parent][St.children] += [child_2]
            # print "\t>>> {} is in root {}".format(child_2, child_2 in root)

            # cur_mx = clusters[parent][St.matrix]
            cur_mxd = clusters[parent][St.matrix_d]
            row_1 = clusters[parent][St.row]

            # ADD HEADER
            # cur_mx[row_1][0] = child_2
            # cur_mx[0][row_1] = child_2

            cur_mxd[(row_1, 0)] = child_2
            cur_mxd[(0, row_1)] = child_2

            # INCREMENT POSITION
            row_1 += 1
            # print "\tPOSITION: {}".format(row_1)
            clusters[parent][St.row] = row_1

            # COPY MATRIX
            # for col in range(1, row_1):
            #     # print cur_mx[0][x], child_1
            #     if cur_mx[0][col] == child_1:
            #         # print "\tFOUND: {} AT POSITION: {}".format(cur_mx[0][col], col)
            #         # print "\tIT WILL BE PRINTED AT: ({}, {})".format(row_1 - 1, col)
            #         # cur_mx[position_1 - 1][x] = 1
            #         cur_mx[row_1 - 1][col] = 1
            #         clusters[root[child_1]][St.annotate] += "\n\tONLY 1 {} HAS A PARENT COMPARED TO {}".format(
            #             child_1, child_2)

            for col in range(1, row_1):
                if (0, col) in cur_mxd and cur_mxd[(0, col)] == child_1:
                    cur_mxd[(row_1 - 1, col)] = 1
                    if annotate:
                        clusters[root[child_1]][St.annotate] += "\n\tONLY 1 {} HAS A PARENT COMPARED TO {}".format(
                            child_1, child_2)

        # 4. ONE CHILD [CHILD 2] HAVE A PARENT OF HIS OWN
        elif has_parent_2 is True:

            # THE CHILD WITH NO PARENT IS ASSIGNED TO THE PARENT OF THE CHILD WITH PARENT
            # print "\n{}:{} | {}:{}".format(child_1, has_parent_1, child_2, has_parent_2)

            parent = root[child_2]
            root[child_1] = parent
            clusters[parent][St.children] += [child_1]
            # print "\t>>> {} is in root {}".format(child_1, child_1 in root)

            # cur_mx = clusters[parent][St.matrix]
            cur_mxd = clusters[parent][St.matrix_d]
            row_2 = clusters[parent][St.row]

            # ADD HEADER
            # print row_2
            # cur_mx[row_2][0] = child_1
            # cur_mx[0][row_2] = child_1

            cur_mxd[(row_2, 0)] = child_1
            cur_mxd[(0, row_2)] = child_1

            # INCREMENT POSITION
            row_2 += 1
            # print "\tPOSITION: {}".format(row_2)
            clusters[parent][St.row] = row_2

            # COPY MATRIX
            # for col in range(1, row_2):
            #     # print cur_mx[0][x], child_1
            #     if cur_mx[0][col] == child_2:
            #         # print "\tFOUND: {} AT POSITION: {}".format(cur_mx[0][col], col)
            #         # print "\tIT WILL BE PRINTED AT: ({}, {})".format(row_2 - 1, col)
            #         # cur_mx[position_2 - 1][x] = 1
            #         cur_mx[row_2 - 1][col] = 1
            #         clusters[root[child_1]][St.annotate] += "\n\tONLY 2 {} HAS A PARENT COMPARED TO {}".format(
            #             child_2, child_1)

            for col in range(1, row_2):
                if (0, col) in cur_mxd and cur_mxd[(0, col)] == child_2:
                    cur_mxd[(row_2 - 1, col)] = 1
                    if annotate:
                        clusters[root[child_1]][St.annotate] += "\n\tONLY 2 {} HAS A PARENT COMPARED TO {}".format(
                            child_2, child_1)

        return counter

    def cluster_helper_set(counter, annotate=False):

        counter += 1
        # child_1 = subject.strip()
        # child_2 = obj.strip()

        child_1 = subject.strip()
        child_2 = object.strip()
        child_1 = child_1 if Ut.is_nt_format(child_1) else "<{}>".format(child_1)
        child_2 = child_2 if Ut.is_nt_format(child_2) else "<{}>".format(child_2)

        # DATE CREATION
        date = "{}".format(datetime.datetime.today().strftime(_format))

        # CHECK WHETHER A CHILD HAS A PARENT
        has_parent_1 = True if child_1 in root else False
        has_parent_2 = True if child_2 in root else False
        # print "\n{}|{} Has Parents {}|{}".format(child_1, child_2, has_parent_1, has_parent_2)

        # *******************************************
        # 1. START BOTH CHILD ARE ORPHANS
        # *******************************************
        if has_parent_1 is False and has_parent_2 is False:

            # print "\nSTART {}:{} | {}:{}".format(child_1, has_parent_1, child_2, has_parent_2)

            # GENERATE THE PARENT
            hash_value = hash(date + str(count) + graph)
            parent = "{}".format(str(hash_value).replace("-", "N")) if str(
                hash_value).startswith("-") \
                else "P{}".format(hash_value)

            # ASSIGN A PARENT TO BOTH CHILD
            root[child_1] = parent
            root[child_2] = parent

            # THE SUBJECT AND OBJECT LINK
            link = (child_1, child_2) if child_1 < child_2 else (child_2, child_1)

            # THE CLUSTER COMPOSED OF NODES, LINKS AND STRENGTHS
            clusters[parent] = {'nodes': set([child_1, child_2]), 'links': set([link]), 'strengths': {link: strength}}
            # print "1",clusters[parent]

            # print parent, child_1, child_2
            if annotate:
                clusters[parent][St.annotate] = "\n\tSTART {} | {}".format(child_1, child_2)

        # *******************************************
        # 2. BOTH CHILD HAVE A PARENT OF THEIR OWN
        # *******************************************
        elif has_parent_1 is True and has_parent_2 is True:

            # 2.1 BOTH CHILD HAVE THE SAME PARENT, DO NOTHING
            if root[child_1] != root[child_2]:

                parent1 = root[child_1]
                parent2 = root[child_2]
                # root2[child_2] = parent1

                if annotate:
                    clusters[parent1][St.annotate] += "\n\tCHOOSE A PARENT {} | {}".format(child_1, child_2)
                # print parent1, parent2

                if parent2 in clusters:
                    # ALL CHILD OF PARENT (SMALL) ARE REASSIGNED A NEW PARENT
                    for child in clusters[parent2]['nodes']: ### check this
                        root[child] = parent1

                    # print 'before', clusters2[parent1]['nodes']
                    # RE-ASSIGNING THE NODES OF CHILD 2
                    clusters[parent1]['nodes'] = clusters[parent1]['nodes'].union(clusters[parent2]['nodes'])
                    # RE-ASSIGNING THE LINKS OF CHILD 2

                    clusters[parent1]['links'] = clusters[parent1]['links'].union(clusters[parent2]['links'])

                    # RE-ASSIGNING THE STRENGTHS OF CHILD 2
                    for key, link_strengths in clusters[parent2]['strengths'].items():
                        if key not in clusters[parent1]['strengths']:
                            clusters[parent1]['strengths'][key] = link_strengths
                        else:
                            clusters[parent1]['strengths'][key] += link_strengths

                    # print 'after', clusters2[parent1]['nodes']

                    #add the current link (child_1, child_2)  ### check this
                    link = (child_1, child_2) if child_1 < child_2 else (child_2, child_1)
                    clusters[parent1]['links'].add(link)

                    if link in clusters[parent1]['strengths']:
                        clusters[parent1]['strengths'][link] += strength
                    else:
                        clusters[parent1]['strengths'][link] = strength

                    clusters.pop(parent2)
            else:
                parent = root[child_1]
                link = (child_1, child_2) if child_1 < child_2 else (child_2, child_1)
                clusters[parent]['links'].add(link)

                if link in clusters[parent]['strengths']:
                    clusters[parent]['strengths'][link] += strength
                else:
                    clusters[parent]['strengths'][link] = strength

                if annotate:
                    clusters[root[child_1]][St.annotate] += "\n\tSAME PARENTS {} | {}".format(child_1, child_2)

        # *******************************************
        # 3. BOTH CHILD HAVE DIFFERENT PARENTS
        # *******************************************
        elif has_parent_1 is True:

            # THE CHILD WITH NO PARENT IS ASSIGNED TO THE PARENT OF THE CHILD WITH PARENT
            # print "\n{}:{} | {}:{}".format(child_1, has_parent_1, child_2, has_parent_2)

            parent = root[child_1]
            root[child_2] = parent

            link = (child_1, child_2) if child_1 < child_2 else (child_2, child_1)
            clusters[parent]['links'].add(link)
            clusters[parent]['nodes'].add(child_2)

            if link in clusters[parent]['strengths']:
                clusters[parent]['strengths'][link] += strength
            else:
                clusters[parent]['strengths'][link] = strength

            if annotate:
                clusters[parent][St.annotate] += "\n\tONLY 1 {} HAS A PARENT COMPARED TO {}".format(
                            child_1, child_2)

        # *******************************************
        # 4. BOTH CHILD HAVE DIFFERENT PARENTS
        # *******************************************
        elif has_parent_2 is True:

            # THE CHILD WITH NO PARENT IS ASSIGNED TO THE PARENT OF THE CHILD WITH PARENT
            # print "\n{}:{} | {}:{}".format(child_1, has_parent_1, child_2, has_parent_2)

            parent = root[child_2]
            root[child_1] = parent

            link = (child_1, child_2) if child_1 < child_2 else (child_2, child_1)
            clusters[parent]['links'].add(link)
            clusters[parent]['nodes'].add(child_1)


            if link in clusters[parent]['strengths']:
                clusters[parent]['strengths'][link] += strength
            else:
                clusters[parent]['strengths'][link] = strength

            if annotate:
                clusters[parent][St.annotate] += "\n\tONLY 2 {} HAS A PARENT COMPARED TO {}".format(
                            child_2, child_1)

        return counter

    # *******************************************
    # RUN THE LINK CLUSTER
    # *******************************************
    standard = 50000
    check = 1
    iteration = 1

    print "\n1. DOWNLOADING THE GRAPH FROM THE TRIPLE STORE"
    data = Qry.get_cluster_rsc_strengths(resources=None, alignments=graph)

    print "2. ITERATING THROUGH THE GRAPH OF SIZE {}".format(len(data))
    for (subject, object), strength in data.items():

        # CALLING THE MAIN HELPER FUNCTION
        count = cluster_helper_set(count, annotate=False)

        # PRINTING THE CREATED CLUSTERS ON THE SERVER SCREEN
        if iteration == check:
            print "\tRESOURCE {:>10}:   {} {}".format(count, subject, object)
            check = check + standard
        iteration += 1
        # print strength
        # break

    # COMPARING HELPERS
    # for subject, predicate, obj in g:
    #
    #     count = cluster_helper_set(count, annotate=False)
    #     # count_mtx = cluster_helper_mtx(count_mtx)
    #     if iteration == check:
    #         print "\tRESOURCE {:>10}:   {} {}".format(count, subject.n3(), obj)
    #         check = check + standard
    #     iteration += 1

    # sizes = set()
    # sizes2 = set()
    # for p, c in clusters.items():
    #     # {St.children: [child_1, child_2], St.matrix: None, St.row: 3, St.matrix_d: mxd}
    #     # print c
    #     mdx = c[St.matrix_d]
    #     countLinks = 0
    #     for x, y in mdx.items():
    #         if y == 1:
    #             countLinks += 1
    #     sizes.add((len(c[St.children]), countLinks))
    # for p, c in clusters2.items():
    #     sizes2.add((len(c['nodes']), len(c['links'])))
    #
    # sizes = sorted(sizes)
    # sizes2 = sorted(sizes2)
    # print 'Clusters sizes:', '\n', sizes, '\n', sizes2

    print "3. NUMBER OF CLUSTER FOUND: {}".format(len(clusters))
    return clusters
