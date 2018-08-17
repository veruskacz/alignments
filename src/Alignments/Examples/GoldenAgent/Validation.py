import datetime
from os.path import join
import Alignments.Utility as Ut
import Alignments.Query as Qry
from Alignments.Utility import get_uri_local_name_plus as local_name
from Alignments.UserActivities.Clustering import links_clustering, list_extended_clusters
from Alignments.UserActivities.Plots import metric


# CLUSTER ID
# CLUSTER SIZE
# MACHINE EVAL
# HUMAN EVAL
# RESOURCES



def investigate_resources(data, resources):

    # DATASET AND THE PROPERTIES OF INTEREST. EACH PROPERTY CAN BE PROVIDED WITH AN ALTERNATIVE NAME
    # data = {
    #     'dataset-1': {
    #         'mandatory': [('property-1', 'name'), ('property-10', ""), ('property-15', '')],
    #         'optional': [('property-00', 'country'), ]
    #     },
    #     'dataset-2': {
    #         'mandatory': [('property-2', 'name'), ('property-23', ""), ('property-30', "")],
    #         'optional': []
    #     },
    #     'dataset-3': {
    #         'mandatory': [('property-3', 'name'), ('property-36', ""), ('property-33', "")],
    #         'optional': []
    #     }
    # }

    # THE LIST OF RESOURCES TO INVESTIGATE
    # resource = ['resource-1', 'resource-2', 'resource-3']

    # QUERY TEMPLE EXAMPLE
    """
    SELECT *
    {
        # LIST OR RESOURCES TO INVESTIGATE
        VALUES ?resource { resource-1 resource-2 resource-3 }

        {
            GRAPH <dataset-2>
            {
				BIND( <dataset-2> as ?dataset)
				?resource <property-2> ?name .
				?resource <property-23> ?dataset-2_property-23 .
				?resource <property-30> ?dataset-2_property-30 .
            }
        }	UNION

        {
            GRAPH <dataset-3>
            {
				BIND( <dataset-3> as ?dataset)
				?resource <property-3> ?name .
				?resource <property-36> ?dataset-3_property-36 .
				?resource <property-33> ?dataset-3_property-33 .
            }
        }	UNION

        {
            GRAPH <dataset-1>
            {
				BIND( <dataset-1> as ?dataset)
				?resource <property-1> ?name .
				?resource <property-10> ?dataset-1_property-10 .
				?resource <property-15> ?dataset-1_property-15 .
				OPTIONAL { ?resource <property-00> ?country . }
            }
        }
    }
    """

    count_union = 0
    sub_query = ""

    template_1 =     """\t{}
        {{
            GRAPH {}
            {{ \n\t\t\t\t{}\n{}{}
            }}
        }}"""

    template_2 = """
    SELECT DISTINCT *
    {{
        # LIST OR RESOURCES TO INVESTIGATE
        VALUES ?resource {{ {} }}
        {}
    }}

    """

    # CONVERTING THE LIST INTO A SPACE SEPARATED LIST
    resource_enumeration = " ".join( Ut.to_nt_format(item) for item in resources)

    for dataset, dictionary in data.items():

        mandatory = dictionary['mandatory']
        optional = dictionary['optional']

        # GENERATE THE SUB-QUERY FOR MANDATORY PROPERTIES
        sub_mandatory = "\n".join(
            "\t\t\t\t?resource {0} ?{1} .".format(
                Ut.to_nt_format(uri), alternative if len(alternative) > 0 else
                "{}_{}".format(local_name(dataset), local_name(uri)) ) for uri, alternative in mandatory)

        # GENERATE THE SUB-QUERY FOR OPTIONAL PROPERTIES
        if len(optional) > 0:
            sub_optional = "\n".join(
                "\n\t\t\t\tOPTIONAL {{ ?resource {0} ?{1} . }}".format(
                    Ut.to_nt_format(uri), alternative if len(alternative) > 0 else
                    "{}_{}".format(local_name(dataset), local_name(uri))) for uri, alternative in optional)
        else:
            sub_optional = ""

        # BIND THE DATASET TO HAVE IT IN THE SELECT
        bind = "BIND( {} as ?dataset)".format(Ut.to_nt_format(dataset))

        # ACCUMULATE THE SUB-QUERIES
        sub_query += template_1.format(
            "UNION\n" if count_union > 0 else "", Ut.to_nt_format(dataset), bind, sub_mandatory, sub_optional)
        count_union += 1

    # THE FINAL QUERY
    query = template_2.format(resource_enumeration, sub_query)
    # print query
    # Qry.display_result(query, is_activated=True)

    response = Qry.sparql_xml_to_matrix(query)

    if response is None:
        return None
    else:
        return response['result']


def write_record(size, record_format, matrix, writer, cluster_id="", separator_size=40, machine_decision=""):

    count = 0
    format_template = "{{:{}}}".format(separator_size)
    # print format_template

    if matrix is not None:
        for record in matrix:
            count += 1

            # print record_line
            if count == 1:
                record_line = " | ".join(
                    format_template.format("") if item is None or len(item) == 0
                    else format_template.format(local_name(item.upper())) for item in record)
                writer.write(record_format.format(
                    cluster_id, size, "-{}-".format(machine_decision), "--", "", "", record_line))
            else:
                record_line = " | ".join(
                    format_template.format("") if item is None or len(item) == 0
                    else format_template.format(local_name(item)) for item in record)
                writer.write(record_format.format("", "", "", "", "--", "--", record_line))

    else:
        print "THE MATRIX IS EMPTY"


def generate_sheet(data, directory, graph, serialisation_dir, related_alignment=None, separator_size=40):

    count = 0
    extended = None
    heder_separator_size = 23
    if related_alignment is None:
        clusters = links_clustering( graph=graph, serialisation_dir=serialisation_dir)
    else:
        clusters, extended = links_clustering( graph=graph, serialisation_dir=serialisation_dir, related_linkset=graph)

    print extended

    # extended = list_extended_clusters(graph, node2cluster, related_linkset, serialisation_dir, reset=False)

    # FILE DATE
    date = datetime.date.isoformat(datetime.date.today()).replace('-', '')

    # THE WRITER
    writer = open(join(directory, "EvalSheet_{}.txt".format(date)), 'wb')

    # RECORD FORMAT
    record_format = "{{:{0}}}{{:<{0}}}{{:<{0}}}{{:<{0}}}{{:<{0}}}{{:<{0}}}{{:<{0}}}\n".format(heder_separator_size)

    # RECORD HEADER
    header = record_format.format(
            "CLUSTER-ID", "CLUSTER-SIZE", "MACHINE-EVAL", "HUMAN-EVAL", "NOT GOOD", "CYCLE", "RESOURCES")

    # WRITE THE FILE HEADER
    writer.write(header)
    print ""

    # ITERATE THROUGH THE CLUSTERS
    for cluster_id, cluster in clusters.items():

        count += 1
        nodes = cluster['nodes']

        # COMPUTE THE MACHINE EVALUATION
        decision = metric(cluster['links'])["AUTOMATED_DECISION"]

        # FETCH DATA ABOUT THE PROVIDED RESOURCES
        matrix = investigate_resources(data, resources=nodes)

        # WRITE THE FETCHED DATA TO SOURCE
        write_record(len(nodes), record_format=record_format, matrix=matrix, writer=writer,
                     cluster_id=cluster_id, machine_decision=decision, separator_size=separator_size)

        # ADD A NEW LINE
        writer.write("\n")


        if count % 10 == 0 or count == 1:
            print "{:6} {:25}{:6}".format(count, cluster_id, decision)

        if count == 20:
            break

    writer.close()


def process_cluster(data, resources, network, writer, with_header, machine_decision, separator_size=20, cluster_id=""):

    # RECORD ITEM SEPARATOR
    # separator_size = 20

    # FILE DATE
    # date = datetime.date.isoformat(datetime.date.today()).replace('-', '')

    # THE WRITER
    # writer = open(join(directory, "EvalSheet_{}.txt".format(date)), 'wb')

    # RECORD FORMAT
    record_format = "{{:{0}}}{{:<{0}}}{{:<{0}}}{{:<{0}}}{{:<{0}}}{{:<{0}}}{{:<{0}}}\n".format(separator_size)
    # print record_format

    # THE HEADER OF THE FILE
    # header = record_format.format(
    #     "CLUSTER-ID", "CLUSTER-SIZE", "MACHINE-EVAL", "HUMAN-EVAL", "NOT GOOD", "CYCLE", "RESOURCES")
    # writer.write(header)

    # FETCH DATA ABOUT THE PROVIDED RESOURCES
    matrix = investigate_resources(data, resources)

    decision = metric(network)["AUTOMATED_DECISION"]

    # WRITE THE FETCHED DATA TO SOURCE
    write_record(record_format=record_format, matrix=matrix, writer=writer,
                 cluster_id=cluster_id, machine_decision=machine_decision)
    writer.write("\n")

    # END OF FILE
    # writer.close()

