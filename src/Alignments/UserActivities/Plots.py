import os
import datetime
import networkx as nx
import cStringIO as Buffer
import Alignments.Query as Qry
import Alignments.Utility as Ut
import Alignments.Settings as St
# import matplotlib.pyplot as plt
import Alignments.UserActivities.Clustering as Cls


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

    node_count = len(nodes)
    average_node_connectivity = nx.average_node_connectivity(g)
    ratio = average_node_connectivity / (len(nodes) - 1)

    edge_discovered = len(graph)
    edge_derived = node_count * (node_count - 1) / 2

    diameter = nx.diameter(g)  # / float(node_count - 1)
    normalised_diameter = round((float(diameter - 1) / float(len(nodes) - 2)), 3)

    bridges = list(nx.bridges(g))
    normalised_bridge = round(float(len(bridges) / float(len(nodes) - 1)), 3)

    closure = round(float(edge_discovered) / float(edge_derived), 3)
    normalised_closure = round(1 - closure, 2)

    conclusion = round((normalised_closure * normalised_diameter + normalised_bridge) / 2, 3)
    interpretation = round((normalised_closure + normalised_diameter + normalised_bridge) / 3, 3)

    # set_cycles = []
    # size = 0
    # for item in cycles:
    #     if len(item) > size:
    #         size = len(item)
    #
    # for item in cycles:
    #     if len(item) == size:
    #         set_cycles += [frozenset(item)]

    """""""""""""""""""""""""""""""""""""""
    RETURN MATRIX COMPUTATIONS
    """""""""""""""""""""""""""""""""""""""
    analysis_builder.write("\n\nNETWORK ANALYSIS")
    analysis_builder.write("\n\tNETWORK {}".format(graph))
    analysis_builder.write("\n\t{:31} : {}".format("MAX DISTANCE:", closure))
    # analysis_builder.write("\n\t{:31} : {}".format("CYCLES", nbr_cycles))
    # if cycles > 0:
    #     analysis_builder.write("\n\t{:31} : {}".format("BIGGEST CYCLES", set(set_cycles)))
    analysis_builder.write("\n\t{:31} : {}".format("BRIDGES", bridges))
    analysis_builder.write("\n\t{:31} : {}".format("MAXIMUM POSSIBLE CONNECTIVITY", len(nodes) - 1))
    analysis_builder.write("\n\t{:31} : {}".format("AVERAGE NODE CONNECTIVITY", average_node_connectivity))
    analysis_builder.write("\n\t{:31} : {}".format("AVERAGE NODE CONNECTIVITY RATIO", ratio))

    # test = dict()
    # for item in cycles:
    #     if len(item) == size:
    #         if set(item) not in test:
    #             test[set(item)] = item
    #
    # print test
    # show graph
    # conclusion = (1 - closure) * (diameter - 1) + len(bridges)
    # analysis_builde_2.write("\nCycles [{}] Bridges [{}]".format(nbr_cycles, len(bridges)))

    """""""""""""""""""""""""""""""""""""""
    PRINTING MATRIX COMPUTATIONS
    """""""""""""""""""""""""""""""""""""""
    analysis_builder_2.write(
        "\nAverage Degree [{}] \nBridges [{}] normalised to [{}]\nDiameter [{}]  normalised to [{}]"
        "\nClosure [{}/{}][{}] normalised to [{}]\n>>> Decision Support [I_1={}] [I_2={}]".
        format(average_node_connectivity, len(bridges), normalised_bridge,  diameter, normalised_diameter,
               edge_discovered, edge_derived, closure, normalised_closure, conclusion, interpretation))

    # analysis_builde_2.write("\nConnectivity: AverageDegree [{}] MaxDegree [{}] "
    #                         "TransitivityClosure [{}] Bridges [{}] Diameter [{}]".format(
    #     average_node_connectivity, len(nodes) - 1, max_distance, len(bridges), diameter))

    if ratio == 1:
        analysis_builder_2.write("\n\nDiagnose: VERY GOOD")
    elif average_node_connectivity == 2 or len(bridges) == 0:
        analysis_builder_2.write("\n\nDiagnose: ACCEPTABLE")
    # elif nbr_cycles == 0:
    #     analysis_builde_2.write("\n\nDiagnose: NEED INVESTIGATION")
    elif len(bridges) > 0:
        analysis_builder_2.write("\n\nDiagnose: NEED BRIDGE INVESTIGATION")


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


def metric(graph):

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
    ratio = average_node_connectivity / (len(nodes) - 1)

    edge_discovered = len(graph)
    edge_derived = node_count * (node_count - 1) / 2

    diameter = nx.diameter(g)  # / float(node_count - 1)
    normalised_diameter = round((float(diameter - 1) / float(len(nodes) - 2)), 3)

    bridges = list(nx.bridges(g))
    normalised_bridge = round(float(len(bridges) / float(len(nodes) - 1)), 3)

    closure = round(float(edge_discovered) / float(edge_derived), 3)
    normalised_closure = round(1 - closure, 2)

    conclusion = round((normalised_closure * normalised_diameter + normalised_bridge) / 2, 3)
    interpretation = round((normalised_closure + normalised_diameter + normalised_bridge) / 3, 3)

    """""""""""""""""""""""""""""""""""""""
    PRINTING MATRIX COMPUTATIONS
    """""""""""""""""""""""""""""""""""""""
    analysis_builder.write(
        "\nAverage Degree [{}] \nBridges [{}] normalised to [{}]\nDiameter [{}]  normalised to [{}]"
        "\nClosure [{}/{}][{}] normalised to [{}]\n>>> Decision Support [I_1={}] [I_2={}]".
        format(average_node_connectivity, len(bridges), normalised_bridge,  diameter, normalised_diameter,
               edge_discovered, edge_derived, closure, normalised_closure, conclusion, interpretation))

    if ratio == 1:
        analysis_builder.write("\n\nDiagnose: VERY GOOD")
    elif average_node_connectivity == 2 or len(bridges) == 0:
        analysis_builder.write("\n\nDiagnose: ACCEPTABLE")
    elif len(bridges) > 0:
        analysis_builder.write("\n\nDiagnose: NEED BRIDGE INVESTIGATION")


    return analysis_builder.getvalue()


def cluster_d_test(linkset, network_size=3, targets=None,
                   directory=None, greater_equal=True, print_it=False, limit=None, activated=False):

    print "\nLINK NETWORK INVESTIGATION"
    if activated is False:
        print "\tTHE FUNCTION I NOT ACTIVATED"
        return ""

    count_1 = 0
    count_2 = 0
    analysis_builder = Buffer.StringIO()

    print "\n"

    linkset = linkset.strip()

    # RUN THE CLUSTER
    clusters_0 = Cls.links_clustering(linkset, limit)

    for i_cluster in clusters_0.items():

        # network = []
        resources = ""
        uri_size = 0
        count_1 += 1
        children = i_cluster[1][St.children]
        # if "<http://www.grid.ac/institutes/grid.10493.3f>" not in children:
        #     continue

        check = len(children) >= network_size if greater_equal else len(children) == network_size

        # NETWORK OF A PARTICULAR SIZE
        if check:
            count_2 += 1
            # file_name = i_cluster[0]

            # 2: FETCHING THE CORRESPONDENTS
            smallest_hash = float('inf')
            for child in children:
                hashed = hash(child)
                if hashed <= smallest_hash:
                    smallest_hash = hashed
                # GENERAL INFO 1: RESOURCES INVOLVED
                analysis_builder.write("\t{}\n".format(child))
                use = "<{}>".format(child) if Ut.is_nt_format(child) is not True else child
                resources += "\n\t\t{}".format(use)
                if len(child) > uri_size:
                    uri_size = len(child)

            # MAKE SURE THE FILE NAME OF THE CLUSTER IS ALWAYS THE SAME
            file_name = "{}".format(str(smallest_hash).replace("-", "N")) if str(
                smallest_hash).startswith("-") \
                else "P{}".format(smallest_hash)

            # QUERY FOR FETCHING ALL LINKED RESOURCES FROM THE LINKSET
            query = """
            SELECT DISTINCT ?lookup ?object
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
            }}
                        """.format(resources, linkset)
            # print query

            # THE RESULT OF THE QUERY ABOUT THE LINKED RESOURCES
            response = Qry.sparql_xml_to_matrix(query)

            # GENERAL INFO 2:
            info = "CLUSTER [{}] NAME [{}] SIZE [{}]".format(count_1, file_name, len(children))
            print "{:>5} {}".format(count_2, info)
            analysis_builder.write("\n{}\n".format(info))
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
                        # r_name = r[-25:]
                        # c_name = c[-25:]
                        r_name = "{}:{}".format(i, Ut.get_uri_local_name(r))
                        c_name = "{}:{}".format(j, Ut.get_uri_local_name(c))
                        # r_smart = {"key": i, "name": r_name}
                        # c_smart = {"key": j, "name": c_name}
                        network += [(r_name, c_name)]
                        # network += [(r_smart, c_smart)]
            # print "\tNETWORK", network

            if print_it:
                print ""
                print analysis_builder.getvalue()

            # SETTING THE DIRECTORY
            if directory:
                linkset_name = Ut.get_uri_local_name(linkset)
                date = datetime.date.isoformat(datetime.date.today()).replace('-', '')
                temp_directory = "{}{}".format(directory, "\{}_Analysis_{}\{}\{}_{}\\".format(
                    network_size, date, linkset_name, len(children), file_name))
                if not os.path.exists(temp_directory):
                    os.makedirs(temp_directory)

                # FIRE THE DRAWING: Supported formats: eps, pdf, pgf, png, ps, raw, rgba, svg, svgz.
                analysis_builder.write(
                    draw_graph(graph=network,
                               file_path="{}{}.{}".format(temp_directory, "cluster_{}".format(file_name), "pdf"),
                               show_image=False)
                )

                # WRITE TO DISC
                Ut.write_2_disc(file_directory=temp_directory, file_name="cluster_{}".format(file_name, ),
                                data=analysis_builder.getvalue(), extension="txt")
                analysis_builder = Buffer.StringIO()
                # exit(0)

    print ">>> FOUND: {}".format(count_2)
