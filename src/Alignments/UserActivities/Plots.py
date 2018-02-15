import os
import datetime
import networkx as nx
import cStringIO as Buffer
import Alignments.Query as Qry
import Alignments.Utility as Ut
import Alignments.Settings as St
import Alignments.NameSpace as Ns
# import matplotlib.pyplot as plt
import math
import Alignments.UserActivities.Clustering as Cls


def sigmoid(x):
    # return math.exp(x)/ (math.exp(x) + 1)
    # return x / float(math.fabs(x) + 1)
    # return math.exp(x) / (math.exp(x) + 10)
    return x / float(math.fabs(x) + 1.6)


# DRAWING THE NETWORK WITH MATPLOT
def draw_graph(graph, file_path=None, show_image=False):

    import matplotlib.pyplot as plt
    # https://networkx.github.io/documentation/latest/auto_examples/drawing/
    # plot_node_colormap.html#sphx-glr-auto-examples-drawing-plot-node-colormap-py
    # extract nodes from graph
    # print "GRAPH:", graph
    analysis_builder = Buffer.StringIO()
    analysis_builder_2 = Buffer.StringIO()
    nodes = set([n1 for n1, n2 in graph] + [n2 for n1, n2 in graph])

    # create networkx graph
    g = nx.Graph()

    # add nodes
    for node in nodes:
        g.add_node(node)

    # add edges
    for edge in graph:
        g.add_edge(edge[0], edge[1])

    # draw graph
    # pos = nx.shell_layout(g)
    # print edge_count
    colors = range(len(graph))
    pos = nx.spring_layout(g)
    try:
        nx.draw(g, pos, with_labels=True, font_weight='bold', node_size=800, edge_color=colors, width=2)
    except Exception as error:
        "{}".format(error)
        nx.draw(g, pos, with_labels=True, font_weight='bold', node_size=800, edge_color="b", width=2)

    # d_centrality = nx.degree_centrality(g)
    # b_centrality = nx.edge_betweenness_centrality(g)
    # G = nx.connectivity.build_auxiliary_node_connectivity(G)
    # cycles = nx.cycle_basis(G)
    # cycles = nx.simple_cycles(G)
    # cycles = list(nx.simple_cycles(g.to_directed()))
    # nbr_cycles = len(list(filter(lambda x: len(x) > 2, cycles)))/2
    # biggest_ring = reduce((lambda x, y: x if len(x) > len(y) else y), cycles)

    """""""""""""""""""""""""""""""""""""""
    MATRIX COMPUTATIONS
    """""""""""""""""""""""""""""""""""""""
    ratio = 0
    bridges = 0
    closure = 0
    diameter = 0
    nb_used = 0
    nd_used = 0
    edge_discovered = 0
    edge_derived = 0
    interpretation = 0
    estimated_quality = 0
    average_node_connectivity = 0
    normalised_diameter = 0
    normalised_bridge = 0
    normalised_closure = 0

    try:
        node_count = len(nodes)
        average_node_connectivity = nx.average_node_connectivity(g)
        ratio = average_node_connectivity / (len(nodes) - 1)

        edge_discovered = len(graph)
        edge_derived = node_count * (node_count - 1) / 2

        diameter = nx.diameter(g)  # / float(node_count - 1)
        if len(nodes) > 2:
            normalised_diameter = round((float(diameter - 1) / float(len(nodes) - 2)), 3)
        else:
            normalised_diameter = float(diameter - 1)

        bridges = len(list(nx.bridges(g)))
        normalised_bridge = round(float(bridges / float(len(nodes) - 1)), 3)

        closure = round(float(edge_discovered) / float(edge_derived), 3)
        normalised_closure = round(1 - closure, 2)

        # conclusion = round((normalised_closure * normalised_diameter + normalised_bridge) / 2, 3)
        interpretation = round((normalised_closure + normalised_diameter + normalised_bridge) / 3, 3)

        nb_used = round(sigmoid(bridges) if sigmoid(bridges) > normalised_bridge else normalised_bridge, 3)
        nd_used = round(sigmoid(diameter - 1)
                        if sigmoid(diameter - 1) > normalised_diameter else normalised_diameter, 3)
        estimated_quality = round((nb_used + nd_used + normalised_closure) / float(3), 3)

    except Exception as error:
        print "There was a problem:\n{}".format(error.message)

    """""""""""""""""""""""""""""""""""""""
    RETURN MATRIX COMPUTATIONS
    """""""""""""""""""""""""""""""""""""""
    analysis_builder.write("\n\nNETWORK ANALYSIS")
    analysis_builder.write("\n\tNETWORK {}".format(graph))
    analysis_builder.write("\n\t{:31} : {}".format("MAX DISTANCE:", closure))
    analysis_builder.write("\n\t{:31} : {}".format("MAXIMUM POSSIBLE CONNECTIVITY", len(nodes) - 1))
    analysis_builder.write("\n\t{:31} : {}".format("AVERAGE NODE CONNECTIVITY", average_node_connectivity))
    analysis_builder.write("\n\t{:31} : {}".format("AVERAGE NODE CONNECTIVITY RATIO", ratio))
    analysis_builder.write("\n\t{:31} : {}".format("BRIDGES", bridges))
    analysis_builder.write("\n\t{:31} : {}".format("CLOSURE", closure))
    analysis_builder.write("\n\t{:31} : {}".format("DIAMETER", diameter))
    analysis_builder.write("\n\t{:31} : {}".format("QUALITY", interpretation))
    analysis_builder.write("\n\t{:31} : {}".format("QUALITY USED", estimated_quality))
    analysis_builder.write("\n\tSUMMARY 1: BRIDGE {} CLOSURE {} DIAMETER {} QUALITY {} QUALITY USED {}".format(
        normalised_bridge, normalised_closure, normalised_diameter, interpretation, estimated_quality))
    analysis_builder.write("\n\tSUMMARY 2: BRIDGE {} CLOSURE {} DIAMETER {} QUALITY {} QUALITY USED {}".format(
        nb_used, normalised_closure, nd_used, interpretation, estimated_quality))


    """""""""""""""""""""""""""""""""""""""
    PRINTING MATRIX COMPUTATIONS IN PLOT
    """""""""""""""""""""""""""""""""""""""
    analysis_builder_2.write(
        "\nMETRICS READING: THE CLOSER TO ZERO, THE BETTER"
        "\n\nAverage Degree [{}] \nBridges [{}] normalised to [{}] [{}]\nDiameter [{}]  normalised to [{}] [{}]"
        "\nClosure [{}/{}][{}] normalised to [{}]\n\n>>> Decision Support [{}] [{}] <<<".format(
            average_node_connectivity, bridges, normalised_bridge, nb_used, diameter, normalised_diameter,
            nd_used, edge_discovered, edge_derived, closure, normalised_closure, interpretation, estimated_quality))

    if estimated_quality <= 0.1:
        analysis_builder_2.write("\n\nInterpretation: GOOD")

    elif bridges == 0 and diameter <= 2:
        analysis_builder_2.write("ACCEPTABLE")

    elif ((estimated_quality > 0.1) and (estimated_quality < 0.25)) or (bridges == 0):
        analysis_builder_2.write("\n\nInterpretation: UNCERTAIN")

    else:
        analysis_builder_2.write("\n\nInterpretation: THE NETWORK IS NOT A GOOD REPRESENTATION OF A SINGLE RESOURCE")

    if bridges > 0:
        analysis_builder_2.write("\n\nEvidence: NEED BRIDGE INVESTIGATION")

    if diameter > 2:
        analysis_builder_2.write("\n\nEvidence: TOO MANY INTERMEDIATES")

    if bridges == 0 and diameter <= 2:
        analysis_builder_2.write("\n\nEvidence: LESS INTERMEDIATES AND NO BRIDGE")

    """""""""""""""""""""""""""""""""""""""
    DRAWING THE NETWORK WITH MATPLOTLIB
    """""""""""""""""""""""""""""""""""""""
    if file_path:
        plt.title("LINKED RESOURCES NETWORK TOPOLOGY ANALYSIS\n{}".format(analysis_builder_2.getvalue()))
        # plt.legend("TEXT")
        # plt.text(-1.3, 1, "NETWORK ANALYSIS")
        # plt.show()
        plt.xlim(-1.9, 1.9)
        plt.ylim(-1.9, 1.9)
        plt.savefig(file_path, dpi=100, bbox_inches="tight", pad_inches=1, edgecolor='r')
        plt.close()

    if show_image:
        plt.show()

    return analysis_builder.getvalue()


# METRIC DESCRIBING THE QUALITY OF A LINKED NETWORK
def metric(graph):

    # THE GRAPH IN AN ARRAY OF TUPLE
    # WHERE THE TUPLE IS A SET OF NODES IN A BINARY RELATIONSHIP
    # network += [(r_name, c_name)]

    analysis_builder = Buffer.StringIO()
    nodes = set([n1 for n1, n2 in graph] + [n2 for n1, n2 in graph])

    # create networkx graph
    g = nx.Graph()

    # add nodes
    for node in nodes:
        g.add_node(node)

    # add edges
    for edge in graph:
        g.add_edge(edge[0], edge[1])

    """""""""""""""""""""""""""""""""""""""
    MATRIX COMPUTATIONS
    """""""""""""""""""""""""""""""""""""""

    node_count = len(nodes)
    average_node_connectivity = nx.average_node_connectivity(g)
    # ratio = average_node_connectivity / (len(nodes) - 1)

    edge_discovered = len(graph)
    edge_derived = node_count * (node_count - 1) / 2

    diameter = nx.diameter(g)  # / float(node_count - 1)
    if len(nodes) > 2:
        normalised_diameter = round((float(diameter - 1) / float(len(nodes) - 2)), 3)
    else:
        normalised_diameter = float(diameter - 1)

    bridges = len(list(nx.bridges(g)))
    normalised_bridge = round(float(bridges / float(len(nodes) - 1)), 3)

    closure = round(float(edge_discovered) / float(edge_derived), 3)
    normalised_closure = round(1 - closure, 2)

    # conclusion = round((normalised_closure * normalised_diameter + normalised_bridge) / 2, 3)
    interpretation = round((normalised_closure + normalised_diameter + normalised_bridge) / 3, 3)

    nb_used = round(sigmoid(bridges) if sigmoid(bridges) > normalised_bridge else normalised_bridge, 3)
    nd_used = round(sigmoid(diameter - 1) if sigmoid(diameter - 1) > normalised_diameter else normalised_diameter, 3)
    estimated_quality = round((nb_used + nd_used + normalised_closure) / float(3), 3)

    """""""""""""""""""""""""""""""""""""""
    PRINTING MATRIX COMPUTATIONS
    """""""""""""""""""""""""""""""""""""""
    analysis_builder.write(
        "\nMETRICS READING: THE CLOSER TO ZERO, THE BETTER\n"
        "\n\tAverage Degree [{}] \nBridges [{}] normalised to [{}] {}\nDiameter [{}]  normalised to [{}] {}"
        "\nClosure [{}/{}][{}] normalised to [{}]\n\n>>> Decision Support [{}] {} <<<".
        format(average_node_connectivity, bridges, normalised_bridge, nb_used,
               diameter, normalised_diameter, nd_used,
               edge_discovered, edge_derived, closure, normalised_closure, interpretation, estimated_quality))

    # if ratio == 1:
    #     analysis_builder.write("\n\nDiagnose: VERY GOOD")
    # elif average_node_connectivity == 2 or bridges == 0:
    #     analysis_builder.write("\n\nDiagnose: ACCEPTABLE")
    # elif bridges > 0:
    #     analysis_builder.write("\n\nDiagnose : NEED BRIDGE INVESTIGATION")

    if estimated_quality <= 0.1:
        analysis_builder.write("\n\nInterpretation: GOOD")
        auto_decision = "GOOD [{}]".format(estimated_quality)

    elif (bridges == 0) and (diameter < 3):
        analysis_builder.write("ACCEPTABLE")
        auto_decision = "ACCEPTABLE [{}]".format(estimated_quality)

    elif ((estimated_quality > 0.1) and (estimated_quality < 0.25)) or (bridges == 0):
        analysis_builder.write("\n\nInterpretation: UNCERTAIN")
        auto_decision = "UNCERTAIN [{}]".format(estimated_quality)

    else:
        analysis_builder.write("\n\nInterpretation: THE NETWORK IS NOT A GOOD REPRESENTATION OF A SINGLE RESOURCE")
        auto_decision = "BAD [{}]".format(estimated_quality)

    if bridges > 0:
        analysis_builder.write("\n\nEvidence: NEED BRIDGE INVESTIGATION")

    if diameter > 2:
        analysis_builder.write("\n\nEvidence:  TOO MANY INTERMEDIATES")

    if bridges == 0 and diameter <= 2:
        analysis_builder.write("\n\nEvidence:  LESS INTERMEDIATES AND NO BRIDGE")

    return {'message': analysis_builder.getvalue(), 'decision':estimated_quality, 'AUTOMATED_DECISION': auto_decision}


def eval_sheet(targets, count, smallest_hash, a_builder, alignment, children, automated_decision):
    first = False
    a_builder.write("\n{:<5}\t{:<20}{:12}{:20}{:23}{:23}".format(count, smallest_hash, "", "", automated_decision, ""))
    if targets is None:
        a_builder.write(Cls.disambiguate_network(alignment, children))
    else:
        response = Cls.disambiguate_network_2(children, targets, output=False)
        if response:
            temp = ""
            dataset = ""
            # for line in response:
            #     print line

            for i in range(1, len(response)):
                resource = Ut.get_uri_local_name(response[i][0])
                if i == 1:
                    temp = "{:25}: {}".format(resource, response[i][1])

                elif dataset == response[i][0]:
                    temp = "{:25} | {}".format(temp, response[i][1])

                else:
                    if first is False:
                        a_builder.write("  {}\n".format(temp))
                    else:
                        a_builder.write("{:108}{}\n".format("", temp))
                    first = True

                    temp = "{:25}: {}".format(resource, response[i][1])

                dataset = response[i][0]
            a_builder.write("{:108}{}\n".format("", temp))


def cluster_d_test(linkset, network_size=3, targets=None,
                   directory=None, greater_equal=True, print_it=False, limit=None, activated=False):
    network = []
    print "LINK NETWORK INVESTIGATION"
    if activated is False:
        print "\tTHE FUNCTION I NOT ACTIVATED"
        return ""
    date = datetime.date.isoformat(datetime.date.today()).replace('-', '')
    linkset_name = Ut.get_uri_local_name(linkset)
    count_1 = 0
    count_2 = 0
    sheet_builder = Buffer.StringIO()
    analysis_builder = Buffer.StringIO()
    sheet_builder.write("Count	ID					STRUCTURE	E-STRUCTURE-SIZE	A. NETWORK QUALITY"
                        "		M. NETWORK QUALITY		REFERENCE\n")
    linkset = linkset.strip()
    check = False

    # RUN THE CLUSTER
    clusters_0 = Cls.links_clustering(linkset, limit)

    for i_cluster in clusters_0.items():

        # network = []
        resources = ""
        uri_size = 0
        count_1 += 1
        children = i_cluster[1][St.children]
        cluster_size = len(children)
        # if "<http://www.grid.ac/institutes/grid.10493.3f>" not in children:
        #     continue

        check = cluster_size >= network_size if greater_equal else cluster_size == network_size

        # NETWORK OF A PARTICULAR SIZE
        if check:
            count_2 += 1
            # file_name = i_cluster[0]

            # 2: FETCHING THE CORRESPONDENTS
            smallest_hash = float('inf')
            child_list = ""
            for child in children:
                hashed = hash(child)
                if hashed <= smallest_hash:
                    smallest_hash = hashed

                # GENERAL INFO 1: RESOURCES INVOLVED
                child_list += "\t{}\n".format(child)

                use = "<{}>".format(child) if Ut.is_nt_format(child) is not True else child
                resources += "\n\t\t\t\t{}".format(use)
                if len(child) > uri_size:
                    uri_size = len(child)

            if directory:
                # MAKE SURE THE FILE NAME OF THE CLUSTER IS ALWAYS THE SAME
                file_name = "{}".format(str(smallest_hash).replace("-", "N")) if str(
                    smallest_hash).startswith("-") \
                    else "P{}".format(smallest_hash)

                # QUERY FOR FETCHING ALL LINKED RESOURCES FROM THE LINKSET
                query = """
                PREFIX prov: <{3}>
                PREFIX ll: <{4}>
                SELECT DISTINCT ?lookup ?object ?Strength ?Evidence
                {{
                    VALUES ?lookup{{ {0} }}

                    {{
                        GRAPH <{1}>
                        {{ ?lookup ?predicate ?object .}}
                    }} UNION
                    {{
                        GRAPH <{1}>
                        {{?object ?predicate ?lookup . }}
                    }}

                    GRAPH <{2}>
                    {{
                        ?predicate  prov:wasDerivedFrom  ?DerivedFrom  .
                        OPTIONAL {{ ?DerivedFrom  ll:hasStrength  ?Strength . }}
                        OPTIONAL {{ ?DerivedFrom  ll:hasEvidence  ?Evidence . }}
                    }}
                }}
                            """.format(resources, linkset, linkset.replace("lens", "singletons"),
                                       Ns.prov, Ns.alivocab)
                # print query

                # THE RESULT OF THE QUERY ABOUT THE LINKED RESOURCES
                response = Qry.sparql_xml_to_matrix(query)

                # A DICTIONARY OF KEY: (SUBJECT-OBJECT) VALUE:STRENGTH
                response_dic = dict()
                result = response[St.result]
                if result:
                    for i in range(1, len(result)):
                        key = (result[i][0], result[i][1])
                        if key not in response_dic:
                            response_dic[key] = result[i][2]

                # print response_dic

                # GENERAL INFO 2:
                info = "SIZE    {}   \nCLUSTER {} \nNAME    {}\n".format(cluster_size, count_1, file_name)
                info2 = "CLUSTER [{}] NAME [{}] SIZE [{}]".format(count_1, file_name, cluster_size)
                analysis_builder.write("{}\n".format(info))
                print "{:>5} {}".format(count_2, info2)

                analysis_builder.write("RESOURCES INVOLVED\n")
                analysis_builder.write(child_list)
                analysis_builder.write("\nCORRESPONDENT FOUND ")
                analysis_builder.write(
                    Qry.display_matrix(response, spacing=uri_size, output=True, line_feed='.', is_activated=True))

                # INFO TYPE 3: PROPERTY-VALUES OF THE RESOURCES INVOLVED
                analysis_builder.write("\n\nDISAMBIGUATION HELPER ")
                if targets is None:
                    analysis_builder.write(Cls.disambiguate_network(linkset, children))
                else:
                    analysis_builder.write(Cls.disambiguate_network_2(children, targets))

                position = i_cluster[1][St.row]
                if St.annotate in i_cluster[1]:
                    analysis_builder.write("\n\nANNOTATED CLUSTER PROCESS")
                    analysis_builder.write(i_cluster[1][St.annotate])

                # THE CLUSTER
                # print "POSITION: {}".format(position)
                # print "\nMATRIX DISPLAY\n"
                # for i in range(0, position):
                #     resource = (i_cluster[1][St.matrix])[i]
                #     print "\t{}".format(resource[:position])
                    # print "\t{}".format(resource)

                # GENERATING THE NETWORK AS A TUPLE WHERE A TUPLE REPRESENT TWO RESOURCES IN A RELATIONSHIP :-)
                network = []
                for i in range(1, position):
                    for j in range(1, position):
                        if (i, j) in (i_cluster[1][St.matrix_d]) and (i_cluster[1][St.matrix_d])[(i, j)] != 0:
                            r = (i_cluster[1][St.matrix_d])[(i, 0)]
                            c = (i_cluster[1][St.matrix_d])[(0, j)]
                            r_name = "{}:{}".format(i, Ut.get_uri_local_name(r))
                            c_name = "{}:{}".format(j, Ut.get_uri_local_name(c))
                            network += [(r_name, c_name)]
                            # network += [(r_smart, c_smart)]
                # print "\tNETWORK", network

            if print_it:
                print ""
                print analysis_builder.getvalue()

            # SETTING THE DIRECTORY
            if directory:
                # linkset_name = Ut.get_uri_local_name(linkset)
                # date = datetime.date.isoformat(datetime.date.today()).replace('-', '')
                temp_directory = "{}{}".format(directory, "\{}_Analysis_{}\{}\{}_{}\\".format(
                    network_size, date, linkset_name, cluster_size, file_name))
                if not os.path.exists(temp_directory):
                    os.makedirs(temp_directory)

                """""""""""""  PLOTTING """""""""""""
                # FIRE THE DRAWING: Supported formats: eps, pdf, pgf, png, ps, raw, rgba, svg, svgz.
                analysis_builder.write(
                    draw_graph(graph=network,
                               file_path="{}{}.{}".format(temp_directory, "cluster_{}".format(file_name), "pdf"),
                               show_image=False)
                )

                """""""""""""  WRITING TO DISC """""""""""""
                # WRITE TO DISC
                Ut.write_2_disc(file_directory=temp_directory, file_name="cluster_{}".format(file_name, ),
                                data=analysis_builder.getvalue(), extension="txt")
                analysis_builder = Buffer.StringIO()

        if directory:
            automated_decision = metric(network)["AUTOMATED_DECISION"]
            eval_sheet(targets, count_2, "{}_{}".format(cluster_size, file_name),
                       sheet_builder, linkset, children, automated_decision)

        if directory:
            # if len(sheet_builder.getvalue()) > 150 and count_2 == 2:
            if len(sheet_builder.getvalue()) > 150 and len(clusters_0) == count_1:
                tmp_directory = "{}{}".format(directory, "\{}_Analysis_{}\{}\\".format(
                    network_size, date, linkset_name))

                """""""""""""  WRITING CLUSTER SHEET TO DISC """""""""""""
                print "\nWRITING CLUSTER SHEET AT\n\t{}".format(tmp_directory)
                Ut.write_2_disc(file_directory=tmp_directory, file_name="{}_ClusterSheet".format(cluster_size),
                                data=sheet_builder.getvalue(), extension="txt")

        # if count_2 == 2:
        #     break

    print ">>> FOUND: {}".format(count_2)

    if directory is None:
        return "{}\t{}".format(network_size, count_2)

    # print sheet_builder.getvalue()
