import datetime
import rdflib
import Alignments.UserActivities.ExportAlignment as Exp

_format = "%a %b %d %H:%M:%S:%f %Y"


def cluster(input):

    count = 0
    clusters = dict()
    root = dict()

    for pair in input:

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

        if (has_parent_1 is False and has_parent_2 is False):

            # GENERATE THE PARENT
            hash_value = hash(date + str(count))
            parent = "_{}".format(str(hash_value).replace("-","N")) if str(hash_value).startswith("-") \
                else "_P{}".format(hash_value)

            # ASSIGN A PARENT TO BOTH CHILD
            root[child_1] = parent
            root[child_2 ] = parent

            # CREATE A CLUSTER
            if parent not in clusters:
                clusters[parent] = [child_1, child_2 ]

        elif (has_parent_1 is True and has_parent_2 is True):

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
            root[child_2 ] = parent
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
        child_1 = subject
        child_2 = obj
        parent = ""

        # DATE CREATION
        date = "{}".format(datetime.datetime.today().strftime(_format))

        # CHECK WHETHER A CHILD HAS A PARENT
        has_parent_1 = True if child_1 in root else False
        has_parent_2 = True if child_2 in root else False

        # print "{}|{} Has Parents {}|{}".format(child_1, child_2, has_parent_1, has_parent_2)

        if has_parent_1 is False and has_parent_2 is False:

            # GENERATE THE PARENT
            hash_value = hash(date + str(count))
            parent = "_{}".format(str(hash_value).replace("-", "N")) if str(hash_value).startswith("-") \
                else "_P{}".format(hash_value)

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


# test = [('x','y'), ('x','B'), ('w','B'), ('x','w'), ('e','d'), ('e','y'),
# ('s', 'w'),('a','b'),('h','j'),('k','h'),('k','s'),('s','a')]
# clus= cluster(test)
# for key, value in clus.items():
#     print "{} {}".format(key, value)


# test = cluster_triples("http://risis.eu/linkset/subset_openAire_20170816_openAire_20170816_"
#                        "embededAlignment_Organization_sameAs_P541043043")
# for key, value in test.items():
#     if len(value) > 8:
#         print "{}\t{}".format(key, len(value))
#     # exit(0)
